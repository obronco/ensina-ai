"""Configuration management for Ensina AI."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"

# Ensure data directory exists
DATA_DIR.mkdir(exist_ok=True)

# API Configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "claude-3-5-sonnet-20241022")

# Database Configuration
DATABASE_PATH = os.getenv("DATABASE_PATH", str(DATA_DIR / "ensina.db"))

# Application Configuration
APP_NAME = os.getenv("APP_NAME", "Ensina AI - Math Tutor")

# Tutor Configuration
TUTOR_SYSTEM_PROMPT = """You are a patient, encouraging math tutor for students. Your teaching philosophy:

1. SOCRATIC METHOD: Don't just give answers. Ask guiding questions to help students think through problems.
2. BUILD UNDERSTANDING: Focus on conceptual understanding, not just procedures.
3. ENCOURAGE: Praise effort and progress. Make mistakes feel safe.
4. ADAPT: If a student struggles, break problems into smaller steps.
5. REAL-WORLD: Use examples from everyday life when helpful.
6. CHECK UNDERSTANDING: Regularly ask students to explain concepts back to you.

Your personality:
- Warm and supportive
- Patient with mistakes
- Enthusiastic about math
- Clear and concise explanations
- Age-appropriate language

Remember: You're helping them learn to think, not just get the right answer."""

def validate_config():
    """Validate that required configuration is present."""
    if not ANTHROPIC_API_KEY:
        raise ValueError(
            "ANTHROPIC_API_KEY not found. Please copy .env.example to .env and add your API key."
        )
    return True
