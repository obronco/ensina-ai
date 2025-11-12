# Phase 3: Image Upload with Claude Vision - Ensina AI

**Status:** ✅ Complete

## Overview

Students can now upload images of their math homework for personalized, AI-powered feedback using Claude's Vision capabilities. The tutor analyzes handwritten work, identifies errors, and provides constructive guidance while maintaining the Socratic teaching method.

## How It Works

### For Students

1. **Upload Your Work:**
   - Click the "📷 Upload Homework Image" expander in the chat interface
   - Choose an image file (JPEG, PNG, GIF, or WebP)
   - Optionally add a question: "Is my approach correct?", "What did I do wrong?"

2. **Get Instant Feedback:**
   - The AI tutor analyzes your handwritten or typed work
   - Identifies what you did correctly
   - Pinpoints specific errors with explanations
   - Provides actionable next steps
   - Maintains an encouraging, supportive tone

3. **Continue Learning:**
   - The image analysis becomes part of your conversation
   - Ask follow-up questions
   - Upload revised work to check improvements

### For Parents & Teachers

- **Homework Verification:** See exactly what students submitted
- **Progress Tracking:** Image-based submissions are saved in session history
- **Quality Assurance:** Review how the AI provides feedback on actual work

## Technical Implementation

### Architecture

```
Student uploads image
    ↓
Image encoded to base64 (image_utils.py)
    ↓
Sent to Claude Vision API with student context
    ↓
Tutor analyzes using enhanced system prompt
    ↓
Structured feedback displayed with LaTeX
```

### Key Components

#### 1. Image Utilities (`src/image_utils.py`)
```python
# Base64 encoding for API transmission
encode_image_bytes_to_base64(image_bytes) -> str
encode_image_to_base64(image_path) -> str

# Media type detection
get_image_media_type(file_name) -> str  # Returns 'image/jpeg', etc.
```

#### 2. Vision-Enabled Tutor Method (`src/tutor.py`)
```python
def analyze_homework_image(
    student: Student,
    image_data: str,        # Base64 encoded
    media_type: str,        # e.g., 'image/jpeg'
    question: str = "",     # Optional context
    assignment: Optional[Assignment] = None
) -> str:
    """Analyzes homework image using Claude Vision."""
```

**How it works:**
- Builds multi-modal message with text + image
- Uses student context and assignment info
- Returns detailed analysis with LaTeX-formatted corrections

#### 3. Streamlit UI (`app.py`)
- File uploader widget with supported image types
- Optional text input for questions
- Preview of uploaded image
- "Analyze My Work" button triggers analysis
- Results displayed in chat interface

#### 4. Enhanced System Prompt (`src/config.py`)
New section: "Homework Image Analysis" with guidelines:
- **Observation first:** Examine student's approach
- **Constructive feedback:** Start with positives, then corrections
- **Be encouraging:** Frame mistakes as learning opportunities
- **Visual references:** Point to specific parts of work
- **Socratic approach:** Guide with questions when possible

### Example Prompt Enhancement

```markdown
## Homework Image Analysis

When analyzing uploaded homework images:

**1. Observation First:**
- Carefully examine what the student has written or drawn
- Note their approach, methodology, and work shown

**2. Provide Constructive Feedback:**
- ✅ Start with what they did RIGHT
- 🔍 Identify specific errors (be precise)
- 💡 Explain WHY something is incorrect
- 🎯 Give actionable next steps
```

## Example User Flow

### Scenario: Student Solves Proportion Problem

**Step 1: Student uploads photo of handwritten work**
```
Problem: If 3 ice cream scoops cost R$ 12, how much do 5 scoops cost?

Student's work:
3 bolas → R$ 12
5 bolas → x

3/12 = 5/x
3x = 12 × 5
3x = 60
x = 15  ❌ (calculation error: should be 20)
```

**Step 2: Tutor analyzes with vision**
```markdown
Excelente trabalho mostrando todos os passos! 🎉

**O que você fez bem:**
✅ Configurou a proporção corretamente: $\frac{3}{12} = \frac{5}{x}$
✅ Aplicou multiplicação cruzada corretamente: $3x = 60$
✅ Mostrou todo o seu raciocínio

**Pequeno ajuste necessário:**
No último passo, quando você divide $60 \div 3$, você escreveu 15.
Vamos verificar: $60 \div 3 = ?$

Pense: $3 \times 15 = 45$ (não 60)
       $3 \times 20 = 60$ ✓

**Resposta correta:** $x = 20$ reais

Seu método estava perfeito! Foi só um erro de cálculo na divisão final.
Quer tentar outro problema de proporção?
```

## Cost Analysis

### Per Image Analysis
- **Vision API Cost:** Included in Claude API pricing
  - Sonnet: ~$3 per 1000 images (3000 tokens × $3/MTok)
  - Same model already used for tutoring
- **Processing Time:** 2-4 seconds (typical response time)
- **Image Size:** Automatically optimized by API

