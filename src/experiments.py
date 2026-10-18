"""
src/experiments.py
------------------
Reproducible multi-point distance comparison experiment.

The experiment samples N random pairs of points on the source surface,
maps each pair through the selected mapping, and compares the Euclidean
distances before and after.  A fixed random seed (EXPERIMENT_SEED from
config.py) makes results identical on every run.

No external data files are required.
"""

import numpy as np
import pandas as pd
from config import EXPERIMENT_SEED, EXPERIMENT_N_PAIRS
from src.surfaces import cylinder_point_from_params, circle_point_from_theta
from src.mappings import (
    cylinder_to_circle,
    plane_to_cylinder,
    identity_map,
    get_mapping_info,
)
from src.distance_analysis import euclidean_distance, distance_distortion


# ══════════════════════════════════════════════════════════════════════════════
# CYLINDER → CIRCLE  EXPERIMENT
# ══════════════════════════════════════════════════════════════════════════════

def run_cylinder_to_circle_experiment(
    radius: float = 1.0,
    height: float = 2.0,
    n_pairs: int = EXPERIMENT_N_PAIRS,
    seed: int = EXPERIMENT_SEED,
) -> pd.DataFrame:
    """
    Sample random point pairs on the cylinder and compare distances
    before and after the cylinder → circle projection.

    Parameters
    ----------
    radius  : float  – cylinder radius
    height  : float  – cylinder height
    n_pairs : int    – number of point pairs to test
    seed    : int    – RNG seed for reproducibility

    Returns
    -------
    pd.DataFrame with columns:
        Pair, θ_A, z_A, θ_B, z_B,
        d_cylinder (Euclidean), d_circle (Euclidean), Absolute Change, Ratio
    """
    rng = np.random.default_rng(seed)

    rows = []
    for i in range(n_pairs):
        # Random angular coordinates in [0, 2π]
        theta_a = rng.uniform(0, 2 * np.pi)
        theta_b = rng.uniform(0, 2 * np.pi)
        # Random fractional heights in [0, 1]
        zf_a = rng.uniform(0, 1)
        zf_b = rng.uniform(0, 1)

        # 3-D points on the cylinder
        p_a = cylinder_point_from_params(theta_a, zf_a, radius, height)
        p_b = cylinder_point_from_params(theta_b, zf_b, radius, height)

        # Map to circle
        q_a = cylinder_to_circle(p_a, circle_radius=radius)
        q_b = cylinder_to_circle(p_b, circle_radius=radius)

        # Distances
        d_cyl = euclidean_distance(p_a, p_b)
        d_circ = euclidean_distance(q_a, q_b)
        dist_info = distance_distortion(d_cyl, d_circ)

        rows.append({
            "Pair": i + 1,
            "θ_A (rad)": round(theta_a, 4),
            "z_A (frac)": round(zf_a, 4),
            "θ_B (rad)": round(theta_b, 4),
            "z_B (frac)": round(zf_b, 4),
            "d_cylinder": round(d_cyl, 6),
            "d_circle": round(d_circ, 6),
            "Abs Change": dist_info["absolute_change"],
            "Ratio (d_after/d_before)": dist_info["ratio"],
        })

    return pd.DataFrame(rows)


# ══════════════════════════════════════════════════════════════════════════════
# PLANE → CYLINDER  EXPERIMENT
# ══════════════════════════════════════════════════════════════════════════════

def run_plane_to_cylinder_experiment(
    plane_size: float = 3.0,
    radius: float = 1.0,
    height: float = 2.0,
    n_pairs: int = EXPERIMENT_N_PAIRS,
    seed: int = EXPERIMENT_SEED,
) -> pd.DataFrame:
    """
    Sample random point pairs on the plane and compare distances
    before and after the plane → cylinder mapping.

    Parameters
    ----------
    plane_size : float – half-width of the square region sampled on the plane
    radius     : float – cylinder radius
    height     : float – cylinder height (used to clamp y)
    n_pairs    : int
    seed       : int

    Returns
    -------
    pd.DataFrame
    """
    rng = np.random.default_rng(seed)

    rows = []
    for i in range(n_pairs):
        # Random points on the plane: x in [-plane_size, plane_size], y in [0, height]
        x_a = rng.uniform(-plane_size, plane_size)
        y_a = rng.uniform(0, height)
        x_b = rng.uniform(-plane_size, plane_size)
        y_b = rng.uniform(0, height)

        p_a = np.array([x_a, y_a, 0.0])
        p_b = np.array([x_b, y_b, 0.0])

        q_a = plane_to_cylinder(p_a, radius=radius, height=height)
        q_b = plane_to_cylinder(p_b, radius=radius, height=height)

        d_plane = euclidean_distance(p_a, p_b)
        d_cyl = euclidean_distance(q_a, q_b)
        dist_info = distance_distortion(d_plane, d_cyl)

        rows.append({
            "Pair": i + 1,
            "x_A": round(x_a, 4),
            "y_A": round(y_a, 4),
            "x_B": round(x_b, 4),
            "y_B": round(y_b, 4),
            "d_plane": round(d_plane, 6),
            "d_cylinder": round(d_cyl, 6),
            "Abs Change": dist_info["absolute_change"],
            "Ratio (d_after/d_before)": dist_info["ratio"],
        })

    return pd.DataFrame(rows)


