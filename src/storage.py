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
class Session:
    """Tutoring session model."""
    id: Optional[int]
    student_id: int
    timestamp: str
    messages: List[Dict[str, str]]  # [{"role": "user/assistant", "content": "..."}]
    summary: Optional[str] = None
    topics: Optional[str] = None  # Comma-separated
    duration_minutes: Optional[int] = None


@dataclass
class Progress:
    """Student progress model."""
    student_id: int
    topic: str
    mastery_level: float  # 0.0 to 1.0
    last_practiced: str


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

        conn.commit()
        conn.close()

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
        duration_minutes: Optional[int] = None
    ) -> Session:
        """Save a tutoring session."""
        conn = self._get_connection()
        cursor = conn.cursor()

        messages_json = json.dumps(messages)
        timestamp = datetime.now().isoformat()

        cursor.execute(
            """
            INSERT INTO sessions (student_id, timestamp, messages, summary, topics, duration_minutes)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (student_id, timestamp, messages_json, summary, topics, duration_minutes)
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
            duration_minutes=duration_minutes
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

        return Session(
            id=row["id"],
            student_id=row["student_id"],
            timestamp=row["timestamp"],
            messages=json.loads(row["messages"]),
            summary=row["summary"],
            topics=row["topics"],
            duration_minutes=row["duration_minutes"]
        )

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

        return [
            Session(
                id=row["id"],
                student_id=row["student_id"],
                timestamp=row["timestamp"],
                messages=json.loads(row["messages"]),
                summary=row["summary"],
                topics=row["topics"],
                duration_minutes=row["duration_minutes"]
            )
            for row in rows
        ]

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
