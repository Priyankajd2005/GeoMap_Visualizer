"""
tests/test_mappings.py
----------------------
Unit tests for all mapping functions in src/mappings.py.

Run with:
    python -m pytest tests/test_mappings.py -v
"""

import numpy as np
import pytest

from src.mappings import (
    cylinder_to_circle,
    cylinder_to_circle_batch,
    plane_to_cylinder,
    plane_to_cylinder_batch,
    identity_map,
    get_mapping_info,
    _validate_point,
)


# ══════════════════════════════════════════════════════════════════════════════
# HELPER
# ══════════════════════════════════════════════════════════════════════════════

def assert_close(a, b, tol=1e-9):
    """Assert that two arrays are element-wise close."""
    np.testing.assert_allclose(a, b, atol=tol)


# ══════════════════════════════════════════════════════════════════════════════
# cylinder_to_circle
# ══════════════════════════════════════════════════════════════════════════════

class TestCylinderToCircle:
    """Tests for the cylinder → circle projection mapping."""

    def test_basic_output_shape(self):
        """Mapped point must have shape (3,)."""
        p = np.array([1.0, 0.0, 0.5])
        result = cylinder_to_circle(p, circle_radius=1.0)
        assert result.shape == (3,), f"Expected shape (3,), got {result.shape}"

    def test_z_is_zero(self):
        """The z-coordinate of the mapped point must always be 0."""
        for z in [0.0, 0.5, 1.0, 2.5]:
            p = np.array([1.0, 0.0, z])
            result = cylinder_to_circle(p, circle_radius=1.0)
            assert result[2] == pytest.approx(0.0, abs=1e-12), \
                f"z should be 0 but got {result[2]} for input z={z}"

    def test_positive_x_axis(self):
        """Point at (1, 0, z) should map to (r, 0, 0)."""
        p = np.array([1.0, 0.0, 0.3])
        result = cylinder_to_circle(p, circle_radius=2.0)
        assert_close(result, [2.0, 0.0, 0.0])

    def test_positive_y_axis(self):
        """Point at (0, 1, z) (angle = π/2) should map to (0, r, 0)."""
        p = np.array([0.0, 1.0, 1.0])
        result = cylinder_to_circle(p, circle_radius=1.0)
        assert_close(result, [0.0, 1.0, 0.0])

    def test_angle_preservation(self):
        """The angular coordinate θ must be preserved through the mapping."""
        theta = np.pi / 3   # 60 degrees
        r_cyl = 2.0
        r_circ = 1.5
        p = np.array([r_cyl * np.cos(theta), r_cyl * np.sin(theta), 0.8])
        result = cylinder_to_circle(p, circle_radius=r_circ)
        expected = np.array([r_circ * np.cos(theta), r_circ * np.sin(theta), 0.0])
        assert_close(result, expected)

    def test_height_independence(self):
        """Two points with the same angle but different heights must map identically."""
        theta = 1.2
        p1 = np.array([np.cos(theta), np.sin(theta), 0.1])
        p2 = np.array([np.cos(theta), np.sin(theta), 2.9])
        r1 = cylinder_to_circle(p1, circle_radius=1.0)
        r2 = cylinder_to_circle(p2, circle_radius=1.0)
        assert_close(r1, r2)

    def test_output_on_circle(self):
        """The mapped point must lie on a circle of the specified radius."""
        for theta in np.linspace(0, 2 * np.pi, 10, endpoint=False):
            p = np.array([np.cos(theta), np.sin(theta), 0.5])
            result = cylinder_to_circle(p, circle_radius=1.5)
            radius_out = np.sqrt(result[0] ** 2 + result[1] ** 2)
            assert radius_out == pytest.approx(1.5, abs=1e-9), \
                f"Mapped point not on circle: radius={radius_out}"

    def test_origin_raises(self):
        """(0, 0, z) has an undefined angle — must raise ValueError."""
        p = np.array([0.0, 0.0, 1.0])
        with pytest.raises(ValueError, match="origin"):
            cylinder_to_circle(p)

    def test_wrong_shape_raises(self):
        """A 2-element array must raise ValueError."""
        with pytest.raises(ValueError):
            cylinder_to_circle(np.array([1.0, 0.0]))

    def test_batch_matches_single(self):
        """Batch version must produce the same result as the single-point version."""
        points = np.array([
            [1.0, 0.0, 0.5],
            [0.0, 1.0, 1.0],
            [-1.0, 0.0, 0.2],
        ])
        batch_result = cylinder_to_circle_batch(points, circle_radius=1.0)
        for i, p in enumerate(points):
            single = cylinder_to_circle(p, circle_radius=1.0)
            assert_close(batch_result[i], single)


# ══════════════════════════════════════════════════════════════════════════════
# plane_to_cylinder
# ══════════════════════════════════════════════════════════════════════════════