# ══════════════════════════════════════════════════════════════════════════════
# IDENTITY EXPERIMENT (control group)
# ══════════════════════════════════════════════════════════════════════════════

def run_identity_experiment(
    n_pairs: int = EXPERIMENT_N_PAIRS,
    seed: int = EXPERIMENT_SEED,
) -> pd.DataFrame:
    """
    Baseline experiment using the identity map.
    All distances should be exactly preserved (ratio ≈ 1.0).
    """
    rng = np.random.default_rng(seed)

    rows = []
    for i in range(n_pairs):
        p_a = rng.uniform(-3, 3, size=3)
        p_b = rng.uniform(-3, 3, size=3)

        q_a = identity_map(p_a)
        q_b = identity_map(p_b)

        d_before = euclidean_distance(p_a, p_b)
        d_after = euclidean_distance(q_a, q_b)
        dist_info = distance_distortion(d_before, d_after)

        rows.append({
            "Pair": i + 1,
            "d_before": round(d_before, 6),
            "d_after": round(d_after, 6),
            "Abs Change": dist_info["absolute_change"],
            "Ratio (d_after/d_before)": dist_info["ratio"],
        })

    return pd.DataFrame(rows)


# ══════════════════════════════════════════════════════════════════════════════
# DISPATCHER: choose experiment by mapping name
# ══════════════════════════════════════════════════════════════════════════════

def run_experiment(mapping_name: str, **kwargs) -> pd.DataFrame:
    """
    Run the appropriate experiment for the given mapping name.

    Parameters
    ----------
    mapping_name : str  – must be one of the keys returned by get_mapping_info.
    **kwargs : passed through to the specific experiment function.

    Returns
    -------
    pd.DataFrame with experiment results.
    """
    dispatch = {
        "Cylinder → Circle": run_cylinder_to_circle_experiment,
        "Plane → Cylinder": run_plane_to_cylinder_experiment,
        "Identity (no change)": run_identity_experiment,
    }
    if mapping_name not in dispatch:
        raise KeyError(
            f"No experiment defined for mapping '{mapping_name}'. "
            f"Available: {list(dispatch.keys())}"
        )
    return dispatch[mapping_name](**kwargs)


# ══════════════════════════════════════════════════════════════════════════════
# INTERPRETATION  (auto-generated textual summary)
# ══════════════════════════════════════════════════════════════════════════════

def generate_interpretation(df: pd.DataFrame, mapping_name: str) -> str:
    """
    Generate a plain-English summary of the experiment results.

    Parameters
    ----------
    df           : pd.DataFrame  – output of run_experiment()
    mapping_name : str

    Returns
    -------
    str – multi-line interpretation text
    """
    # Find the column names for before/after distances
    col_names = df.columns.tolist()
    # Columns ending in specific patterns
    before_col = next((c for c in col_names if c.startswith("d_") and
                       "after" not in c and "circle" not in c and
                       "cylinder" not in c.replace("d_cylinder", "")), None)

    # Locate absolute change column
    change_col = "Abs Change"
    ratio_col = "Ratio (d_after/d_before)"

    changes = df[change_col]
    ratios = df[ratio_col].dropna()

    mean_change = changes.mean()
    max_change = changes.max()
    min_change = changes.min()
    mean_ratio = ratios.mean()
    preserved_count = (changes < 1e-9).sum()

    lines = [
        f"**Mapping**: {mapping_name}",
        f"**Number of point pairs tested**: {len(df)}",
        "",
        f"- Average absolute distance change: **{mean_change:.6f}**",
        f"- Maximum change: **{max_change:.6f}** | Minimum change: **{min_change:.6f}**",
        f"- Average ratio d_after / d_before: **{mean_ratio:.4f}**",
        f"- Pairs where distance was exactly preserved: **{preserved_count} / {len(df)}**",
        "",
    ]

    if mapping_name == "Identity (no change)":
        lines.append(
            "✅ As expected for the identity map, all distances are preserved "
            "to within floating-point precision. This confirms the analysis code "
            "is working correctly."
        )
    elif mean_ratio < 0.99:
        lines.append(
            "📉 On average, the mapping **reduces** the Euclidean distance between "
            "pairs. This is typical for a projection that collapses one dimension "
            "(e.g. dropping the z-coordinate). "
            "The mapping is **not** an isometry."
        )
    elif mean_ratio > 1.01:
        lines.append(
            "📈 On average, the mapping **increases** the Euclidean distance between "
            "pairs. This can happen when the wrapping introduces curvature. "
            "The mapping is **not** an isometry."
        )
    else:
        lines.append(
            "⚖️ The average ratio is close to 1.0, but individual pairs still show "
            "variation. The mapping does not guarantee isometric behaviour for all "
            "pairs and should not be classified as an isometry without further "
            "mathematical verification."
        )

    lines += [
        "",
        "*Note: These results are computed numerically using a fixed random seed "
        f"({EXPERIMENT_SEED}) and are fully reproducible. "
        "They are intended as educational illustrations, not scientific claims.*",
    ]

    return "\n".join(lines)
