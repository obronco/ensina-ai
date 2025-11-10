"""Tests for storage layer."""
import pytest
from datetime import datetime
from src.storage import Storage, Student, Session, Progress, LearningIndicators


class TestStudentOperations:
    """Test student CRUD operations."""

    def test_create_student(self, storage):
        """Test creating a student."""
        student = storage.create_student(
            name="João Silva",
            grade_level=5,
            parent_email="parent@example.com"
        )

        assert student.id is not None
        assert student.name == "João Silva"
        assert student.grade_level == 5
        assert student.parent_email == "parent@example.com"
        assert student.created_at is not None

    def test_get_student(self, storage, sample_student):
        """Test retrieving a student by ID."""
        retrieved = storage.get_student(sample_student.id)

        assert retrieved is not None
        assert retrieved.id == sample_student.id
        assert retrieved.name == sample_student.name
        assert retrieved.grade_level == sample_student.grade_level

    def test_get_nonexistent_student(self, storage):
        """Test retrieving a student that doesn't exist."""
        result = storage.get_student(99999)
        assert result is None

    def test_list_students(self, storage):
        """Test listing all students."""
        # Create multiple students
        storage.create_student("Student 1", 3, "parent1@test.com")
        storage.create_student("Student 2", 5, "parent2@test.com")
        storage.create_student("Student 3", 7, "parent3@test.com")

        students = storage.list_students()

        assert len(students) == 3
        assert all(isinstance(s, Student) for s in students)
        # Should be ordered by name
        assert students[0].name == "Student 1"

    def test_list_students_empty(self, storage):
        """Test listing students when none exist."""
        students = storage.list_students()
        assert students == []


class TestSessionOperations:
    """Test session CRUD operations."""

    def test_create_session(self, storage, sample_student, sample_messages):
        """Test creating a session."""
        session = storage.create_session(
            student_id=sample_student.id,
            messages=sample_messages,
            summary="Student learned about basic fractions",
            topics="fractions, basic concepts",
            duration_minutes=15
        )

        assert session.id is not None
        assert session.student_id == sample_student.id
        assert len(session.messages) == len(sample_messages)
        assert session.summary == "Student learned about basic fractions"
        assert session.topics == "fractions, basic concepts"
        assert session.duration_minutes == 15
        assert session.timestamp is not None

    def test_create_session_minimal(self, storage, sample_student):
        """Test creating a session with minimal data."""
        messages = [
            {"role": "user", "content": "Help with math"},
            {"role": "assistant", "content": "Sure! What do you need?"}
        ]

        session = storage.create_session(
            student_id=sample_student.id,
            messages=messages
        )

        assert session.id is not None
        assert session.summary is None
        assert session.topics is None
        assert session.duration_minutes is None

    def test_get_session(self, storage, sample_student, sample_messages):
        """Test retrieving a session by ID."""
        created_session = storage.create_session(
            student_id=sample_student.id,
            messages=sample_messages,
            summary="Test summary"
        )

        retrieved = storage.get_session(created_session.id)

        assert retrieved is not None
        assert retrieved.id == created_session.id
        assert len(retrieved.messages) == len(sample_messages)
        assert retrieved.summary == "Test summary"

    def test_get_nonexistent_session(self, storage):
        """Test retrieving a session that doesn't exist."""
        result = storage.get_session(99999)
        assert result is None

    def test_list_sessions(self, storage, sample_student, sample_messages):
        """Test listing sessions for a student."""
        # Create multiple sessions
        for i in range(3):
            storage.create_session(
                student_id=sample_student.id,
                messages=sample_messages,
                topics=f"topic_{i}"
            )

        sessions = storage.list_sessions(sample_student.id)

        assert len(sessions) == 3
        assert all(isinstance(s, Session) for s in sessions)
        assert all(s.student_id == sample_student.id for s in sessions)

    def test_list_sessions_with_limit(self, storage, sample_student, sample_messages):
        """Test listing sessions with a limit."""
        # Create 5 sessions
        for i in range(5):
            storage.create_session(
                student_id=sample_student.id,
                messages=sample_messages
            )

        sessions = storage.list_sessions(sample_student.id, limit=3)

        assert len(sessions) == 3

    def test_list_sessions_empty(self, storage, sample_student):
        """Test listing sessions when none exist."""
        sessions = storage.list_sessions(sample_student.id)
        assert sessions == []

    def test_update_session_summary(self, storage, sample_student, sample_messages):
        """Test updating a session's summary."""
        session = storage.create_session(
            student_id=sample_student.id,
            messages=sample_messages
        )

        # Update summary
        storage.update_session_summary(
            session_id=session.id,
            summary="Updated summary",
            topics="new, topics"
        )

        # Retrieve and verify
        updated = storage.get_session(session.id)
        assert updated.summary == "Updated summary"
        assert updated.topics == "new, topics"


