"""Configuration management for Ensina AI."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file (local development)
load_dotenv()

# Try to import Streamlit for secrets (deployed environment)
try:
    import streamlit as st
    # Check if we're running in Streamlit Cloud (secrets will be available)
    if hasattr(st, 'secrets') and len(st.secrets) > 0:
        _use_streamlit_secrets = True
    else:
        _use_streamlit_secrets = False
except (ImportError, FileNotFoundError):
    _use_streamlit_secrets = False

def _get_config(key: str, default=None):
    """Get configuration from Streamlit secrets or environment variables."""
    if _use_streamlit_secrets:
        return st.secrets.get(key, default)
    return os.getenv(key, default)

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"

# Ensure data directory exists
DATA_DIR.mkdir(exist_ok=True)

# API Configuration
ANTHROPIC_API_KEY = _get_config("ANTHROPIC_API_KEY")
OPENAI_API_KEY = _get_config("OPENAI_API_KEY")

# LLM Provider Configuration
LLM_PROVIDER = _get_config("LLM_PROVIDER", "anthropic")  # "anthropic" or "openai"
OPENAI_BASE_URL = _get_config("OPENAI_BASE_URL")  # For OpenAI-compatible endpoints

# Model Configuration
# SLOW_MODEL: For complex tasks requiring deep reasoning (tutoring, analysis)
SLOW_MODEL = _get_config("SLOW_MODEL", "claude-3-5-sonnet-20241022")

# FAST_MODEL: For simple tasks (guardrails, classification, parsing)
FAST_MODEL = _get_config("FAST_MODEL", "claude-3-5-haiku-20241022")

# Legacy support - DEFAULT_MODEL maps to SLOW_MODEL
DEFAULT_MODEL = _get_config("DEFAULT_MODEL", SLOW_MODEL)

# Database Configuration
DATABASE_PATH = _get_config("DATABASE_PATH", str(DATA_DIR / "ensina.db"))

# Application Configuration
APP_NAME = _get_config("APP_NAME", "Ensina AI - Math Tutor")

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

## Visual Math Communication

Use these tools to make math clearer and more engaging:

**1. LaTeX for Mathematical Notation:**
Use LaTeX to display equations beautifully. Wrap inline math in single $ and display math in double $$:

Examples:
- Fractions: $\\frac{3}{5}$ or display: $$\\frac{numerador}{denominador}$$
- Multiplication: $3 \\times 5 = 15$
- Division: $20 \\div 4 = 5$
- Exponents: $x^2$ or $2^3 = 8$
- Roots: $\\sqrt{16} = 4$ or $\\sqrt[3]{27} = 3$
- Equations: $2x + 5 = 13$
- Proportions: $\\frac{a}{b} = \\frac{c}{d}$

**2. Tables for Organizing Information:**
Use Markdown tables to organize proportional relationships, data, and comparisons:

Example for rule of three (regra de três):
```
| Quantidade | Preço |
|------------|-------|
| 3 bolas    | R$ 12 |
| 5 bolas    | ?     |
```

**3. Step-by-Step Formatting:**
Break complex problems into clear numbered steps:

**Passo 1:** Identify the known values
**Passo 2:** Set up the equation
**Passo 3:** Solve for x
**Passo 4:** Check your answer

Use LaTeX generously - it makes math beautiful and professional! Students love seeing proper mathematical notation.

Remember: You're helping them learn to think, not just get the right answer."""

def validate_config():
    """Validate that required configuration is present."""
    if LLM_PROVIDER == "anthropic":
        if not ANTHROPIC_API_KEY:
            raise ValueError(
                "ANTHROPIC_API_KEY not found. Please copy .env.example to .env and add your API key."
            )
    elif LLM_PROVIDER == "openai":
        # For local endpoints, API key might not be needed
        if not OPENAI_BASE_URL and not OPENAI_API_KEY:
            raise ValueError(
                "OPENAI_API_KEY not found. Please set OPENAI_API_KEY in .env or use OPENAI_BASE_URL for local endpoints."
            )
    else:
        raise ValueError(
            f"Unknown LLM_PROVIDER: {LLM_PROVIDER}. Supported values: 'anthropic', 'openai'"
        )
    return True
