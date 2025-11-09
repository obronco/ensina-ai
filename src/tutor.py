"""Core AI tutoring logic for Ensina AI."""
from typing import List, Dict, Optional
from anthropic import Anthropic
from src.config import ANTHROPIC_API_KEY, DEFAULT_MODEL, TUTOR_SYSTEM_PROMPT
from src.storage import Storage, Student


class MathTutor:
    """AI-powered math tutor using Claude with Socratic method."""

    def __init__(self, storage: Storage):
        """Initialize tutor with Claude client and storage."""
        self.client = Anthropic(api_key=ANTHROPIC_API_KEY)
        self.storage = storage
        self.model = DEFAULT_MODEL

    def _build_system_prompt(self, student: Student) -> str:
        """Build personalized system prompt based on student info."""
        prompt = TUTOR_SYSTEM_PROMPT + f"\n\nStudent Context:\n"
        prompt += f"- Name: {student.name}\n"
        prompt += f"- Grade Level: {student.grade_level}\n"
        prompt += f"- Adjust your language and examples to be appropriate for a grade {student.grade_level} student.\n"
        return prompt

    async def get_response(
        self,
        student: Student,
        conversation_history: List[Dict[str, str]],
        new_message: str
    ) -> str:
        """
        Get tutor response to student message.

        Args:
            student: Student information
            conversation_history: Previous messages in this session
            new_message: New message from student

        Returns:
            Tutor's response
        """
        # Build messages for Claude API
        messages = conversation_history + [
            {"role": "user", "content": new_message}
        ]

        # Get response from Claude
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=self._build_system_prompt(student),
            messages=messages
        )

        return response.content[0].text

    def get_response_sync(
        self,
        student: Student,
        conversation_history: List[Dict[str, str]],
        new_message: str
    ) -> str:
        """
        Synchronous version of get_response for Streamlit compatibility.

        Args:
            student: Student information
            conversation_history: Previous messages in this session
            new_message: New message from student

        Returns:
            Tutor's response
        """
        # Build messages for Claude API
        messages = conversation_history + [
            {"role": "user", "content": new_message}
        ]

        # Get response from Claude
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=self._build_system_prompt(student),
            messages=messages
        )

        return response.content[0].text

    def generate_session_summary(
        self,
        student: Student,
        messages: List[Dict[str, str]]
    ) -> Dict[str, str]:
        """
        Generate summary of tutoring session for parent review.

        Args:
            student: Student information
            messages: Full conversation history

        Returns:
            Dictionary with 'summary' and 'topics' keys
        """
        # Build conversation text for analysis
        conversation_text = "\n\n".join([
            f"{msg['role'].upper()}: {msg['content']}"
            for msg in messages
        ])

        summary_prompt = f"""Analyze this tutoring session and provide a brief summary for the student's parent.

Student: {student.name} (Grade {student.grade_level})

Conversation:
{conversation_text}

Please provide:
1. A 2-3 sentence summary of what the student worked on
2. Key topics covered (comma-separated list)
3. Any areas where the student struggled or excelled
4. Recommended next steps if applicable

Format your response as:
SUMMARY: [your summary here]
TOPICS: [topic1, topic2, topic3]
"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=512,
            messages=[{"role": "user", "content": summary_prompt}]
        )

        summary_text = response.content[0].text

        # Parse the response
        summary = ""
        topics = ""

        for line in summary_text.split("\n"):
            if line.startswith("SUMMARY:"):
                summary = line.replace("SUMMARY:", "").strip()
            elif line.startswith("TOPICS:"):
                topics = line.replace("TOPICS:", "").strip()

        return {
            "summary": summary or summary_text[:200],  # Fallback to first 200 chars
            "topics": topics or "General math discussion"
        }

    def get_initial_greeting(self, student: Student) -> str:
        """Get initial greeting for student when starting a session."""
        greetings = [
            f"Hi {student.name}! I'm excited to help you with math today. What would you like to work on?",
            f"Hello {student.name}! Ready to tackle some math? What topic are you studying?",
            f"Hey {student.name}! What math question can I help you with today?",
        ]

        # Simple rotation based on student ID
        return greetings[student.id % len(greetings)] if student.id else greetings[0]
