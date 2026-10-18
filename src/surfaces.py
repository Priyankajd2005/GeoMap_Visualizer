"""
src/surfaces.py
---------------
Functions that generate coordinate grids and sample points for each surface.

Surfaces implemented
--------------------
1. Plane   – a flat rectangular region in the XY plane at z = 0
2. Cylinder – a right circular cylinder aligned along the Z axis
3. Circle  – a 1-D circle embedded in the XY plane at z = 0

All functions return NumPy arrays that can be passed directly to plotting
libraries (Matplotlib or Plotly).
"""

import numpy as np
from config import GRID_POINTS


# ══════════════════════════════════════════════════════════════════════════════
# 1. PLANE
# ══════════════════════════════════════════════════════════════════════════════

def generate_plane(half_size: float = 3.0, n: int = GRID_POINTS):
    """
    Generate a grid of points on a flat plane in the XY plane (z = 0).

    Parameters
    ----------
    half_size : float
        The plane extends from -half_size to +half_size in both X and Y.
    n : int
        Number of grid lines along each axis.

    Returns
    -------
    X, Y, Z : np.ndarray, shape (n, n)
        Meshgrid arrays suitable for surface plotting.
    """
    if half_size <= 0:
        raise ValueError(f"half_size must be positive, got {half_size}.")
    if n < 2:
        raise ValueError(f"n must be at least 2, got {n}.")

    x_vals = np.linspace(-half_size, half_size, n)
    y_vals = np.linspace(-half_size, half_size, n)
    X, Y = np.meshgrid(x_vals, y_vals)
    Z = np.zeros_like(X)   # the plane sits at z = 0
    return X, Y, Z


def sample_points_on_plane(half_size: float = 3.0, n: int = GRID_POINTS):
    """
    Return a flat list of (x, y, z=0) sample points on the plane.

    Parameters
    ----------
    half_size : float
        Same meaning as in generate_plane.
    n : int
        Total points = n × n.

    Returns
    -------
    points : np.ndarray, shape (n*n, 3)
    """
    X, Y, Z = generate_plane(half_size, n)
    points = np.column_stack([X.ravel(), Y.ravel(), Z.ravel()])
    return points


# ══════════════════════════════════════════════════════════════════════════════
# 2. CYLINDER
# ══════════════════════════════════════════════════════════════════════════════

def generate_cylinder(radius: float = 1.0, height: float = 2.0,
                      n_theta: int = GRID_POINTS, n_z: int = GRID_POINTS):
    """
    Generate a grid of points on the lateral surface of a cylinder.

    Parametric equations
    --------------------
        x(θ, z) = r · cos(θ)
        y(θ, z) = r · sin(θ)
        z(θ, z) = z

    where θ ∈ [0, 2π] and z ∈ [0, height].

    Parameters
    ----------
    radius : float  – radius of the cylinder (must be > 0)
    height : float  – height of the cylinder (must be > 0)
    n_theta : int   – grid resolution along θ
    n_z : int       – grid resolution along z

    Returns
    -------
    X, Y, Z : np.ndarray, shape (n_z, n_theta)
    """
    if radius <= 0:
        raise ValueError(f"radius must be positive, got {radius}.")
    if height <= 0:
        raise ValueError(f"height must be positive, got {height}.")

    theta = np.linspace(0, 2 * np.pi, n_theta)
    z_vals = np.linspace(0, height, n_z)
    Theta, Z = np.meshgrid(theta, z_vals)

    X = radius * np.cos(Theta)
    Y = radius * np.sin(Theta)
    return X, Y, Z


def sample_points_on_cylinder(radius: float = 1.0, height: float = 2.0,
                               n_theta: int = GRID_POINTS, n_z: int = GRID_POINTS):
    """
    Return a flat list of (x, y, z) sample points on the cylinder surface.

    Returns
    -------
    points : np.ndarray, shape (n_theta * n_z, 3)
    """
    X, Y, Z = generate_cylinder(radius, height, n_theta, n_z)
    points = np.column_stack([X.ravel(), Y.ravel(), Z.ravel()])
    return points


def cylinder_point_from_params(theta: float, z_frac: float,
                               radius: float = 1.0, height: float = 2.0):
    """
    Convert cylindrical parameters (θ, fractional height) to a 3-D point.

    Parameters
    ----------
    theta  : float  – angle in radians, will be wrapped to [0, 2π]
    z_frac : float  – height as a fraction of the full height, in [0, 1]
    radius : float
    height : float

    Returns
    -------
    point : np.ndarray, shape (3,)   → [x, y, z]
    """
    theta = theta % (2 * np.pi)
    z_frac = float(np.clip(z_frac, 0.0, 1.0))
    x = radius * np.cos(theta)
    y = radius * np.sin(theta)
    z = z_frac * height
    return np.array([x, y, z])


# ══════════════════════════════════════════════════════════════════════════════
# 3. CIRCLE
# ══════════════════════════════════════════════════════════════════════════════

def generate_circle(radius: float = 1.0, n: int = GRID_POINTS):
    """
    Generate points on a circle in the XY plane (z = 0).

    Parametric equations
    --------------------
        x(θ) = r · cos(θ)
        y(θ) = r · sin(θ)
        z(θ) = 0

    Parameters
    ----------
    radius : float – radius of the circle (must be > 0)
    n      : int   – number of sample points around the circle

    Returns
    -------
    x, y, z : np.ndarray, shape (n,)
    """
    if radius <= 0:
        raise ValueError(f"radius must be positive, got {radius}.")

    theta = np.linspace(0, 2 * np.pi, n)
    x = radius * np.cos(theta)
    y = radius * np.sin(theta)
    z = np.zeros(n)
    return x, y, z


def circle_point_from_theta(theta: float, radius: float = 1.0):
    """
    Return the 3-D position on a circle for a given angle θ.

    Parameters
    ----------
    theta  : float – angle in radians
    radius : float

    Returns
    -------
    point : np.ndarray, shape (3,)   → [x, y, 0]
    """
    x = radius * np.cos(theta)
    y = radius * np.sin(theta)
    return np.array([x, y, 0.0])
