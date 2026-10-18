"""
app.py
------
GeoMap Visualizer – Streamlit entry point.

Run with:
    streamlit run app.py

The application is organised into four tabs:
  1. Surface & Mapping  – interactive 3-D plots and distance analysis
  2. Research Experiment – reproducible multi-pair distance comparison
  3. Math Background    – educational explanations with equations
  4. About              – project metadata and limitations
"""

import numpy as np
import streamlit as st

from config import (
    APP_TITLE,
    APP_SUBTITLE,
    APP_VERSION,
    CYLINDER_RADIUS_DEFAULT,
    CYLINDER_HEIGHT_DEFAULT,
    PLANE_SIZE_DEFAULT,
    CIRCLE_RADIUS_DEFAULT,
    EXPERIMENT_N_PAIRS,
)
from src.surfaces import (
    cylinder_point_from_params,
    circle_point_from_theta,
)
from src.mappings import get_mapping_info
from src.distance_analysis import (
    euclidean_distance,
    cylinder_geodesic_distance,
    circle_arc_length,
    analyse_mapping_distances,
)
from src.experiments import run_experiment, generate_interpretation
from components.plots import (
    plot_plane,
    plot_cylinder,
    plot_circle,
    plot_mapping,
    plot_experiment_distortion,
    plot_experiment_ratio,
)
from components.metrics import (
    render_distance_comparison,
    render_distortion_table,
    render_point_coordinates,
    render_experiment_table,
    render_info_box,
    render_warning_box,
)

# ── Page configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Header ────────────────────────────────────────────────────────────────────
st.title(f"🗺️ {APP_TITLE}")
st.caption(f"{APP_SUBTITLE}  •  v{APP_VERSION}")
st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR  – global controls
# ══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.header("⚙️ Controls")

    # ── Surface selection ─────────────────────────────────────────────────────
    st.subheader("1. Surface")
    surface_choice = st.selectbox(
        "Select a surface to display",
        options=["Cylinder", "Plane", "Circle"],
        index=0,
        help="Choose the geometric surface to explore.",
    )

    # ── Geometric parameters ──────────────────────────────────────────────────
    st.subheader("2. Parameters")

    if surface_choice == "Cylinder":
        radius = st.slider("Cylinder radius", 0.5, 3.0, CYLINDER_RADIUS_DEFAULT, 0.1)
        height = st.slider("Cylinder height", 0.5, 5.0, CYLINDER_HEIGHT_DEFAULT, 0.1)
        half_size = PLANE_SIZE_DEFAULT
        circle_radius = radius  # circle has same radius for mapping

    elif surface_choice == "Plane":
        half_size = st.slider("Plane half-size", 1.0, 5.0, PLANE_SIZE_DEFAULT, 0.5)
        radius = st.slider("Target cylinder radius", 0.5, 3.0, CYLINDER_RADIUS_DEFAULT, 0.1)
        height = st.slider("Target cylinder height", 0.5, 5.0, CYLINDER_HEIGHT_DEFAULT, 0.1)
        circle_radius = CIRCLE_RADIUS_DEFAULT

    else:  # Circle
        circle_radius = st.slider("Circle radius", 0.5, 3.0, CIRCLE_RADIUS_DEFAULT, 0.1)
        radius = circle_radius
        height = CYLINDER_HEIGHT_DEFAULT
        half_size = PLANE_SIZE_DEFAULT

    # ── Mapping selection ─────────────────────────────────────────────────────
    st.subheader("3. Mapping")

    # Only show mappings that make sense for the selected source surface
    available_mappings = {
        "Cylinder": ["Cylinder → Circle", "Identity (no change)"],
        "Plane":    ["Plane → Cylinder", "Identity (no change)"],
        "Circle":   ["Identity (no change)"],
    }
    mapping_choice = st.selectbox(
        "Select a mapping",
        options=available_mappings[surface_choice],
        help="The function f: S₁ → S₂ applied to each point.",
    )

    mapping_info = get_mapping_info(mapping_choice)

    # ── Point A controls ──────────────────────────────────────────────────────
    st.subheader("4. Point A")
    if surface_choice == "Cylinder":
        theta_a = st.slider("θ_A (radians)", 0.0, 2 * float(np.pi), 0.5, 0.05,
                            format="%.2f")
        zfrac_a = st.slider("z_A (fraction of height)", 0.0, 1.0, 0.2, 0.05)
        point_a = cylinder_point_from_params(theta_a, zfrac_a, radius, height)
    elif surface_choice == "Plane":
        xa = st.slider("x_A", -half_size, half_size, -1.0, 0.1)
        ya = st.slider("y_A", 0.0, height, 0.5, 0.1)
        point_a = np.array([xa, ya, 0.0])
    else:
        theta_a = st.slider("θ_A (radians)", 0.0, 2 * float(np.pi), 0.5, 0.05,
                            format="%.2f")
        point_a = circle_point_from_theta(theta_a, circle_radius)

    # ── Point B controls ──────────────────────────────────────────────────────
    st.subheader("5. Point B")
    if surface_choice == "Cylinder":
        theta_b = st.slider("θ_B (radians)", 0.0, 2 * float(np.pi), 2.0, 0.05,
                            format="%.2f")
        zfrac_b = st.slider("z_B (fraction of height)", 0.0, 1.0, 0.7, 0.05)
        point_b = cylinder_point_from_params(theta_b, zfrac_b, radius, height)
    elif surface_choice == "Plane":
        xb = st.slider("x_B", -half_size, half_size, 1.5, 0.1)
        yb = st.slider("y_B", 0.0, height, 1.5, 0.1)
        point_b = np.array([xb, yb, 0.0])
    else:
        theta_b = st.slider("θ_B (radians)", 0.0, 2 * float(np.pi), 2.0, 0.05,
                            format="%.2f")
        point_b = circle_point_from_theta(theta_b, circle_radius)

    st.markdown("---")
    st.caption("📐 GeoMap Visualizer — for educational use only.")

