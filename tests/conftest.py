"""Pytest configuration and fixtures."""
import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, MagicMock
from src.storage import Storage, Student
from src.tutor import MathTutor


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
def mock_anthropic_client():
    """Mock Anthropic client for testing without API calls."""
    mock_client = Mock()

    # Mock the messages.create response
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="This is a mocked tutor response.")]

    mock_client.messages.create.return_value = mock_response

    return mock_client


@pytest.fixture
def tutor_with_mock(storage, mock_anthropic_client, monkeypatch):
    """Create a MathTutor with mocked Anthropic client."""
    tutor = MathTutor(storage)

    # Replace the real client with our mock
    tutor.client = mock_anthropic_client

    return tutor
