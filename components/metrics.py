"""
components/metrics.py
---------------------
Streamlit rendering helpers for distance metrics, comparison tables,
and distance analysis cards.

These functions wrap `st.*` calls so that the main app.py stays clean
and focused on layout logic.
"""

import streamlit as st
import pandas as pd
from config import DISTANCE_DECIMAL_PLACES


def render_distance_card(label: str, value: float, delta: float | None = None,
                         help_text: str = "") -> None:
    """
    Render a Streamlit metric card for a distance value.

    Parameters
    ----------
    label     : str    – card header
    value     : float  – the distance to display
    delta     : float  – change relative to a reference (shown as +/- indicator)
    help_text : str    – tooltip text shown next to the label
    """
    formatted = f"{value:.{DISTANCE_DECIMAL_PLACES}f}"
    delta_str = f"{delta:+.{DISTANCE_DECIMAL_PLACES}f}" if delta is not None else None
    st.metric(label=label, value=formatted, delta=delta_str, help=help_text)


def render_distance_comparison(d_before: float, d_after: float,
                               source_name: str = "Original",
                               target_name: str = "Mapped") -> None:
    """
    Render a three-column metric block comparing distances before and after
    a mapping.

    Parameters
    ----------
    d_before    : float
    d_after     : float
    source_name : str  – label for the "before" distance
    target_name : str  – label for the "after" distance
    """
    delta = d_after - d_before
    col1, col2, col3 = st.columns(3)

    with col1:
        render_distance_card(
            label=f"d({source_name})",
            value=d_before,
            help_text="Euclidean distance between the two points on the source surface.",
        )
    with col2:
        render_distance_card(
            label=f"d({target_name})",
            value=d_after,
            help_text="Euclidean distance between the two mapped points on the target surface.",
        )
    with col3:
        render_distance_card(
            label="Δ Distance",
            value=abs(delta),
            delta=delta,
            help_text=(
                "Absolute difference |d_after − d_before|. "
                "Zero would indicate a distance-preserving map (isometry)."
            ),
        )


def render_distortion_table(analysis: dict) -> None:
    """
    Render a neat Markdown/DataFrame table summarising one distance analysis.

    Parameters
    ----------
    analysis : dict  – output of distance_analysis.analyse_mapping_distances()
    """
    rows = {
        "Property": [
            "d_before (source surface)",
            "d_after (target surface)",
            "Absolute change |Δd|",
            "Relative change |Δd| / d_before",
            "Ratio d_after / d_before",
            "Distance preserved?",
        ],
        "Value": [
            f"{analysis['d_before']:.{DISTANCE_DECIMAL_PLACES}f}",
            f"{analysis['d_after']:.{DISTANCE_DECIMAL_PLACES}f}",
            f"{analysis['absolute_change']:.{DISTANCE_DECIMAL_PLACES}f}",
            (f"{analysis['relative_change']:.{DISTANCE_DECIMAL_PLACES}f}"
             if analysis["relative_change"] is not None else "N/A (d_before ≈ 0)"),
            (f"{analysis['ratio']:.{DISTANCE_DECIMAL_PLACES}f}"
             if analysis["ratio"] is not None else "N/A (d_before ≈ 0)"),
            "✅ Yes" if analysis["preserved"] else "❌ No",
        ],
    }
    df = pd.DataFrame(rows)
    st.table(df)


def render_point_coordinates(point_a, point_b,
                              label_a: str = "Point A",
                              label_b: str = "Point B") -> None:
    """
    Display coordinates of two points in an expandable section.

    Parameters
    ----------
    point_a, point_b : array-like of shape (3,)
    label_a, label_b : str
    """
    with st.expander("📍 Point Coordinates", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**{label_a}**")
            st.code(
                f"x = {point_a[0]:.4f}\n"
                f"y = {point_a[1]:.4f}\n"
                f"z = {point_a[2]:.4f}",
                language="text",
            )
        with col2:
            st.markdown(f"**{label_b}**")
            st.code(
                f"x = {point_b[0]:.4f}\n"
                f"y = {point_b[1]:.4f}\n"
                f"z = {point_b[2]:.4f}",
                language="text",
            )


def render_experiment_table(df: pd.DataFrame) -> None:
    """
    Render the experiment results DataFrame in Streamlit with row highlighting.

    Parameters
    ----------
    df : pd.DataFrame  – output of src.experiments.run_experiment()
    """
    st.dataframe(
        df.style.format(precision=6).background_gradient(
            subset=["Abs Change"], cmap="YlOrRd"
        ),
        use_container_width=True,
    )


def render_info_box(text: str) -> None:
    """Render an informational callout box."""
    st.info(text, icon="ℹ️")


def render_warning_box(text: str) -> None:
    """Render a warning callout box."""
    st.warning(text, icon="⚠️")