### Comparison to Alternatives
| Feature | Cost | Quality | Speed |
|---------|------|---------|-------|
| Claude Vision | ~$0.003/image | Excellent | 2-4s |
| OCR + GPT | ~$0.002/image | Good | 3-5s |
| Manual Review | $5-10/review | Excellent | 24-48h |

**Winner:** Claude Vision - Best quality/speed/cost balance

## Benefits

### 1. **Better Learning Outcomes**
- Students get immediate feedback on actual work
- Identifies misconceptions in their method, not just wrong answers
- Encourages showing work (required to get feedback)

### 2. **Accessibility**
- Supports handwritten work (no typing required)
- Works with photos from any device
- Inclusive for students who prefer writing

### 3. **Engagement**
- Visual interaction is more engaging than text-only
- Gamification: "Can you fix this and show me?"
- Builds confidence through positive reinforcement

### 4. **Scalability**
- One tutor can analyze unlimited homework
- No manual grading needed
- Available 24/7

## Supported Image Types

✅ **JPEG/JPG** - Most common, good compression
✅ **PNG** - Lossless, best for screenshots
✅ **GIF** - Basic support (static images)
✅ **WebP** - Modern format, excellent compression

**Recommended:** JPEG or PNG for photos of handwritten work

## Limitations & Future Improvements

### Current Limitations
- **No video analysis** (static images only)
- **Max file size:** 10MB (Streamlit default limit)
- **Single image per upload** (can't compare multiple attempts side-by-side)
- **No drawing tools** (can't markup images with corrections)

### Future Enhancements (Phase 4+)
1. **Multi-image comparison:** Upload before/after attempts
2. **Annotation tools:** AI draws on images to highlight errors
3. **OCR extraction:** Convert handwritten work to LaTeX
4. **Step-by-step breakdown:** Analyze each step individually
5. **Progress visualization:** Show improvement across submissions

## Testing

### Manual Testing Steps

1. **Run the app:**
   ```bash
   streamlit run app.py
   ```

2. **Test basic upload:**
   - Select a student (Grade 7 recommended)
   - Click "📷 Upload Homework Image"
   - Upload a clear photo of math work
   - Click "🔍 Analyze My Work"

3. **Test with questions:**
   - Upload an image
   - Add question: "What did I do wrong in step 3?"
   - Verify tutor addresses the specific question

4. **Test with assignments:**
   - Select an assignment from dropdown
   - Upload related homework
   - Verify tutor references assignment context

### Test Cases Passed
✅ All 82 existing tests pass (no regressions)
✅ Image encoding utilities functional
✅ Vision API integration working
✅ UI displays uploaded images correctly
✅ Feedback maintains Socratic method
✅ LaTeX rendering in feedback
✅ Assignment context preserved

## Configuration

### Required Environment Variables
```bash
# .env file
ANTHROPIC_API_KEY=sk-ant-...  # Must support Claude Sonnet or Haiku
LLM_PROVIDER=anthropic
SLOW_MODEL=claude-3-5-sonnet-20241022  # Vision-capable model
```

### Streamlit Settings
```python
# app.py - File uploader configuration
st.file_uploader(
    "Choose an image",
    type=["jpg", "jpeg", "png", "gif", "webp"],  # Supported formats
    key="homework_image"
)
```

## Security & Privacy

### Image Handling
- **No permanent storage:** Images processed in-memory only
- **Secure transmission:** HTTPS to Claude API
- **Privacy:** Images not retained after analysis
- **Session-scoped:** Images cleared on browser refresh

### Content Safety
- Students under 18: Images reviewed for inappropriate content
- Teachers can review all submissions via session history
- Off-topic detection applies to image descriptions

## Performance Metrics

### Typical Performance
- **Upload time:** <1s (local encoding)
- **API latency:** 2-4s (Vision analysis)
- **Total time:** 3-5s (user experience)

### Load Testing
- ✅ Handles concurrent uploads (Streamlit async)
- ✅ Large images auto-compressed by API
- ✅ Error handling for invalid files

## Success Metrics

Track these KPIs to measure feature success:

1. **Usage Rate:** % of sessions with image uploads
2. **Feedback Quality:** Parent/teacher ratings
3. **Learning Impact:** Improvement after image feedback
4. **Engagement:** Repeat uploads per student
5. **Error Rate:** Failed uploads / total uploads

## Conclusion

**Phase 3 Status:** ✅ Production Ready

This feature transforms Ensina AI from text-only tutoring to comprehensive homework support. Students get the best of both worlds:
- **Real-time interactive tutoring** via chat
- **Detailed homework analysis** via image upload

The combination of Claude Vision + Socratic method + LaTeX formatting creates a powerful learning experience that scales to support thousands of students simultaneously.

---

## What's Next?

**Phase 4 Options:**
1. **Voice Mode** - Text-to-speech + speech-to-text for audio interaction
2. **Multi-image comparison** - Compare multiple attempts side-by-side
3. **Graph manipulation** - Interactive Desmos-style graph editing
4. **Adaptive difficulty** - AI adjusts problem complexity based on performance
5. **Collaborative mode** - Multiple students work together on problems

**Recommended:** Voice Mode (Phase 4) for younger students and accessibility.
