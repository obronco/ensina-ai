@echo off
REM Run tests for Ensina AI (Windows)

echo Running Ensina AI Tests...
echo.

REM Set a dummy API key for tests (not used, but prevents config errors)
set ANTHROPIC_API_KEY=test_key_for_testing

REM Run tests with coverage
echo Running tests with coverage...
echo.

python -m pytest -v --cov=src --cov-report=term-missing --cov-report=html

if %ERRORLEVEL% EQU 0 (
    echo.
    echo All tests passed!
    echo.
    echo Coverage report generated in htmlcov\index.html
) else (
    echo.
    echo Some tests failed. Please review the output above.
    exit /b 1
)
