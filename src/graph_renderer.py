"""Graph rendering utilities for mathematical visualization."""
import json
from typing import Dict, Any, Optional
import plotly.graph_objects as go
import plotly.express as px


class GraphRenderer:
    """Renders mathematical graphs from structured specifications."""

    @staticmethod
    def parse_graph_spec(spec_text: str) -> Optional[Dict[str, Any]]:
        """
        Parse graph specification from JSON text.

        Args:
            spec_text: JSON string with graph specification

        Returns:
            Parsed dictionary or None if invalid
        """
        try:
            spec = json.loads(spec_text)
            # Validate required fields
            if "type" not in spec:
                return None
            return spec
        except (json.JSONDecodeError, Exception):
            return None

    @staticmethod
    def create_line_graph(spec: Dict[str, Any]) -> go.Figure:
        """Create a line graph from specification."""
        data = spec.get("data", {})
        x = data.get("x", [])
        y = data.get("y", [])

        fig = go.Figure()

        # Add line trace
        fig.add_trace(go.Scatter(
            x=x,
            y=y,
            mode='lines+markers',
            name=spec.get("equation", "y = f(x)"),
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=8)
        ))

        # Update layout
        fig.update_layout(
            title=spec.get("title", "Graph"),
            xaxis_title=spec.get("x_label", "x"),
            yaxis_title=spec.get("y_label", "y"),
            showlegend=True,
            hovermode='x unified',
            template='plotly_white'
        )

        # Add grid
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')

        return fig

    @staticmethod
    def create_scatter_graph(spec: Dict[str, Any]) -> go.Figure:
        """Create a scatter plot from specification."""
        data = spec.get("data", {})
        x = data.get("x", [])
        y = data.get("y", [])

        fig = go.Figure()

        # Add scatter trace
        fig.add_trace(go.Scatter(
            x=x,
            y=y,
            mode='markers',
            name=spec.get("label", "Data"),
            marker=dict(size=12, color='#ff7f0e')
        ))

        # Update layout
        fig.update_layout(
            title=spec.get("title", "Scatter Plot"),
            xaxis_title=spec.get("x_label", "x"),
            yaxis_title=spec.get("y_label", "y"),
            showlegend=True,
            template='plotly_white'
        )

        # Add grid
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')

        return fig

    @staticmethod
    def create_bar_chart(spec: Dict[str, Any]) -> go.Figure:
        """Create a bar chart from specification."""
        data = spec.get("data", {})
        x = data.get("x", [])
        y = data.get("y", [])

        fig = go.Figure()

        # Add bar trace
        fig.add_trace(go.Bar(
            x=x,
            y=y,
            name=spec.get("label", "Values"),
            marker=dict(color='#2ca02c')
        ))

        # Update layout
        fig.update_layout(
            title=spec.get("title", "Bar Chart"),
            xaxis_title=spec.get("x_label", "Category"),
            yaxis_title=spec.get("y_label", "Value"),
            showlegend=True,
            template='plotly_white'
        )

        return fig

    @classmethod
    def render(cls, spec: Dict[str, Any]) -> Optional[go.Figure]:
        """
        Render a graph from specification.

        Args:
            spec: Graph specification dictionary

        Returns:
            Plotly figure or None if type not supported
        """
        graph_type = spec.get("type", "").lower()

        if graph_type == "line":
            return cls.create_line_graph(spec)
        elif graph_type == "scatter":
            return cls.create_scatter_graph(spec)
        elif graph_type == "bar":
            return cls.create_bar_chart(spec)
        else:
            return None
