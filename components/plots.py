"""
components/plots.py
-------------------
Plotly figure builders for surfaces, mapped points, and experiment charts.

All functions return `plotly.graph_objects.Figure` objects that can be
displayed directly in Streamlit with `st.plotly_chart(fig)`.
"""

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from config import (
    GRID_POINTS,
    SURFACE_ALPHA,
    SURFACE_COLOR,
    POINT_COLOR_A,
    POINT_COLOR_B,
    MAPPED_POINT_COLOR_A,
    MAPPED_POINT_COLOR_B,
    LINE_COLOR,
)
from src.surfaces import (
    generate_plane,
    generate_cylinder,
    generate_circle,
)


# ══════════════════════════════════════════════════════════════════════════════
# SURFACE FIGURES
# ══════════════════════════════════════════════════════════════════════════════

def plot_plane(half_size: float = 3.0, n: int = GRID_POINTS,
               point_a=None, point_b=None) -> go.Figure:
    """
    Create a 3-D Plotly figure of a flat plane with optional sample points.

    Parameters
    ----------
    half_size : float
    n         : int
    point_a, point_b : array-like of shape (3,) or None

    Returns
    -------
    go.Figure
    """
    X, Y, Z = generate_plane(half_size, n)

    fig = go.Figure()
    fig.add_trace(go.Surface(
        x=X, y=Y, z=Z,
        colorscale=[[0, SURFACE_COLOR], [1, "lightblue"]],
        opacity=SURFACE_ALPHA,
        showscale=False,
        name="Plane",
    ))
    _add_points(fig, point_a, point_b)
    _style_3d(fig, title=f"Flat Plane  (±{half_size})")
    return fig


def plot_cylinder(radius: float = 1.0, height: float = 2.0,
                  n: int = GRID_POINTS,
                  point_a=None, point_b=None) -> go.Figure:
    """
    Create a 3-D Plotly figure of a cylinder with optional sample points.
    """
    X, Y, Z = generate_cylinder(radius, height, n, n)

    fig = go.Figure()
    fig.add_trace(go.Surface(
        x=X, y=Y, z=Z,
        colorscale=[[0, SURFACE_COLOR], [1, "lightblue"]],
        opacity=SURFACE_ALPHA,
        showscale=False,
        name="Cylinder",
    ))
    _add_points(fig, point_a, point_b)
    _style_3d(fig, title=f"Cylinder  (r={radius}, h={height})")
    return fig


def plot_circle(radius: float = 1.0, n: int = GRID_POINTS,
                point_a=None, point_b=None) -> go.Figure:
    """
    Create a 3-D Plotly figure of a circle (1-D curve in 3-D space).
    """
    x, y, z = generate_circle(radius, n)

    fig = go.Figure()
    fig.add_trace(go.Scatter3d(
        x=x, y=y, z=z,
        mode="lines",
        line=dict(color=SURFACE_COLOR, width=6),
        name="Circle",
    ))
    _add_points(fig, point_a, point_b)
    _style_3d(fig, title=f"Circle  (r={radius})")
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# MAPPING FIGURE (source + target surfaces + connecting lines)
# ══════════════════════════════════════════════════════════════════════════════

def plot_mapping(
    source_surface: str,
    target_surface: str,
    point_a_original: np.ndarray,
    point_b_original: np.ndarray,
    point_a_mapped: np.ndarray,
    point_b_mapped: np.ndarray,
    radius: float = 1.0,
    height: float = 2.0,
    half_size: float = 3.0,
) -> go.Figure:
    """
    Show both source and target surfaces side by side with the original
    points, their mapped images, and connecting lines.

    Parameters
    ----------
    source_surface : str  – "Cylinder", "Plane", or "Circle"
    target_surface : str  – "Cylinder", "Plane", or "Circle"
    point_a_original, point_b_original : np.ndarray, shape (3,)
    point_a_mapped, point_b_mapped     : np.ndarray, shape (3,)
    radius, height, half_size           : geometric parameters

    Returns
    -------
    go.Figure  (two 3-D subplots)
    """
    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{"type": "scene"}, {"type": "scene"}]],
        subplot_titles=[f"Original: {source_surface}", f"Mapped: {target_surface}"],
    )

    # ── Source surface ────────────────────────────────────────────────────────
    _add_surface_traces(fig, source_surface, radius, height, half_size, col=1)

    # Original points
    for pt, color, label in [
        (point_a_original, POINT_COLOR_A, "A (original)"),
        (point_b_original, POINT_COLOR_B, "B (original)"),
    ]:
        fig.add_trace(
            go.Scatter3d(
                x=[pt[0]], y=[pt[1]], z=[pt[2]],
                mode="markers+text",
                marker=dict(size=8, color=color),
                text=[label],
                textposition="top center",
                name=label,
                showlegend=True,
            ),
            row=1, col=1,
        )

    # Line between original points
    fig.add_trace(
        go.Scatter3d(
            x=[point_a_original[0], point_b_original[0]],
            y=[point_a_original[1], point_b_original[1]],
            z=[point_a_original[2], point_b_original[2]],
            mode="lines",
            line=dict(color=LINE_COLOR, width=4, dash="dash"),
            name="d_original",
        ),
        row=1, col=1,
    )

    # ── Target surface ────────────────────────────────────────────────────────
    _add_surface_traces(fig, target_surface, radius, height, half_size, col=2)

    # Mapped points
    for pt, color, label in [
        (point_a_mapped, MAPPED_POINT_COLOR_A, "f(A) mapped"),
        (point_b_mapped, MAPPED_POINT_COLOR_B, "f(B) mapped"),
    ]:
        fig.add_trace(
            go.Scatter3d(
                x=[pt[0]], y=[pt[1]], z=[pt[2]],
                mode="markers+text",
                marker=dict(size=8, color=color, symbol="diamond"),
                text=[label],
                textposition="top center",
                name=label,
                showlegend=True,
            ),
            row=1, col=2,
        )

    # Line between mapped points
    fig.add_trace(
        go.Scatter3d(
            x=[point_a_mapped[0], point_b_mapped[0]],
            y=[point_a_mapped[1], point_b_mapped[1]],
            z=[point_a_mapped[2], point_b_mapped[2]],
            mode="lines",
            line=dict(color=LINE_COLOR, width=4, dash="dash"),
            name="d_mapped",
        ),
        row=1, col=2,
    )

    fig.update_layout(
        height=520,
        title_text="Mapping Visualisation",
        margin=dict(l=0, r=0, t=60, b=0),
    )
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# EXPERIMENT CHART
# ══════════════════════════════════════════════════════════════════════════════

