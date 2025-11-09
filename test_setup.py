"""Test script to verify Ensina AI setup."""
import sys
from pathlib import Path

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    try:
        from src import config, storage, tutor
        print("✅ All modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_config():
    """Test configuration."""
    print("\nTesting configuration...")
    try:
        from src.config import validate_config, DATABASE_PATH, APP_NAME
        print(f"  App Name: {APP_NAME}")
        print(f"  Database: {DATABASE_PATH}")
        validate_config()
        print("✅ Configuration valid")
        return True
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("   Make sure to copy .env.example to .env and add your API key")
        return False

def test_database():
    """Test database creation."""
    print("\nTesting database...")
    try:
        from src.storage import Storage
        from src.config import DATABASE_PATH

        # Create test database
        test_db = DATABASE_PATH.replace("ensina.db", "test_ensina.db")
        storage = Storage(test_db)

        # Test student creation
        student = storage.create_student("Test Student", 5, "test@example.com")
        assert student.id is not None
        print(f"  Created student: {student.name}")

        # Test student retrieval
        retrieved = storage.get_student(student.id)
        assert retrieved.name == "Test Student"
        print(f"  Retrieved student: {retrieved.name}")

        # Test session creation
        messages = [
            {"role": "assistant", "content": "Hello!"},
            {"role": "user", "content": "Hi, I need help with fractions"},
            {"role": "assistant", "content": "Great! Let's start with the basics..."}
        ]
        session = storage.create_session(
            student_id=student.id,
            messages=messages,
            summary="Student learned about fractions",
            topics="fractions, basic concepts",
            duration_minutes=15
        )
        assert session.id is not None
        print(f"  Created session: {session.id}")

        # Test session retrieval
        sessions = storage.list_sessions(student.id)
        assert len(sessions) == 1
        print(f"  Retrieved {len(sessions)} session(s)")

        # Cleanup
        Path(test_db).unlink(missing_ok=True)

        print("✅ Database operations working")
        return True

    except Exception as e:
        print(f"❌ Database error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("Ensina AI - Setup Verification")
    print("=" * 60)

    results = []

    results.append(("Imports", test_imports()))
    results.append(("Configuration", test_config()))
    results.append(("Database", test_database()))

    print("\n" + "=" * 60)
    print("Test Results:")
    print("=" * 60)

    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{name:20s} {status}")

    all_passed = all(passed for _, passed in results)

    if all_passed:
        print("\n✅ All tests passed! Your setup is ready.")
        print("\nNext steps:")
        print("1. Run: streamlit run app.py")
        print("2. Go to Setup page and add a student")
        print("3. Start learning!")
    else:
        print("\n❌ Some tests failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
