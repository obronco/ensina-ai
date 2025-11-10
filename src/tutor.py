"""Core AI tutoring logic for Ensina AI."""
from typing import List, Dict, Optional
import re
from anthropic import Anthropic
from src.config import ANTHROPIC_API_KEY, DEFAULT_MODEL, TUTOR_SYSTEM_PROMPT
from src.storage import Storage, Student, LearningIndicators


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

    def analyze_learning_indicators(
        self,
        student: Student,
        messages: List[Dict[str, str]]
    ) -> LearningIndicators:
        """
        Analyze conversation to extract detailed learning signals.

        Args:
            student: Student information
            messages: Full conversation history

        Returns:
            LearningIndicators with detailed learning signals
        """
        # Build conversation text
        conversation_text = "\n\n".join([
            f"{msg['role'].upper()}: {msg['content']}"
            for msg in messages
        ])

        analysis_prompt = f"""Analyze this tutoring session and identify detailed learning signals.

Student: {student.name} (Grade {student.grade_level})

Conversation:
{conversation_text}

Analyze the conversation and identify:

1. STRUGGLED_WITH: Specific concepts the student found difficult (list each one)
2. MASTERED: Concepts the student demonstrated understanding of (list each one)
3. MISCONCEPTIONS: Specific incorrect beliefs or errors in reasoning (list each one)
4. BREAKTHROUGH_MOMENTS: Messages where the student showed sudden understanding (message numbers or quotes)
5. NEEDS_REVIEW: Does this topic need more practice? (YES or NO)

Format your response exactly as:
STRUGGLED_WITH: [concept1, concept2, ...]
MASTERED: [concept1, concept2, ...]
MISCONCEPTIONS: [misconception1, misconception2, ...]
BREAKTHROUGH_MOMENTS: [moment1, moment2, ...]
NEEDS_REVIEW: [YES or NO]
"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=512,
            messages=[{"role": "user", "content": analysis_prompt}]
        )

        analysis_text = response.content[0].text

        # Parse the response
        struggled_with = []
        mastered = []
        misconceptions = []
        breakthrough_moments = []
        needs_review = False

        for line in analysis_text.split("\n"):
            line = line.strip()
            if line.startswith("STRUGGLED_WITH:"):
                content = line.replace("STRUGGLED_WITH:", "").strip()
                struggled_with = [s.strip() for s in content.strip("[]").split(",") if s.strip()]
            elif line.startswith("MASTERED:"):
                content = line.replace("MASTERED:", "").strip()
                mastered = [s.strip() for s in content.strip("[]").split(",") if s.strip()]
            elif line.startswith("MISCONCEPTIONS:"):
                content = line.replace("MISCONCEPTIONS:", "").strip()
                misconceptions = [s.strip() for s in content.strip("[]").split(",") if s.strip()]
            elif line.startswith("BREAKTHROUGH_MOMENTS:"):
                content = line.replace("BREAKTHROUGH_MOMENTS:", "").strip()
                breakthrough_moments = [s.strip() for s in content.strip("[]").split(",") if s.strip()]
            elif line.startswith("NEEDS_REVIEW:"):
                content = line.replace("NEEDS_REVIEW:", "").strip()
                needs_review = "YES" in content.upper()

        return LearningIndicators(
            struggled_with=struggled_with,
            mastered=mastered,
            misconceptions=misconceptions,
            breakthrough_moments=breakthrough_moments,
            needs_review=needs_review
        )

    def estimate_confidence(
        self,
        student: Student,
        messages: List[Dict[str, str]]
    ) -> float:
        """
        Estimate student confidence level from conversation (0.0 to 1.0).

        Uses heuristics based on conversation patterns:
        - Positive feedback from tutor
        - Student explaining concepts back
        - Number of hints needed
        - Hesitation indicators

        Args:
            student: Student information
            messages: Full conversation history

        Returns:
            Confidence estimate (0.0 = very uncertain, 1.0 = very confident)
        """
        if len(messages) < 2:
            return 0.5  # Neutral for very short conversations

        confidence = 0.5  # Start neutral

        # Analyze tutor responses for positive/negative indicators
        positive_phrases = [
            "perfect", "exactly", "great job", "excellent", "that's right",
            "correct", "you got it", "well done", "good thinking"
        ]

        negative_phrases = [
            "not quite", "let's try again", "think about", "remember",
            "careful", "almost", "needs work"
        ]

        # Count indicators in assistant messages
        positive_count = 0
        negative_count = 0

        for msg in messages:
            if msg["role"] == "assistant":
                content_lower = msg["content"].lower()
                positive_count += sum(1 for phrase in positive_phrases if phrase in content_lower)
                negative_count += sum(1 for phrase in negative_phrases if phrase in content_lower)

        # Adjust confidence based on feedback ratio
        total_feedback = positive_count + negative_count
        if total_feedback > 0:
            positive_ratio = positive_count / total_feedback
            confidence = 0.3 + (positive_ratio * 0.6)  # Range: 0.3 to 0.9

        # Look for student hesitation
        hesitation_words = ["i think", "maybe", "i'm not sure", "probably", "i guess"]
        student_hesitation = sum(
            1 for msg in messages
            if msg["role"] == "user" and any(word in msg["content"].lower() for word in hesitation_words)
        )

        # Reduce confidence for hesitation
        confidence -= min(student_hesitation * 0.1, 0.2)

        # Ensure in valid range
        return max(0.0, min(1.0, confidence))

    def extract_subtopics(
        self,
        student: Student,
        messages: List[Dict[str, str]],
        main_topics: str
    ) -> List[str]:
        """
        Extract specific subtopics from conversation.

        Args:
            student: Student information
            messages: Full conversation history
            main_topics: Main topics identified

        Returns:
            List of specific subtopics
        """
        # For simple implementation, use Claude to break down topics
        conversation_text = "\n\n".join([
            f"{msg['role'].upper()}: {msg['content']}"
            for msg in messages[:10]  # Use first 10 messages to save tokens
        ])

        prompt = f"""Based on this math tutoring conversation, list the specific subtopics discussed.