# ══════════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════════

tab_surface, tab_experiment, tab_math, tab_about = st.tabs([
    "🗺️ Surface & Mapping",
    "🔬 Research Experiment",
    "📚 Math Background",
    "ℹ️ About",
])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 – SURFACE & MAPPING
# ─────────────────────────────────────────────────────────────────────────────
with tab_surface:

    # ── Compute mapped points ─────────────────────────────────────────────────
    try:
        map_fn = mapping_info["function"]
        if mapping_choice == "Cylinder → Circle":
            point_a_mapped = map_fn(point_a, circle_radius=radius)
            point_b_mapped = map_fn(point_b, circle_radius=radius)
        elif mapping_choice == "Plane → Cylinder":
            point_a_mapped = map_fn(point_a, radius=radius, height=height)
            point_b_mapped = map_fn(point_b, radius=radius, height=height)
        else:  # identity
            point_a_mapped = map_fn(point_a)
            point_b_mapped = map_fn(point_b)
        mapping_error = None
    except Exception as e:
        point_a_mapped = point_a.copy()
        point_b_mapped = point_b.copy()
        mapping_error = str(e)

    # ── Mapping info banner ───────────────────────────────────────────────────
    st.subheader(f"Mapping: {mapping_choice}")
    col_info1, col_info2 = st.columns([3, 1])
    with col_info1:
        st.markdown(mapping_info["description"])
        st.code(f"Formula: {mapping_info['formula']}", language="text")
    with col_info2:
        iso_status = "✅ Yes" if mapping_info["preserves_distances"] else "❌ No"
        st.metric("Isometry?", iso_status)
        st.caption(f"**Lost info:** {mapping_info['lost_information']}")

    if mapping_error:
        render_warning_box(f"Mapping error: {mapping_error}. Displaying identity instead.")

    # ── 3-D plots ─────────────────────────────────────────────────────────────
    st.subheader("3-D Visualisation")

    if mapping_choice == "Identity (no change)":
        # Single plot — source only
        if surface_choice == "Cylinder":
            fig_surface = plot_cylinder(radius, height, point_a=point_a, point_b=point_b)
        elif surface_choice == "Plane":
            fig_surface = plot_plane(half_size, point_a=point_a, point_b=point_b)
        else:
            fig_surface = plot_circle(circle_radius, point_a=point_a, point_b=point_b)
        st.plotly_chart(fig_surface, use_container_width=True)

    else:
        # Side-by-side source + target
        fig_mapping = plot_mapping(
            source_surface=surface_choice,
            target_surface=mapping_info["target"],
            point_a_original=point_a,
            point_b_original=point_b,
            point_a_mapped=point_a_mapped,
            point_b_mapped=point_b_mapped,
            radius=radius,
            height=height,
            half_size=half_size,
        )
        st.plotly_chart(fig_mapping, use_container_width=True)

    # ── Distance analysis ─────────────────────────────────────────────────────
    st.subheader("📏 Distance Analysis")

    analysis = analyse_mapping_distances(
        point_a, point_b, point_a_mapped, point_b_mapped
    )

    render_distance_comparison(
        analysis["d_before"], analysis["d_after"],
        source_name=surface_choice,
        target_name=mapping_info["target"],
    )

    render_point_coordinates(point_a, point_b)
    render_point_coordinates(
        point_a_mapped, point_b_mapped,
        label_a="f(A) mapped", label_b="f(B) mapped",
    )

    st.subheader("📊 Full Distortion Table")
    render_distortion_table(analysis)

    # ── Intrinsic distance note ───────────────────────────────────────────────
    st.subheader("🔵 Intrinsic Distance Estimate")

    if surface_choice == "Cylinder":
        d_geo = cylinder_geodesic_distance(point_a, point_b, radius)
        d_eucl = analysis["d_before"]
        st.markdown(f"""
| Distance type | Value |
|---|---|
| Euclidean (through 3-D space) | `{d_eucl:.6f}` |
| Geodesic (along cylinder surface, unroll method) | `{d_geo:.6f}` |
        """)
        render_info_box(
            "The **geodesic distance** on a cylinder is computed by unrolling the "
            "cylinder into a flat rectangle. The two numbers differ whenever the "
            "two points are not on the same vertical line of the cylinder, because "
            "the Euclidean straight line cuts *through* the cylinder wall."
        )

    elif surface_choice == "Circle":
        d_arc = circle_arc_length(point_a, point_b, circle_radius)
        d_eucl = analysis["d_before"]
        st.markdown(f"""
| Distance type | Value |
|---|---|
| Euclidean (chord through centre) | `{d_eucl:.6f}` |
| Arc length (along circle) | `{d_arc:.6f}` |
        """)
        render_info_box(
            "The **arc length** is the intrinsic distance on the circle — the length "
            "of the curve connecting the two points along the circle itself. "
            "It is always ≥ the Euclidean (chord) distance."
        )

    elif surface_choice == "Plane":
        d_eucl = analysis["d_before"]
        render_info_box(
            f"On a **flat plane**, the Euclidean distance and the geodesic distance "
            f"are identical: `{d_eucl:.6f}`. "
            "A straight line lying flat on the plane is already the shortest path."
        )


# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 – RESEARCH EXPERIMENT
# ─────────────────────────────────────────────────────────────────────────────
with tab_experiment:
    st.subheader("🔬 Reproducible Distance Comparison Experiment")

    render_info_box(
        "This experiment samples a fixed set of point pairs on the source surface "
        "using a deterministic random seed and compares Euclidean distances before "
        "and after the mapping. Results are identical on every run."
    )

    st.markdown(f"**Current mapping:** `{mapping_choice}`  |  "
                f"**Number of pairs:** `{EXPERIMENT_N_PAIRS}`  |  "
                f"**Seed:** `42`")

    # Run experiment
    with st.spinner("Running experiment…"):
        try:
            if mapping_choice == "Cylinder → Circle":
                exp_df = run_experiment(
                    mapping_choice, radius=radius, height=height
                )
            elif mapping_choice == "Plane → Cylinder":
                exp_df = run_experiment(
                    mapping_choice,
                    plane_size=half_size,
                    radius=radius,
                    height=height,
                )
            else:
                exp_df = run_experiment(mapping_choice)
            exp_error = None
        except Exception as e:
            exp_df = None
            exp_error = str(e)

    if exp_error:
        render_warning_box(f"Experiment error: {exp_error}")
    else:
        # Table
        st.subheader("Numerical Results Table")
        render_experiment_table(exp_df)

        # Charts
        col_chart1, col_chart2 = st.columns(2)
        with col_chart1:
            st.plotly_chart(
                plot_experiment_distortion(exp_df, mapping_choice),
                use_container_width=True,
            )
        with col_chart2:
            st.plotly_chart(
                plot_experiment_ratio(exp_df, mapping_choice),
                use_container_width=True,
            )

        # Auto interpretation
        st.subheader("📝 Auto-generated Interpretation")
        interpretation = generate_interpretation(exp_df, mapping_choice)
        st.markdown(interpretation)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 – MATH BACKGROUND
