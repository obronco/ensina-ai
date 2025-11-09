# Contributing to Ensina AI

## Architecture Principles

This project is built with clean architecture to enable easy migration and scaling:

### 1. Separation of Concerns

```
Domain Logic    → src/tutor.py, src/storage.py (core business logic)
Infrastructure  → SQLite, Claude API (swappable implementations)
Presentation    → Streamlit UI (swappable to web framework)
```

### 2. Abstraction Guidelines

When adding features:

- **Storage**: Add methods to `Storage` class with clear interfaces
- **AI Logic**: Keep in `MathTutor` class, independent of UI
- **UI**: Keep in `app.py`, don't mix with business logic

### 3. Future-Proofing

The architecture supports these migrations without major rewrites:

- SQLite → PostgreSQL: Change connection in `storage.py`
- Claude → Other LLM: Implement same interface in `tutor.py`
- Streamlit → FastAPI+React: Reuse `storage.py` and `tutor.py`

## Adding Features

### Adding a New Storage Method

```python
# In src/storage.py
class Storage:
    def your_new_method(self, param: Type) -> ReturnType:
        """Clear docstring."""
        conn = self._get_connection()
        # Implementation
        conn.close()
```

### Adding AI Capabilities

```python
# In src/tutor.py
class MathTutor:
    def new_capability(self, context: ContextType) -> ResponseType:
        """Keep AI logic here, not in UI."""
        # Implementation
```

### Adding UI Pages

```python
# In app.py
elif page == "New Page":
    st.title("New Feature")
    # Use storage and tutor, don't implement logic here
```

## Testing

Before committing:

1. Run setup test: `python test_setup.py`
2. Test manually with real student interaction
3. Check parent dashboard displays correctly

## Code Style

- Use type hints
- Write docstrings for public methods
- Keep functions focused and small
- Use meaningful variable names

## Future Roadmap

See README.md for planned enhancements. High-priority items:

1. Multi-tenant authentication
2. Structured curriculum
3. Gamification (badges, progress tracking)
4. Mobile-friendly UI
5. Email notifications to parents

## Questions?

Open an issue for discussion before major changes.