class TestProgressOperations:
    """Test progress tracking operations."""

    def test_update_progress(self, storage, sample_student):
        """Test creating/updating progress."""
        storage.update_progress(
            student_id=sample_student.id,
            topic="fractions",
            mastery_level=0.75
        )

        progress = storage.get_progress(sample_student.id)

        assert len(progress) == 1
        assert progress[0].topic == "fractions"
        assert progress[0].mastery_level == 0.75
        assert progress[0].last_practiced is not None

    def test_update_progress_multiple_topics(self, storage, sample_student):
        """Test tracking progress for multiple topics."""
        topics = [
            ("fractions", 0.8),
            ("decimals", 0.6),
            ("multiplication", 0.9)
        ]

        for topic, level in topics:
            storage.update_progress(
                student_id=sample_student.id,
                topic=topic,
                mastery_level=level
            )

        progress = storage.get_progress(sample_student.id)

        assert len(progress) == 3
        assert {p.topic for p in progress} == {"fractions", "decimals", "multiplication"}

    def test_update_progress_upsert(self, storage, sample_student):
        """Test that updating progress for same topic replaces old value."""
        # Initial progress
        storage.update_progress(sample_student.id, "fractions", 0.5)

        # Update same topic
        storage.update_progress(sample_student.id, "fractions", 0.9)

        progress = storage.get_progress(sample_student.id)

        # Should only have one entry for fractions
        assert len(progress) == 1
        assert progress[0].topic == "fractions"
        assert progress[0].mastery_level == 0.9

    def test_get_progress_empty(self, storage, sample_student):
        """Test getting progress when none exists."""
        progress = storage.get_progress(sample_student.id)
        assert progress == []


class TestDataIntegrity:
    """Test data integrity and edge cases."""

    def test_session_messages_json_serialization(self, storage, sample_student):
        """Test that complex message structures are preserved."""
        complex_messages = [
            {
                "role": "user",
                "content": "What is 2+2?",
                "metadata": {"timestamp": "2025-01-01T10:00:00"}
            },
            {
                "role": "assistant",
                "content": "Let's think about this...",
                "metadata": {"confidence": 0.95}
            }
        ]

        session = storage.create_session(
            student_id=sample_student.id,
            messages=complex_messages
        )

        retrieved = storage.get_session(session.id)

        # Messages should be exactly the same
        assert retrieved.messages == complex_messages

    def test_multiple_students_isolation(self, storage):
        """Test that students' data is properly isolated."""
        student1 = storage.create_student("Student 1", 3, "p1@test.com")
        student2 = storage.create_student("Student 2", 5, "p2@test.com")

        messages = [{"role": "user", "content": "test"}]

        # Create sessions for each student
        storage.create_session(student1.id, messages, topics="topic1")
        storage.create_session(student2.id, messages, topics="topic2")

        # Each student should only see their own sessions
        student1_sessions = storage.list_sessions(student1.id)
        student2_sessions = storage.list_sessions(student2.id)

        assert len(student1_sessions) == 1
        assert len(student2_sessions) == 1
        assert student1_sessions[0].topics == "topic1"
        assert student2_sessions[0].topics == "topic2"

    def test_unicode_handling(self, storage):
        """Test that unicode characters are handled correctly."""
        student = storage.create_student(
            name="João José García 你好",
            grade_level=5,
            parent_email="test@test.com"
        )

        messages = [
            {"role": "user", "content": "Olá! Cómo estás? 你好吗？"},
            {"role": "assistant", "content": "¡Muy bien! 很好！"}
        ]

        session = storage.create_session(
            student_id=student.id,
            messages=messages,
            summary="学生学习了数学"
        )

        # Retrieve and verify
        retrieved_student = storage.get_student(student.id)
        retrieved_session = storage.get_session(session.id)

        assert retrieved_student.name == "João José García 你好"
        assert retrieved_session.messages[0]["content"] == "Olá! Cómo estás? 你好吗？"
        assert retrieved_session.summary == "学生学习了数学"


