"""
config.py
---------
Central configuration for GeoMap Visualizer.
Stores default values used by the surfaces, mappings, and UI.
"""

# ── Surface grid resolution ───────────────────────────────────────────────────
GRID_POINTS = 40          # number of sample points along each axis
CYLINDER_RADIUS_DEFAULT = 1.0
CYLINDER_HEIGHT_DEFAULT = 2.0
PLANE_SIZE_DEFAULT = 3.0  # half-width of the square plane
CIRCLE_RADIUS_DEFAULT = 1.0

# ── Distance analysis ─────────────────────────────────────────────────────────
DISTANCE_DECIMAL_PLACES = 6

# ── Experiment settings ───────────────────────────────────────────────────────
EXPERIMENT_SEED = 42      # fixed seed → reproducible results
EXPERIMENT_N_PAIRS = 20   # number of point pairs to sample

# ── Plot appearance ───────────────────────────────────────────────────────────
SURFACE_ALPHA = 0.35
SURFACE_COLOR = "royalblue"
POINT_COLOR_A = "red"
POINT_COLOR_B = "green"
MAPPED_POINT_COLOR_A = "darkred"
MAPPED_POINT_COLOR_B = "darkgreen"
LINE_COLOR = "orange"

# ── Application metadata ──────────────────────────────────────────────────────
APP_TITLE = "GeoMap Visualizer"
APP_SUBTITLE = "Interactive Geometric Mapping & Distance Analysis"
APP_VERSION = "1.0.0"
