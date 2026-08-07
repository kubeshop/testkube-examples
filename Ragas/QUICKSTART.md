# Quick Start: 5 Minutes to Running RAGAS Tests

## Step 1: Copy Files (30 seconds)

```
your-project/
├── src/rag/
│   └── rag_pipeline.py              # REPLACE with updated version
├── tests/
│   ├── conftest.py                  # NEW
│   ├── test_rag.py                  # REPLACE with updated version
│   └── fixtures/
│       └── rag_test_cases.yml        # NEW
├── requirements.txt                 # NEW
└── .env                             # NEW (copy from .env.example)
```

## Step 2: Install & Setup (2 minutes)

```bash
# Install packages
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env and paste your Google API key
nano .env  # or use your editor
```

Get API key from: https://makersuite.google.com/app/apikey

## Step 3: Run Tests (2-3 minutes)

```bash
pytest tests/test_rag.py -v
```

## Step 4: Review Results

Look for:
- ✓ All tests passed = RAG is working well
- Scores above 0.80 = Good quality
- Summary table at end = Overall metrics

## Key Changes Made

| What | Why |
|------|-----|
| `eval_mode=True` | Sets temperature to 0 for consistent evaluation |
| Embeddings added | Required for proper RAGAS metrics |
| Retry logic | Handles API rate limits automatically |
| 20 test cases | Comprehensive coverage of your knowledge base |
| Summary report | See aggregate scores at the end |

## Threshold Meanings

- **Faithfulness ≥ 0.80**: Answer doesn't hallucinate ✓
- **Answer Relevancy ≥ 0.80**: Answers the question ✓
- **Context Recall ≥ 0.75**: Found the info needed ✓

If scores are low, improve your:
1. Knowledge base content
2. Prompt templates
3. Document chunking strategy

## Common Issues

| Error | Fix |
|-------|-----|
| `GOOGLE_API_KEY not set` | Check `.env` file exists and has key |
| `Connection timeout` | Add `--timeout=300` to pytest command |
| `Low RAGAS scores` | Review knowledge base quality |
| `Rate limit exceeded` | Retry logic handles this; just wait |

## Run Single Test

```bash
pytest tests/test_rag.py::test_rag_quality_gate_ragas[test_refund_policy_basic] -v
```

## Files Explained

- **rag_pipeline.py** - Your RAG with eval mode support
- **test_rag.py** - 20 test cases with RAGAS metrics
- **conftest.py** - Pytest setup
- **rag_test_cases.yml** - Test Q&A pairs (customize this!)
- **requirements.txt** - All dependencies

## Customizing Tests

Edit `tests/fixtures/rag_test_cases.yml`:

```yaml
- id: "my_test"
  query: "What's your return policy?"
  expected_answer: "We offer 30-day returns."
```

Rerun: `pytest tests/test_rag.py -v`

## See Detailed Output

```bash
# Verbose output
pytest tests/test_rag.py -v -s

# Show print statements
pytest tests/test_rag.py -v -s --tb=short
```

Done! You're evaluating your RAG pipeline. 🚀
