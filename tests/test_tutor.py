"""Tests for tutoring logic with mocked LLM."""
import pytest
from unittest.mock import Mock, MagicMock, patch
from src.tutor import MathTutor
from src.storage import Student


class TestTutorInitialization:
    """Test tutor initialization."""

    def test_tutor_creation(self, storage):
        """Test that tutor can be created with storage."""
        tutor = MathTutor(storage)

        assert tutor.storage == storage
        assert tutor.llm is not None
        assert tutor.slow_model is not None
        assert tutor.fast_model is not None


class TestTutorResponses:
    """Test tutor response generation with mocked API."""

    def test_get_response_sync(self, tutor_with_mock, sample_student):
        """Test getting a response from the tutor."""
        conversation_history = [
            {"role": "assistant", "content": "Hello! How can I help?"}
        ]
        new_message = "I need help with fractions"

        response = tutor_with_mock.get_response_sync(
            student=sample_student,
            conversation_history=conversation_history,
            new_message=new_message
        )

        # Verify response is returned
        assert response == "This is a mocked tutor response."

        # Verify the LLM was called correctly
        tutor_with_mock.llm.chat.assert_called_once()

        # Get the call arguments
        call_args = tutor_with_mock.llm.chat.call_args

        # Verify messages were formatted correctly
        assert call_args.kwargs["messages"] == [
            {"role": "assistant", "content": "Hello! How can I help?"},
            {"role": "user", "content": "I need help with fractions"}
        ]

        # Verify system prompt includes student context
        assert "Test Student" in call_args.kwargs["system"]
        assert "Grade Level: 5" in call_args.kwargs["system"]

    def test_system_prompt_includes_student_context(self, tutor_with_mock, sample_student):
        """Test that system prompt is personalized for the student."""
        conversation_history = []
        new_message = "Hello"

        tutor_with_mock.get_response_sync(
            student=sample_student,
            conversation_history=conversation_history,
            new_message=new_message
        )

        call_args = tutor_with_mock.llm.chat.call_args
        system_prompt = call_args.kwargs["system"]

        # Verify student details are in system prompt
        assert sample_student.name in system_prompt
        assert str(sample_student.grade_level) in system_prompt
        assert "Socratic" in system_prompt or "socratic" in system_prompt.lower()

    def test_conversation_history_preserved(self, tutor_with_mock, sample_student):
        """Test that conversation history is properly maintained."""
        long_history = [
            {"role": "assistant", "content": "Message 1"},
            {"role": "user", "content": "Message 2"},
            {"role": "assistant", "content": "Message 3"},
            {"role": "user", "content": "Message 4"},
        ]

        tutor_with_mock.get_response_sync(
            student=sample_student,
            conversation_history=long_history,
            new_message="Message 5"
        )

        call_args = tutor_with_mock.llm.chat.call_args
        messages = call_args.kwargs["messages"]

        # Should have all previous messages plus the new one
        assert len(messages) == 5
        assert messages[-1] == {"role": "user", "content": "Message 5"}

    def test_different_grade_levels(self, tutor_with_mock, storage):
        """Test that different grade levels get appropriate context."""
        # Test with elementary student
        elementary = storage.create_student("Kid", 3, "parent@test.com")
        tutor_with_mock.get_response_sync(elementary, [], "Help me")

        call_args_elem = tutor_with_mock.llm.chat.call_args
        system_elem = call_args_elem.kwargs["system"]

        # Reset mock
        tutor_with_mock.llm.chat.reset_mock()

        # Test with high school student
        highschool = storage.create_student("Teen", 11, "parent@test.com")
        tutor_with_mock.get_response_sync(highschool, [], "Help me")

        call_args_hs = tutor_with_mock.llm.chat.call_args
        system_hs = call_args_hs.kwargs["system"]

        # Both should have grade level mentioned
        assert "grade 3" in system_elem.lower()
        assert "grade 11" in system_hs.lower()


