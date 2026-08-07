"""
RAGAS test suite for RAG quality evaluation with Gemini.

Metrics:
- Faithfulness (threshold 0.80)
- Answer Relevancy (threshold 0.80)

Exports results in DeepEval-compatible InfluxDB line protocol format for Testkube Insights plotting.
"""

import os
os.environ["RAGAS_DO_NOT_TRACK"] = "true"

import time
import math
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()

import pytest
import yaml

from datasets import Dataset
from ragas import evaluate
from ragas.metrics import Faithfulness, AnswerRelevancy
from ragas.run_config import RunConfig

from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    GoogleGenerativeAIEmbeddings,
)

from src.rag.rag_pipeline import get_pipeline

TEST_CASES_PATH = Path(__file__).parent / "fixtures" / "rag_test_cases.yml"
TEST_RESULTS = []


def load_test_cases():
    if not TEST_CASES_PATH.exists():
        raise FileNotFoundError(f"Test cases file not found at {TEST_CASES_PATH}")
    with open(TEST_CASES_PATH, "r") as f:
        data = yaml.safe_load(f)
    if not data or "test_cases" not in data:
        raise ValueError("Invalid test cases format")
    return data["test_cases"]


def get_gemini_clients():
    llm = ChatGoogleGenerativeAI(
        model="gemini-3.1-flash-lite",
        google_api_key=os.environ["GOOGLE_API_KEY"],
        temperature=0,
    )
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=os.environ["GOOGLE_API_KEY"],
    )
    return llm, embeddings


def retry_with_backoff(func, max_retries=3, base_delay=2):
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            delay = base_delay * (2 ** attempt)
            print(f"Retry {attempt + 1}/{max_retries}: {str(e)[:100]}")
            print(f"Waiting {delay}s...")
            time.sleep(delay)


@pytest.mark.parametrize("test_case", load_test_cases(), ids=lambda tc: tc["id"])
def test_rag_quality_gate_ragas(test_case):
    
    pipeline = get_pipeline(eval_mode=True)
    result = retry_with_backoff(lambda: pipeline.query(test_case["query"]))

    dataset = Dataset.from_dict({
        "question": [test_case["query"]],
        "answer": [result["answer"]],
        "contexts": [result["retrieved_context"]],
        "ground_truth": [test_case["expected_answer"]],
    })

    gemini_llm, gemini_embeddings = get_gemini_clients()

    metrics_results = retry_with_backoff(
        lambda: evaluate(
            dataset,
            metrics=[
                Faithfulness(llm=gemini_llm),
                AnswerRelevancy(llm=gemini_llm, embeddings=gemini_embeddings),
            ],
            run_config=RunConfig(max_workers=1),
            raise_exceptions=False,
        )
    )

    faith_score = metrics_results["faithfulness"][0]
    relevancy_score = metrics_results["answer_relevancy"][0]

    # Handle NaN values
    if faith_score is None or math.isnan(float(faith_score)):
        faith_score = 0.0
    if relevancy_score is None or math.isnan(float(relevancy_score)):
        relevancy_score = 0.0

    faith_score = float(faith_score)
    relevancy_score = float(relevancy_score)

    passed = faith_score >= 0.80 and relevancy_score >= 0.80

    TEST_RESULTS.append({
        "id": test_case["id"],
        "category": test_case.get("category", "general"),
        "faithfulness": faith_score,
        "answer_relevancy": relevancy_score,
        "passed": passed,
    })

    print(f"\n{test_case['id']}:")
    print(f"  Faithfulness:     {faith_score:.2f} (threshold: 0.80)")
    print(f"  Answer Relevancy: {relevancy_score:.2f} (threshold: 0.80)")

    assert faith_score >= 0.80, f"Faithfulness failed: {faith_score:.2f} < 0.80"
    assert relevancy_score >= 0.80, f"Answer Relevancy failed: {relevancy_score:.2f} < 0.80"


def calculate_stats(scores):
    """Calculate mean, min, max, std"""
    if not scores:
        return {}
    valid_scores = [s for s in scores if not math.isnan(s)]
    if not valid_scores:
        return {}
    
    mean = sum(valid_scores) / len(valid_scores)
    min_val = min(valid_scores)
    max_val = max(valid_scores)
    variance = sum((x - mean) ** 2 for x in valid_scores) / len(valid_scores)
    std = math.sqrt(variance)
    
    return {
        "mean": mean,
        "min": min_val,
        "max": max_val,
        "std": std,
        "count": len(valid_scores),
    }


