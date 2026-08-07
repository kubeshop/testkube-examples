"""
Pytest configuration and fixtures.
"""

import os
from dotenv import load_dotenv

# Load environment variables before any imports
load_dotenv()


def pytest_configure(config):
    """Configure pytest before test collection."""
    # Verify required environment variable
    if not os.environ.get("GOOGLE_API_KEY"):
        raise RuntimeError(
            "GOOGLE_API_KEY environment variable not set. "
            "Please add it to your .env file."
        )


def pytest_collection_modifyitems(config, items):
    """Add markers to tests."""
    for item in items:
        if "rag" in str(item.fspath):
            item.add_marker("ragas")


def pytest_sessionstart(session):
    """Print session info."""
    print("\n" + "=" * 70)
    print("Starting RAGAS RAG Quality Evaluation")
    print("=" * 70)


def pytest_sessionfinish(session, exitstatus):
    """Print final status."""
    if exitstatus == 0:
        print("\n✓ All tests passed!")
    else:
        print(f"\n✗ Tests failed with exit code: {exitstatus}")