class TestSessionSummaryGeneration:
    """Test AI-generated session summaries with mocked API."""

    def test_generate_session_summary(self, tutor_with_mock, sample_student, sample_messages):
        """Test generating a summary from a conversation."""
        # Mock the summary response
        tutor_with_mock.llm.chat.return_value = "SUMMARY: Student practiced basic fraction concepts.\nTOPICS: fractions, addition"

        result = tutor_with_mock.generate_session_summary(
            student=sample_student,
            messages=sample_messages
        )

        # Verify structure
        assert "summary" in result
        assert "topics" in result

        # Verify content
        assert "practiced basic fraction concepts" in result["summary"]
        assert "fractions" in result["topics"]
        assert "addition" in result["topics"]

    def test_summary_includes_conversation_context(self, tutor_with_mock, sample_student):
        """Test that the summary request includes the full conversation."""
        messages = [
            {"role": "user", "content": "What is 1/2 + 1/2?"},
            {"role": "assistant", "content": "Let's think about this..."},
            {"role": "user", "content": "Is it 1?"},
            {"role": "assistant", "content": "Correct!"}
        ]

        tutor_with_mock.llm.chat.return_value = "SUMMARY: Student learned fraction addition.\nTOPICS: fractions, addition"

        tutor_with_mock.generate_session_summary(sample_student, messages)

        # Verify the API was called
        call_args = tutor_with_mock.llm.chat.call_args
        prompt = call_args.kwargs["messages"][0]["content"]

        # The prompt should include the conversation
        assert "1/2 + 1/2" in prompt
        assert "Correct!" in prompt

    def test_summary_handles_malformed_response(self, tutor_with_mock, sample_student):
        """Test that summary generation handles unexpected response formats."""
        # Mock a response without the expected format
        tutor_with_mock.llm.chat.return_value = "Just some random text without proper formatting"

        result = tutor_with_mock.generate_session_summary(
            student=sample_student,
            messages=[{"role": "user", "content": "test"}]
        )

        # Should still return something
        assert "summary" in result
        assert "topics" in result

        # Should have fallbacks
        assert len(result["summary"]) > 0
        assert len(result["topics"]) > 0

    def test_summary_with_empty_conversation(self, tutor_with_mock, sample_student):
        """Test summary generation with minimal conversation."""
        messages = [{"role": "user", "content": "Hi"}]

        tutor_with_mock.llm.chat.return_value = "SUMMARY: Brief greeting.\nTOPICS: greeting"

        result = tutor_with_mock.generate_session_summary(sample_student, messages)

        assert result["summary"] is not None
        assert result["topics"] is not None


class TestInitialGreeting:
    """Test initial greeting generation."""

    def test_get_initial_greeting(self, tutor_with_mock, sample_student):
        """Test getting an initial greeting for a student."""
        greeting = tutor_with_mock.get_initial_greeting(sample_student)

        # Should include student name
        assert sample_student.name in greeting

        # Should be friendly/welcoming
        assert any(word in greeting.lower() for word in ["hi", "hello", "hey"])

        # Should mention math
        assert "math" in greeting.lower()

    def test_greeting_different_students(self, tutor_with_mock, storage):
        """Test that greetings can vary."""
        students = [
            storage.create_student(f"Student {i}", 5, f"p{i}@test.com")
            for i in range(5)
        ]

        greetings = [
            tutor_with_mock.get_initial_greeting(student)
            for student in students
        ]

        # All greetings should include student names
        for i, greeting in enumerate(greetings):
            assert f"Student {i}" in greeting


class TestTutorConfiguration:
    """Test tutor configuration and model settings."""

    def test_tutor_uses_configured_model(self, tutor_with_mock, sample_student):
        """Test that tutor uses the configured model."""
        tutor_with_mock.get_response_sync(sample_student, [], "test message")

        call_args = tutor_with_mock.llm.chat.call_args

        # Should use the model from config
        assert "model" in call_args.kwargs
        assert "claude" in call_args.kwargs["model"].lower()

    def test_tutor_sets_reasonable_max_tokens(self, tutor_with_mock, sample_student):
        """Test that tutor sets appropriate token limits."""
        tutor_with_mock.get_response_sync(sample_student, [], "test message")

        call_args = tutor_with_mock.llm.chat.call_args

        # Should have a max_tokens parameter
        assert "max_tokens" in call_args.kwargs
        assert call_args.kwargs["max_tokens"] > 0
        assert call_args.kwargs["max_tokens"] <= 4096  # Reasonable limit


