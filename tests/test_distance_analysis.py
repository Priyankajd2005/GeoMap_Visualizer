"""
tests/test_distance_analysis.py
--------------------------------
Unit tests for src/distance_analysis.py.

Run with:
    python -m pytest tests/test_distance_analysis.py -v
"""

import numpy as np
import pytest

from src.distance_analysis import (
    euclidean_distance,
    euclidean_distance_rounded,
    cylinder_geodesic_distance,
    circle_arc_length,
    distance_distortion,
    analyse_mapping_distances,
    _validate_pair,
)


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def assert_close(a, b, tol=1e-9):
    assert abs(a - b) < tol, f"{a} is not close to {b} (tol={tol})"


# ══════════════════════════════════════════════════════════════════════════════
# euclidean_distance
# ══════════════════════════════════════════════════════════════════════════════

class TestEuclideanDistance:

    def test_same_point_is_zero(self):
        """Distance from a point to itself must be 0."""
        p = np.array([1.0, 2.0, 3.0])
        assert euclidean_distance(p, p) == pytest.approx(0.0, abs=1e-12)

    def test_symmetry(self):
        """d(p, q) must equal d(q, p)."""
        p = np.array([1.0, 0.0, 0.0])
        q = np.array([0.0, 1.0, 0.0])
        assert euclidean_distance(p, q) == pytest.approx(euclidean_distance(q, p))

    def test_unit_vectors_along_axes(self):
        """Distance between (1,0,0) and (0,1,0) = sqrt(2)."""
        p = np.array([1.0, 0.0, 0.0])
        q = np.array([0.0, 1.0, 0.0])
        assert euclidean_distance(p, q) == pytest.approx(np.sqrt(2), abs=1e-9)

    def test_known_3d_distance(self):
        """d((0,0,0), (1,2,2)) = 3."""
        p = np.array([0.0, 0.0, 0.0])
        q = np.array([1.0, 2.0, 2.0])
        assert euclidean_distance(p, q) == pytest.approx(3.0, abs=1e-9)

    def test_non_negative(self):
        """Distance must always be ≥ 0."""
        rng = np.random.default_rng(0)
        for _ in range(20):
            p = rng.uniform(-5, 5, size=3)
            q = rng.uniform(-5, 5, size=3)
            assert euclidean_distance(p, q) >= 0.0

    def test_triangle_inequality(self):
        """d(p, r) ≤ d(p, q) + d(q, r) for all points."""
        rng = np.random.default_rng(1)
        for _ in range(20):
            p = rng.uniform(-3, 3, size=3)
            q = rng.uniform(-3, 3, size=3)
            r = rng.uniform(-3, 3, size=3)
            assert euclidean_distance(p, r) <= euclidean_distance(p, q) + euclidean_distance(q, r) + 1e-10

    def test_wrong_shape_raises(self):
        """Points with shape ≠ (3,) must raise ValueError."""
        p = np.array([1.0, 2.0])
        q = np.array([1.0, 2.0, 3.0])
        with pytest.raises(ValueError):
            euclidean_distance(p, q)

    def test_list_input_accepted(self):
        """Plain Python lists must be accepted."""
        d = euclidean_distance([0.0, 0.0, 0.0], [3.0, 4.0, 0.0])
        assert d == pytest.approx(5.0, abs=1e-9)

    def test_returns_float(self):
        """Return type must be float (or float-like scalar)."""
        d = euclidean_distance(np.array([0.0, 0.0, 0.0]), np.array([1.0, 0.0, 0.0]))
        assert isinstance(d, float)


class TestEuclideanDistanceRounded:

    def test_rounding(self):
        """Result should be rounded to the specified number of decimal places."""
        p = np.array([0.0, 0.0, 0.0])
        q = np.array([1.0, 0.0, 0.0])
        result = euclidean_distance_rounded(p, q, decimals=3)
        assert result == round(1.0, 3)

    def test_default_decimals(self):
        """Default rounding should match DISTANCE_DECIMAL_PLACES."""
        from config import DISTANCE_DECIMAL_PLACES
        p = np.array([0.0, 0.0, 0.0])
        q = np.array([1.0, 0.0, 0.0])
        result = euclidean_distance_rounded(p, q)
        assert result == round(1.0, DISTANCE_DECIMAL_PLACES)


