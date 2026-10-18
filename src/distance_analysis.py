"""
src/distance_analysis.py
------------------------
Helper functions for measuring Euclidean distances and analysing
how a geometric mapping changes those distances.

Key concepts
------------
- **Ambient Euclidean distance**: the straight-line (ruler) distance
  between two points measured through 3-D space.
  Formula: d(p, q) = sqrt((x2-x1)² + (y2-y1)² + (z2-z1)²)

- **Intrinsic / geodesic distance**: the length of the shortest path
  that stays *on the surface* between two points.  For a flat plane
  this equals the Euclidean distance.  For a cylinder the geodesic
  is a helix, and for a circle it is the arc length.

- **Distortion**: the ratio d_mapped / d_original (or the difference).
  A distortion of 1.0 means the mapping preserved distance exactly.
"""

import numpy as np
from config import DISTANCE_DECIMAL_PLACES


# ══════════════════════════════════════════════════════════════════════════════
# EUCLIDEAN DISTANCE
# ══════════════════════════════════════════════════════════════════════════════

def euclidean_distance(p: np.ndarray, q: np.ndarray) -> float:
    """
    Compute the 3-D Euclidean (straight-line) distance between two points.

    Parameters
    ----------
    p, q : np.ndarray, shape (3,)

    Returns
    -------
    float  – the distance d(p, q) ≥ 0

    Raises
    ------
    ValueError  – if either point does not have exactly 3 coordinates.
    """
    p, q = _validate_pair(p, q)
    return float(np.linalg.norm(p - q))


def euclidean_distance_rounded(p: np.ndarray, q: np.ndarray,
                               decimals: int = DISTANCE_DECIMAL_PLACES) -> float:
    """Euclidean distance rounded to `decimals` decimal places."""
    return round(euclidean_distance(p, q), decimals)


# ══════════════════════════════════════════════════════════════════════════════
# CYLINDER GEODESIC
# ══════════════════════════════════════════════════════════════════════════════

def cylinder_geodesic_distance(p: np.ndarray, q: np.ndarray,
                               radius: float = 1.0) -> float:
    """
    Approximate the intrinsic (geodesic) distance between two points on a
    cylinder by "unrolling" the cylinder into a flat rectangle.

    On a cylinder of radius r the intrinsic distance between two points
    (θ₁, z₁) and (θ₂, z₂) is:

        d_geo = sqrt( (r · Δθ_min)² + Δz² )

    where Δθ_min is the minimum angular separation (in [0, π]).

    This is exact for geodesics that do not wrap more than once around
    the cylinder.

    Parameters
    ----------
    p, q   : np.ndarray, shape (3,)  – points in 3-D Cartesian [x, y, z]
    radius : float

    Returns
    -------
    float – the geodesic distance on the cylinder surface
    """
    p, q = _validate_pair(p, q)
    if radius <= 0:
        raise ValueError(f"radius must be positive, got {radius}.")

    theta_p = np.arctan2(p[1], p[0])
    theta_q = np.arctan2(q[1], q[0])

    # Minimum angular separation (handle wrap-around)
    delta_theta = abs(theta_p - theta_q)
    delta_theta = min(delta_theta, 2 * np.pi - delta_theta)

    arc_length = radius * delta_theta    # arc length along the base circle
    delta_z = abs(p[2] - q[2])

    return float(np.sqrt(arc_length**2 + delta_z**2))


# ══════════════════════════════════════════════════════════════════════════════
# CIRCLE GEODESIC (arc length)
# ══════════════════════════════════════════════════════════════════════════════

def circle_arc_length(p: np.ndarray, q: np.ndarray, radius: float = 1.0) -> float:
    """
    Compute the shorter arc length between two points on a circle.

    The intrinsic distance on a circle is:
        d_arc = r · |Δθ_min|

    Parameters
    ----------
    p, q   : np.ndarray, shape (3,)  – points on the circle (z ignored)
    radius : float

    Returns
    -------
    float – arc length ≥ 0
    """
    p, q = _validate_pair(p, q)
    theta_p = np.arctan2(p[1], p[0])
    theta_q = np.arctan2(q[1], q[0])

    delta_theta = abs(theta_p - theta_q)
    delta_theta = min(delta_theta, 2 * np.pi - delta_theta)

    return float(radius * delta_theta)


# ══════════════════════════════════════════════════════════════════════════════
# DISTORTION METRICS
# ══════════════════════════════════════════════════════════════════════════════

def distance_distortion(d_before: float, d_after: float) -> dict:
    """
    Quantify how a mapping changed the distance between two points.

    Parameters
    ----------
    d_before : float  – distance before the mapping (must be ≥ 0)
    d_after  : float  – distance after the mapping  (must be ≥ 0)

    Returns
    -------
    dict with keys:
        'absolute_change' : |d_after - d_before|
        'relative_change' : |d_after - d_before| / d_before  (or None if d_before ≈ 0)
        'ratio'           : d_after / d_before               (or None if d_before ≈ 0)
        'preserved'       : bool – True if change < 1e-9
    """
    if d_before < 0 or d_after < 0:
        raise ValueError("Distances must be non-negative.")

    absolute_change = abs(d_after - d_before)
    preserved = absolute_change < 1e-9

    if d_before > 1e-12:
        relative_change = absolute_change / d_before
        ratio = d_after / d_before
    else:
        relative_change = None
        ratio = None

    return {
        "absolute_change": round(absolute_change, DISTANCE_DECIMAL_PLACES),
        "relative_change": (
            round(relative_change, DISTANCE_DECIMAL_PLACES)
            if relative_change is not None else None
        ),
        "ratio": round(ratio, DISTANCE_DECIMAL_PLACES) if ratio is not None else None,
        "preserved": preserved,
    }


def analyse_mapping_distances(point_a_original: np.ndarray,
                               point_b_original: np.ndarray,
                               point_a_mapped: np.ndarray,
                               point_b_mapped: np.ndarray) -> dict:
    """
    Full distance analysis before and after a mapping.

    Parameters
    ----------
    point_a_original, point_b_original : np.ndarray, shape (3,)
        Two points on the *source* surface.
    point_a_mapped, point_b_mapped : np.ndarray, shape (3,)
        Their images on the *target* surface.

    Returns
    -------
    dict with detailed distance information.
    """
    d_before = euclidean_distance(point_a_original, point_b_original)
    d_after = euclidean_distance(point_a_mapped, point_b_mapped)
    distortion = distance_distortion(d_before, d_after)

    return {
        "point_a_original": point_a_original.tolist(),
        "point_b_original": point_b_original.tolist(),
        "point_a_mapped": point_a_mapped.tolist(),
        "point_b_mapped": point_b_mapped.tolist(),
        "d_before": round(d_before, DISTANCE_DECIMAL_PLACES),
        "d_after": round(d_after, DISTANCE_DECIMAL_PLACES),
        **distortion,
    }


# ══════════════════════════════════════════════════════════════════════════════
# PRIVATE HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _validate_pair(p, q):
    """Convert p, q to float arrays and verify they have exactly 3 elements."""
    p = np.asarray(p, dtype=float)
    q = np.asarray(q, dtype=float)
    for name, arr in [("p", p), ("q", q)]:
        if arr.shape != (3,):
            raise ValueError(
                f"Expected point '{name}' to have shape (3,), got {arr.shape}."
            )
    return p, q