class TestErrorHandling:
    """Test error handling in tutor logic."""

    def test_api_error_propagates(self, tutor_with_mock, sample_student):
        """Test that API errors are propagated appropriately."""
        # Make the mock raise an exception
        tutor_with_mock.llm.chat.side_effect = Exception("API Error")

        with pytest.raises(Exception) as exc_info:
            tutor_with_mock.get_response_sync(
                sample_student,
                [],
                "test message"
            )

        assert "API Error" in str(exc_info.value)


class TestBusinessLogic:
    """Test core business logic without UI concerns."""

    def test_tutor_builds_correct_message_format(self, tutor_with_mock, sample_student):
        """Test that messages are formatted correctly for the API."""
        history = [
            {"role": "assistant", "content": "Hello"},
            {"role": "user", "content": "Hi"},
        ]

        tutor_with_mock.get_response_sync(sample_student, history, "New message")

        call_args = tutor_with_mock.llm.chat.call_args
        messages = call_args.kwargs["messages"]

        # Should have exactly 3 messages
        assert len(messages) == 3

        # Should maintain alternating roles
        assert messages[0]["role"] == "assistant"
        assert messages[1]["role"] == "user"
        assert messages[2]["role"] == "user"

        # Should have correct content
        assert messages[0]["content"] == "Hello"
        assert messages[1]["content"] == "Hi"
        assert messages[2]["content"] == "New message"

    def test_empty_conversation_history(self, tutor_with_mock, sample_student):
        """Test handling of empty conversation history."""
        response = tutor_with_mock.get_response_sync(
            student=sample_student,
            conversation_history=[],
            new_message="First message"
        )

        assert response is not None

        call_args = tutor_with_mock.llm.chat.call_args
        messages = call_args.kwargs["messages"]

        # Should just have the new message
        assert len(messages) == 1
        assert messages[0]["content"] == "First message"

    def test_summary_parsing_variations(self, tutor_with_mock, sample_student):
        """Test parsing different summary response formats."""
        test_cases = [
            # Standard format
            ("SUMMARY: Good session.\nTOPICS: math, fractions",
             "Good session.", "math, fractions"),

            # With extra whitespace
            ("SUMMARY:   Good session.  \nTOPICS:   math, fractions  ",
             "Good session.", "math, fractions"),

            # Multiple lines for summary
            ("SUMMARY: Good session.\nMore details here.\nTOPICS: math",
             "Good session.", "math"),
        ]

        for response_text, expected_summary, expected_topics in test_cases:
            mock_response = MagicMock()
            mock_response.content = [MagicMock(text=response_text)]
            tutor_with_mock.llm.chat.return_value = mock_response.content[0].text

            result = tutor_with_mock.generate_session_summary(
                sample_student,
                [{"role": "user", "content": "test"}]
            )

            assert expected_summary in result["summary"]
            assert expected_topics in result["topics"]


class TestConfidenceEstimation:
    """Test confidence estimation from conversations."""

    def test_estimate_confidence_high(self, tutor_with_mock, sample_student):
        """Test confidence estimation for successful session."""
        messages = [
            {"role": "assistant", "content": "Let's solve this problem."},
            {"role": "user", "content": "I think it's 5?"},
            {"role": "assistant", "content": "Perfect! That's exactly right!"},
            {"role": "user", "content": "And this one is 10"},
            {"role": "assistant", "content": "Excellent work! You've got it."},
        ]

        confidence = tutor_with_mock.estimate_confidence(sample_student, messages)

        # Should be high confidence (multiple positive feedback)
        assert confidence > 0.6

    def test_estimate_confidence_low(self, tutor_with_mock, sample_student):
        """Test confidence estimation for struggling session."""
        messages = [
            {"role": "assistant", "content": "Let's try this problem."},
            {"role": "user", "content": "I'm not sure... maybe 3?"},
            {"role": "assistant", "content": "Not quite, let's think about this differently."},
            {"role": "user", "content": "I guess 5?"},
            {"role": "assistant", "content": "Almost, but think about what we just discussed."},
        ]

        confidence = tutor_with_mock.estimate_confidence(sample_student, messages)

        # Should be lower confidence (hesitation + correction)
        assert confidence < 0.6

    def test_estimate_confidence_short_conversation(self, tutor_with_mock, sample_student):
        """Test confidence estimation for very short conversation."""
        messages = [{"role": "user", "content": "Hi"}]

        confidence = tutor_with_mock.estimate_confidence(sample_student, messages)

        # Should be neutral for short conversations
        assert confidence == 0.5


