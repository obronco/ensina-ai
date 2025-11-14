# Frontend Framework Conversion Plan

## Executive Summary

**Current State:** Streamlit-based monolithic application with Python backend  
**Target State:** Modern frontend framework (React/Next.js) with REST API backend  
**Timeline:** 6-8 weeks for MVP, 10-12 weeks for feature parity  
**Risk Level:** Medium - requires architectural changes but backend logic is well-isolated

---

## Table of Contents

1. [Why Convert?](#why-convert)
2. [Architecture Overview](#architecture-overview)
3. [Technology Stack Recommendations](#technology-stack-recommendations)
4. [Migration Strategy](#migration-strategy)
5. [Detailed Implementation Plan](#detailed-implementation-plan)
6. [API Design](#api-design)
7. [Database Considerations](#database-considerations)
8. [Authentication & Security](#authentication--security)
9. [Deployment Strategy](#deployment-strategy)
10. [Risk Assessment](#risk-assessment)
11. [Timeline & Milestones](#timeline--milestones)
12. [Cost Analysis](#cost-analysis)

---

## Why Convert?

### Current Limitations with Streamlit

**1. User Experience Constraints**
- Full page reloads on every interaction (slow UX)
- Limited control over UI/UX design and animations
- Difficult to implement complex client-side interactions
- No offline capabilities or PWA support
- Limited mobile responsiveness customization

**2. Performance Issues**
- Server-side rendering only (every interaction hits server)
- Session state management is cumbersome
- Difficult to optimize for multiple concurrent users
- No request batching or optimistic updates

**3. Scalability Concerns**
- Each user session requires persistent server connection
- Memory-intensive for many concurrent users
- Difficult to implement load balancing effectively
- No built-in caching strategies

**4. Development Constraints**
- Limited component reusability
- Difficult to implement real-time features (WebSockets)
- Testing is challenging
- No separation between frontend and backend deployments
- Vendor lock-in with Streamlit ecosystem

**5. Feature Limitations for Learning Platform**
- Difficult to implement:
  - Rich text editors
  - Drag-and-drop interfaces
  - Interactive problem-solving widgets
  - Collaborative features
  - Advanced data visualizations
  - Game-like elements for engagement

### Benefits of Modern Frontend Framework

**1. Superior User Experience**
- ✅ Instant client-side interactions (no page reloads)
- ✅ Smooth animations and transitions
- ✅ Progressive Web App (PWA) capabilities
- ✅ Responsive mobile-first design
- ✅ Offline support for critical features
- ✅ Native-like mobile experience

**2. Performance & Scalability**
- ✅ Client-side rendering reduces server load
- ✅ Code splitting and lazy loading
- ✅ Request batching and caching
- ✅ Optimistic updates for perceived speed
- ✅ CDN-friendly static assets
- ✅ Horizontal scaling of API independently

**3. Development Velocity**
- ✅ Huge ecosystem of ready-made components
- ✅ Better testing frameworks (Jest, Cypress, Playwright)
- ✅ Hot module replacement for faster development
- ✅ TypeScript for type safety
- ✅ Better debugging tools
- ✅ Component reusability across projects

**4. Feature Richness**
- ✅ Rich text editors (TipTap, Quill, ProseMirror)
- ✅ Advanced data viz (D3.js, Recharts, Chart.js)
- ✅ Drag-and-drop (react-beautiful-dnd)
- ✅ Real-time collaboration (Socket.io, Yjs)
- ✅ Interactive math widgets (mathquill, mathjs)
- ✅ Gamification libraries

**5. Business Benefits**
- ✅ Easier to hire frontend developers (React skills common)
- ✅ Better SEO with Next.js SSR/SSG
- ✅ Independent deployment of frontend/backend
- ✅ Multi-platform support (web, mobile app with React Native)
- ✅ White-label potential for different schools/districts

---

## Architecture Overview

### Current Architecture (Streamlit)

```
┌─────────────────────────────────────────────────────────┐
│                    Streamlit App                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  app.py (UI + Logic Entangled)                   │  │
│  │  - Page routing (if/elif)                         │  │
│  │  - UI rendering (st.*)                            │  │
│  │  - Session state management                       │  │
│  │  - Direct calls to:                               │  │
│  │    • tutor.py (LLM logic)                         │  │
│  │    • storage.py (database)                        │  │
│  │    • graph_renderer.py                            │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                         │
                         ↓
        ┌────────────────────────────────┐
        │   SQLite Database              │
        │   Anthropic/OpenAI API         │
        └────────────────────────────────┘
```

**Issues:**
- UI and business logic tightly coupled
- No API layer for future mobile/desktop apps
- Server-side state management
- Difficult to test components independently

### Target Architecture (React + FastAPI)

```
┌──────────────────────────────────────────────────────────┐
│                     Frontend (React/Next.js)              │
│  ┌────────────────────────────────────────────────────┐  │
│  │  Pages/Routes                                       │  │
│  │  - /student    - /parent    - /teacher - /setup    │  │
│  └────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────┐  │
│  │  Components (Reusable)                             │  │
│  │  - ChatInterface  - Dashboard  - AssignmentView   │  │
│  │  - StudentProfile - Analytics  - ImageUpload      │  │
│  └────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────┐  │
│  │  State Management (Zustand/Redux)                  │  │
│  │  - Auth state    - Chat state    - User profile   │  │
│  └────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────┐  │
│  │  API Client (Axios/Fetch)                          │  │
│  │  - REST API calls   - WebSocket for real-time     │  │
│  └────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
                         │
                         │ HTTPS/WSS
                         ↓
┌──────────────────────────────────────────────────────────┐
│                  Backend API (FastAPI)                    │
│  ┌────────────────────────────────────────────────────┐  │
│  │  API Endpoints                                      │  │
│  │  /api/v1/                                           │  │
│  │    - /auth/*      (login, register, token)         │  │
│  │    - /students/*  (CRUD, profile)                  │  │
│  │    - /teachers/*  (CRUD, assignments)              │  │
│  │    - /sessions/*  (create, list, get)              │  │
│  │    - /chat        (WebSocket for real-time)        │  │
│  │    - /assignments/* (CRUD, submissions)            │  │
│  │    - /upload/*    (image upload, homework)         │  │
│  └────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────┐  │
│  │  Business Logic Layer (Reused from current)        │  │
│  │  - tutor.py      (AI tutoring)                     │  │
│  │  - storage.py    (database operations)             │  │
│  │  - graph_renderer.py (visualization)               │  │
│  │  - image_utils.py (image processing)               │  │
│  └────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────┐  │
│  │  Middleware                                         │  │
│  │  - Authentication (JWT)                            │  │
│  │  - Rate limiting                                   │  │
│  │  - CORS                                             │  │
│  │  - Error handling                                  │  │
│  └────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
                         │
                         ↓
        ┌────────────────────────────────────┐
        │   Database (SQLite → PostgreSQL)   │
        │   External APIs (Anthropic, OpenAI)│
        │   File Storage (S3/local)          │
        └────────────────────────────────────┘
```

**Advantages:**
- Clean separation of concerns
- Independent deployment and scaling
- API-first design enables mobile apps later
- Better testing at each layer
- Stateless backend (easier to scale)

---

## Technology Stack Recommendations

### Option 1: Next.js + FastAPI (RECOMMENDED)

**Frontend: Next.js 14+ (React)**
- ✅ **Best for:** Production-ready learning platform
- ✅ Server-side rendering (SSR) + Static generation (SSG)
- ✅ Built-in routing with file-based system
- ✅ API routes for BFF (Backend for Frontend) if needed
- ✅ Excellent performance with automatic code splitting
- ✅ Great SEO (important for public-facing pages)
- ✅ Built-in Image optimization
- ✅ Large ecosystem and community
- ⚠️ Slightly steeper learning curve than Vite+React

**Backend: FastAPI (Python)**
- ✅ Async support (important for LLM streaming)
- ✅ Automatic OpenAPI documentation
- ✅ Native Pydantic validation (already using dataclasses)
- ✅ WebSocket support for real-time chat
- ✅ Easy to migrate existing Python code
- ✅ Excellent performance (Starlette + Uvicorn)
- ✅ Type hints throughout

**Why this combo?**
- Minimal Python rewrite (business logic stays)
- FastAPI is modern, fast, and Pythonic
- Next.js is industry standard for React apps
- Both have excellent TypeScript support
- Easy to deploy (Vercel + Railway/Fly.io)

### Option 2: Vite + React + FastAPI

**Frontend: Vite + React**
- ✅ **Best for:** Faster initial development
- ✅ Extremely fast hot module replacement (HMR)
- ✅ Simpler than Next.js (just a SPA)
- ✅ Smaller bundle size initially
- ⚠️ Client-side rendering only (worse SEO)
- ⚠️ Need to set up routing manually (React Router)
- ⚠️ No built-in SSR without manual setup

**Backend: FastAPI**
- (Same as Option 1)

**Why consider this?**
- Faster to prototype initially
- Less complexity than Next.js
- Good for internal tools (SEO not critical)
- Easier learning curve for beginners

### Option 3: SvelteKit + FastAPI

**Frontend: SvelteKit**
- ✅ **Best for:** Lightweight, fast apps
- ✅ Compiled framework (smaller bundle)
- ✅ Simpler state management
- ✅ Built-in SSR and routing
- ⚠️ Smaller ecosystem than React
- ⚠️ Fewer component libraries
- ⚠️ Harder to find developers

**Backend: FastAPI**
- (Same as Option 1)

### Recommended: **Option 1 (Next.js + FastAPI)**

**Reasoning:**
1. **Future-proof:** Most popular React framework, huge community
2. **Performance:** SSR + SSG = fast initial loads
3. **SEO:** Important if platform goes public/commercial
4. **Developer availability:** Easier to hire Next.js developers
5. **Ecosystem:** Vast library of components and tools
6. **Migration path:** Can incrementally migrate pages
7. **Backend reuse:** Keep Python business logic with minimal changes

### Additional Technology Decisions

**State Management:**
- **Zustand** (recommended) - Simple, lightweight, React hooks-based
- Redux Toolkit - If team prefers Redux patterns
- React Query/TanStack Query - Excellent for server state

**UI Component Library:**
- **Shadcn/ui** (recommended) - Modern, customizable, Tailwind-based
- Material-UI (MUI) - If need comprehensive components quickly
- Chakra UI - Good middle ground

**Styling:**
- **Tailwind CSS** (recommended) - Utility-first, fast development
- CSS Modules - If prefer traditional CSS
- styled-components - If prefer CSS-in-JS

**Real-time Communication:**
- **Socket.io** - For WebSocket chat
- Server-Sent Events (SSE) - For streaming LLM responses

**Math Rendering:**
- **KaTeX** (recommended) - Fast, lightweight
- MathJax - If need more features

**Graphing:**
- **Plotly.js** - Keep consistency with current graphs
- Recharts - If want simpler React-native graphs
- D3.js - If need custom visualizations

**Authentication:**
- **NextAuth.js** - If using Next.js, seamless integration
- JWT + HTTPOnly cookies - Manual but flexible
- Auth0/Clerk - If want managed auth ($$)

**Database Migration:**
- **SQLAlchemy** - Already structured for this
- Keep SQLite for development
- PostgreSQL for production

---

## Migration Strategy

### Strategy: **Incremental Migration (Strangler Pattern)**

Rather than rewriting everything at once, we'll gradually replace Streamlit pages with React pages.

### Phase 0: Preparation (Week 1)
**Goal:** Set up parallel infrastructure

```
Current (Keep Running):
/app.py (Streamlit) → Port 8501

New (Build Alongside):
/frontend (Next.js) → Port 3000
/backend (FastAPI)  → Port 8000
```

**Tasks:**
- [ ] Initialize Next.js project in `/frontend` folder
- [ ] Initialize FastAPI project in `/backend` folder
- [ ] Set up monorepo structure or separate repos
- [ ] Configure CORS for cross-origin development
- [ ] Set up shared types/contracts (TypeScript + Pydantic)
- [ ] Set up CI/CD pipelines for both

**Deliverable:** Boilerplate apps running side-by-side

---

### Phase 1: API Layer (Weeks 2-3)
**Goal:** Create REST API that wraps existing business logic

**Approach:**
```python
# backend/main.py
from fastapi import FastAPI
from src.storage import Storage
from src.tutor import MathTutor

app = FastAPI()
storage = Storage("data/ensina.db")
tutor = MathTutor(storage)

@app.get("/api/v1/students")
async def list_students():
    students = storage.list_students()
    return students
```

**Priority Endpoints:**
1. **Authentication** (new)
   - POST /api/v1/auth/login
   - POST /api/v1/auth/logout
   - GET /api/v1/auth/me

2. **Students** (wrap storage.py)
   - GET /api/v1/students
   - GET /api/v1/students/{id}
   - POST /api/v1/students
   - PUT /api/v1/students/{id}

3. **Sessions** (wrap storage.py)
   - GET /api/v1/sessions?student_id=X
   - GET /api/v1/sessions/{id}
   - POST /api/v1/sessions

4. **Chat** (wrap tutor.py)
   - WebSocket /api/v1/chat/stream
   - POST /api/v1/chat/message

5. **Teachers & Assignments**
   - Standard CRUD endpoints

**Testing:**
- Use FastAPI's automatic Swagger docs at `/docs`
- Test each endpoint with Postman/curl
- Write integration tests

**Deliverable:** Fully functional API that can be used by any client

---

### Phase 2: Student Chat Interface (Weeks 3-5)
**Goal:** Replace student page with React version

**Why start here?**
- Core feature (highest value)
- Tests WebSocket integration
- Validates architecture early
- Immediate user-facing improvement

**Components to Build:**
```
/frontend/src/
├── pages/
│   └── student/
│       └── index.tsx           # Main student page
├── components/
│   ├── Chat/
│   │   ├── ChatInterface.tsx   # Main chat container
│   │   ├── MessageList.tsx     # Scrollable messages
│   │   ├── MessageBubble.tsx   # Individual message
│   │   ├── ChatInput.tsx       # Input with send button
│   │   └── TypingIndicator.tsx # "Tutor is typing..."
│   ├── Math/
│   │   ├── LaTeXRenderer.tsx   # KaTeX rendering
│   │   └── GraphRenderer.tsx   # Plotly graphs
│   └── Layout/
│       ├── StudentLayout.tsx   # Header, nav, footer
│       └── Sidebar.tsx         # Student selector
└── lib/
    ├── api.ts                  # API client functions
    ├── websocket.ts            # WebSocket manager
    └── types.ts                # TypeScript interfaces
```

**Key Features:**
1. **Real-time Chat:**
   ```typescript
   // WebSocket connection
   const socket = io('ws://localhost:8000/api/v1/chat/stream');
   
   socket.on('message', (data) => {
     setMessages(prev => [...prev, data]);
   });
   ```

2. **LaTeX Rendering:**
   ```typescript
   import katex from 'katex';
   // Parse and render $...$ and $$...$$ blocks
   ```

3. **Graph Rendering:**
   ```typescript
   import Plot from 'react-plotly.js';
   // Parse ```graph blocks and render
   ```

4. **Image Upload:**
   ```typescript
   const uploadImage = async (file: File) => {
     const formData = new FormData();
     formData.append('image', file);
     await api.post('/upload/homework', formData);
   };
   ```

**Testing:**
- Component tests (Jest + React Testing Library)
- E2E tests (Playwright)
- Visual regression tests (Chromatic/Percy)

**Deliverable:** Fully functional student chat page

**Migration:**
- Keep Streamlit student page as fallback
- Add feature flag to switch between versions
- Gradual rollout (10% → 50% → 100%)

---

### Phase 3: Parent Dashboard (Week 5-6)
**Goal:** Replace parent dashboard with React version

**Components:**
```
/frontend/src/
├── pages/
│   └── parent/
│       └── index.tsx           # Parent dashboard
├── components/
│   ├── Dashboard/
│   │   ├── StatsCard.tsx       # Metric cards
│   │   ├── SessionList.tsx     # List of sessions
│   │   ├── SessionDetail.tsx   # Expandable session
│   │   ├── IncidentAlert.tsx   # Off-topic warnings
│   │   └── AnalyticsChart.tsx  # Progress charts
│   └── Student/
│       └── StudentSelector.tsx # Dropdown/tabs
```

**Data Visualization:**
- Use Recharts or Chart.js for progress charts
- Time spent over time
- Topics mastered visualization
- Confidence trends

**Features:**
- Session filtering (date range, topic)
- Export session transcripts (PDF)
- Email summaries (future)

**Deliverable:** Parent dashboard with improved analytics

---

### Phase 4: Teacher View (Weeks 6-7)
**Goal:** Replace teacher view with React version

**Components:**
```
/frontend/src/
├── pages/
│   └── teacher/
│       ├── index.tsx              # Teacher home
│       ├── assignments.tsx        # Assignment list
│       ├── create-assignment.tsx  # Assignment form
│       └── review.tsx             # Review submissions
├── components/
│   ├── Assignment/
│   │   ├── AssignmentCard.tsx
│   │   ├── AssignmentForm.tsx
│   │   └── SubmissionReview.tsx
│   └── Editor/
│       └── RichTextEditor.tsx     # For assignment creation
```

**Enhanced Features:**
- Rich text editor for assignments (TipTap)
- Bulk assignment creation
- Rubric/grading criteria
- Automated feedback suggestions (using AI)
- Export class analytics

**Deliverable:** Teacher view with improved UX

---

### Phase 5: Setup & Admin (Week 7)
**Goal:** Replace setup page with React version

**Features:**
- User management (CRUD)
- System settings
- API key management
- Database backup/restore

**Components:**
```
/frontend/src/
├── pages/
│   └── admin/
│       ├── index.tsx
│       ├── students.tsx
│       ├── teachers.tsx
│       └── settings.tsx
```

**Deliverable:** Admin panel

---

### Phase 6: Testing & Polish (Week 8)
**Goal:** Production readiness

**Tasks:**
- [ ] Full E2E test coverage
- [ ] Performance optimization
- [ ] Accessibility audit (WCAG 2.1)
- [ ] Mobile responsive testing
- [ ] Browser compatibility testing
- [ ] Security audit
- [ ] Load testing
- [ ] Documentation

**Deliverable:** Production-ready application

---

### Phase 7: Deployment & Cutover (Weeks 9-10)
**Goal:** Launch new version

**Tasks:**
- [ ] Deploy to production environment
- [ ] Set up monitoring and alerting
- [ ] Run parallel (Streamlit + React) for 1 week
- [ ] Gradual traffic migration
- [ ] Deprecate Streamlit version
- [ ] Archive old code

**Deliverable:** Fully migrated platform

---

## API Design

### RESTful API Structure

**Base URL:** `https://api.ensina.ai/api/v1`

### Authentication Endpoints

```
POST   /auth/register          # Create new account
POST   /auth/login             # Login (returns JWT)
POST   /auth/logout            # Logout (invalidate token)
POST   /auth/refresh           # Refresh JWT token
GET    /auth/me                # Get current user
POST   /auth/forgot-password   # Password reset request
POST   /auth/reset-password    # Complete password reset
```

**Authentication Flow:**
```typescript
// Login
POST /api/v1/auth/login
{
  "email": "student@example.com",
  "password": "password123",
  "role": "student" // or "parent", "teacher"
}

// Response
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhb...",
  "refresh_token": "dGciOiJIUzI1NiIsIn...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": 1,
    "email": "student@example.com",
    "role": "student",
    "profile": { ... }
  }
}
```

### Students Endpoints

```
GET    /students               # List all students (parent/teacher only)
GET    /students/:id           # Get student by ID
POST   /students               # Create student (parent/admin)
PUT    /students/:id           # Update student
DELETE /students/:id           # Delete student
GET    /students/:id/sessions  # Get student's sessions
GET    /students/:id/progress  # Get learning progress
GET    /students/:id/incidents # Get incidents
```

**Example:**
```typescript
// Get student profile
GET /api/v1/students/123

// Response
{
  "id": 123,
  "name": "João Silva",
  "grade_level": 5,
  "parent_email": "parent@example.com",
  "created_at": "2024-01-15T10:30:00Z",
  "stats": {
    "total_sessions": 42,
    "total_minutes": 630,
    "topics_covered": 8,
    "avg_confidence": 0.75
  }
}
```

### Chat/Tutoring Endpoints

```
WebSocket /chat/stream                # Real-time chat
POST      /chat/message               # Send message (alternative to WS)
POST      /chat/analyze-image         # Upload homework image
GET       /chat/suggestions           # Get conversation starters
```

**WebSocket Protocol:**
```typescript
// Client → Server
{
  "type": "message",
  "student_id": 123,
  "assignment_id": 456, // optional
  "content": "How do I solve 2x + 5 = 13?",
  "session_id": "abc-123" // session identifier
}

// Server → Client (streaming response)
{
  "type": "chunk",
  "content": "Great question! Let's work through this together. ",
  "session_id": "abc-123"
}

{
  "type": "chunk",
  "content": "What do you think we should do first to isolate x?",
  "session_id": "abc-123"
}

{
  "type": "complete",
  "full_message": "Great question! Let's work through this together. What do you think we should do first to isolate x?",
  "session_id": "abc-123",
  "metadata": {
    "tokens_used": 45,
    "latency_ms": 1200
  }
}
```

### Sessions Endpoints

```
GET    /sessions                    # List sessions (with filters)
GET    /sessions/:id                # Get session details
POST   /sessions                    # Create/start session
PUT    /sessions/:id                # Update session (end, add notes)
DELETE /sessions/:id                # Delete session
GET    /sessions/:id/summary        # Get AI summary
POST   /sessions/:id/export         # Export transcript (PDF)
```

**Example:**
```typescript
// List sessions with filters
GET /api/v1/sessions?student_id=123&date_from=2024-01-01&topics=fractions

// Response
{
  "sessions": [
    {
      "id": 1,
      "student_id": 123,
      "timestamp": "2024-01-15T14:30:00Z",
      "duration_minutes": 25,
      "topics": "fractions, division",
      "summary": "Student worked on comparing fractions...",
      "student_confidence": 0.8,
      "difficulty_level": 5,
      "message_count": 18
    },
    ...
  ],
  "total": 42,
  "page": 1,
  "per_page": 20
}
```

### Teachers Endpoints

```
GET    /teachers               # List teachers
GET    /teachers/:id           # Get teacher details
POST   /teachers               # Create teacher
PUT    /teachers/:id           # Update teacher
DELETE /teachers/:id           # Delete teacher
```

### Assignments Endpoints

```
GET    /assignments                    # List assignments
GET    /assignments/:id                # Get assignment
POST   /assignments                    # Create assignment
PUT    /assignments/:id                # Update assignment
DELETE /assignments/:id                # Delete assignment
GET    /assignments/:id/submissions    # Get submissions
```

**Example:**
```typescript
// Create assignment
POST /api/v1/assignments

{
  "teacher_id": 456,
  "title": "Solving Linear Equations",
  "description": "Solve for x: 2x + 5 = 13\n\nShow all your work...",
  "grade_level": 8,
  "topics": "algebra, linear equations",
  "due_date": "2024-02-01T23:59:59Z"
}

// Response
{
  "id": 789,
  "teacher_id": 456,
  "title": "Solving Linear Equations",
  "description": "Solve for x: 2x + 5 = 13\n\nShow all your work...",
  "grade_level": 8,
  "topics": "algebra, linear equations",
  "created_at": "2024-01-15T10:00:00Z",
  "due_date": "2024-02-01T23:59:59Z",
  "submission_count": 0
}
```

### Submissions Endpoints

```
GET    /submissions/:id                # Get submission
POST   /submissions                    # Submit assignment
PUT    /submissions/:id/review         # Add teacher review
GET    /submissions/:id/session        # Get linked session
```

### File Upload Endpoints

```
POST   /upload/homework                # Upload homework image
POST   /upload/profile-picture         # Upload profile pic
GET    /upload/:id                     # Get uploaded file
DELETE /upload/:id                     # Delete file
```

**Example:**
```typescript
// Upload homework image
POST /api/v1/upload/homework
Content-Type: multipart/form-data

{
  "file": <binary>,
  "student_id": 123,
  "question": "Is my approach correct?"
}

// Response
{
  "id": "abc-123",
  "url": "https://storage.ensina.ai/homework/abc-123.jpg",
  "analysis": {
    "detected_text": "2x + 5 = 13\nx = 4",
    "feedback": "Great work showing your steps! However..."
  }
}
```

### Progress Endpoints

```
GET    /progress/student/:id           # Get student progress
PUT    /progress/student/:id/topic     # Update topic mastery
GET    /progress/insights/:id          # Get learning insights
```

### Analytics Endpoints

```
GET    /analytics/student/:id          # Student analytics
GET    /analytics/teacher/:id          # Teacher class analytics
GET    /analytics/topics               # Topic difficulty heatmap
GET    /analytics/engagement           # Engagement metrics
```

---

## Database Considerations

### Current Schema (SQLite)

✅ **Keep the schema** - it's well-designed!

Current tables:
- `students`
- `sessions`
- `progress`
- `teachers`
- `assignments`
- `submissions`
- `incidents`

### Required Schema Changes

**1. Add Users Table (for authentication)**

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('student', 'parent', 'teacher', 'admin')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    email_verified BOOLEAN DEFAULT FALSE
);
```

**2. Link existing tables to users:**

```sql
ALTER TABLE students ADD COLUMN user_id INTEGER REFERENCES users(id);
ALTER TABLE teachers ADD COLUMN user_id INTEGER REFERENCES users(id);
```

**3. Add parent-student relationship:**

```sql
CREATE TABLE parent_student (
    parent_id INTEGER REFERENCES users(id),
    student_id INTEGER REFERENCES students(id),
    relationship TEXT, -- 'mother', 'father', 'guardian'
    PRIMARY KEY (parent_id, student_id)
);
```

**4. Add refresh tokens:**

```sql
CREATE TABLE refresh_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id),
    token TEXT UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    revoked BOOLEAN DEFAULT FALSE
);
```

**5. File uploads:**

```sql
CREATE TABLE uploads (
    id TEXT PRIMARY KEY, -- UUID
    user_id INTEGER REFERENCES users(id),
    filename TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    mime_type TEXT NOT NULL,
    storage_path TEXT NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Migration Path: SQLite → PostgreSQL

**Timeline:** Move to PostgreSQL in Phase 7 (production deployment)

**Why PostgreSQL?**
- Better concurrency handling
- Full-text search for session transcripts
- JSON column types (already using JSON in sessions)
- Better performance for analytics queries
- Row-level security for multi-tenancy

**Migration Tool:** **Alembic** (database migration tool)

```bash
# Generate migration
alembic revision --autogenerate -m "Initial migration"

# Apply migration
alembic upgrade head
```

**Dual-Database Strategy (optional):**
- Keep SQLite for development
- Use PostgreSQL for production
- Abstraction via SQLAlchemy (same code works for both)

### Using SQLAlchemy ORM

**Current approach:** Raw SQL with dataclasses  
**New approach:** SQLAlchemy models with Pydantic validation

```python
# backend/models.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Student(Base):
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, nullable=False)
    grade_level = Column(Integer, nullable=False)
    parent_email = Column(String, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="student_profile")
    sessions = relationship("Session", back_populates="student")
```

```python
# backend/schemas.py
from pydantic import BaseModel, EmailStr
from typing import Optional

class StudentCreate(BaseModel):
    name: str
    grade_level: int
    parent_email: EmailStr

class StudentResponse(BaseModel):
    id: int
    name: str
    grade_level: int
    parent_email: str
    created_at: str
    
    class Config:
        from_attributes = True  # Pydantic v2
```

**Benefits:**
- Type safety with Pydantic
- Automatic validation
- Easy relationships
- Database-agnostic queries
- Migration support with Alembic

---

## Authentication & Security

### Authentication Strategy

**Approach: JWT (JSON Web Tokens) with HTTPOnly cookies**

**Why JWT?**
- Stateless (backend doesn't store sessions)
- Scalable (no session store needed)
- Works with mobile apps (not just web)
- Industry standard

**Why HTTPOnly cookies?**
- XSS protection (JavaScript can't access token)
- Automatically sent with requests
- Secure flag for HTTPS only
- SameSite flag for CSRF protection

### Authentication Flow

```
1. User logs in with email/password
   POST /api/v1/auth/login

2. Backend validates credentials
   - Hash password with bcrypt/argon2
   - Check against database

3. Generate tokens:
   - Access token (short-lived, 15 min)
   - Refresh token (long-lived, 7 days)

4. Set HTTPOnly cookies:
   Set-Cookie: access_token=xxx; HttpOnly; Secure; SameSite=Strict
   Set-Cookie: refresh_token=yyy; HttpOnly; Secure; SameSite=Strict

5. Frontend makes authenticated requests
   - Browser automatically sends cookies
   - Backend validates JWT on each request

6. Token refresh:
   - When access token expires
   - Use refresh token to get new access token
   POST /api/v1/auth/refresh
```

### Implementation with FastAPI

```python
# backend/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "your-secret-key-change-this"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Dependency for protected routes
async def get_current_user(token: str = Depends(HTTPBearer())):
    user_id = verify_token(token.credentials)
    # Fetch user from database
    user = storage.get_user(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user
```

```python
# Using the dependency
@app.get("/api/v1/students/me")
async def get_my_profile(current_user: User = Depends(get_current_user)):
    # current_user is authenticated user
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Not a student")
    return current_user
```

### Frontend Authentication (Next.js)

```typescript
// frontend/lib/auth.ts
import axios from 'axios';

export async function login(email: string, password: string) {
  const response = await axios.post('/api/v1/auth/login', {
    email,
    password
  }, {
    withCredentials: true // Send cookies
  });
  
  return response.data.user;
}

export async function logout() {
  await axios.post('/api/v1/auth/logout', {}, {
    withCredentials: true
  });
}

export async function getCurrentUser() {
  const response = await axios.get('/api/v1/auth/me', {
    withCredentials: true
  });
  return response.data;
}
```

```typescript
// frontend/components/ProtectedRoute.tsx
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';

export function ProtectedRoute({ children, allowedRoles }: Props) {
  const { user, loading } = useAuth();
  const router = useRouter();
  
  useEffect(() => {
    if (!loading && !user) {
      router.push('/login');
    }
    if (!loading && user && !allowedRoles.includes(user.role)) {
      router.push('/unauthorized');
    }
  }, [user, loading]);
  
  if (loading) return <LoadingSpinner />;
  if (!user) return null;
  
  return <>{children}</>;
}
```

### Security Best Practices

**1. Password Security:**
```python
# Use bcrypt or argon2
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hash password
hashed = pwd_context.hash(plain_password)

# Verify password
is_valid = pwd_context.verify(plain_password, hashed)
```

**2. Rate Limiting:**
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/v1/auth/login")
@limiter.limit("5/minute")  # Max 5 login attempts per minute
async def login(request: Request, ...):
    ...
```

**3. CORS Configuration:**
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://ensina.ai"],  # Production domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**4. Input Validation:**
```python
from pydantic import BaseModel, EmailStr, constr

class LoginRequest(BaseModel):
    email: EmailStr  # Validates email format
    password: constr(min_length=8, max_length=100)  # Length constraints
```

**5. SQL Injection Prevention:**
- Use SQLAlchemy ORM (parameterized queries)
- Never concatenate user input into SQL strings

**6. XSS Prevention:**
- React automatically escapes content
- For LaTeX/HTML rendering, use DOMPurify

```typescript
import DOMPurify from 'dompurify';

const cleanHTML = DOMPurify.sanitize(userContent);
```

**7. CSRF Protection:**
- SameSite cookies
- CSRF tokens for state-changing operations

**8. File Upload Security:**
```python
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def validate_upload(file: UploadFile):
    # Check extension
    if not file.filename.endswith(tuple(ALLOWED_EXTENSIONS)):
        raise HTTPException(400, "Invalid file type")
    
    # Check size
    file.file.seek(0, 2)  # Seek to end
    size = file.file.tell()
    file.file.seek(0)  # Reset
    
    if size > MAX_FILE_SIZE:
        raise HTTPException(400, "File too large")
    
    # Verify file is actually an image
    try:
        from PIL import Image
        Image.open(file.file)
        file.file.seek(0)
    except:
        raise HTTPException(400, "Invalid image file")
```

### Role-Based Access Control (RBAC)

```python
# backend/rbac.py
from enum import Enum
from fastapi import HTTPException

class Role(Enum):
    STUDENT = "student"
    PARENT = "parent"
    TEACHER = "teacher"
    ADMIN = "admin"

def require_role(*allowed_roles: Role):
    def decorator(func):
        async def wrapper(*args, current_user: User = Depends(get_current_user), **kwargs):
            if current_user.role not in [r.value for r in allowed_roles]:
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

# Usage
@app.get("/api/v1/students")
@require_role(Role.PARENT, Role.TEACHER, Role.ADMIN)
async def list_students(current_user: User = Depends(get_current_user)):
    # Only parents, teachers, and admins can list students
    return storage.list_students()
```

---

## Deployment Strategy

### Development Environment

```
Frontend: http://localhost:3000 (Next.js dev server)
Backend:  http://localhost:8000 (Uvicorn)
Database: SQLite (data/ensina.db)
```

### Staging Environment

**Frontend: Vercel**
- Automatic deployments from `develop` branch
- Preview URLs for each PR
- Environment variables in Vercel dashboard

**Backend: Railway / Fly.io**
- Deployed from `develop` branch
- PostgreSQL database (Railway Postgres or Fly.io Postgres)
- Automatic SSL

**Cost:** ~$15-20/month

### Production Environment

**Option 1: Vercel + Railway (Recommended for MVP)**

```
Frontend:  Vercel
           - https://ensina.ai
           - Global CDN
           - Edge functions
           - $20/month (Pro plan)

Backend:   Railway
           - https://api.ensina.ai
           - PostgreSQL database
           - Redis for caching
           - $20/month

Storage:   AWS S3 / Cloudflare R2
           - Homework images
           - Uploaded files
           - $5/month

Total:     ~$45/month
```

**Pros:**
- Easy to set up
- Great DX (developer experience)
- Automatic deployments
- Built-in monitoring

**Cons:**
- Limited control
- Vendor lock-in
- Can get expensive at scale

**Option 2: AWS (Best for Scale)**

```
Frontend:  Cloudfront + S3
           - Static assets on S3
           - CDN via CloudFront
           - ~$10/month

Backend:   ECS Fargate / EC2
           - Docker containers
           - Auto-scaling
           - ~$50-100/month

Database:  RDS PostgreSQL
           - Managed database
           - Automated backups
           - ~$50/month (db.t3.micro)

Storage:   S3
           - ~$5/month

Total:     ~$115-165/month
```

**Pros:**
- Full control
- Best for enterprise
- Excellent scaling
- Cost-effective at scale

**Cons:**
- More complex setup
- Requires DevOps knowledge
- More maintenance

**Option 3: DigitalOcean (Good Middle Ground)**

```
Frontend:  DO App Platform
           - $12/month

Backend:   DO App Platform
           - $12/month

Database:  Managed PostgreSQL
           - $15/month (smallest)

Spaces:    DO Spaces (S3-compatible)
           - $5/month

Total:     ~$44/month
```

**Pros:**
- Simpler than AWS
- Good documentation
- Flat pricing
- Includes monitoring

**Cons:**
- Fewer features than AWS
- Limited regions
- Smaller community

### Recommended: **Start with Vercel + Railway, migrate to AWS if needed**

### CI/CD Pipeline

**GitHub Actions Workflow:**

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main, develop]

jobs:
  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Install dependencies
        working-directory: ./frontend
        run: npm ci
      
      - name: Run tests
        working-directory: ./frontend
        run: npm test
      
      - name: Build
        working-directory: ./frontend
        run: npm run build
      
      - name: Deploy to Vercel
        if: github.ref == 'refs/heads/main'
        run: vercel --prod --token ${{ secrets.VERCEL_TOKEN }}

  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        working-directory: ./backend
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      
      - name: Run tests
        working-directory: ./backend
        run: pytest --cov=./ --cov-report=xml
      
      - name: Deploy to Railway
        if: github.ref == 'refs/heads/main'
        run: railway up --service backend
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
```

### Monitoring & Observability

**Application Monitoring:**
- **Sentry** - Error tracking ($26/month for team)
- **LogRocket** - Session replay ($99/month)
- **DataDog** - Full observability ($15/host/month)

**Recommended for MVP: Sentry (errors) + Vercel Analytics (frontend)**

```python
# Backend - Sentry integration
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[FastApiIntegration()],
    traces_sample_rate=1.0,
)
```

```typescript
// Frontend - Sentry integration
import * as Sentry from "@sentry/nextjs";

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  tracesSampleRate: 1.0,
});
```

**Logging:**
- **Structured logging** with `structlog` (Python)
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Log aggregation with CloudWatch / Logtail / Better Stack

**Metrics:**
- Response times
- Error rates
- Active users
- LLM API costs
- Database query performance

**Alerts:**
- Error rate > 1%
- Response time > 2s (p95)
- API cost spike (>$50/day)
- Database connections > 80%

---

## Risk Assessment

### Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **WebSocket reliability** | Medium | High | Fallback to SSE or polling; implement reconnection logic |
| **Data migration errors** | Medium | High | Thorough testing; backup before migration; rollback plan |
| **Performance regression** | Low | Medium | Load testing; performance budgets; monitoring |
| **Third-party API breaking changes** | Low | High | Version pinning; wrapper abstraction; monitoring |
| **Security vulnerability** | Low | High | Security audit; penetration testing; bug bounty |
| **Browser compatibility** | Low | Low | Support modern browsers only (last 2 versions) |

### Business Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **User adoption issues** | Medium | High | Gradual rollout; user testing; feedback loops |
| **Timeline overrun** | High | Medium | Buffer time (10-12 weeks vs 8 weeks); MVP scope |
| **Budget overrun** | Low | Low | Fixed-scope phases; cost monitoring |
| **Talent availability** | Medium | Medium | Clear documentation; knowledge transfer |
| **Regulatory compliance** | Low | High | FERPA/COPPA compliance review; legal counsel |

### Mitigation Strategies

**1. Gradual Rollout:**
- Week 1: Internal testing (team only)
- Week 2: Beta testing (10 volunteer students)
- Week 3: 25% of users
- Week 4: 50% of users
- Week 5: 100% migration

**2. Feature Flags:**
```typescript
// Feature flag system
const features = {
  useNewChatInterface: process.env.NEXT_PUBLIC_USE_NEW_CHAT === 'true',
  useWebSocket: process.env.NEXT_PUBLIC_USE_WEBSOCKET === 'true',
};

// Usage
{features.useNewChatInterface ? <NewChat /> : <LegacyChat />}
```

**3. Rollback Plan:**
- Keep Streamlit version running for 2 weeks after full migration
- Database backups before each phase
- Blue-green deployment (swap instantly if issues)
- DNS-level traffic routing

**4. User Communication:**
- Email announcing new version
- In-app notification of changes
- Video tutorial of new features
- Support channel for issues

---

## Timeline & Milestones

### Detailed Timeline (12 weeks total)

```
Week 1: Preparation & Setup
├─ Day 1-2: Project structure setup
├─ Day 3-4: API boilerplate (FastAPI)
├─ Day 5: Frontend boilerplate (Next.js)
└─ Deliverable: Running boilerplate apps

Week 2: Core API Development
├─ Day 1-2: Authentication endpoints
├─ Day 3: Student/teacher CRUD
├─ Day 4-5: Session endpoints
└─ Deliverable: Working API (no WebSocket yet)

Week 3: WebSocket & Chat API
├─ Day 1-2: WebSocket setup
├─ Day 3-4: Streaming chat integration
├─ Day 5: Testing & documentation
└─ Deliverable: Real-time chat API

Week 4: Student Interface (Part 1)
├─ Day 1-2: Chat UI components
├─ Day 3: LaTeX rendering
├─ Day 4: Graph rendering
├─ Day 5: Integration with API
└─ Deliverable: Basic chat working

Week 5: Student Interface (Part 2)
├─ Day 1-2: Image upload
├─ Day 3: Assignment selection
├─ Day 4-5: Polish & testing
└─ Deliverable: Complete student page

Week 6: Parent Dashboard
├─ Day 1-2: Dashboard layout
├─ Day 3: Session list/detail
├─ Day 4: Analytics charts
├─ Day 5: Incidents view
└─ Deliverable: Parent dashboard

Week 7: Teacher View
├─ Day 1-2: Assignment CRUD
├─ Day 3-4: Submission review
├─ Day 5: Rich text editor
└─ Deliverable: Teacher view

Week 8: Admin & Polish
├─ Day 1-2: Admin panel
├─ Day 3-5: Cross-browser testing, bug fixes
└─ Deliverable: Feature-complete app

Week 9: Testing & Security
├─ Day 1-2: E2E test suite
├─ Day 3: Security audit
├─ Day 4: Performance optimization
├─ Day 5: Accessibility audit
└─ Deliverable: Production-ready app

Week 10: Staging Deployment
├─ Day 1-2: Deploy to staging
├─ Day 3-5: Beta testing with real users
└─ Deliverable: Validated in staging

Week 11: Production Deployment
├─ Day 1: Production deploy (10% traffic)
├─ Day 2: Monitoring & fixes
├─ Day 3: 50% traffic
├─ Day 4: 100% traffic
├─ Day 5: Monitoring
└─ Deliverable: Live in production

Week 12: Deprecation & Docs
├─ Day 1-2: Deprecate Streamlit
├─ Day 3-4: Documentation
├─ Day 5: Post-mortem & retrospective
└─ Deliverable: Full migration complete
```

### Key Milestones

| Week | Milestone | Success Criteria |
|------|-----------|------------------|
| 1 | Project Setup | Both apps run locally |
| 3 | API Complete | All endpoints working, documented |
| 5 | Student Page | Can have full chat session |
| 7 | Teacher View | Can create & review assignments |
| 8 | Feature Complete | All pages working |
| 9 | Production Ready | Tests pass, security audit done |
| 11 | Live | 100% traffic on new version |
| 12 | Migration Complete | Streamlit deprecated |

---

## Cost Analysis

### Development Costs

**Team Size:** 2 developers (1 frontend, 1 backend/full-stack)

| Role | Rate | Hours | Total |
|------|------|-------|-------|
| Frontend Developer | $75/hr | 200 hrs (5 weeks × 40 hrs) | $15,000 |
| Backend Developer | $75/hr | 160 hrs (4 weeks × 40 hrs) | $12,000 |
| UI/UX Design | $100/hr | 40 hrs | $4,000 |
| QA Testing | $50/hr | 40 hrs | $2,000 |
| **Total Development** | | | **$33,000** |

**Internal development (if you have team):** Time cost of 12 weeks

### Infrastructure Costs

**Year 1 (Production):**

| Service | Monthly | Annual |
|---------|---------|--------|
| Vercel Pro | $20 | $240 |
| Railway (Backend + DB) | $25 | $300 |
| AWS S3 Storage | $5 | $60 |
| Sentry (Error tracking) | $26 | $312 |
| Domain & SSL | $2 | $24 |
| **Total Infrastructure** | **$78** | **$936** |

**LLM API Costs (variable):**
- Current with optimization: ~$160/week for 100 students
- Annual: ~$8,320
- Per student per year: ~$83

**Total Year 1 Operating:** ~$9,256/year (~$771/month)

### Break-Even Analysis

**Assumptions:**
- Charge $10/month per student
- Or $100/year per student

**Break-even:** 94 students

**At 200 students:**
- Revenue: $20,000/year
- Costs: $9,256/year (infrastructure) + $16,600 (LLM) = $25,856
- **Profit/Loss: -$5,856**

**At 500 students:**
- Revenue: $50,000/year
- Costs: $9,256 + $41,500 (LLM) = $50,756
- **Profit/Loss: -$756**

**At 1000 students:**
- Revenue: $100,000/year
- Costs: $12,000 (infra scales up) + $83,000 (LLM) = $95,000
- **Profit: $5,000**

**Note:** LLM costs are the main variable. Need efficient usage or higher pricing.

### ROI for School/District

**For a school with 500 students:**
- Current: Hire human tutor ($30/hr × 10 hrs/week × 40 weeks = $12,000/year)
- With Ensina AI: $10/student/month × 500 = $60,000/year
- **Savings:** N/A (more expensive than human, but 24/7 available for all students)

**Value Proposition:**
- Not cheaper than 1 human tutor
- But gives EVERY student access to 1-on-1 tutoring 24/7
- Effective cost per student-hour is much lower
- Frees up teachers for in-person help

---

## Conclusion & Recommendations

### Should You Migrate?

**Migrate if:**
- ✅ You want to scale beyond 50 concurrent users
- ✅ You need better UX (smooth interactions, mobile support)
- ✅ You plan to add advanced features (gamification, collaboration)
- ✅ You want to build a mobile app later
- ✅ You have budget for 12 weeks of development
- ✅ You want to raise funding (modern stack more attractive to investors)

**Stay with Streamlit if:**
- ❌ You have < 20 users
- ❌ It's just for personal/family use
- ❌ Budget is very limited
- ❌ You're iterating on product-market fit
- ❌ You're not technical (Streamlit is easier to maintain)

### Recommended Approach

**Phase 1: API-First (4 weeks)**
1. Build FastAPI backend
2. Keep Streamlit frontend
3. Make Streamlit call API instead of direct function calls
4. **Benefit:** Backend can serve other clients (mobile app, etc.)

**Phase 2: Gradual Frontend Migration (8 weeks)**
1. Replace one page at a time
2. Start with highest-value page (student chat)
3. Use feature flags to switch between old/new
4. **Benefit:** Reduce risk, get feedback early

**Phase 3: Polish & Scale (4 weeks)**
1. Migrate remaining pages
2. Deprecate Streamlit
3. Optimize and scale

**Total:** 16 weeks (4 months) with lower risk

### Next Steps

**Immediate (This Week):**
1. ✅ Review this plan with team
2. ✅ Get buy-in from stakeholders
3. ✅ Allocate budget (development + infrastructure)
4. ✅ Set up project tracking (Jira, Linear, etc.)

**Week 1:**
1. [ ] Hire developers (if needed)
2. [ ] Create GitHub repos
3. [ ] Set up development environment
4. [ ] Kick-off meeting

**Week 2:**
1. [ ] Begin API development
2. [ ] Set up CI/CD
3. [ ] Design system / component library

### Success Metrics

**Technical:**
- [ ] API response time < 200ms (p95)
- [ ] Page load time < 1.5s (p95)
- [ ] Test coverage > 80%
- [ ] Zero critical security vulnerabilities
- [ ] 99.9% uptime

**User Experience:**
- [ ] Chat latency < 1s to first token
- [ ] Mobile usable score > 90 (Lighthouse)
- [ ] Accessibility score > 95 (WCAG 2.1 AA)
- [ ] User satisfaction > 4/5

**Business:**
- [ ] Migration complete within 12 weeks
- [ ] Zero data loss during migration
- [ ] User retention > 90%
- [ ] Support tickets < 5% of users

---

## Appendix: Additional Resources

### Learning Resources

**Next.js:**
- Official Docs: https://nextjs.org/docs
- Learn Course: https://nextjs.org/learn
- YouTube: Vercel's Channel

**FastAPI:**
- Official Docs: https://fastapi.tiangolo.com
- Tutorial: https://fastapi.tiangolo.com/tutorial/
- Book: "Building Python Web APIs with FastAPI"

**React:**
- Official Docs: https://react.dev
- Course: "Epic React" by Kent C. Dodds

**TypeScript:**
- Official Handbook: https://www.typescriptlang.org/docs/
- Course: "Total TypeScript" by Matt Pocock

### Tools & Libraries

**Frontend:**
```json
{
  "dependencies": {
    "next": "^14.0.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "@tanstack/react-query": "^5.0.0",
    "zustand": "^4.4.0",
    "axios": "^1.6.0",
    "socket.io-client": "^4.5.0",
    "katex": "^0.16.0",
    "plotly.js": "^2.27.0",
    "react-plotly.js": "^2.6.0",
    "@radix-ui/react-*": "latest",
    "tailwindcss": "^3.3.0",
    "zod": "^3.22.0"
  },
  "devDependencies": {
    "typescript": "^5.0.0",
    "@types/react": "^18.2.0",
    "eslint": "^8.0.0",
    "prettier": "^3.0.0",
    "@testing-library/react": "^14.0.0",
    "@playwright/test": "^1.40.0"
  }
}
```

**Backend:**
```python
# requirements.txt
fastapi==0.104.0
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
alembic==1.12.0
pydantic[email]==2.5.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
aiofiles==23.2.1
python-socketio==5.10.0
redis==5.0.1
psycopg2-binary==2.9.9
sentry-sdk==1.38.0
structlog==23.2.0
pytest==7.4.0
pytest-asyncio==0.21.0
httpx==0.25.0  # for testing

# Keep existing
anthropic>=0.39.0
openai>=1.54.0
plotly>=5.18.0
python-dotenv>=1.0.0
```

### Example Code Snippets

**FastAPI Main App:**
```python
# backend/main.py
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import structlog

logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up...")
    # Initialize database, connections, etc.
    yield
    # Shutdown
    logger.info("Shutting down...")
    # Cleanup

app = FastAPI(
    title="Ensina AI API",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
from routers import auth, students, sessions, chat
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(students.router, prefix="/api/v1/students", tags=["students"])
app.include_router(sessions.router, prefix="/api/v1/sessions", tags=["sessions"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])

@app.get("/")
async def root():
    return {"message": "Ensina AI API", "version": "1.0.0"}
```

**Next.js API Route (example):**
```typescript
// frontend/app/api/health/route.ts
export async function GET() {
  return Response.json({ status: 'ok' });
}
```

**React Chat Component:**
```typescript
// frontend/components/Chat/ChatInterface.tsx
import { useState, useEffect, useRef } from 'react';
import { io } from 'socket.io-client';

export function ChatInterface({ studentId }: Props) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const socketRef = useRef<Socket>();

  useEffect(() => {
    socketRef.current = io('http://localhost:8000/api/v1/chat/stream');
    
    socketRef.current.on('message', (data) => {
      setMessages(prev => [...prev, data]);
    });

    return () => {
      socketRef.current?.disconnect();
    };
  }, []);

  const sendMessage = () => {
    socketRef.current?.emit('message', {
      student_id: studentId,
      content: input,
    });
    setInput('');
  };

  return (
    <div className="flex flex-col h-screen">
      <div className="flex-1 overflow-y-auto">
        {messages.map((msg, i) => (
          <MessageBubble key={i} message={msg} />
        ))}
      </div>
      <div className="p-4 border-t">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
          placeholder="Ask your question..."
          className="w-full p-2 border rounded"
        />
      </div>
    </div>
  );
}
```

---

## Final Thoughts

This migration is a significant undertaking but will position Ensina AI as a modern, scalable learning platform. The architecture proposed here will support:

1. **Current features** - Everything Streamlit does today
2. **Better UX** - Smooth, fast, mobile-friendly
3. **Future features** - Gamification, collaboration, mobile apps
4. **Scalability** - Handle thousands of concurrent users
5. **Developer experience** - Modern stack, easy to hire for

**Risk is manageable** with incremental migration and good testing.

**ROI is positive** if planning to scale beyond 100 active users.

**Time investment** of 12 weeks is justified for a production platform.

Good luck with the migration! 🚀

---

**Document Version:** 1.0  
**Last Updated:** 2024-11-14  
**Author:** AI Assistant (Claude)  
**Status:** Draft for Review
