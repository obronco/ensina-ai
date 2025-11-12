"""Main Streamlit application for Ensina AI."""
import streamlit as st
from datetime import datetime
import re
from src.config import validate_config, APP_NAME, DATABASE_PATH
from src.storage import Storage
from src.tutor import MathTutor
from src.graph_renderer import GraphRenderer

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


def parse_and_display_message(content: str):
    """
    Parse message content and display text and graphs.

    Args:
        content: Message content that may contain graph specifications
    """
    # Pattern to match ```graph ... ``` blocks
    graph_pattern = r'```graph\s*\n(.*?)\n```'

    # Find all graph blocks
    graphs = re.findall(graph_pattern, content, re.DOTALL)

    if graphs:
        # Split content by graph blocks
        parts = re.split(graph_pattern, content, flags=re.DOTALL)

        # Display alternating text and graphs
        for i, part in enumerate(parts):
            if i % 2 == 0:
                # Text content
                if part.strip():
                    st.markdown(part)
            else:
                # Graph specification (this is a captured group from the split)
                # Skip it as we'll handle graphs from the separate list
                pass

        # Render graphs
        for graph_json in graphs:
            spec = GraphRenderer.parse_graph_spec(graph_json)
            if spec:
                try:
                    fig = GraphRenderer.render(spec)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.error(f"Error rendering graph: {e}")
    else:
        # No graphs, just display markdown
        st.markdown(content)


