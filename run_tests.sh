#!/bin/bash
# Run tests for Ensina AI

echo "🧪 Running Ensina AI Tests..."
echo ""

# Set a dummy API key for tests (not used, but prevents config errors)
export ANTHROPIC_API_KEY=test_key_for_testing

# Run tests with coverage
echo "Running tests with coverage..."
echo ""

python -m pytest -v --cov=src --cov-report=term-missing --cov-report=html

TEST_EXIT_CODE=$?

echo ""
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "✅ All tests passed!"
    echo ""
    echo "📊 Coverage report generated in htmlcov/index.html"
else
    echo "❌ Some tests failed. Please review the output above."
    exit 1
fi