class TestEnhancedSessionAnalytics:
    """Test enhanced session analytics features."""

    def test_create_session_with_analytics(self, storage, sample_student, sample_learning_indicators):
        """Test creating a session with full analytics data."""
        messages = [{"role": "user", "content": "Help with fractions"}]

        session = storage.create_session(
            student_id=sample_student.id,
            messages=messages,
            summary="Student learned fractions",
            topics="fractions",
            duration_minutes=15,
            subtopics=["adding fractions", "common denominators"],
            difficulty_level=5,
            student_confidence=0.75,
            learning_indicators=sample_learning_indicators,
            questions_asked=3
        )

        assert session.id is not None
        assert session.subtopics == ["adding fractions", "common denominators"]
        assert session.difficulty_level == 5
        assert session.student_confidence == 0.75
        assert session.learning_indicators == sample_learning_indicators
        assert session.questions_asked == 3

    def test_retrieve_session_with_analytics(self, storage, sample_student, sample_learning_indicators):
        """Test retrieving a session preserves analytics data."""
        messages = [{"role": "user", "content": "test"}]

        created = storage.create_session(
            student_id=sample_student.id,
            messages=messages,
            topics="fractions",
            subtopics=["numerator", "denominator"],
            difficulty_level=6,
            student_confidence=0.8,
            learning_indicators=sample_learning_indicators,
            questions_asked=5
        )

        retrieved = storage.get_session(created.id)

        assert retrieved.subtopics == ["numerator", "denominator"]
        assert retrieved.difficulty_level == 6
        assert retrieved.student_confidence == 0.8
        assert retrieved.learning_indicators.struggled_with == sample_learning_indicators.struggled_with
        assert retrieved.learning_indicators.mastered == sample_learning_indicators.mastered
        assert retrieved.questions_asked == 5

    def test_backward_compatibility_simple_session(self, storage, sample_student):
        """Test that sessions without analytics still work (backward compatibility)."""
        messages = [{"role": "user", "content": "test"}]

        session = storage.create_session(
            student_id=sample_student.id,
            messages=messages,
            summary="Simple session",
            topics="math"
        )

        assert session.id is not None
        assert session.summary == "Simple session"
        assert session.subtopics is None
        assert session.difficulty_level is None
        assert session.student_confidence is None
        assert session.learning_indicators is None

    def test_learning_indicators_serialization(self, storage, sample_student):
        """Test that LearningIndicators are properly serialized and deserialized."""
        indicators = LearningIndicators(
            struggled_with=["concept A", "concept B"],
            mastered=["concept C"],
            misconceptions=["error D"],
            breakthrough_moments=["aha moment E"],
            needs_review=True
        )

        session = storage.create_session(
            student_id=sample_student.id,
            messages=[{"role": "user", "content": "test"}],
            learning_indicators=indicators
        )

        retrieved = storage.get_session(session.id)

        assert retrieved.learning_indicators.struggled_with == ["concept A", "concept B"]
        assert retrieved.learning_indicators.mastered == ["concept C"]
        assert retrieved.learning_indicators.misconceptions == ["error D"]
        assert retrieved.learning_indicators.breakthrough_moments == ["aha moment E"]
        assert retrieved.learning_indicators.needs_review is True