# ══════════════════════════════════════════════════════════════════════════════
# cylinder_geodesic_distance
# ══════════════════════════════════════════════════════════════════════════════

class TestCylinderGeodesicDistance:

    def test_same_point_is_zero(self):
        """Geodesic from a point to itself must be 0."""
        p = np.array([1.0, 0.0, 0.5])
        assert cylinder_geodesic_distance(p, p, radius=1.0) == pytest.approx(0.0, abs=1e-9)

    def test_vertical_path(self):
        """Two points at the same angle, different heights → geodesic = |Δz|."""
        r = 1.0
        p = np.array([r, 0.0, 0.0])
        q = np.array([r, 0.0, 1.5])
        assert cylinder_geodesic_distance(p, q, radius=r) == pytest.approx(1.5, abs=1e-9)

    def test_horizontal_arc(self):
        """Two points at the same height, different angles → geodesic = r·|Δθ|."""
        r = 2.0
        theta_diff = np.pi / 4   # 45 degrees
        p = np.array([r, 0.0, 1.0])
        q = np.array([r * np.cos(theta_diff), r * np.sin(theta_diff), 1.0])
        expected_arc = r * theta_diff
        result = cylinder_geodesic_distance(p, q, radius=r)
        assert result == pytest.approx(expected_arc, abs=1e-9)

    def test_geodesic_ge_euclidean(self):
        """Geodesic distance must always be ≥ Euclidean distance."""
        rng = np.random.default_rng(42)
        r = 1.0
        for _ in range(20):
            theta_a = rng.uniform(0, 2 * np.pi)
            theta_b = rng.uniform(0, 2 * np.pi)
            z_a = rng.uniform(0, 2)
            z_b = rng.uniform(0, 2)
            p = np.array([r * np.cos(theta_a), r * np.sin(theta_a), z_a])
            q = np.array([r * np.cos(theta_b), r * np.sin(theta_b), z_b])
            geo = cylinder_geodesic_distance(p, q, radius=r)
            eucl = euclidean_distance(p, q)
            assert geo >= eucl - 1e-10, \
                f"Geodesic {geo} < Euclidean {eucl}"

    def test_invalid_radius_raises(self):
        """Non-positive radius must raise ValueError."""
        p = np.array([1.0, 0.0, 0.0])
        q = np.array([0.0, 1.0, 0.0])
        with pytest.raises(ValueError, match="radius"):
            cylinder_geodesic_distance(p, q, radius=0.0)

    def test_symmetry(self):
        """Geodesic distance must be symmetric."""
        p = np.array([1.0, 0.0, 0.0])
        q = np.array([0.0, 1.0, 1.0])
        d_pq = cylinder_geodesic_distance(p, q, radius=1.0)
        d_qp = cylinder_geodesic_distance(q, p, radius=1.0)
        assert d_pq == pytest.approx(d_qp, abs=1e-9)


# ══════════════════════════════════════════════════════════════════════════════
# circle_arc_length
# ══════════════════════════════════════════════════════════════════════════════

class TestCircleArcLength:

    def test_same_point_is_zero(self):
        p = np.array([1.0, 0.0, 0.0])
        assert circle_arc_length(p, p, radius=1.0) == pytest.approx(0.0, abs=1e-9)

    def test_quarter_circle(self):
        """Arc from (1,0,0) to (0,1,0) on unit circle = π/2."""
        p = np.array([1.0, 0.0, 0.0])
        q = np.array([0.0, 1.0, 0.0])
        assert circle_arc_length(p, q, radius=1.0) == pytest.approx(np.pi / 2, abs=1e-9)

    def test_half_circle(self):
        """Arc from (1,0,0) to (-1,0,0) = π (shorter arc)."""
        p = np.array([1.0, 0.0, 0.0])
        q = np.array([-1.0, 0.0, 0.0])
        assert circle_arc_length(p, q, radius=1.0) == pytest.approx(np.pi, abs=1e-9)

    def test_arc_ge_euclidean(self):
        """Arc length ≥ chord (Euclidean) length for any two points on a circle."""
        r = 1.5
        for theta in np.linspace(0.1, np.pi, 10):
            p = np.array([r, 0.0, 0.0])
            q = np.array([r * np.cos(theta), r * np.sin(theta), 0.0])
            arc = circle_arc_length(p, q, radius=r)
            chord = euclidean_distance(p, q)
            assert arc >= chord - 1e-10, f"arc {arc} < chord {chord} at theta={theta}"

    def test_symmetry(self):
        """arc(p, q) == arc(q, p)."""
        p = np.array([1.0, 0.0, 0.0])
        q = np.array([0.0, 1.0, 0.0])
        assert circle_arc_length(p, q) == pytest.approx(circle_arc_length(q, p))

    def test_scaled_by_radius(self):
        """Arc length scales linearly with radius."""
        p = np.array([1.0, 0.0, 0.0])
        q = np.array([0.0, 1.0, 0.0])
        arc1 = circle_arc_length(p / 1, q / 1, radius=1.0)
        # Re-scale points to radius 3.0
        p3 = np.array([3.0, 0.0, 0.0])
        q3 = np.array([0.0, 3.0, 0.0])
        arc3 = circle_arc_length(p3, q3, radius=3.0)
        assert arc3 == pytest.approx(3 * arc1, abs=1e-9)


