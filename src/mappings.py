"""
src/mappings.py
---------------
Mathematically defined mappings between geometric surfaces.

A mapping f: S₁ → S₂ takes a point on surface S₁ and returns the
corresponding point on surface S₂.  These mappings are NOT guaranteed to
preserve distances (i.e. they are NOT necessarily isometries).

Mappings implemented
--------------------
1. cylinder_to_circle  – projects a cylinder point onto the unit circle
                         by dropping the z coordinate.
2. plane_to_cylinder   – wraps a horizontal strip of the plane around a
                         cylinder.
3. identity            – trivial map: every point maps to itself.

Each mapping function accepts and returns NumPy arrays of shape (3,).
A vectorised version that works on (N, 3) arrays is also provided.
"""

import numpy as np


# ══════════════════════════════════════════════════════════════════════════════
# 1. CYLINDER → CIRCLE
# ══════════════════════════════════════════════════════════════════════════════

def cylinder_to_circle(point: np.ndarray, circle_radius: float = 1.0) -> np.ndarray:
    """
    Map a point on a cylinder to a point on a circle by discarding z.

    The mapping is:
        f(x, y, z) = (r_c · cos(θ),  r_c · sin(θ),  0)

    where θ = atan2(y, x) is the angular coordinate of the input point
    and r_c is the target circle radius.

    Note: z-information is completely lost. This is a projection, not an
    isometry — distances are generally not preserved.

    Parameters
    ----------
    point : np.ndarray, shape (3,)
        A point [x, y, z] on the cylinder.
    circle_radius : float
        Radius of the target circle.

    Returns
    -------
    mapped : np.ndarray, shape (3,)
        The corresponding point on the circle.

    Raises
    ------
    ValueError  – if the point has (x, y) = (0, 0) (undefined angle).
    """
    _validate_point(point)
    x, y, _ = float(point[0]), float(point[1]), float(point[2])

    if x == 0.0 and y == 0.0:
        raise ValueError(
            "Cannot map the origin (x=0, y=0) — the angle θ is undefined."
        )

    theta = np.arctan2(y, x)                  # extract angle from xy-plane
    mapped_x = circle_radius * np.cos(theta)
    mapped_y = circle_radius * np.sin(theta)
    return np.array([mapped_x, mapped_y, 0.0])


def cylinder_to_circle_batch(points: np.ndarray,
                              circle_radius: float = 1.0) -> np.ndarray:
    """
    Vectorised version of cylinder_to_circle for an array of points.

    Parameters
    ----------
    points : np.ndarray, shape (N, 3)
    circle_radius : float

    Returns
    -------
    mapped : np.ndarray, shape (N, 3)
    """
    points = np.atleast_2d(points)
    x, y = points[:, 0], points[:, 1]
    theta = np.arctan2(y, x)
    mapped_x = circle_radius * np.cos(theta)
    mapped_y = circle_radius * np.sin(theta)
    mapped_z = np.zeros(len(points))
    return np.column_stack([mapped_x, mapped_y, mapped_z])


# ══════════════════════════════════════════════════════════════════════════════
# 2. PLANE → CYLINDER  (wrap the x-axis around the cylinder)
# ══════════════════════════════════════════════════════════════════════════════

def plane_to_cylinder(point: np.ndarray,
                      radius: float = 1.0,
                      height: float = 2.0) -> np.ndarray:
    """
    Map a point on the plane to a point on a cylinder.

    The mapping treats the x-coordinate of the plane as an arc-length along
    the cylinder's circumference, and the y-coordinate as height:

        θ = x / radius         (wrapping the x-axis around the circle)
        f(x, y, 0) = (r·cos(θ),  r·sin(θ),  y)

    y is clamped to [0, height].  This is NOT an isometry in general:
    while arc-lengths along the x direction ARE preserved, distances in
    mixed directions are distorted.

    Parameters
    ----------
    point         : np.ndarray, shape (3,)
    radius        : float  – cylinder radius (must be > 0)
    height        : float  – cylinder height (used only for clamping)

    Returns
    -------
    mapped : np.ndarray, shape (3,)
    """
    _validate_point(point)
    if radius <= 0:
        raise ValueError(f"radius must be positive, got {radius}.")

    x, y, _ = float(point[0]), float(point[1]), float(point[2])
    theta = x / radius                          # arc-length → angle
    mapped_x = radius * np.cos(theta)
    mapped_y = radius * np.sin(theta)
    mapped_z = float(np.clip(y, 0.0, height))   # clamp to cylinder height
    return np.array([mapped_x, mapped_y, mapped_z])


