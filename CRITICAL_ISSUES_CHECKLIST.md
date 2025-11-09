# Critical Issues Checklist - Ensina.ai MVP

Quick reference checklist for addressing critical architecture issues.

## 🔴 P0 - Critical (Must Fix Before Production)

### Database Connection Management
- [ ] Replace all `conn = self._get_connection()` with context managers
- [ ] Add `try/finally` or `with` statements to ensure connection cleanup
- [ ] Implement connection pooling (even for SQLite)
- [ ] Add transaction management for multi-step operations
- [ ] Test connection leak scenarios

**Files to Fix:**
- `src/storage.py` - All methods (create_student, get_student, list_students, create_session, etc.)

**Example Fix:**
```python
def create_student(self, name: str, grade_level: int, parent_email: str) -> Student:
    with self._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(...)
        conn.commit()
        # Connection automatically closed
```

---

### Error Handling
- [ ] Wrap all Anthropic API calls in try/except blocks
- [ ] Wrap all database operations in try/except blocks
- [ ] Add retry logic for transient API failures
- [ ] Add user-friendly error messages in UI
- [ ] Add error logging
- [ ] Handle timeout scenarios

**Files to Fix:**
- `src/tutor.py` - get_response_sync(), generate_session_summary()
- `src/storage.py` - All database methods
- `app.py` - All tutor and storage calls

**Example Fix:**
```python
try:
    response = tutor.get_response_sync(...)
except anthropic.APIError as e:
    st.error("Sorry, the tutor is temporarily unavailable. Please try again.")
    logger.error(f"API error: {e}")
except Exception as e:
    st.error("An unexpected error occurred.")
    logger.exception("Unexpected error in tutor response")
```

---

### Security - Authentication
- [ ] Implement basic authentication (password or session-based)
- [ ] Add authorization checks (students can only see their data)
- [ ] Add role-based access control (student vs parent)
- [ ] Secure parent dashboard access
- [ ] Add session timeout

**Files to Fix:**
- `app.py` - Add authentication layer
- `src/storage.py` - Add authorization checks

---

### Security - Input Validation
- [ ] Validate email format for parent_email
- [ ] Validate grade level (1-12 range)
- [ ] Sanitize student names
- [ ] Validate message content (prevent prompt injection)
- [ ] Add length limits on all inputs

**Files to Fix:**
- `src/storage.py` - Add validation before database operations
- `app.py` - Validate form inputs
- `src/tutor.py` - Sanitize messages before sending to API

**Example Fix:**
```python
from pydantic import BaseModel, EmailStr, Field

class StudentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    grade_level: int = Field(..., ge=1, le=12)
    parent_email: EmailStr
```

---

### Security - Data Protection
- [ ] Document security assumptions
- [ ] Add privacy policy documentation
- [ ] Consider data encryption at rest
- [ ] Add API key rotation mechanism
- [ ] Document COPPA/FERPA compliance considerations

---

## 🟠 P1 - High Priority (Fix Soon)

### Fragile Summary Parsing
- [ ] Use Anthropic structured output feature
- [ ] OR improve parsing with better error handling
- [ ] Add validation of parsed results
- [ ] Add retry logic for malformed responses
- [ ] Improve fallback handling

**Files to Fix:**
- `src/tutor.py:136-149` - generate_session_summary()

**Example Fix:**
```python
# Use structured output
response = self.client.messages.create(
    model=self.model,
    max_tokens=512,
    messages=[{"role": "user", "content": summary_prompt}],
    response_format={"type": "json_object"}  # Structured output
)
```

---

### Data Validation Layer
- [ ] Create Pydantic models for Student, Session, etc.
- [ ] Validate all inputs before database operations
- [ ] Return clear validation error messages
- [ ] Add validation tests

**Files to Fix:**
- Create `src/models.py` or `src/validation.py`
- Update `src/storage.py` to use validation

---

### Logging Infrastructure
- [ ] Add structured logging (use `logging` module)
- [ ] Log all API calls (without sensitive data)
- [ ] Log all errors with context
- [ ] Add audit logging for data access
- [ ] Configure log levels

**Files to Fix:**
- Create `src/logger.py` or add to `src/config.py`
- Add logging throughout application

---

## 🟡 P2 - Medium Priority (Nice to Have)

### Code Cleanup
- [ ] Remove unused `get_response()` async method OR implement properly
- [ ] Remove unused progress tracking code OR implement it
- [ ] Extract magic numbers to constants
- [ ] Reduce code duplication

**Files to Fix:**
- `src/tutor.py` - Remove or fix async method
- `src/storage.py` - Remove or implement progress tracking

---

### Configuration Management
- [ ] Move hard-coded values to config
- [ ] Make max_tokens configurable
- [ ] Add configuration validation
- [ ] Document all configuration options

**Files to Fix:**
- `src/config.py` - Add more configuration options
- `src/tutor.py` - Use config values instead of hard-coded

---

### Session State Management
- [ ] Simplify session state logic
- [ ] Add auto-save functionality
- [ ] Handle edge cases (student switching, page refresh)
- [ ] Add session recovery

**Files to Fix:**
- `app.py:76-88` - Improve session state management

---

### Performance Improvements
- [ ] Add caching for student list
- [ ] Implement pagination for sessions
- [ ] Add lazy loading for messages
- [ ] Add timeout to API calls
- [ ] Consider async operations

---

## 📝 Documentation Tasks

- [ ] Document security assumptions and limitations
- [ ] Create Architecture Decision Records (ADRs)
- [ ] Document SQLite limitations and migration path
- [ ] Add deployment security checklist
- [ ] Document error handling strategy
- [ ] Add troubleshooting guide for common issues

---

## 🧪 Testing Tasks

- [ ] Add error handling tests
- [ ] Add input validation tests
- [ ] Add security tests (authentication, authorization)
- [ ] Add integration tests
- [ ] Add concurrent access tests
- [ ] Add edge case tests

---

## Quick Win Priorities

**Start with these for maximum impact:**

1. **Database Connection Management** (2-3 hours)
   - Quick win with high impact
   - Prevents resource leaks
   - Improves reliability

2. **Error Handling** (4-6 hours)
   - Prevents crashes
   - Improves user experience
   - Essential for production

3. **Input Validation** (3-4 hours)
   - Prevents data corruption
   - Improves security
   - Uses existing Pydantic dependency

4. **Basic Authentication** (6-8 hours)
   - Critical for security
   - Can start simple (password)
   - Can enhance later

---

## Estimated Effort

- **P0 Issues:** 20-30 hours
- **P1 Issues:** 10-15 hours
- **P2 Issues:** 8-12 hours
- **Total:** ~40-60 hours of development work

---

## Notes

- All fixes should include tests
- Document changes in code comments
- Update README with new features/limitations
- Consider creating GitHub issues for tracking
