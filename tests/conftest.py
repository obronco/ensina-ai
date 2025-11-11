"""Pytest configuration and fixtures."""
import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from src.storage import Storage, Student, LearningIndicators
from src.tutor import MathTutor


@pytest.fixture(autouse=True)
def mock_llm_factory(monkeypatch):
    """Mock the create_llm_provider factory for all tests."""
    # Create a mock provider
    mock_provider = Mock()
    mock_provider.chat.return_value = "This is a mocked tutor response."
    mock_provider.slow_model = "claude-3-5-sonnet-20241022"
    mock_provider.fast_model = "claude-3-5-haiku-20241022"

    # Patch where it's imported in tutor.py
    import src.tutor
    monkeypatch.setattr(src.tutor, "create_llm_provider", lambda **kwargs: mock_provider)

    return mock_provider


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    yield db_path

    # Cleanup
    Path(db_path).unlink(missing_ok=True)


@pytest.fixture
def storage(temp_db):
    """Create a Storage instance with temporary database."""
    return Storage(temp_db)


@pytest.fixture
def sample_student(storage):
    """Create a sample student for testing."""
    return storage.create_student(
        name="Test Student",
        grade_level=5,
        parent_email="parent@test.com"
    )


@pytest.fixture
def sample_messages():
    """Sample conversation messages."""
    return [
        {"role": "assistant", "content": "Hi! What math topic do you need help with?"},
        {"role": "user", "content": "I don't understand fractions"},
        {"role": "assistant", "content": "Great! Let's start with the basics. Imagine you have a pizza..."},
        {"role": "user", "content": "Okay, I get it now!"},
        {"role": "assistant", "content": "Excellent! Can you tell me what 1/2 + 1/2 equals?"},
        {"role": "user", "content": "Is it 1?"},
        {"role": "assistant", "content": "Perfect! You've got it."},
    ]


@pytest.fixture
def mock_llm_provider():
    """Mock LLM provider for testing without API calls."""
    mock_provider = Mock()

    # Mock the chat method
    mock_provider.chat.return_value = "This is a mocked tutor response."

    # Set model attributes
    mock_provider.slow_model = "claude-3-5-sonnet-20241022"
    mock_provider.fast_model = "claude-3-5-haiku-20241022"

    return mock_provider


@pytest.fixture
def mock_anthropic_client():
    """Mock Anthropic client for testing without API calls."""
    mock_client = Mock()

    # Mock the messages.create response
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="This is a mocked tutor response.")]

    mock_client.messages.create.return_value = mock_response

    return mock_client


@pytest.fixture
def sample_learning_indicators():
    """Sample learning indicators for testing."""
    return LearningIndicators(
        struggled_with=["finding common denominators"],
        mastered=["identifying numerator and denominator"],
        misconceptions=["thought you add numerators and denominators"],
        breakthrough_moments=["Oh! The bottom number has to match first!"],
        needs_review=True
    )


@pytest.fixture
def tutor_with_mock(storage):
    """Create a MathTutor with mocked LLM provider."""
    # The autouse mock_llm_factory fixture ensures the factory returns a mock
    tutor = MathTutor(storage)
    return tutor