class TestQuestionCounting:
    """Test counting student questions."""

    def test_count_student_questions(self, tutor_with_mock):
        """Test counting questions in messages."""
        messages = [
            {"role": "user", "content": "What is 2+2?"},
            {"role": "assistant", "content": "Let's figure it out!"},
            {"role": "user", "content": "Is it 4?"},
            {"role": "user", "content": "I understand now"},  # Not a question
            {"role": "user", "content": "What about 3+3?"},
        ]

        count = tutor_with_mock.count_student_questions(messages)

        assert count == 3  # Three messages with question marks

    def test_count_no_questions(self, tutor_with_mock):
        """Test counting when no questions asked."""
        messages = [
            {"role": "user", "content": "I need help"},
            {"role": "assistant", "content": "Sure!"},
            {"role": "user", "content": "Thanks"},
        ]

        count = tutor_with_mock.count_student_questions(messages)

        assert count == 0


class TestDifficultyEstimation:
    """Test difficulty level estimation."""

    def test_estimate_difficulty_basic(self, tutor_with_mock, sample_student):
        """Test difficulty for basic topics."""
        difficulty = tutor_with_mock.estimate_difficulty(sample_student, "addition, subtraction")

        # Should be lower than grade level for basic topics
        assert difficulty < sample_student.grade_level

    def test_estimate_difficulty_advanced(self, tutor_with_mock, sample_student):
        """Test difficulty for advanced topics."""
        difficulty = tutor_with_mock.estimate_difficulty(sample_student, "algebra, geometry")

        # Should be higher than grade level for advanced topics
        assert difficulty > sample_student.grade_level

    def test_estimate_difficulty_grade_appropriate(self, tutor_with_mock, sample_student):
        """Test difficulty for grade-appropriate topics."""
        difficulty = tutor_with_mock.estimate_difficulty(sample_student, "fractions, decimals")

        # Should be around grade level
        assert 1 <= difficulty <= 10


class TestEnhancedSessionSummary:
    """Test comprehensive session summary generation."""

    def test_generate_enhanced_summary(self, tutor_with_mock, sample_student, sample_messages):
        """Test generating enhanced summary with all analytics."""
        # Mock responses for all the API calls
        mock_responses = [
            # Basic summary
            "SUMMARY: Student learned fractions.\nTOPICS: fractions",
            # Subtopics
            "adding fractions, simplifying fractions",
            # Learning indicators
            """STRUGGLED_WITH: [common denominators]
MASTERED: [basic fractions]
MISCONCEPTIONS: [adding numerators and denominators]
BREAKTHROUGH_MOMENTS: [understood the concept]
NEEDS_REVIEW: YES""",
        ]

        tutor_with_mock.llm.chat.side_effect = mock_responses

        result = tutor_with_mock.generate_enhanced_session_summary(sample_student, sample_messages)

        # Verify all components are present
        assert "summary" in result
        assert "topics" in result
        assert "subtopics" in result
        assert "difficulty_level" in result
        assert "student_confidence" in result
        assert "learning_indicators" in result
        assert "questions_asked" in result

        # Verify data types
        assert isinstance(result["subtopics"], list)
        assert isinstance(result["difficulty_level"], int)
        assert isinstance(result["student_confidence"], float)
        assert isinstance(result["questions_asked"], int)

    def test_enhanced_summary_includes_basic_fields(self, tutor_with_mock, sample_student, sample_messages):
        """Test that enhanced summary includes original basic summary fields."""
        mock_responses = [
            "SUMMARY: Test summary.\nTOPICS: test topics",
            "subtopic1, subtopic2",
            """STRUGGLED_WITH: []
MASTERED: []
MISCONCEPTIONS: []
BREAKTHROUGH_MOMENTS: []
NEEDS_REVIEW: NO""",
        ]

        tutor_with_mock.llm.chat.side_effect = mock_responses

        result = tutor_with_mock.generate_enhanced_session_summary(sample_student, sample_messages)

        assert "Test summary" in result["summary"]
        assert result["topics"] == "test topics"