def generate_influxdb_lines(results, suite_name="rag-quality-gate"):
    """
    Generate InfluxDB line protocol in DeepEval-compatible format.
    RAGAS metrics exported for Testkube Insights visualization.
    
    Format:
    ragas,metric=faithfulness,suite=rag-quality-gate \
      mean_score=0.98125,min_score=0.875,max_score=1.0,std_score=0.040685,\
      passed=20i,failed=0i,tests=20i,errors=0i
    """
    lines = []

    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    failed = total - passed
    errors = 0

    # Overall faithfulness
    faith_scores = [r["faithfulness"] for r in results]
    faith_stats = calculate_stats(faith_scores)

    if faith_stats:
        line = (
            f"ragas,metric=faithfulness,suite={suite_name} "
            f"mean_score={faith_stats['mean']:.6f},"
            f"min_score={faith_stats['min']:.6f},"
            f"max_score={faith_stats['max']:.6f},"
            f"std_score={faith_stats['std']:.6f},"
            f"passed={passed}i,failed={failed}i,tests={total}i,errors={errors}i"
        )
        lines.append(line)

    # Overall answer relevancy
    relevancy_scores = [r["answer_relevancy"] for r in results]
    relevancy_stats = calculate_stats(relevancy_scores)

    if relevancy_stats:
        line = (
            f"ragas,metric=answer_relevancy,suite={suite_name} "
            f"mean_score={relevancy_stats['mean']:.6f},"
            f"min_score={relevancy_stats['min']:.6f},"
            f"max_score={relevancy_stats['max']:.6f},"
            f"std_score={relevancy_stats['std']:.6f},"
            f"passed={passed}i,failed={failed}i,tests={total}i,errors={errors}i"
        )
        lines.append(line)

    # Overall summary (no metric tag)
    overall_line = (
        f"ragas,suite={suite_name} "
        f"passed={passed}i,failed={failed}i,tests={total}i,errors={errors}i"
    )
    lines.append(overall_line)

    # Per-category metrics
    by_category = defaultdict(list)
    for result in results:
        by_category[result["category"]].append(result)

    for category in sorted(by_category.keys()):
        category_results = by_category[category]
        category_passed = sum(1 for r in category_results if r["passed"])
        category_failed = len(category_results) - category_passed
        category_total = len(category_results)

        # Category faithfulness
        category_faith = [r["faithfulness"] for r in category_results]
        faith_cat_stats = calculate_stats(category_faith)

        if faith_cat_stats:
            cat_line = (
                f"ragas,metric=faithfulness,suite={suite_name},category={category} "
                f"mean_score={faith_cat_stats['mean']:.6f},"
                f"min_score={faith_cat_stats['min']:.6f},"
                f"max_score={faith_cat_stats['max']:.6f},"
                f"std_score={faith_cat_stats['std']:.6f},"
                f"passed={category_passed}i,failed={category_failed}i,"
                f"tests={category_total}i,errors=0i"
            )
            lines.append(cat_line)

        # Category answer relevancy
        category_relevancy = [r["answer_relevancy"] for r in category_results]
        relevancy_cat_stats = calculate_stats(category_relevancy)

        if relevancy_cat_stats:
            cat_line = (
                f"ragas,metric=answer_relevancy,suite={suite_name},category={category} "
                f"mean_score={relevancy_cat_stats['mean']:.6f},"
                f"min_score={relevancy_cat_stats['min']:.6f},"
                f"max_score={relevancy_cat_stats['max']:.6f},"
                f"std_score={relevancy_cat_stats['std']:.6f},"
                f"passed={category_passed}i,failed={category_failed}i,"
                f"tests={category_total}i,errors=0i"
            )
            lines.append(cat_line)

    return lines