Main topics: {main_topics}

Conversation:
{conversation_text}

List specific subtopics as a comma-separated list (e.g., "adding fractions, common denominators, simplifying fractions")

SUBTOPICS:"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=100,
            messages=[{"role": "user", "content": prompt}]
        )

        subtopics_text = response.content[0].text.strip()

        # Parse comma-separated list
        subtopics = [s.strip() for s in subtopics_text.split(",") if s.strip()]

        return subtopics[:5]  # Limit to 5 subtopics

    def count_student_questions(self, messages: List[Dict[str, str]]) -> int:
        """Count number of questions asked by student."""
        count = 0
        for msg in messages:
            if msg["role"] == "user":
                # Simple heuristic: count messages ending with ?
                if "?" in msg["content"]:
                    count += 1
        return count

    def estimate_difficulty(self, student: Student, topics: str) -> int:
        """
        Estimate difficulty level of session content (1-10).

        Based on student's grade level and topics covered.
        """
        # Simple heuristic based on grade level and topic complexity
        base_difficulty = student.grade_level

        # Adjust for advanced topics
        advanced_keywords = ["algebra", "geometry", "calculus", "trigonometry", "polynomial"]
        if any(keyword in topics.lower() for keyword in advanced_keywords):
            base_difficulty += 2

        # Adjust for basic topics
        basic_keywords = ["counting", "addition", "subtraction", "shapes"]
        if any(keyword in topics.lower() for keyword in basic_keywords):
            base_difficulty -= 1

        return max(1, min(10, base_difficulty))

    def generate_enhanced_session_summary(
        self,
        student: Student,
        messages: List[Dict[str, str]]
    ) -> Dict:
        """
        Generate comprehensive session analysis with all analytics.

        Returns:
            Dictionary with summary, topics, and all learning analytics
        """
        # Get basic summary and topics
        basic_summary = self.generate_session_summary(student, messages)

        # Extract subtopics
        subtopics = self.extract_subtopics(student, messages, basic_summary["topics"])

        # Analyze learning indicators
        learning_indicators = self.analyze_learning_indicators(student, messages)

        # Estimate confidence
        confidence = self.estimate_confidence(student, messages)

        # Count questions
        questions_asked = self.count_student_questions(messages)

        # Estimate difficulty
        difficulty = self.estimate_difficulty(student, basic_summary["topics"])

        return {
            "summary": basic_summary["summary"],
            "topics": basic_summary["topics"],
            "subtopics": subtopics,
            "difficulty_level": difficulty,
            "student_confidence": confidence,
            "learning_indicators": learning_indicators,
            "questions_asked": questions_asked
        }