# Sidebar navigation
st.sidebar.title("🎓 " + APP_NAME)
page = st.sidebar.radio(
    "Navigate",
    ["👨‍🎓 Student", "👨‍👩‍👧 Parent Dashboard", "👨‍🏫 Teacher View", "⚙️ Setup"]
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

    # Assignment selection (optional)
    st.markdown("---")
    assignments = storage.list_assignments(grade_level=student.grade_level)

    if assignments:
        st.markdown("### 📝 Available Assignments")

        # Check if student already has a submission for any assignment
        assignment_options = {}
        for assignment in assignments:
            submission = storage.get_student_submission(assignment.id, student.id)
            status = "✅ Completed" if submission else "📌 Open"
            assignment_options[f"{status} - {assignment.title}"] = assignment.id

        if assignment_options:
            # Determine default index based on current assignment
            options_list = ["-- Free Practice --"] + list(assignment_options.keys())
            default_index = 0

            # If there's a current assignment, try to find it in the list
            if hasattr(st.session_state, 'current_assignment_id') and st.session_state.current_assignment_id:
                try:
                    for idx, option_label in enumerate(options_list):
                        if option_label != "-- Free Practice --":
                            if assignment_options.get(option_label) == st.session_state.current_assignment_id:
                                default_index = idx
                                break
                except:
                    default_index = 0

            selected_assignment_label = st.selectbox(
                "Select an assignment (or choose 'Free Practice' below)",
                options_list,
                index=default_index,
                key="assignment_selector"
            )

            if selected_assignment_label != "-- Free Practice --":
                assignment_id = assignment_options[selected_assignment_label]
                assignment = storage.get_assignment(assignment_id)

                # Show assignment details
                with st.expander("📋 Assignment Details", expanded=True):
                    st.markdown(f"**{assignment.title}**")
                    st.markdown(assignment.description)
                    st.markdown(f"*Topics: {assignment.topics}*")
                    if assignment.due_date:
                        st.markdown(f"*Due: {assignment.due_date[:10]}*")

                # Store assignment in session state
                st.session_state.current_assignment_id = assignment_id
            else:
                st.session_state.current_assignment_id = None
        else:
            st.session_state.current_assignment_id = None
    else:
        st.session_state.current_assignment_id = None

    st.markdown("---")

    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.session_start = datetime.now()

    if "current_student_id" not in st.session_state:
        st.session_state.current_student_id = None

    if "previous_assignment_id" not in st.session_state:
        st.session_state.previous_assignment_id = None

    # Reset conversation if student changed
    if st.session_state.current_student_id != student.id:
        st.session_state.messages = []
        st.session_state.session_start = datetime.now()
        st.session_state.current_student_id = student.id
        st.session_state.previous_assignment_id = None

    # Reset conversation if assignment changed
    current_assignment_id = st.session_state.get('current_assignment_id', None)
    if st.session_state.previous_assignment_id != current_assignment_id:
        st.session_state.messages = []
        st.session_state.session_start = datetime.now()
        st.session_state.previous_assignment_id = current_assignment_id

    # Get current assignment if one is selected
    current_assignment = None
    if hasattr(st.session_state, 'current_assignment_id') and st.session_state.current_assignment_id:
        current_assignment = storage.get_assignment(st.session_state.current_assignment_id)

    # Display initial greeting if no messages
    if not st.session_state.messages:
        greeting = tutor.get_initial_greeting(student, current_assignment)
        st.session_state.messages.append({
            "role": "assistant",
            "content": greeting
        })

    # Show assignment mode indicator
    if current_assignment:
        st.info(f"📝 **Assignment Mode:** {current_assignment.title}")

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            parse_and_display_message(message["content"])

    # Chat input
    if prompt := st.chat_input("Type your math question here..."):
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Check topic relevance (guardrail)
        relevance_check = tutor.check_topic_relevance(student, prompt)

        if not relevance_check["is_relevant"]:
            # Log incident
            storage.create_incident(
                student_id=student.id,
                incident_type="off_topic",
                message=prompt,
                reason=relevance_check["reason"]
            )

            # Display neutral warning (marked as off-topic)
            with st.chat_message("assistant"):
                warning = relevance_check["suggested_response"]
                st.markdown(warning)

            # Add to session state with off_topic marker for display, but exclude from conversation history
            st.session_state.messages.append({
                "role": "user",
                "content": prompt,
                "off_topic": True
            })
            st.session_state.messages.append({
                "role": "assistant",
                "content": warning,
                "off_topic": True
            })

        else:
            # Message is on-topic, proceed normally
            # Add user message to chat
            st.session_state.messages.append({
                "role": "user",
                "content": prompt
            })

            # Get tutor response - filter out off-topic messages from history
            on_topic_history = [
                {"role": msg["role"], "content": msg["content"]}
                for msg in st.session_state.messages[:-1]
                if not msg.get("off_topic", False)
            ]

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    # Get response from tutor with filtered history
                    response = tutor.get_response_sync(
                        student=student,
                        conversation_history=on_topic_history,
                        new_message=prompt,
                        assignment=current_assignment
                    )

                    parse_and_display_message(response)

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

                    # Filter out off-topic messages before saving
                    on_topic_messages = [
                        {"role": msg["role"], "content": msg["content"]}
                        for msg in st.session_state.messages
                        if not msg.get("off_topic", False)
                    ]

                    # Generate enhanced summary with analytics (only on-topic messages)
                    summary_data = tutor.generate_enhanced_session_summary(student, on_topic_messages)

                    # Save to database with full analytics
                    session = storage.create_session(
                        student_id=student.id,
                        messages=on_topic_messages,
                        summary=summary_data["summary"],
                        topics=summary_data["topics"],
                        duration_minutes=duration,
                        subtopics=summary_data["subtopics"],
                        difficulty_level=summary_data["difficulty_level"],
                        student_confidence=summary_data["student_confidence"],
                        learning_indicators=summary_data["learning_indicators"],
                        questions_asked=summary_data["questions_asked"]
                    )

                    # If working on an assignment, create a submission
                    if hasattr(st.session_state, 'current_assignment_id') and st.session_state.current_assignment_id:
                        try:
                            storage.create_submission(
                                assignment_id=st.session_state.current_assignment_id,
                                student_id=student.id,
                                session_id=session.id
                            )
                            st.success("✅ Session saved and assignment submitted!")
                        except Exception as e:
                            # Handle duplicate submission (student already submitted this assignment)
                            if "UNIQUE constraint failed" in str(e):
                                st.success("✅ Session saved! (Assignment was already submitted)")
                            else:
                                st.error(f"Session saved but submission failed: {e}")
                    else:
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

    # Check for incidents
    incidents = storage.get_incidents(student.id, unresolved_only=False)
    if incidents:
        st.markdown("---")
        st.markdown("### ⚠️ Incidents")

        unresolved_count = sum(1 for i in incidents if not i.resolved)

        if unresolved_count > 0:
            st.warning(f"**{unresolved_count} unresolved incident(s)**")
        else:
            st.info("All incidents have been reviewed")

        with st.expander(f"View Incidents ({len(incidents)} total)", expanded=unresolved_count > 0):
            for incident in incidents[:10]:  # Show last 10 incidents
                status_icon = "✅" if incident.resolved else "🔴"
                st.markdown(f"**{status_icon} {incident.timestamp[:16]} - {incident.incident_type.replace('_', ' ').title()}**")
                st.markdown(f"*Message:* \"{incident.message}\"")
                st.markdown(f"*Reason:* {incident.reason}")

                if not incident.resolved:
                    if st.button(f"Mark as reviewed", key=f"resolve_{incident.id}"):
                        storage.mark_incident_resolved(incident.id)
                        st.success("Marked as reviewed")
                        st.rerun()

                st.markdown("---")

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
# TEACHER VIEW PAGE
# ============================================================================
elif page == "👨‍🏫 Teacher View":
    st.title("👨‍🏫 Teacher View")

    # Teacher selection
    teachers = storage.list_teachers()

    if not teachers:
        st.warning("No teachers found. Please add a teacher in the Setup page first.")

        # Quick add teacher form
        st.markdown("### ➕ Add Teacher")
        with st.form("add_teacher_quick"):
            teacher_name = st.text_input("Name", placeholder="Ms. Smith")
            teacher_email = st.text_input("Email", placeholder="teacher@school.com")
            teacher_school = st.text_input("School (optional)", placeholder="Lincoln Elementary")

            if st.form_submit_button("Add Teacher"):
                if teacher_name and teacher_email:
                    storage.create_teacher(teacher_name, teacher_email, teacher_school or None)
                    st.success(f"Added {teacher_name}!")
                    st.rerun()
                else:
                    st.error("Please provide name and email")
        st.stop()

    # Select teacher
    teacher_options = {f"{t.name} ({t.email})": t.id for t in teachers}
    selected_teacher_name = st.selectbox("Select Teacher", list(teacher_options.keys()))
    teacher_id = teacher_options[selected_teacher_name]
    teacher = storage.get_teacher(teacher_id)

    st.markdown(f"**School:** {teacher.school or 'Not specified'}")
    st.markdown("---")

    # Tabs for different teacher functions
    tab1, tab2, tab3 = st.tabs(["📝 My Assignments", "➕ Create Assignment", "📊 Review Submissions"])

    # TAB 1: View Assignments
    with tab1:
        st.markdown("### My Assignments")

        assignments = storage.list_assignments(teacher_id=teacher_id)

        if not assignments:
            st.info("No assignments created yet. Use the 'Create Assignment' tab to get started.")
        else:
            for assignment in assignments:
                # Get submission count
                submissions = storage.get_submissions(assignment.id)
                unreviewed = sum(1 for s in submissions if not s.teacher_reviewed)

                with st.expander(
                    f"**{assignment.title}** - Grade {assignment.grade_level} "
                    f"({len(submissions)} submissions, {unreviewed} unreviewed)"
                ):
                    st.markdown(f"**Description:** {assignment.description}")
                    st.markdown(f"**Topics:** {assignment.topics}")
                    st.markdown(f"**Created:** {assignment.created_at[:16]}")
                    if assignment.due_date:
                        st.markdown(f"**Due:** {assignment.due_date[:16]}")

                    if submissions:
                        st.markdown(f"**Submissions:** {len(submissions)}")
                        if st.button(f"Review Submissions", key=f"review_{assignment.id}"):
                            st.session_state.review_assignment_id = assignment.id
                            st.rerun()

    # TAB 2: Create Assignment
    with tab2:
        st.markdown("### Create New Assignment")

        with st.form("create_assignment"):
            title = st.text_input("Assignment Title", placeholder="Solving Linear Equations")
            description = st.text_area(
                "Description/Problem Statement",
                placeholder="Solve the following equation for x: 2x + 5 = 13",
                height=150
            )
            grade_level = st.number_input("Grade Level", min_value=1, max_value=12, value=8)
            topics = st.text_input("Topics (comma-separated)", placeholder="algebra, linear equations")
            due_date = st.date_input("Due Date (optional)")

            if st.form_submit_button("Create Assignment"):
                if title and description and topics:
                    due_date_str = due_date.strftime("%Y-%m-%d") if due_date else None
                    assignment = storage.create_assignment(
                        teacher_id=teacher_id,
                        title=title,
                        description=description,
                        grade_level=grade_level,
                        topics=topics,
                        due_date=due_date_str
                    )
                    st.success(f"✅ Created assignment: {assignment.title}")
                    st.rerun()
                else:
                    st.error("Please fill in all required fields")

    # TAB 3: Review Submissions
    with tab3:
        st.markdown("### Review Student Submissions")

        # Check if we're reviewing a specific assignment
        if "review_assignment_id" in st.session_state:
            assignment_id = st.session_state.review_assignment_id
            assignment = storage.get_assignment(assignment_id)

            st.markdown(f"## {assignment.title}")
            st.markdown(f"*{assignment.description}*")
            st.markdown("---")

            if st.button("← Back to Assignments"):
                del st.session_state.review_assignment_id
                st.rerun()

            # Get all submissions
            submissions = storage.get_submissions(assignment_id)

            if not submissions:
                st.info("No submissions yet for this assignment.")
            else:
                for submission in submissions:
                    student = storage.get_student(submission.student_id)
                    session = storage.get_session(submission.session_id)

                    status = "✅ Reviewed" if submission.teacher_reviewed else "🔴 Needs Review"

                    with st.expander(
                        f"{status} - {student.name} (Grade {student.grade_level}) - "
                        f"Submitted {submission.submitted_at[:16]}"
                    ):
                        # Show session analytics
                        col1, col2, col3, col4 = st.columns(4)

                        with col1:
                            duration = session.duration_minutes or 0
                            st.metric("Time Spent", f"{duration} min")

                        with col2:
                            confidence = session.student_confidence or 0
                            confidence_pct = int(confidence * 100)
                            emoji = "😊" if confidence > 0.7 else "😐" if confidence > 0.4 else "😰"
                            st.metric("Confidence", f"{confidence_pct}% {emoji}")

                        with col3:
                            questions = session.questions_asked or 0
                            st.metric("Questions Asked", questions)

                        with col4:
                            difficulty = session.difficulty_level or 0
                            st.metric("Difficulty", f"{difficulty}/10")

                        # Show conversation
                        st.markdown("#### Conversation Transcript")
                        with st.container():
                            for msg in session.messages:
                                role = msg["role"]
                                content = msg["content"]
                                if role == "user":
                                    st.markdown(f"**Student:** {content}")
                                else:
                                    st.markdown(f"*AI Tutor:* {content}")
                                st.markdown("")

                        # Show learning indicators
                        if session.learning_indicators:
                            st.markdown("#### Learning Analytics")
                            indicators = session.learning_indicators

                            if indicators.mastered:
                                st.markdown("**✅ Mastered:**")
                                for item in indicators.mastered:
                                    st.markdown(f"- {item}")

                            if indicators.struggled_with:
                                st.markdown("**⚠️ Struggled With:**")
                                for item in indicators.struggled_with:
                                    st.markdown(f"- {item}")

                            if indicators.misconceptions:
                                st.markdown("**❌ Misconceptions:**")
                                for item in indicators.misconceptions:
                                    st.markdown(f"- {item}")

                            if indicators.breakthrough_moments:
                                st.markdown("**💡 Breakthrough Moments:**")
                                for item in indicators.breakthrough_moments:
                                    st.markdown(f"- {item}")

                        # Teacher review section
                        st.markdown("---")
                        st.markdown("#### Teacher Review")

                        if submission.teacher_reviewed:
                            st.info(f"**Your Notes:** {submission.teacher_notes}")
                            if st.button("Edit Review", key=f"edit_{submission.id}"):
                                st.session_state[f"editing_{submission.id}"] = True
                                st.rerun()

                        if not submission.teacher_reviewed or st.session_state.get(f"editing_{submission.id}", False):
                            with st.form(f"review_{submission.id}"):
                                notes = st.text_area(
                                    "Teacher Notes",
                                    value=submission.teacher_notes or "",
                                    placeholder="Student showed good understanding of linear equations. "
                                    "Recommend more practice with multi-step problems.",
                                    height=100
                                )

                                if st.form_submit_button("Save Review"):
                                    storage.update_submission_review(submission.id, notes)
                                    st.success("Review saved!")
                                    if f"editing_{submission.id}" in st.session_state:
                                        del st.session_state[f"editing_{submission.id}"]
                                    st.rerun()
        else:
            # Show all assignments
            assignments = storage.list_assignments(teacher_id=teacher_id)

            if not assignments:
                st.info("No assignments created yet.")
            else:
                st.markdown("Select an assignment to review submissions:")

                for assignment in assignments:
                    submissions = storage.get_submissions(assignment.id)
                    unreviewed = sum(1 for s in submissions if not s.teacher_reviewed)

                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**{assignment.title}** - {len(submissions)} submissions, {unreviewed} unreviewed")
                    with col2:
                        if st.button("Review →", key=f"select_{assignment.id}"):
                            st.session_state.review_assignment_id = assignment.id
                            st.rerun()

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

    # Teachers section
    st.markdown("---")
    st.markdown("### 👨‍🏫 Teachers")
    teachers = storage.list_teachers()

    if teachers:
        for teacher in teachers:
            with st.expander(f"{teacher.name} - {teacher.email}"):
                st.markdown(f"**School:** {teacher.school or 'Not specified'}")
                st.markdown(f"**Created:** {teacher.created_at}")
    else:
        st.info("No teachers added yet.")

    # Add new teacher
    st.markdown("### ➕ Add New Teacher")

    with st.form("add_teacher"):
        teacher_name = st.text_input("Teacher Name", placeholder="Ms. Smith")
        teacher_email = st.text_input("Teacher Email", placeholder="teacher@school.com")
        teacher_school = st.text_input("School (optional)", placeholder="Lincoln Elementary")

        submitted_teacher = st.form_submit_button("Add Teacher")

        if submitted_teacher:
            if not teacher_name or not teacher_email:
                st.error("Please fill in name and email.")
            else:
                teacher = storage.create_teacher(teacher_name, teacher_email, teacher_school or None)
                st.success(f"✅ Added {teacher.name}!")
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
