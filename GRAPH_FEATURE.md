# Interactive Graph Feature - Ensina AI

Phase 2 implementation: Structured graph output with Plotly rendering for visualizing mathematical functions, equations, and relationships.

## Overview

The tutor can now generate interactive graphs to help students visualize:
- Linear functions and proportional relationships
- Data patterns and comparisons
- Step-by-step transformations
- Abstract mathematical concepts

## How It Works

1. **Tutor outputs structured graph specification** in JSON format within special code blocks
2. **App parses the specification** and renders with Plotly
3. **Student sees interactive graph** with zoom, pan, and hover features

## Graph Types Supported

### 1. Line Graph
For continuous functions and proportional relationships.

**Example:** Visualizing y = 2x
```graph
{
  "type": "line",
  "title": "Relação Proporcional: y = 2x",
  "equation": "y = 2x",
  "data": {
    "x": [0, 1, 2, 3, 4, 5],
    "y": [0, 2, 4, 6, 8, 10]
  },
  "x_label": "x",
  "y_label": "y"
}
```

**Use cases:**
- Linear equations: y = mx + b
- Proportional relationships (regra de três)
- Function behavior visualization
- Rate of change demonstrations

### 2. Scatter Plot
For discrete data points and patterns.

**Example:** Plotting test scores
```graph
{
  "type": "scatter",
  "title": "Notas dos Estudantes",
  "data": {
    "x": [1, 2, 3, 4, 5],
    "y": [7.5, 8.0, 6.5, 9.0, 8.5]
  },
  "x_label": "Prova",
  "y_label": "Nota"
}
```

**Use cases:**
- Data distribution
- Correlation analysis
- Discrete measurements
- Pattern identification

### 3. Bar Chart
For comparing categories or discrete values.

**Example:** Comparing class averages
```graph
{
  "type": "bar",
  "title": "Média por Turma",
  "data": {
    "x": ["7A", "7B", "7C"],
    "y": [8.2, 7.8, 8.5]
  },
  "x_label": "Turma",
  "y_label": "Média"
}
```

**Use cases:**
- Category comparisons
- Survey results
- Frequency distributions
- Performance comparisons

## Technical Implementation

### Backend: GraphRenderer (src/graph_renderer.py)
```python
class GraphRenderer:
    @staticmethod
    def parse_graph_spec(spec_text: str) -> Optional[Dict[str, Any]]
        # Parses JSON graph specification

    @staticmethod
    def create_line_graph(spec: Dict[str, Any]) -> go.Figure
        # Creates Plotly line graph

    @staticmethod
    def create_scatter_graph(spec: Dict[str, Any]) -> go.Figure
        # Creates Plotly scatter plot

    @staticmethod
    def create_bar_chart(spec: Dict[str, Any]) -> go.Figure
        # Creates Plotly bar chart

    @classmethod
    def render(cls, spec: Dict[str, Any]) -> Optional[go.Figure]
        # Main render method
```

### Frontend: app.py Integration
```python
def parse_and_display_message(content: str):
    """Parse message content and display text and graphs."""
    # Finds ```graph...``` blocks using regex
    # Parses JSON specifications
    # Renders with st.plotly_chart()
```

### Tutor Prompt: config.py
The tutor system prompt includes:
- Graph format specification
- Examples for each graph type
- Guidelines for when to use graphs
- JSON structure documentation

## Example Usage Scenarios

### Scenario 1: Ice Cream Shop (Regra de Três)

**Student asks:** "Como o preço muda quando eu compro mais bolas?"

**Tutor response:**
```
Ótima pergunta! Vamos visualizar essa relação:

| Bolas | Preço |
|-------|-------|
| 3     | R$ 12 |
| 5     | R$ 20 |
| 10    | R$ 40 |

A relação é proporcional: $\frac{preço}{bolas} = 4$

Veja o gráfico:

```graph
{
  "type": "line",
  "title": "Preço vs Quantidade de Bolas",
  "equation": "Preço = 4 × Bolas",
  "data": {
    "x": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    "y": [0, 4, 8, 12, 16, 20, 24, 28, 32, 36, 40]
  },
  "x_label": "Número de Bolas",
  "y_label": "Preço (R$)"
}
```

Repare que a linha é reta! Isso mostra que a relação é proporcional.
```

### Scenario 2: Linear Function

**Student asks:** "Como funciona y = 2x + 3?"

**Tutor response:**
```
Vamos explorar essa função:

A equação $y = 2x + 3$ tem dois componentes:
- **2x**: A parte que cresce (coeficiente angular = 2)
- **+3**: Onde a linha cruza o eixo y (coeficiente linear = 3)

Veja o gráfico:

```graph
{
  "type": "line",
  "title": "Função Linear: y = 2x + 3",
  "equation": "y = 2x + 3",
  "data": {
    "x": [-2, -1, 0, 1, 2, 3, 4],
    "y": [-1, 1, 3, 5, 7, 9, 11]
  },
  "x_label": "x",
  "y_label": "y"
}
```

O que você percebe sobre como y aumenta quando x aumenta?
```

## Benefits

### For Students:
✅ **Visual Learning** - See abstract concepts come to life
✅ **Interactive Exploration** - Zoom and pan to explore patterns
✅ **Better Understanding** - Graphs make relationships clear
✅ **Engaging Experience** - More interesting than plain text

### For Teachers:
✅ **Quality Visualization** - Professional, accurate graphs
✅ **Consistent Format** - All graphs follow same structure
✅ **Quick Generation** - AI creates appropriate visualizations
✅ **Curriculum Aligned** - Supports standards-based math education

### Technical:
✅ **Zero Cost** - No image generation APIs needed
✅ **Fast** - Instant rendering with Plotly
✅ **Safe** - No code execution, only JSON parsing
✅ **Responsive** - Works on mobile and desktop

## Testing

```bash
# Run tutor tests
python -m pytest tests/test_tutor.py -v

# All 34 tests pass ✅
```

## Next Steps

Phase 3: Image Upload (Claude Vision for homework analysis)
- Student uploads photo of their work
- Tutor analyzes diagrams and provides feedback
- Catches errors in student's written work

Phase 4: Voice Mode (Portuguese TTS/STT)
- Audio input for natural interaction
- Text-to-speech for engaging responses
- Accessibility for younger students

## Cost Analysis

**Phase 2 (Graphs):**
- API Cost: $0 (no additional LLM calls)
- Processing: Client-side Plotly rendering
- Latency: < 100ms for graph rendering
- **Total added cost: $0 per session**

Compare to:
- AI image generation: $0.04 per image
- Screenshot + Vision API: ~$0.01 per image

Phase 2 provides better value: free, instant, and precise!