def plot_experiment_distortion(df, mapping_name: str) -> go.Figure:
    """
    Bar chart of the absolute distance change for each point pair in the
    experiment DataFrame.

    Parameters
    ----------
    df           : pd.DataFrame  – output of run_experiment()
    mapping_name : str

    Returns
    -------
    go.Figure
    """
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df["Pair"],
        y=df["Abs Change"],
        marker_color="steelblue",
        name="Absolute Change",
    ))

    # Mean line
    mean_val = df["Abs Change"].mean()
    fig.add_hline(
        y=mean_val,
        line_dash="dash",
        line_color="red",
        annotation_text=f"Mean = {mean_val:.4f}",
        annotation_position="top right",
    )

    fig.update_layout(
        title=f"Distance Distortion per Point Pair  —  {mapping_name}",
        xaxis_title="Point Pair Index",
        yaxis_title="|d_after − d_before|",
        height=380,
        margin=dict(l=40, r=20, t=60, b=40),
    )
    return fig


def plot_experiment_ratio(df, mapping_name: str) -> go.Figure:
    """
    Scatter plot of the distance ratio (d_after / d_before) for each pair.
    A ratio of 1.0 (dashed line) would indicate isometric behaviour.
    """
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df["Pair"],
        y=df["Ratio (d_after/d_before)"],
        mode="markers+lines",
        marker=dict(size=8, color="darkorange"),
        line=dict(color="darkorange", width=1),
        name="Ratio",
    ))

    # Isometry reference line at ratio = 1
    fig.add_hline(
        y=1.0,
        line_dash="dash",
        line_color="green",
        annotation_text="Isometry (ratio = 1)",
        annotation_position="bottom right",
    )

    fig.update_layout(
        title=f"Distance Ratio per Point Pair  —  {mapping_name}",
        xaxis_title="Point Pair Index",
        yaxis_title="d_after / d_before",
        height=380,
        margin=dict(l=40, r=20, t=60, b=40),
    )
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# PRIVATE HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _add_points(fig: go.Figure, point_a, point_b):
    """Add point A and point B markers to a single-subplot figure."""
    for pt, color, label in [
        (point_a, POINT_COLOR_A, "Point A"),
        (point_b, POINT_COLOR_B, "Point B"),
    ]:
        if pt is not None:
            pt = np.asarray(pt)
            fig.add_trace(go.Scatter3d(
                x=[pt[0]], y=[pt[1]], z=[pt[2]],
                mode="markers+text",
                marker=dict(size=9, color=color),
                text=[label],
                textposition="top center",
                name=label,
            ))


def _style_3d(fig: go.Figure, title: str = ""):
    """Apply consistent 3-D layout styling."""
    fig.update_layout(
        height=480,
        margin=dict(l=0, r=0, t=50, b=0),
        scene=dict(
            xaxis_title="X",
            yaxis_title="Y",
            zaxis_title="Z",
            aspectmode="data",
        ),
        title_text=title,
    )


def _add_surface_traces(fig, surface_name, radius, height, half_size, col):
    """Add a surface mesh trace to the given subplot column."""
    n = GRID_POINTS

    if surface_name == "Plane":
        X, Y, Z = generate_plane(half_size, n)
        fig.add_trace(
            go.Surface(x=X, y=Y, z=Z,
                       colorscale=[[0, SURFACE_COLOR], [1, "lightblue"]],
                       opacity=SURFACE_ALPHA, showscale=False, name="Plane"),
            row=1, col=col,
        )

    elif surface_name == "Cylinder":
        X, Y, Z = generate_cylinder(radius, height, n, n)
        fig.add_trace(
            go.Surface(x=X, y=Y, z=Z,
                       colorscale=[[0, SURFACE_COLOR], [1, "lightblue"]],
                       opacity=SURFACE_ALPHA, showscale=False, name="Cylinder"),
            row=1, col=col,
        )

    elif surface_name == "Circle":
        x, y, z = generate_circle(radius, n)
        fig.add_trace(
            go.Scatter3d(x=x, y=y, z=z, mode="lines",
                         line=dict(color=SURFACE_COLOR, width=6), name="Circle"),
            row=1, col=col,
        )