# ══════════════════════════════════════════════════════════════════════════════
# distance_distortion
# ══════════════════════════════════════════════════════════════════════════════

class TestDistanceDistortion:

    def test_preserved_when_equal(self):
        """If d_before == d_after the mapping is considered to preserve distance."""
        result = distance_distortion(1.0, 1.0)
        assert result["preserved"] is True
        assert result["absolute_change"] == pytest.approx(0.0, abs=1e-9)

    def test_not_preserved_when_different(self):
        result = distance_distortion(1.0, 2.0)
        assert result["preserved"] is False

    def test_absolute_change(self):
        result = distance_distortion(3.0, 1.0)
        assert result["absolute_change"] == pytest.approx(2.0, abs=1e-9)

    def test_relative_change(self):
        result = distance_distortion(4.0, 2.0)
        assert result["relative_change"] == pytest.approx(0.5, abs=1e-9)

    def test_ratio(self):
        result = distance_distortion(2.0, 1.0)
        assert result["ratio"] == pytest.approx(0.5, abs=1e-9)

    def test_none_when_before_zero(self):
        """relative_change and ratio must be None when d_before ≈ 0."""
        result = distance_distortion(0.0, 1.0)
        assert result["relative_change"] is None
        assert result["ratio"] is None

    def test_negative_distances_raise(self):
        with pytest.raises(ValueError):
            distance_distortion(-1.0, 1.0)
        with pytest.raises(ValueError):
            distance_distortion(1.0, -1.0)

    def test_returns_dict_with_required_keys(self):
        result = distance_distortion(1.0, 1.5)
        for key in ["absolute_change", "relative_change", "ratio", "preserved"]:
            assert key in result


# ══════════════════════════════════════════════════════════════════════════════
# analyse_mapping_distances
# ══════════════════════════════════════════════════════════════════════════════

class TestAnalyseMappingDistances:

    def test_structure(self):
        """Return dict must contain all expected keys."""
        p_a = np.array([1.0, 0.0, 0.0])
        p_b = np.array([0.0, 1.0, 0.0])
        q_a = np.array([1.0, 0.0, 0.0])
        q_b = np.array([0.0, 1.0, 0.0])
        result = analyse_mapping_distances(p_a, p_b, q_a, q_b)
        for key in ["d_before", "d_after", "absolute_change", "preserved"]:
            assert key in result

    def test_identity_analysis_preserved(self):
        """Identity map must report preserved=True."""
        p_a = np.array([1.5, -0.5, 0.3])
        p_b = np.array([0.2, 0.8, 1.1])
        result = analyse_mapping_distances(p_a, p_b, p_a.copy(), p_b.copy())
        assert result["preserved"] is True
        assert result["absolute_change"] == pytest.approx(0.0, abs=1e-9)

    def test_different_points_gives_correct_distances(self):
        """Distances before and after must match direct euclidean_distance calls."""
        p_a = np.array([0.0, 0.0, 0.0])
        p_b = np.array([3.0, 4.0, 0.0])
        q_a = np.array([1.0, 0.0, 0.0])
        q_b = np.array([0.0, 1.0, 0.0])
        result = analyse_mapping_distances(p_a, p_b, q_a, q_b)
        assert result["d_before"] == pytest.approx(5.0, abs=1e-6)
        assert result["d_after"] == pytest.approx(np.sqrt(2), abs=1e-6)