@pytest.fixture(scope="session", autouse=True)
def print_session_summary():
    yield

    if not TEST_RESULTS:
        return

    print("\n" + "=" * 80)
    print("RAGAS EVALUATION SUMMARY")
    print("=" * 80)

    passed = sum(1 for r in TEST_RESULTS if r["passed"])
    total = len(TEST_RESULTS)
    pass_rate = (passed / total * 100) if total > 0 else 0

    print(f"\nOverall: {passed}/{total} tests passed ({pass_rate:.1f}%)\n")

    # Overall mean scores
    faith_scores = [r["faithfulness"] for r in TEST_RESULTS]
    relevancy_scores = [r["answer_relevancy"] for r in TEST_RESULTS]
    
    faith_stats = calculate_stats(faith_scores)
    relevancy_stats = calculate_stats(relevancy_scores)

    print("OVERALL MEAN SCORES")
    print("-" * 80)

    if faith_stats:
        print(f"Faithfulness:")
        print(f"  Mean:   {faith_stats['mean']:.4f}")
        print(f"  Min:    {faith_stats['min']:.4f}")
        print(f"  Max:    {faith_stats['max']:.4f}")
        print(f"  Std:    {faith_stats['std']:.4f}")

    if relevancy_stats:
        print(f"\nAnswer Relevancy:")
        print(f"  Mean:   {relevancy_stats['mean']:.4f}")
        print(f"  Min:    {relevancy_stats['min']:.4f}")
        print(f"  Max:    {relevancy_stats['max']:.4f}")
        print(f"  Std:    {relevancy_stats['std']:.4f}")

    # Per-category breakdown
    print("\n" + "-" * 80)
    print("PER-CATEGORY BREAKDOWN")
    print("-" * 80)

    by_category = defaultdict(list)
    for result in TEST_RESULTS:
        by_category[result["category"]].append(result)

    for category in sorted(by_category.keys()):
        category_results = by_category[category]
        category_passed = sum(1 for r in category_results if r["passed"])
        category_total = len(category_results)
        category_pass_rate = (category_passed / category_total * 100) if category_total > 0 else 0

        print(f"\n[{category.upper()}] {category_passed}/{category_total} passed ({category_pass_rate:.1f}%)")

    # Test-level details
    print("\n" + "-" * 80)
    print("TEST-LEVEL DETAILS")
    print("-" * 80)
    print(f"{'Test ID':<20} {'Category':<15} {'Faith':<10} {'Relev':<10} {'Status':<8}")
    print("-" * 80)

    for result in TEST_RESULTS:
        status = "PASS" if result["passed"] else "FAIL"
        print(
            f"{result['id']:<20} {result['category']:<15} "
            f"{result['faithfulness']:<10.4f} {result['answer_relevancy']:<10.4f} {status:<8}"
        )

    # Export to files
    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)

    # InfluxDB line protocol export (DeepEval-compatible format)
    influx_file = results_dir / "ragas_metrics.txt"
    influxdb_lines = generate_influxdb_lines(TEST_RESULTS)

    with open(influx_file, "w") as f:
        for line in influxdb_lines:
            f.write(line + "\n")

    # JSON export (for Testkube ingestion)
    json_file = results_dir / "ragas_results.json"
    flat_results = []

    # Overall metrics
    overall_metrics = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "suite": "rag-quality-gate",
        "type": "overall",
        "total_tests": total,
        "passed_tests": passed,
        "failed_tests": total - passed,
        "pass_rate": pass_rate,
    }

    if faith_stats:
        overall_metrics.update({
            "faithfulness_mean": faith_stats["mean"],
            "faithfulness_min": faith_stats["min"],
            "faithfulness_max": faith_stats["max"],
            "faithfulness_std": faith_stats["std"],
        })

    if relevancy_stats:
        overall_metrics.update({
            "answer_relevancy_mean": relevancy_stats["mean"],
            "answer_relevancy_min": relevancy_stats["min"],
            "answer_relevancy_max": relevancy_stats["max"],
            "answer_relevancy_std": relevancy_stats["std"],
        })

    flat_results.append(overall_metrics)

    # Per-category metrics
    for category in sorted(by_category.keys()):
        category_results = by_category[category]
        category_passed = sum(1 for r in category_results if r["passed"])
        category_total = len(category_results)

        category_faith = [r["faithfulness"] for r in category_results]
        category_relevancy = [r["answer_relevancy"] for r in category_results]

        faith_cat_stats = calculate_stats(category_faith)
        relevancy_cat_stats = calculate_stats(category_relevancy)

        category_metric = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "suite": "rag-quality-gate",
            "category": category,
            "type": "category",
            "total_tests": category_total,
            "passed_tests": category_passed,
            "failed_tests": category_total - category_passed,
            "pass_rate": (category_passed / category_total * 100) if category_total > 0 else 0,
        }

        if faith_cat_stats:
            category_metric.update({
                "faithfulness_mean": faith_cat_stats["mean"],
                "faithfulness_min": faith_cat_stats["min"],
                "faithfulness_max": faith_cat_stats["max"],
                "faithfulness_std": faith_cat_stats["std"],
            })

        if relevancy_cat_stats:
            category_metric.update({
                "answer_relevancy_mean": relevancy_cat_stats["mean"],
                "answer_relevancy_min": relevancy_cat_stats["min"],
                "answer_relevancy_max": relevancy_cat_stats["max"],
                "answer_relevancy_std": relevancy_cat_stats["std"],
            })

        flat_results.append(category_metric)

    # Individual test results
    for result in TEST_RESULTS:
        test_metric = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "suite": "rag-quality-gate",
            "test_id": result["id"],
            "category": result["category"],
            "type": "test",
            "faithfulness": result["faithfulness"],
            "answer_relevancy": result["answer_relevancy"],
            "passed": result["passed"],
        }
        flat_results.append(test_metric)

    with open(json_file, "w") as f:
        json.dump(flat_results, f, indent=2, default=str)

    # Print exports
    print("\n" + "=" * 80)
    print("EXPORTS GENERATED")
    print("=" * 80)
    print(f"\nInfluxDB Line Protocol (DeepEval-compatible for plotting):")
    print(f"  {influx_file}")
    print(f"\nJSON Results (for Testkube Insights ingestion):")
    print(f"  {json_file}")

    print("\n" + "-" * 80)
    print("INFLUXDB LINE PROTOCOL METRICS")
    print("-" * 80)
    for line in influxdb_lines:
        print(line)

    print("=" * 80)