def plane_to_cylinder_batch(points: np.ndarray,
                             radius: float = 1.0,
                             height: float = 2.0) -> np.ndarray:
    """
    Vectorised version of plane_to_cylinder.

    Parameters
    ----------
    points : np.ndarray, shape (N, 3)

    Returns
    -------
    mapped : np.ndarray, shape (N, 3)
    """
    points = np.atleast_2d(points)
    x, y = points[:, 0], points[:, 1]
    theta = x / radius
    mapped_x = radius * np.cos(theta)
    mapped_y = radius * np.sin(theta)
    mapped_z = np.clip(y, 0.0, height)
    return np.column_stack([mapped_x, mapped_y, mapped_z])


# ══════════════════════════════════════════════════════════════════════════════
# 3. IDENTITY MAP
# ══════════════════════════════════════════════════════════════════════════════

def identity_map(point: np.ndarray) -> np.ndarray:
    """
    The trivial mapping f(p) = p (every point maps to itself).

    This is an isometry: d(f(p), f(q)) = d(p, q) for all p, q.

    Parameters
    ----------
    point : np.ndarray, shape (3,)

    Returns
    -------
    np.ndarray, shape (3,)   – a copy of the input point
    """
    _validate_point(point)
    return np.array(point, dtype=float)


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _validate_point(point):
    """Raise ValueError if `point` is not a 3-element array-like."""
    arr = np.asarray(point)
    if arr.shape != (3,):
        raise ValueError(
            f"Expected a point with exactly 3 coordinates, got shape {arr.shape}."
        )


def get_mapping_info(mapping_name: str) -> dict:
    """
    Return metadata about a named mapping.

    Parameters
    ----------
    mapping_name : str  – one of "Cylinder → Circle", "Plane → Cylinder",
                          "Identity (no change)"

    Returns
    -------
    dict with keys: 'function', 'source', 'target', 'description',
                    'preserves_distances', 'lost_information'
    """
    info = {
        "Cylinder → Circle": {
            "function": cylinder_to_circle,
            "batch_function": cylinder_to_circle_batch,
            "source": "Cylinder",
            "target": "Circle",
            "description": (
                "Projects each cylinder point onto the circle by extracting the "
                "angular coordinate θ = atan2(y, x) and ignoring z. "
                "The z-coordinate (height) is permanently lost."
            ),
            "preserves_distances": False,
            "lost_information": "Height (z coordinate) is discarded.",
            "formula": "f(x, y, z) = (r·cos(θ), r·sin(θ), 0)  where θ = atan2(y, x)",
        },
        "Plane → Cylinder": {
            "function": plane_to_cylinder,
            "batch_function": plane_to_cylinder_batch,
            "source": "Plane",
            "target": "Cylinder",
            "description": (
                "Wraps the plane around a cylinder by interpreting the x-coordinate "
                "as arc-length along the circumference. "
                "Arc-lengths in the pure x-direction are preserved, "
                "but diagonal distances are generally distorted."
            ),
            "preserves_distances": False,
            "lost_information": (
                "Straight-line distance is distorted for non-horizontal paths."
            ),
            "formula": "f(x, y, 0) = (r·cos(x/r), r·sin(x/r), y)",
        },
        "Identity (no change)": {
            "function": identity_map,
            "batch_function": lambda pts: pts,
            "source": "Any",
            "target": "Same",
            "description": (
                "The identity mapping sends every point to itself. "
                "It is a perfect isometry: all distances are preserved exactly."
            ),
            "preserves_distances": True,
            "lost_information": "None — this mapping loses no information.",
            "formula": "f(x, y, z) = (x, y, z)",
        },
    }

    if mapping_name not in info:
        raise KeyError(
            f"Unknown mapping '{mapping_name}'. "
            f"Available: {list(info.keys())}"
        )
    return info[mapping_name]