class TestPlaneToCylinder:
    """Tests for the plane → cylinder wrapping mapping."""

    def test_basic_output_shape(self):
        """Mapped point must have shape (3,)."""
        p = np.array([0.0, 0.5, 0.0])
        result = plane_to_cylinder(p, radius=1.0, height=2.0)
        assert result.shape == (3,)

    def test_origin_maps_to_positive_x(self):
        """Plane origin (0, 0, 0) should map to (r, 0, 0) on cylinder."""
        p = np.array([0.0, 0.0, 0.0])
        result = plane_to_cylinder(p, radius=1.0, height=2.0)
        # θ = 0/r = 0  →  cos(0)=1, sin(0)=0
        assert_close(result, [1.0, 0.0, 0.0])

    def test_arc_length_preserved_along_x(self):
        """
        For two points with the same y-coordinate, the arc length along the
        cylinder base should equal |x2 - x1|.
        """
        r = 1.0
        p1 = np.array([0.0, 1.0, 0.0])
        p2 = np.array([1.0, 1.0, 0.0])
        q1 = plane_to_cylinder(p1, radius=r, height=3.0)
        q2 = plane_to_cylinder(p2, radius=r, height=3.0)

        theta1 = np.arctan2(q1[1], q1[0])
        theta2 = np.arctan2(q2[1], q2[0])
        arc = r * abs(theta2 - theta1)
        expected_arc = abs(p2[0] - p1[0])
        assert arc == pytest.approx(expected_arc, abs=1e-9), \
            f"Arc length {arc} ≠ expected {expected_arc}"

    def test_y_becomes_z(self):
        """The y-coordinate of the plane point should become z on the cylinder."""
        p = np.array([0.0, 1.3, 0.0])
        result = plane_to_cylinder(p, radius=1.0, height=5.0)
        assert result[2] == pytest.approx(1.3, abs=1e-9)

    def test_y_clamped_to_height(self):
        """y values beyond height must be clamped."""
        p = np.array([0.0, 10.0, 0.0])
        result = plane_to_cylinder(p, radius=1.0, height=2.0)
        assert result[2] == pytest.approx(2.0, abs=1e-9)

    def test_output_on_cylinder(self):
        """Mapped point must lie on the cylinder (x² + y² = r²)."""
        r = 1.5
        for x in [-2.0, -1.0, 0.0, 0.5, 1.5]:
            p = np.array([x, 0.5, 0.0])
            result = plane_to_cylinder(p, radius=r, height=3.0)
            r_out = np.sqrt(result[0] ** 2 + result[1] ** 2)
            assert r_out == pytest.approx(r, abs=1e-9), \
                f"Mapped point not on cylinder: radius={r_out}"

    def test_invalid_radius_raises(self):
        """Non-positive radius must raise ValueError."""
        p = np.array([0.0, 0.0, 0.0])
        with pytest.raises(ValueError, match="radius"):
            plane_to_cylinder(p, radius=0.0)

    def test_batch_matches_single(self):
        """Batch version must match single-point version for each point."""
        points = np.array([
            [0.0, 0.5, 0.0],
            [1.0, 1.0, 0.0],
            [-0.5, 0.2, 0.0],
        ])
        batch = plane_to_cylinder_batch(points, radius=1.0, height=2.0)
        for i, p in enumerate(points):
            single = plane_to_cylinder(p, radius=1.0, height=2.0)
            assert_close(batch[i], single)


# ══════════════════════════════════════════════════════════════════════════════
# identity_map
# ══════════════════════════════════════════════════════════════════════════════

class TestIdentityMap:
    """Tests for the identity mapping f(p) = p."""

    def test_returns_same_values(self):
        """Identity map must return the exact same coordinates."""
        p = np.array([1.5, -2.3, 0.7])
        result = identity_map(p)
        assert_close(result, p)

    def test_returns_copy_not_same_object(self):
        """Returned array must be a separate object (not the same reference)."""
        p = np.array([1.0, 2.0, 3.0])
        result = identity_map(p)
        assert result is not p

    def test_wrong_shape_raises(self):
        """A non-3-element array must raise ValueError."""
        with pytest.raises(ValueError):
            identity_map(np.array([1.0, 2.0]))


# ══════════════════════════════════════════════════════════════════════════════
# get_mapping_info
# ══════════════════════════════════════════════════════════════════════════════

class TestGetMappingInfo:
    """Tests for the mapping metadata helper."""

    @pytest.mark.parametrize("name", [
        "Cylinder → Circle",
        "Plane → Cylinder",
        "Identity (no change)",
    ])
    def test_known_mappings_return_dict(self, name):
        """All registered mapping names must return a dict."""
        info = get_mapping_info(name)
        assert isinstance(info, dict)

    def test_required_keys_present(self):
        """Each info dict must contain all required keys."""
        required_keys = {
            "function", "batch_function", "source", "target",
            "description", "preserves_distances", "lost_information", "formula",
        }
        for name in ["Cylinder → Circle", "Plane → Cylinder", "Identity (no change)"]:
            info = get_mapping_info(name)
            missing = required_keys - set(info.keys())
            assert not missing, f"Keys missing for '{name}': {missing}"

    def test_unknown_mapping_raises(self):
        """An unregistered name must raise KeyError."""
        with pytest.raises(KeyError):
            get_mapping_info("Sphere → Torus")

    def test_identity_is_marked_isometry(self):
        """The identity map must be flagged as preserving distances."""
        info = get_mapping_info("Identity (no change)")
        assert info["preserves_distances"] is True

    def test_cylinder_to_circle_not_isometry(self):
        """The cylinder → circle projection must NOT be flagged as an isometry."""
        info = get_mapping_info("Cylinder → Circle")
        assert info["preserves_distances"] is False


# ══════════════════════════════════════════════════════════════════════════════
# _validate_point (private helper)
# ══════════════════════════════════════════════════════════════════════════════

class TestValidatePoint:
    def test_valid_array_passes(self):
        """A (3,) array must not raise."""
        _validate_point(np.array([1.0, 2.0, 3.0]))

    def test_list_passes(self):
        """A plain Python list of length 3 must not raise."""
        _validate_point([1.0, 2.0, 3.0])

    def test_wrong_length_raises(self):
        """Arrays of length ≠ 3 must raise."""
        for bad in [[1.0, 2.0], [1.0, 2.0, 3.0, 4.0], []]:
            with pytest.raises(ValueError):
                _validate_point(np.array(bad))
