# RAGAS RAG Quality Evaluation Suite

Complete setup for evaluating your RAG pipeline quality using RAGAS metrics with Gemini.

## What's Included

- **rag_pipeline.py** - Updated RAG pipeline with eval_mode support
- **test_rag.py** - RAGAS test suite with 20 test cases, retry logic, and summary reporting
- **rag_test_cases.yml** - 20 pre-configured test cases
- **conftest.py** - Pytest configuration and setup
- **requirements.txt** - All Python dependencies
- **.env.example** - Environment variable template

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Then edit `.env` and add your Google API key:

```
GOOGLE_API_KEY=your-actual-api-key-here
```

Get your API key from: https://makersuite.google.com/app/apikey

### 3. Create Directory Structure

Ensure your project has this structure:

```
project/
├── src/
│   └── rag/
│       ├── __init__.py
│       ├── rag_pipeline.py          (updated file)
│       ├── prompts.py               (your existing prompts)
│       └── ...
├── tests/
│   ├── __init__.py
│   ├── conftest.py                  (new file)
│   ├── test_rag.py                  (updated file)
│   └── fixtures/
│       └── rag_test_cases.yml        (new file)
├── .env                             (create from .env.example)
├── .env.example                     (reference)
├── requirements.txt                 (new file)
└── ...
```

## Running the Tests

### Run All Tests

```bash
pytest tests/test_rag.py -v
```

### Run Specific Test

```bash
pytest tests/test_rag.py::test_rag_quality_gate_ragas[test_refund_policy_basic] -v
```

### Run With Timeout (useful for API issues)

```bash
pytest tests/test_rag.py -v --timeout=300
```

## What Changed

### 1. **Embeddings Support**
   - Added `gemini_embeddings` to the RAGAS evaluate function
   - Required for proper context recall and relevancy evaluation

### 2. **Eval Mode**
   - Pipeline now supports `eval_mode=True` parameter
   - Automatically sets temperature to 0.0 for consistent evaluation
   - Production mode (default) keeps temperature at 0.7

### 3. **Retry Logic**
   - Both query and evaluation phases include exponential backoff
   - Handles Google API rate limits gracefully
   - Max 3 retries with delays of 1s, 2s, 4s

### 4. **Better Error Handling**
   - Clear error messages for pipeline initialization
   - Timeout handling in pytest configuration
   - API key validation at session start

### 5. **Session Summary Report**
   - Prints detailed table of all test results
   - Shows aggregate metrics across all 20 tests
   - Pass/fail indicators for each metric threshold

## Test Case Structure

Each test case in `rag_test_cases.yml` has:

```yaml
- id: "unique_test_identifier"
  query: "User question to ask RAG"
  expected_answer: "Ground truth answer the RAG should provide"
```

The 20 included test cases cover:
- Refund policy (3 tests)
- Shipping options (4 tests)
- Payment methods (3 tests)
- Order tracking (2 tests)
- Password reset (3 tests)
- Bulk orders (3 tests)
- Mixed scenarios (2 tests)

## RAGAS Metrics Explained

### Faithfulness (threshold: 0.80)
- Measures if the answer is grounded in retrieved context
- Prevents hallucinations
- Score range: 0.0 - 1.0

### Answer Relevancy (threshold: 0.80)
- Measures if the answer addresses the user's question
- Prevents off-topic responses
- Score range: 0.0 - 1.0

### Context Recall (threshold: 0.75)
- Measures if retrieved context contains necessary information
- Lower threshold (0.75) because sometimes relevant info is implicit
- Score range: 0.0 - 1.0

## Example Output

```
test_refund_policy_basic:
  Faithfulness:     0.92 (threshold: 0.80)
  Answer Relevancy: 0.88 (threshold: 0.80)
  Context Recall:   0.95 (threshold: 0.75)

...

======================================================================
RAGAS EVALUATION SUMMARY
======================================================================

Overall: 20/20 tests passed

Test ID                        Faithful     Relevant     Recall
----------------------------------------------------------------------
test_refund_policy_basic       0.92 ✓        0.88 ✓       0.95 ✓
test_refund_timeframe          0.89 ✓        0.91 ✓       0.93 ✓
...

Average Scores:
  Faithfulness:     0.88
  Answer Relevancy: 0.86
  Context Recall:   0.82
======================================================================
```

## Customizing Test Cases

To add more test cases:

1. Open `tests/fixtures/rag_test_cases.yml`
2. Add a new entry under `test_cases:`
3. Use a unique `id` (no spaces, kebab-case)
4. Provide `query` and `expected_answer`
5. Run tests as usual

Example:

```yaml
- id: "test_custom_scenario"
  query: "Can I combine my refund with store credit?"
  expected_answer: "Your expected ground truth here."
```

## Troubleshooting

### "GOOGLE_API_KEY not set"
- Make sure `.env` file exists in project root
- Verify the key is set correctly
- Run: `echo $GOOGLE_API_KEY` to check

### Rate Limit Errors
- Tests include automatic retry with backoff
- If still failing, increase `max_retries` in `test_rag.py`
- Or add delays between test runs

### Chroma Vector Store Issues
- Chroma creates a local database by default
- Clear with: `rm -rf .chroma/` if corrupted
- Pipeline will recreate on next run

### Low RAGAS Scores
- Increase your knowledge base quality
- Improve prompt templates in `src/rag/prompts.py`
- Adjust chunk size/overlap in RAG pipeline
- Review retrieved context relevance

## API Cost Considerations

Running 20 tests involves:
- 20 RAG queries (using Gemini Flash)
- 60 evaluation calls (3 metrics × 20 tests, using Gemini Flash + embeddings)
- Estimate: ~$0.50-$1.00 per full test run

Use `--timeout=300` to prevent accidental long runs.

## Next Steps

1. Customize `rag_test_cases.yml` with your actual Q&A scenarios
2. Run: `pytest tests/test_rag.py -v`
3. Review the summary report
4. Iterate on RAG pipeline if scores are below thresholds
5. Integrate into CI/CD for continuous quality monitoring

## Support

- RAGAS docs: https://docs.ragas.io/
- LangChain docs: https://python.langchain.com/
- Google Gemini docs: https://ai.google.dev/
