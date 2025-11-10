"""Main Streamlit application for Ensina AI."""
import streamlit as st
from datetime import datetime
from src.config import validate_config, APP_NAME, DATABASE_PATH
from src.storage import Storage
from src.tutor import MathTutor

# Page configuration
st.set_page_config(
    page_title=APP_NAME,
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Validate configuration
try:
    validate_config()
except ValueError as e:
    st.error(f"⚠️ Configuration Error: {e}")
    st.stop()

# Initialize storage and tutor (cached)
@st.cache_resource
def get_storage():
    """Get storage instance (cached)."""
    return Storage(DATABASE_PATH)

@st.cache_resource
def get_tutor():
    """Get tutor instance (cached)."""
    storage = get_storage()
    return MathTutor(storage)

storage = get_storage()
tutor = get_tutor()

# Sidebar navigation
st.sidebar.title("🎓 " + APP_NAME)
page = st.sidebar.radio(
    "Navigate",
    ["👨‍🎓 Student", "👨‍👩‍👧 Parent Dashboard", "⚙️ Setup"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.info(
    "Ensina AI is an AI-powered math tutor that uses the Socratic method "
    "to help students learn through guided questioning."
)

# ============================================================================
# STUDENT PAGE
# ============================================================================
if page == "👨‍🎓 Student":
    st.title("📚 Math Tutor")

    # Student selection
    students = storage.list_students()

    if not students:
        st.warning("⚠️ No students found. Please add a student in the Setup page first.")
        st.stop()

    # Student selector
    student_names = {s.name: s for s in students}
    selected_name = st.selectbox(
        "Who are you?",
        options=list(student_names.keys())
    )
    student = student_names[selected_name]

    st.markdown(f"### Hello, {student.name}! 👋")
    st.markdown(f"*Grade {student.grade_level}*")

    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.session_start = datetime.now()

    if "current_student_id" not in st.session_state:
        st.session_state.current_student_id = None

    # Reset conversation if student changed
    if st.session_state.current_student_id != student.id:
        st.session_state.messages = []
        st.session_state.session_start = datetime.now()
        st.session_state.current_student_id = student.id

    # Display initial greeting if no messages
    if not st.session_state.messages:
        greeting = tutor.get_initial_greeting(student)
        st.session_state.messages.append({
            "role": "assistant",
            "content": greeting
        })

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Type your math question here..."):
        # Add user message to chat
        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get tutor response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Get response from tutor
                response = tutor.get_response_sync(
                    student=student,
                    conversation_history=st.session_state.messages[:-1],  # Exclude the message we just added
                    new_message=prompt
                )

                st.markdown(response)

        # Add assistant response to chat
        st.session_state.messages.append({
            "role": "assistant",
            "content": response
        })

    # Session controls
    st.markdown("---")
    col1, col2 = st.columns([1, 4])

    with col1:
        if st.button("🔄 New Session"):
            if len(st.session_state.messages) > 1:  # More than just greeting
                # Save session before resetting
                with st.spinner("Saving session..."):
                    # Calculate duration
                    duration = int((datetime.now() - st.session_state.session_start).total_seconds() / 60)

                    # Generate enhanced summary with analytics
                    summary_data = tutor.generate_enhanced_session_summary(student, st.session_state.messages)

                    # Save to database with full analytics
                    storage.create_session(
                        student_id=student.id,
                        messages=st.session_state.messages,
                        summary=summary_data["summary"],
                        topics=summary_data["topics"],
                        duration_minutes=duration,
                        subtopics=summary_data["subtopics"],
                        difficulty_level=summary_data["difficulty_level"],
                        student_confidence=summary_data["student_confidence"],
                        learning_indicators=summary_data["learning_indicators"],
                        questions_asked=summary_data["questions_asked"]
                    )

                    st.success("✅ Session saved!")

            # Reset conversation
            st.session_state.messages = []
            st.session_state.session_start = datetime.now()
            st.rerun()

    with col2:
        if len(st.session_state.messages) > 1:
            duration = int((datetime.now() - st.session_state.session_start).total_seconds() / 60)
            st.caption(f"⏱️ Session duration: {duration} minutes | Messages: {len(st.session_state.messages)}")

# ============================================================================
# PARENT DASHBOARD PAGE
# ============================================================================
elif page == "👨‍👩‍👧 Parent Dashboard":
    st.title("📊 Parent Dashboard")

    students = storage.list_students()

    if not students:
        st.warning("⚠️ No students found. Please add a student in the Setup page first.")
        st.stop()

    # Student selector
    student_names = {f"{s.name} (Grade {s.grade_level})": s for s in students}
    selected_name = st.selectbox(
        "Select student",
        options=list(student_names.keys())
    )
    student = student_names[selected_name]

    # Get sessions
    sessions = storage.list_sessions(student.id)

    if not sessions:
        st.info(f"No tutoring sessions yet for {student.name}.")
        st.stop()

    # Display summary statistics
    st.markdown("### 📈 Overview")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Sessions", len(sessions))

    with col2:
        total_minutes = sum(s.duration_minutes or 0 for s in sessions)
        st.metric("Total Time", f"{total_minutes} min")

    with col3:
        # Get unique topics
        all_topics = []
        for s in sessions:
            if s.topics:
                all_topics.extend([t.strip() for t in s.topics.split(",")])
        unique_topics = len(set(all_topics))
        st.metric("Topics Covered", unique_topics)

    st.markdown("---")

    # Display sessions
    st.markdown("### 📚 Recent Sessions")

    for session in sessions:
        # Build title with confidence indicator if available
        confidence_emoji = ""
        if session.student_confidence:
            if session.student_confidence >= 0.7:
                confidence_emoji = "😊"
            elif session.student_confidence >= 0.5:
                confidence_emoji = "😐"
            else:
                confidence_emoji = "😟"

        with st.expander(
            f"📅 {session.timestamp[:10]} at {session.timestamp[11:16]} - "
            f"{session.topics or 'General Math'} ({session.duration_minutes or 0} min) {confidence_emoji}"
        ):
            # Summary
            if session.summary:
                st.markdown("**Summary:**")
                st.info(session.summary)
            else:
                st.warning("No summary available for this session.")

            # Analytics section if available
            if session.student_confidence or session.subtopics or session.learning_indicators:
                st.markdown("**📊 Learning Analytics:**")

                col1, col2, col3 = st.columns(3)

                with col1:
                    if session.student_confidence:
                        st.metric("Confidence", f"{int(session.student_confidence * 100)}%")

                with col2:
                    if session.difficulty_level:
                        st.metric("Difficulty", f"{session.difficulty_level}/10")

                with col3:
                    if session.questions_asked:
                        st.metric("Questions Asked", session.questions_asked)

            # Topics and Subtopics
            if session.topics:
                st.markdown("**Topics:**")
                topics_list = [t.strip() for t in session.topics.split(",")]
                st.markdown("• " + "\n• ".join(topics_list))

                if session.subtopics:
                    st.markdown("**Subtopics:**")
                    st.markdown("• " + "\n• ".join(session.subtopics))

            # Learning Indicators
            if session.learning_indicators:
                indicators = session.learning_indicators

                if indicators.mastered:
                    st.markdown("**✅ Mastered:**")
                    st.success("• " + "\n• ".join(indicators.mastered))

                if indicators.struggled_with:
                    st.markdown("**⚠️ Struggled With:**")
                    st.warning("• " + "\n• ".join(indicators.struggled_with))

                if indicators.misconceptions:
                    st.markdown("**🔍 Misconceptions:**")
                    st.error("• " + "\n• ".join(indicators.misconceptions))

                if indicators.breakthrough_moments:
                    st.markdown("**💡 Breakthrough Moments:**")
                    st.info("• " + "\n• ".join(indicators.breakthrough_moments))

                if indicators.needs_review:
                    st.markdown("**📝 Recommendation:**")
                    st.info("This topic needs more practice and review.")

            # Full conversation
            st.markdown("**Full Conversation:**")

            for msg in session.messages:
                if msg["role"] == "user":
                    st.markdown(f"**{student.name}:** {msg['content']}")
                else:
                    st.markdown(f"**Tutor:** {msg['content']}")

            st.markdown("---")

# ============================================================================
# SETUP PAGE
# ============================================================================
elif page == "⚙️ Setup":
    st.title("⚙️ Setup")

    # Display existing students
    st.markdown("### 👥 Students")
    students = storage.list_students()

    if students:
        for student in students:
            with st.expander(f"{student.name} - Grade {student.grade_level}"):
                st.markdown(f"**Parent Email:** {student.parent_email}")
                st.markdown(f"**Created:** {student.created_at}")
    else:
        st.info("No students added yet.")

    # Add new student
    st.markdown("### ➕ Add New Student")

    with st.form("add_student"):
        name = st.text_input("Student Name", placeholder="João Silva")
        grade = st.number_input("Grade Level", min_value=1, max_value=12, value=5)
        email = st.text_input("Parent Email", placeholder="parent@example.com")

        submitted = st.form_submit_button("Add Student")

        if submitted:
            if not name or not email:
                st.error("Please fill in all fields.")
            else:
                student = storage.create_student(name, grade, email)
                st.success(f"✅ Added {student.name}!")
                st.rerun()

    # Configuration info
    st.markdown("---")
    st.markdown("### 🔧 Configuration")

    st.code(f"""
Database: {DATABASE_PATH}
API: Anthropic Claude
Model: {tutor.model}
    """)

    st.markdown("### 📖 Instructions")
    st.markdown("""
1. **Add Students**: Use the form above to add students
2. **Student Mode**: Students can chat with the AI tutor
3. **Parent Dashboard**: Review session summaries and progress
4. **Sessions Auto-save**: When students start a new session or close the app
    """)