class TestAnalyticsQueries:
    """Test analytics query methods."""

    def test_get_popular_topics(self, storage, sample_student):
        """Test getting popular topics across sessions."""
        messages = [{"role": "user", "content": "test"}]

        # Create sessions with different topics
        storage.create_session(sample_student.id, messages, topics="fractions")
        storage.create_session(sample_student.id, messages, topics="fractions")
        storage.create_session(sample_student.id, messages, topics="decimals")

        popular = storage.get_popular_topics()

        assert len(popular) >= 2
        assert popular[0]["topic"] == "fractions"
        assert popular[0]["count"] == 2

    def test_get_popular_topics_by_grade(self, storage):
        """Test filtering popular topics by grade level."""
        messages = [{"role": "user", "content": "test"}]

        student1 = storage.create_student("Student 1", 3, "p1@test.com")
        student2 = storage.create_student("Student 2", 5, "p2@test.com")

        storage.create_session(student1.id, messages, topics="addition")
        storage.create_session(student2.id, messages, topics="fractions")

        grade3_topics = storage.get_popular_topics(grade_level=3)
        grade5_topics = storage.get_popular_topics(grade_level=5)

        assert any(t["topic"] == "addition" for t in grade3_topics)
        assert any(t["topic"] == "fractions" for t in grade5_topics)

    def test_get_student_topic_history(self, storage, sample_student):
        """Test getting chronological topic history for a student."""
        messages = [{"role": "user", "content": "test"}]

        storage.create_session(
            sample_student.id, messages,
            topics="fractions",
            subtopics=["basic fractions"],
            student_confidence=0.6
        )
        storage.create_session(
            sample_student.id, messages,
            topics="decimals",
            subtopics=["decimal notation"],
            student_confidence=0.7
        )

        history = storage.get_student_topic_history(sample_student.id)

        assert len(history) == 2
        assert history[0]["topics"] == "fractions"
        assert history[0]["subtopics"] == ["basic fractions"]
        assert history[0]["confidence"] == 0.6
        assert history[1]["topics"] == "decimals"

    def test_get_struggling_areas(self, storage, sample_student):
        """Test identifying areas where student consistently struggles."""
        messages = [{"role": "user", "content": "test"}]

        # Create multiple sessions with same struggle
        indicators1 = LearningIndicators(
            struggled_with=["common denominators", "simplifying"],
            mastered=[],
            misconceptions=[],
            breakthrough_moments=[],
            needs_review=True
        )
        indicators2 = LearningIndicators(
            struggled_with=["common denominators"],
            mastered=[],
            misconceptions=[],
            breakthrough_moments=[],
            needs_review=True
        )

        storage.create_session(
            sample_student.id, messages,
            learning_indicators=indicators1
        )
        storage.create_session(
            sample_student.id, messages,
            learning_indicators=indicators2
        )

        struggles = storage.get_struggling_areas(sample_student.id)

        assert "common denominators" in struggles
        # Should be sorted by frequency
        assert struggles[0] == "common denominators"

    def test_get_average_confidence(self, storage, sample_student):
        """Test calculating average confidence for a student."""
        messages = [{"role": "user", "content": "test"}]

        storage.create_session(
            sample_student.id, messages,
            topics="fractions",
            student_confidence=0.7
        )
        storage.create_session(
            sample_student.id, messages,
            topics="fractions",
            student_confidence=0.9
        )

        avg_confidence = storage.get_average_confidence(sample_student.id)

        assert avg_confidence == 0.8  # (0.7 + 0.9) / 2

    def test_get_average_confidence_by_topic(self, storage, sample_student):
        """Test calculating average confidence filtered by topic."""
        messages = [{"role": "user", "content": "test"}]

        storage.create_session(
            sample_student.id, messages,
            topics="fractions",
            student_confidence=0.6
        )
        storage.create_session(
            sample_student.id, messages,
            topics="decimals",
            student_confidence=0.9
        )

        fractions_confidence = storage.get_average_confidence(sample_student.id, "fractions")
        decimals_confidence = storage.get_average_confidence(sample_student.id, "decimals")

        assert fractions_confidence == 0.6
        assert decimals_confidence == 0.9

    def test_get_average_confidence_no_data(self, storage, sample_student):
        """Test average confidence returns None when no data exists."""
        avg = storage.get_average_confidence(sample_student.id)
        assert avg is None
