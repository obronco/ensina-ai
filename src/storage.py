"""Storage layer for Ensina AI using SQLite."""
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional, Any
from pathlib import Path
from dataclasses import dataclass, asdict


@dataclass
class Student:
    """Student model."""
    id: Optional[int]
    name: str
    grade_level: int
    parent_email: str
    created_at: Optional[str] = None


@dataclass
class LearningIndicators:
    """Learning signals extracted from a session."""
    struggled_with: List[str]  # Concepts student found difficult
    mastered: List[str]  # Concepts student understood well
    misconceptions: List[str]  # Specific errors in understanding
    breakthrough_moments: List[str]  # Messages where understanding clicked
    needs_review: bool  # Whether topic needs more practice


@dataclass
class Session:
    """Tutoring session model."""
    id: Optional[int]
    student_id: int
    timestamp: str
    messages: List[Dict[str, str]]  # [{"role": "user/assistant", "content": "..."}]
    summary: Optional[str] = None
    topics: Optional[str] = None  # Comma-separated
    duration_minutes: Optional[int] = None
    # Enhanced analytics fields
    subtopics: Optional[List[str]] = None  # More granular topic breakdown
    difficulty_level: Optional[int] = None  # 1-10 estimate
    student_confidence: Optional[float] = None  # 0.0-1.0 from conversation analysis
    learning_indicators: Optional[LearningIndicators] = None  # Detailed learning signals
    questions_asked: Optional[int] = None  # Count of student questions


@dataclass
class Progress:
    """Student progress model."""
    student_id: int
    topic: str
    mastery_level: float  # 0.0 to 1.0
    last_practiced: str


@dataclass
class Incident:
    """Off-topic or inappropriate interaction incident."""
    id: Optional[int]
    student_id: int
    session_id: Optional[int]  # May not be associated with a session yet
    timestamp: str
    incident_type: str  # "off_topic", "inappropriate", etc.
    message: str  # The message that triggered the incident
    reason: str  # Why it was flagged
    resolved: bool = False  # Whether parent has acknowledged