class TestTopicRelevanceGuardrail:
    """Test the topic relevance checking (guardrail)."""

    def test_short_messages_allowed(self, tutor_with_mock, sample_student):
        """Short messages like greetings should be allowed."""
        result = tutor_with_mock.check_topic_relevance(sample_student, "Hi")
        assert result["is_relevant"] is True
        assert result["suggested_response"] is None

    def test_greeting_messages_allowed(self, tutor_with_mock, sample_student):
        """Common greetings should be allowed."""
        greetings = ["hello", "hey", "thanks", "thank you", "bye"]
        for greeting in greetings:
            result = tutor_with_mock.check_topic_relevance(sample_student, greeting)
            assert result["is_relevant"] is True

    def test_math_message_relevant(self, tutor_with_mock, sample_student):
        """Math-related messages should be marked as relevant."""
        # Mock LLM to respond with RELEVANT
        tutor_with_mock.llm.chat.return_value = "RELEVANT"

        result = tutor_with_mock.check_topic_relevance(sample_student, "Can you help me with fractions?")
        assert result["is_relevant"] is True
        assert result["suggested_response"] is None

    def test_off_topic_message_flagged(self, tutor_with_mock, sample_student):
        """Off-topic messages should be flagged."""
        # Mock LLM to respond with OFF_TOPIC
        tutor_with_mock.llm.chat.return_value = "OFF_TOPIC: Not related to math"

        result = tutor_with_mock.check_topic_relevance(sample_student, "What's the weather today?")
        assert result["is_relevant"] is False
        assert "math" in result["suggested_response"].lower()
        assert sample_student.name in result["suggested_response"]

    def test_guardrail_fails_open(self, tutor_with_mock, sample_student):
        """If guardrail check fails, should allow message (fail open)."""
        # Mock API failure
        tutor_with_mock.llm.chat.side_effect = Exception("API Error")

        result = tutor_with_mock.check_topic_relevance(sample_student, "Can you help with history?")
        assert result["is_relevant"] is True  # Fail open
        assert "failed" in result["reason"].lower()


class TestLearningIndicatorsAnalysis:
    """Test learning indicators analysis."""

    def test_analyze_learning_indicators(self, tutor_with_mock, sample_student):
        """Test extracting learning indicators from conversation."""
        messages = [
            {"role": "user", "content": "I don't understand fractions"},
            {"role": "assistant", "content": "Let's break it down..."},
            {"role": "user", "content": "Oh! Now I get it!"},
        ]

        # Mock the API response
        mock_response = MagicMock(content=[MagicMock(text="""STRUGGLED_WITH: [understanding fractions initially]
MASTERED: [basic concept of fractions]
MISCONCEPTIONS: [thought fractions were whole numbers]
BREAKTHROUGH_MOMENTS: [Oh! Now I get it!]
NEEDS_REVIEW: NO""")])

        tutor_with_mock.llm.chat.return_value = mock_response.content[0].text

        indicators = tutor_with_mock.analyze_learning_indicators(sample_student, messages)

        assert len(indicators.struggled_with) > 0
        assert len(indicators.mastered) > 0
        assert len(indicators.breakthrough_moments) > 0
        assert indicators.needs_review is False

    def test_extract_subtopics(self, tutor_with_mock, sample_student):
        """Test extracting subtopics from conversation."""
        messages = [
            {"role": "user", "content": "Help with adding fractions"},
            {"role": "assistant", "content": "Let's find common denominators first..."},
        ]

        # Mock the API response
        mock_response = MagicMock(content=[MagicMock(text="adding fractions, common denominators, simplifying")])
        tutor_with_mock.llm.chat.return_value = mock_response.content[0].text

        subtopics = tutor_with_mock.extract_subtopics(sample_student, messages, "fractions")

        assert isinstance(subtopics, list)
        assert len(subtopics) > 0
        assert len(subtopics) <= 5  # Should be limited to 5
