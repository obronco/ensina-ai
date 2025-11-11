# Ensina AI 📚

An AI-powered math tutor that uses the Socratic method to help students learn through guided questioning. Built with Claude AI and Streamlit.

## Features

### For Students
- **🤖 Socratic Tutoring**: AI instructor asks guiding questions instead of just giving answers
- **👨‍🎓 Student Interface**: Clean chat interface for students to get math help
- **📝 Assignment Mode**: Complete teacher-assigned problems with full AI assistance
- **🛡️ Content Guardrails**: Off-topic message detection keeps students focused on math
- **🎯 Grade-Appropriate**: Tutor adapts language to student's grade level

### For Teachers
- **👨‍🏫 Assignment Creation**: Create math problems and assign to students by grade level
- **📊 Submission Review**: See complete conversation transcripts showing student thinking
- **🔍 Engagement Analytics**: Time spent, questions asked, confidence level, difficulty
- **💡 Learning Indicators**: Mastered concepts, struggles, misconceptions, breakthrough moments
- **✍️ Teacher Feedback**: Add notes and mark submissions as reviewed

### For Parents
- **👨‍👩‍👧 Parent Dashboard**: Review session summaries and track progress
- **⚠️ Incident Reports**: View off-topic message attempts with resolution tracking
- **📈 Learning Analytics**: Confidence tracking, topics mastered, areas needing review
- **💾 Progress Tracking**: Automatic session saving with detailed summaries

## Architecture

Built with clean abstractions for easy future migration:

```
src/
├── config.py       # Configuration management
├── storage.py      # Database layer (SQLite, swappable to Postgres)
├── tutor.py        # AI tutoring logic (Claude, swappable to other LLMs)
└── app.py          # Streamlit UI (swappable to web framework)
```

## Quick Start

### Prerequisites