# ─────────────────────────────────────────────────────────────────────────────
with tab_math:
    st.subheader("📚 Mathematical Background")

    with st.expander("▶ What is a Surface?", expanded=True):
        st.markdown(r"""
A **surface** in mathematics is a 2-dimensional shape embedded in 3-dimensional space.
You can think of it as a thin sheet that you can bend, curve, or fold.

Common examples:
- A **flat plane** — the simplest surface, where every point has coordinates (x, y, 0).
- A **cylinder** — a plane bent into a tube. Points are given by:
  $$x = r\cos\theta, \quad y = r\sin\theta, \quad z = z$$
  where $\theta \in [0, 2\pi]$ is the angle and $z$ is the height.
- A **circle** — technically a 1-D curve, but useful as a target surface:
  $$x = r\cos\theta, \quad y = r\sin\theta, \quad z = 0$$
        """)

    with st.expander("▶ What is a Mapping?"):
        st.markdown(r"""
A **mapping** (or **map**) $f: S_1 \to S_2$ is a function that takes every
point on surface $S_1$ and assigns it to a point on surface $S_2$.

**Example — Cylinder to Circle projection:**

$$f(x, y, z) = \bigl(r\cos\theta,\; r\sin\theta,\; 0\bigr), \quad
\theta = \arctan\!\left(\frac{y}{x}\right)$$

This map "collapses" the cylinder onto the circle by simply ignoring the height $z$.
Every point at the same angle $\theta$ but different heights maps to the *same*
point on the circle — so information is lost.
        """)

    with st.expander("▶ Euclidean Distance vs Intrinsic Distance"):
        st.markdown(r"""
**Euclidean (ambient) distance** is the straight-line distance through 3-D space:

$$d_E(p, q) = \sqrt{(x_2-x_1)^2 + (y_2-y_1)^2 + (z_2-z_1)^2}$$

This is the distance a ruler would measure if you could drill through the solid.

**Intrinsic (geodesic) distance** is the length of the *shortest path that stays
on the surface*:

- On a **plane**: $d_{\text{geo}} = d_E$ (the shortest path is a straight line).
- On a **cylinder** (unrolled): $d_{\text{geo}} = \sqrt{(r\,\Delta\theta)^2 + (\Delta z)^2}$
- On a **circle** (arc): $d_{\text{arc}} = r\,|\Delta\theta|$

These two measures are equal only on flat surfaces.
        """)

    with st.expander("▶ What is an Isometry?"):
        st.markdown(r"""
A mapping $f: S_1 \to S_2$ is called an **isometry** if it preserves all distances:

$$d\bigl(f(p),\, f(q)\bigr) = d(p, q) \quad \text{for every pair } p, q \in S_1$$

**Examples:**
- Rotation, reflection, and translation of the plane are isometries.
- Unrolling a cylinder onto a flat plane (the "development") is a local isometry.
- Projecting a cylinder onto a circle (dropping $z$) is **NOT** an isometry —
  pairs with different heights that share the same angle map to the same point,
  making the distance zero even though the original distance was non-zero.

> ⚠️ **Important**: this app never claims that any implemented mapping is an
> isometry unless its mathematical conditions have been explicitly verified.
        """)

    with st.expander("▶ Differential Geometry — A First Glimpse"):
        st.markdown(r"""
**Differential Geometry** studies surfaces and their properties using calculus.
The central object is the **metric tensor** $g_{ij}$, which encodes how distances
are measured at each point.

For a parametric surface $\mathbf{r}(u, v)$:

$$g_{ij} = \frac{\partial \mathbf{r}}{\partial u^i} \cdot
            \frac{\partial \mathbf{r}}{\partial u^j}$$

The arc length of a curve $\gamma(t)$ on the surface is:

$$L[\gamma] = \int_a^b \sqrt{g_{ij}\,\dot{u}^i\,\dot{u}^j}\; dt$$

For the **cylinder** with radius $r$, $\mathbf{r}(\theta, z) = (r\cos\theta, r\sin\theta, z)$:

$$g = \begin{pmatrix} r^2 & 0 \\ 0 & 1 \end{pmatrix}$$

This app implements the geodesic distances derived from these formulas.
        """)

    with st.expander("▶ Assumptions and Limitations of This App"):
        st.markdown(r"""
1. **Euclidean distances only** — ambient (chord) distances are used for the
   mapping comparison, not geodesic distances.
2. **Cylinder geodesic** is computed by the "unroll" formula, which is exact
   for paths that wind at most once around the cylinder.
3. **No peer review** — this is an educational tool, not a scientific publication.
4. **No isometry claims** — the app never asserts that a projection is an isometry.
5. **Finite numerical precision** — results are rounded to 6 decimal places.
        """)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 4 – ABOUT
# ─────────────────────────────────────────────────────────────────────────────
with tab_about:
    st.subheader("ℹ️ About GeoMap Visualizer")
    st.markdown(f"""
**Version:** {APP_VERSION}

**Purpose:** An interactive educational tool for second-year B.Tech Computer
Science students to explore foundational concepts in Differential Geometry
through computational experiments.

**Technology stack:**
- Python 3.11
- NumPy — numerical computations
- Streamlit — interactive web interface
- Plotly — interactive 3-D visualisations
- Pandas — tabular data and experiment results
- pytest — unit testing

**Author note:** This project was built for research internship portfolio
purposes and is intended as a *demonstration of computational exploration*,
not as original mathematical research.

**Limitations:**
- Only three surfaces are implemented.
- Only two non-trivial mappings are implemented.
- Geodesic computation uses simplified closed-form formulae.
- The application has not been scientifically validated.

**Future work:**
- Add sphere, torus, and Möbius strip surfaces.
- Implement conformal maps and area-preserving maps.
- Use `geomstats` for exact geodesic computation.
- Export experiment data to CSV.

---
*GeoMap Visualizer is provided for educational purposes only.*
    """)