class Storage:
    """SQLite storage with clean abstraction for future migration."""

    def __init__(self, db_path: str):
        """Initialize storage and create tables if needed."""
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Access columns by name
        return conn

    def _init_db(self):
        """Create database tables if they don't exist."""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Students table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                grade_level INTEGER NOT NULL,
                parent_email TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                messages TEXT NOT NULL,  -- JSON
                summary TEXT,
                topics TEXT,
                duration_minutes INTEGER,
                FOREIGN KEY (student_id) REFERENCES students(id)
            )
        """)

        # Add new analytics columns if they don't exist (for existing databases)
        self._add_analytics_columns(cursor)

        # Progress table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS progress (
                student_id INTEGER NOT NULL,
                topic TEXT NOT NULL,
                mastery_level REAL NOT NULL,
                last_practiced DATE NOT NULL,
                PRIMARY KEY (student_id, topic),
                FOREIGN KEY (student_id) REFERENCES students(id)
            )
        """)

        # Incidents table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS incidents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                session_id INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                incident_type TEXT NOT NULL,
                message TEXT NOT NULL,
                reason TEXT NOT NULL,
                resolved BOOLEAN DEFAULT 0,
                FOREIGN KEY (student_id) REFERENCES students(id),
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            )
        """)

        conn.commit()
        conn.close()

    def _add_analytics_columns(self, cursor):
        """Add analytics columns to sessions table if they don't exist."""
        # Get existing columns
        cursor.execute("PRAGMA table_info(sessions)")
        existing_columns = {row[1] for row in cursor.fetchall()}

        # Add new columns if they don't exist
        new_columns = {
            "subtopics": "TEXT",  # JSON array
            "difficulty_level": "INTEGER",
            "student_confidence": "REAL",
            "learning_indicators": "TEXT",  # JSON object
            "questions_asked": "INTEGER"
        }

        for column, column_type in new_columns.items():
            if column not in existing_columns:
                try:
                    cursor.execute(f"ALTER TABLE sessions ADD COLUMN {column} {column_type}")
                except sqlite3.OperationalError:
                    # Column might already exist from a previous run
                    pass

    # Student operations
    def create_student(self, name: str, grade_level: int, parent_email: str) -> Student:
        """Create a new student."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO students (name, grade_level, parent_email) VALUES (?, ?, ?)",
            (name, grade_level, parent_email)
        )
        student_id = cursor.lastrowid

        cursor.execute("SELECT * FROM students WHERE id = ?", (student_id,))
        row = cursor.fetchone()

        conn.commit()
        conn.close()

        return Student(
            id=row["id"],
            name=row["name"],
            grade_level=row["grade_level"],
            parent_email=row["parent_email"],
            created_at=row["created_at"]
        )

    def get_student(self, student_id: int) -> Optional[Student]:
        """Get student by ID."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM students WHERE id = ?", (student_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return Student(
            id=row["id"],
            name=row["name"],
            grade_level=row["grade_level"],
            parent_email=row["parent_email"],
            created_at=row["created_at"]
        )

    def list_students(self) -> List[Student]:
        """List all students."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM students ORDER BY name")
        rows = cursor.fetchall()
        conn.close()

        return [
            Student(
                id=row["id"],
                name=row["name"],
                grade_level=row["grade_level"],
                parent_email=row["parent_email"],
                created_at=row["created_at"]
            )
            for row in rows
        ]

    # Session operations
    def create_session(
        self,
        student_id: int,
        messages: List[Dict[str, str]],
        summary: Optional[str] = None,
        topics: Optional[str] = None,
        duration_minutes: Optional[int] = None,
        subtopics: Optional[List[str]] = None,
        difficulty_level: Optional[int] = None,
        student_confidence: Optional[float] = None,
        learning_indicators: Optional[LearningIndicators] = None,
        questions_asked: Optional[int] = None
    ) -> Session:
        """Save a tutoring session with enhanced analytics."""
        conn = self._get_connection()
        cursor = conn.cursor()

        messages_json = json.dumps(messages)
        timestamp = datetime.now().isoformat()

        # Serialize complex fields
        subtopics_json = json.dumps(subtopics) if subtopics else None
        learning_indicators_json = None
        if learning_indicators:
            learning_indicators_json = json.dumps({
                "struggled_with": learning_indicators.struggled_with,
                "mastered": learning_indicators.mastered,
                "misconceptions": learning_indicators.misconceptions,
                "breakthrough_moments": learning_indicators.breakthrough_moments,
                "needs_review": learning_indicators.needs_review
            })

        cursor.execute(
            """
            INSERT INTO sessions (
                student_id, timestamp, messages, summary, topics, duration_minutes,
                subtopics, difficulty_level, student_confidence, learning_indicators, questions_asked
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (student_id, timestamp, messages_json, summary, topics, duration_minutes,
             subtopics_json, difficulty_level, student_confidence, learning_indicators_json, questions_asked)
        )
        session_id = cursor.lastrowid

        conn.commit()
        conn.close()

        return Session(
            id=session_id,
            student_id=student_id,
            timestamp=timestamp,
            messages=messages,
            summary=summary,
            topics=topics,
            duration_minutes=duration_minutes,
            subtopics=subtopics,
            difficulty_level=difficulty_level,
            student_confidence=student_confidence,
            learning_indicators=learning_indicators,
            questions_asked=questions_asked
        )

    def _deserialize_session(self, row) -> Session:
        """Helper to deserialize a session row."""
        # Deserialize learning indicators if present
        learning_indicators = None
        if "learning_indicators" in row.keys() and row["learning_indicators"]:
            data = json.loads(row["learning_indicators"])
            learning_indicators = LearningIndicators(
                struggled_with=data.get("struggled_with", []),
                mastered=data.get("mastered", []),
                misconceptions=data.get("misconceptions", []),
                breakthrough_moments=data.get("breakthrough_moments", []),
                needs_review=data.get("needs_review", False)
            )

        # Helper to safely get optional fields
        def get_field(field_name):
            return row[field_name] if field_name in row.keys() else None

        return Session(
            id=row["id"],
            student_id=row["student_id"],
            timestamp=row["timestamp"],
            messages=json.loads(row["messages"]),
            summary=row["summary"],
            topics=row["topics"],
            duration_minutes=row["duration_minutes"],
            subtopics=json.loads(get_field("subtopics")) if get_field("subtopics") else None,
            difficulty_level=get_field("difficulty_level"),
            student_confidence=get_field("student_confidence"),
            learning_indicators=learning_indicators,
            questions_asked=get_field("questions_asked")
        )

    def get_session(self, session_id: int) -> Optional[Session]:
        """Get session by ID."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return self._deserialize_session(row)

    def list_sessions(self, student_id: int, limit: int = 50) -> List[Session]:
        """List sessions for a student."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM sessions WHERE student_id = ? ORDER BY timestamp DESC LIMIT ?",
            (student_id, limit)
        )
        rows = cursor.fetchall()
        conn.close()

        return [self._deserialize_session(row) for row in rows]

    def update_session_summary(self, session_id: int, summary: str, topics: str):
        """Update session with AI-generated summary."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE sessions SET summary = ?, topics = ? WHERE id = ?",
            (summary, topics, session_id)
        )

        conn.commit()
        conn.close()

    # Progress operations
    def update_progress(self, student_id: int, topic: str, mastery_level: float):
        """Update or create progress for a topic."""
        conn = self._get_connection()
        cursor = conn.cursor()

        today = datetime.now().date().isoformat()

        cursor.execute(
            """
            INSERT INTO progress (student_id, topic, mastery_level, last_practiced)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(student_id, topic) DO UPDATE SET
                mastery_level = ?,
                last_practiced = ?
            """,
            (student_id, topic, mastery_level, today, mastery_level, today)
        )

        conn.commit()
        conn.close()

    def get_progress(self, student_id: int) -> List[Progress]:
        """Get all progress for a student."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM progress WHERE student_id = ? ORDER BY last_practiced DESC",
            (student_id,)
        )
        rows = cursor.fetchall()
        conn.close()

        return [
            Progress(
                student_id=row["student_id"],
                topic=row["topic"],
                mastery_level=row["mastery_level"],
                last_practiced=row["last_practiced"]
            )
            for row in rows
        ]

    # Analytics operations
    def get_popular_topics(self, grade_level: Optional[int] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most discussed topics across students."""
        conn = self._get_connection()
        cursor = conn.cursor()

        if grade_level:
            cursor.execute("""
                SELECT topics, COUNT(*) as count
                FROM sessions s
                JOIN students st ON s.student_id = st.id
                WHERE st.grade_level = ? AND topics IS NOT NULL
                GROUP BY topics
                ORDER BY count DESC
                LIMIT ?
            """, (grade_level, limit))
        else:
            cursor.execute("""
                SELECT topics, COUNT(*) as count
                FROM sessions
                WHERE topics IS NOT NULL
                GROUP BY topics
                ORDER BY count DESC
                LIMIT ?
            """, (limit,))

        rows = cursor.fetchall()
        conn.close()

        return [{"topic": row["topics"], "count": row["count"]} for row in rows]

    def get_student_topic_history(self, student_id: int) -> List[Dict[str, Any]]:
        """Get chronological history of topics discussed by a student."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT topics, subtopics, timestamp, student_confidence
            FROM sessions
            WHERE student_id = ? AND topics IS NOT NULL
            ORDER BY timestamp ASC
        """, (student_id,))

        rows = cursor.fetchall()
        conn.close()

        return [{
            "topics": row["topics"],
            "subtopics": json.loads(row["subtopics"]) if row["subtopics"] else [],
            "timestamp": row["timestamp"],
            "confidence": row["student_confidence"]
        } for row in rows]

    def get_struggling_areas(self, student_id: int) -> List[str]:
        """Identify topics where student consistently struggles."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT learning_indicators
            FROM sessions
            WHERE student_id = ? AND learning_indicators IS NOT NULL
        """, (student_id,))

        rows = cursor.fetchall()
        conn.close()

        # Aggregate struggled_with across sessions
        struggles = {}
        for row in rows:
            indicators = json.loads(row["learning_indicators"])
            for struggle in indicators.get("struggled_with", []):
                struggles[struggle] = struggles.get(struggle, 0) + 1

        # Return topics mentioned multiple times, sorted by frequency
        return [topic for topic, count in sorted(struggles.items(), key=lambda x: x[1], reverse=True) if count >= 2]

    def get_average_confidence(self, student_id: int, topic: Optional[str] = None) -> Optional[float]:
        """Get average confidence level for student, optionally filtered by topic."""
        conn = self._get_connection()
        cursor = conn.cursor()

        if topic:
            cursor.execute("""
                SELECT AVG(student_confidence) as avg_conf
                FROM sessions
                WHERE student_id = ? AND topics LIKE ? AND student_confidence IS NOT NULL
            """, (student_id, f"%{topic}%"))
        else:
            cursor.execute("""
                SELECT AVG(student_confidence) as avg_conf
                FROM sessions
                WHERE student_id = ? AND student_confidence IS NOT NULL
            """, (student_id,))

        row = cursor.fetchone()
        conn.close()

        return row["avg_conf"] if row and row["avg_conf"] else None

    # Incident operations
    def create_incident(
        self,
        student_id: int,
        incident_type: str,
        message: str,
        reason: str,
        session_id: Optional[int] = None
    ) -> Incident:
        """Log an incident (e.g., off-topic message)."""
        conn = self._get_connection()
        cursor = conn.cursor()

        timestamp = datetime.now().isoformat()

        cursor.execute(
            """
            INSERT INTO incidents (student_id, session_id, timestamp, incident_type, message, reason, resolved)
            VALUES (?, ?, ?, ?, ?, ?, 0)
            """,
            (student_id, session_id, timestamp, incident_type, message, reason)
        )
        incident_id = cursor.lastrowid

        conn.commit()
        conn.close()

        return Incident(
            id=incident_id,
            student_id=student_id,
            session_id=session_id,
            timestamp=timestamp,
            incident_type=incident_type,
            message=message,
            reason=reason,
            resolved=False
        )

    def get_incidents(self, student_id: int, unresolved_only: bool = False) -> List[Incident]:
        """Get incidents for a student."""
        conn = self._get_connection()
        cursor = conn.cursor()

        if unresolved_only:
            cursor.execute(
                "SELECT * FROM incidents WHERE student_id = ? AND resolved = 0 ORDER BY timestamp DESC",
                (student_id,)
            )
        else:
            cursor.execute(
                "SELECT * FROM incidents WHERE student_id = ? ORDER BY timestamp DESC",
                (student_id,)
            )

        rows = cursor.fetchall()
        conn.close()

        return [
            Incident(
                id=row["id"],
                student_id=row["student_id"],
                session_id=row["session_id"],
                timestamp=row["timestamp"],
                incident_type=row["incident_type"],
                message=row["message"],
                reason=row["reason"],
                resolved=bool(row["resolved"])
            )
            for row in rows
        ]

    def mark_incident_resolved(self, incident_id: int):
        """Mark an incident as resolved (parent acknowledged)."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE incidents SET resolved = 1 WHERE id = ?",
            (incident_id,)
        )

        conn.commit()
        conn.close()

    def count_incidents(self, student_id: int, incident_type: Optional[str] = None) -> int:
        """Count incidents for a student, optionally filtered by type."""
        conn = self._get_connection()
        cursor = conn.cursor()

        if incident_type:
            cursor.execute(
                "SELECT COUNT(*) as count FROM incidents WHERE student_id = ? AND incident_type = ?",
                (student_id, incident_type)
            )
        else:
            cursor.execute(
                "SELECT COUNT(*) as count FROM incidents WHERE student_id = ?",
                (student_id,)
            )

        row = cursor.fetchone()
        conn.close()

        return row["count"] if row else 0