- Python 3.11 or higher
- Anthropic API key ([Get one here](https://console.anthropic.com/))

### Installation

1. **Clone and navigate to the repository:**
   ```bash
   cd ensina-ai
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   ```

4. **Edit `.env` and add your Anthropic API key:**
   ```bash
   ANTHROPIC_API_KEY=your_api_key_here
   ```

5. **Run the application:**
   ```bash
   streamlit run app.py
   ```

6. **Open your browser:**
   The app will automatically open at `http://localhost:8501`

## Usage

### First Time Setup

1. Go to **⚙️ Setup** page
2. Add a student with their name, grade level, and parent email
3. Navigate to **👨‍🎓 Student** page to start learning!

### Student Mode

1. Select your name from the dropdown
2. Ask math questions in the chat
3. The tutor will guide you with questions, not just answers
4. Click "🔄 New Session" when done to save your progress

### Parent Dashboard

1. Go to **👨‍👩‍👧 Parent Dashboard**
2. Select a student to view their sessions
3. See summaries, topics covered, and full conversations
4. Track time spent and areas where they struggled or excelled

## How It Works

### Socratic Method

The AI tutor is designed to:
- Ask guiding questions instead of giving direct answers
- Build conceptual understanding, not just procedural knowledge
- Encourage critical thinking
- Make mistakes feel safe and part of learning
- Use age-appropriate language and examples

### Example Interaction

```
Student: I don't understand fractions

Tutor: Great question! Let me help you understand fractions.
Imagine you have a pizza. If you cut it into 4 equal pieces
and eat 1 piece, what fraction of the pizza did you eat?

Student: 1/4?

Tutor: Exactly! The bottom number (4) tells us how many equal
pieces the pizza was cut into. What do you think the top
number (1) represents?
```

## Project Structure

```
ensina-ai/
├── src/
│   ├── config.py           # Configuration and settings
│   ├── storage.py          # Database models and operations
│   ├── tutor.py            # AI tutoring logic
│   └── __init__.py
├── tests/
│   ├── test_storage.py     # Storage layer tests
│   ├── test_tutor.py       # Tutor logic tests (mocked LLM)
│   ├── conftest.py         # Test fixtures
│   └── __init__.py
├── data/
│   └── ensina.db           # SQLite database (auto-created)
├── app.py                  # Main Streamlit application
├── test_setup.py           # Setup verification script
├── requirements.txt        # Python dependencies
├── pytest.ini              # Pytest configuration
├── .env.example            # Environment template
├── .gitignore
└── README.md
```

## Database Schema

### Students
- `id`: Primary key
- `name`: Student name
- `grade_level`: 1-12
- `parent_email`: Contact for reports
- `created_at`: Timestamp

### Teachers
- `id`: Primary key
- `name`: Teacher name
- `email`: Unique email address
- `school`: School name (optional)
- `created_at`: Timestamp

### Assignments
- `id`: Primary key
- `teacher_id`: Foreign key to teachers
- `title`: Assignment title
- `description`: Problem statement/description
- `grade_level`: Target grade (1-12)
- `topics`: Expected topics (comma-separated)
- `created_at`: Timestamp
- `due_date`: Optional deadline

### Sessions
- `id`: Primary key
- `student_id`: Foreign key to students
- `timestamp`: Session start time
- `messages`: Full conversation (JSON)
- `summary`: AI-generated summary
- `topics`: Comma-separated topics
- `duration_minutes`: Session length
- `subtopics`: Granular topic breakdown (JSON)
- `difficulty_level`: 1-10 estimate
- `student_confidence`: 0.0-1.0 confidence score
- `learning_indicators`: Detailed learning signals (JSON)
- `questions_asked`: Count of student questions

### Submissions
- `id`: Primary key
- `assignment_id`: Foreign key to assignments
- `student_id`: Foreign key to students
- `session_id`: Foreign key to sessions
- `submitted_at`: Timestamp
- `teacher_reviewed`: Boolean flag
- `teacher_notes`: Teacher feedback

### Incidents
- `id`: Primary key
- `student_id`: Foreign key to students
- `session_id`: Foreign key to sessions (optional)
- `timestamp`: When incident occurred
- `incident_type`: Type (e.g., "off_topic")
- `message`: The flagged message
- `reason`: Why it was flagged
- `resolved`: Boolean (parent acknowledged)

### Progress
- `student_id`: Foreign key to students
- `topic`: Math topic (e.g., "fractions")
- `mastery_level`: 0.0 to 1.0
- `last_practiced`: Date

## Future Enhancements

The architecture is designed to make these additions straightforward:

- [ ] Multi-tenant accounts with authentication
- [ ] Structured curriculum with lessons and modules
- [ ] Gamification (badges, XP, streaks)
- [ ] Mobile app (reuse API layer)
- [ ] Progress analytics and insights
- [ ] Email summaries to parents
- [ ] Practice problem generation
- [ ] Multiple subjects beyond math
- [ ] Migrate to PostgreSQL for scale
- [ ] Deploy to Streamlit Cloud or web hosting

## Testing

The project includes comprehensive unit tests for business logic with mocked LLM calls.

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=term-missing

# Run specific test file
pytest tests/test_storage.py
pytest tests/test_tutor.py

# Run with verbose output
pytest -v

# Generate HTML coverage report
pytest --cov=src --cov-report=html
# Then open htmlcov/index.html in your browser
```

### Test Structure

- **`tests/test_storage.py`**: Tests for database operations (no mocking needed)
- **`tests/test_tutor.py`**: Tests for AI tutor logic with mocked Claude API
- **`tests/conftest.py`**: Shared fixtures and test configuration

### What's Tested

- ✅ Student CRUD operations
- ✅ Session creation and retrieval
- ✅ Progress tracking
- ✅ Data integrity and isolation
- ✅ Tutor response generation (mocked)
- ✅ Session summary generation (mocked)
- ✅ System prompt personalization
- ✅ Message formatting
- ✅ Error handling

All tests use mocked LLM calls, so **no API key required** and **zero cost** to run tests!

## Configuration

Edit `.env` to customize:

```bash
# Required
ANTHROPIC_API_KEY=your_key_here

# Model Configuration (Optional - defaults provided)
# SLOW_MODEL: For complex tasks (tutoring, analysis) - high quality
SLOW_MODEL=claude-3-5-sonnet-20241022

# FAST_MODEL: For simple tasks (guardrails, classification) - fast & cheaper
FAST_MODEL=claude-3-5-haiku-20241022

# Optional
DATABASE_PATH=data/ensina.db
APP_NAME=Ensina AI
```

### Cost Optimization Strategy

The system uses two models strategically:

**Sonnet (SLOW_MODEL)** - Used for:
- Main tutoring conversations (quality matters)
- Session summaries and analytics
- Learning indicators analysis

**Haiku (FAST_MODEL)** - Used for:
- Content guardrails (off-topic detection)
- Simple text extraction (subtopics)
- Quick classifications

This reduces costs by ~60% while maintaining tutoring quality!

## Deployment

### Local Use
```bash
streamlit run app.py
```

### Streamlit Cloud (Public Hosting)

**Quick Start:**
1. Push your code to GitHub (excluding `.env`)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Add `ANTHROPIC_API_KEY` to Secrets in Streamlit Cloud settings
5. Deploy!

**📖 Detailed Instructions**: See [DEPLOYMENT.md](./DEPLOYMENT.md) for complete step-by-step guide including:
- Setting up secrets
- Database persistence considerations
- Cost estimation
- Production recommendations
- Troubleshooting

## Cost Considerations

**With Optimized Model Strategy:**
- **Sonnet**: $3/MTok input, $15/MTok output
- **Haiku**: $0.25/MTok input, $1.25/MTok output (12x cheaper!)
- **Typical session**: ~$0.01-0.03 per session (60% reduction vs Sonnet-only)
- **Estimate**: ~$3-6/month for 1 student with daily use
- Monitor usage in [Anthropic Console](https://console.anthropic.com/)

**Cost Breakdown per Session:**
- Main tutoring (Sonnet): ~$0.01-0.02
- Guardrails (Haiku): ~$0.0005
- Subtopics (Haiku): ~$0.0005
- Analytics (Sonnet): ~$0.003

**For Teachers (100 students, 2 sessions/week):**
- Without optimization: ~$400/week
- With optimization: ~$160/week (~60% savings!)

## Troubleshooting

### "Configuration Error: ANTHROPIC_API_KEY not found"
- Make sure you copied `.env.example` to `.env`
- Add your API key to `.env` file
- Restart the application

### Database issues
- Delete `data/ensina.db` to reset
- Database will be recreated automatically

### Import errors
- Make sure you're running from the project root
- Verify all dependencies: `pip install -r requirements.txt`

## Contributing

This is a personal project, but feedback and suggestions are welcome!

## License

MIT License - Feel free to use and modify for your own family or educational purposes.

## Credits

Built with:
- [Anthropic Claude](https://www.anthropic.com/claude) - AI tutoring
- [Streamlit](https://streamlit.io/) - Web interface
- [SQLite](https://www.sqlite.org/) - Database

---

Made with ❤️ for better math education
