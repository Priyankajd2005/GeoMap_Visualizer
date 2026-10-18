# Limitations

This document honestly states the assumptions and limitations of GeoMap
Visualizer so that users understand what the project does and does not claim.

---

## Mathematical Limitations

### 1. Simplified Geodesic Formulas

The **cylinder geodesic** is computed using the "unroll" formula:

$$d_{\text{geo}} = \sqrt{(r\,\Delta\theta)^2 + (\Delta z)^2}$$

This formula is **exact** only for geodesics that do not wind more than once
around the cylinder.  For very long paths that spiral around multiple times,
the true shortest geodesic would follow a shorter helical path, and this
formula would overestimate the distance.

### 2. Ambient Euclidean Distance Used for Comparison

The mapping distortion experiment compares **Euclidean (ambient)** distances,
not intrinsic geodesic distances.  A mapping that compresses Euclidean distance
does not necessarily distort geodesic distances proportionally.

### 3. Only Three Surfaces

Only the flat plane, right circular cylinder, and circle are implemented.
Curved surfaces such as the sphere, torus, and paraboloid are not included.

### 4. Only Two Non-Trivial Mappings

Only the cylinder → circle projection and the plane → cylinder wrapping are
implemented.  Conformal maps, area-preserving maps, and harmonic maps are
not included.

### 5. No Curvature Computation

The Gaussian curvature and mean curvature of the surfaces are not computed
or displayed.  These would be natural next steps in a more advanced project.

---

## Computational Limitations

### 6. Finite Grid Resolution

Surfaces are approximated by a finite grid (`GRID_POINTS = 40` by default).
Visual artefacts may appear at low resolutions.

### 7. No Symbolic Mathematics

All calculations are purely numerical.  No symbolic verification (e.g. via
SymPy) is performed.

### 8. No Geodesic ODE Solver

The geodesic equations (a system of second-order ODEs) are not solved numerically.
The intrinsic distances are approximated by closed-form expressions that are
valid only for the specific surfaces and paths described above.

---

## Educational Limitations

### 9. Not Scientifically Validated

This project has not been peer-reviewed or validated against published numerical
results.  It is intended as an educational illustration only.

### 10. No Novel Research

The experiments in this project replicate well-known mathematical facts
(e.g. that a projection from a cylinder to a circle is not an isometry) for
educational purposes.  They are presented as computational demonstrations, not
as new scientific discoveries.

### 11. Simplified Terminology

Some mathematical terms (e.g. "intrinsic distance", "geodesic") are used in
simplified forms appropriate for an undergraduate audience.  A graduate-level
treatment would require more rigour.

---

## Future Improvements

| Priority | Improvement |
|----------|-------------|
| High | Add sphere and torus surfaces |
| High | Use `geomstats` library for exact geodesic computation |
| Medium | Implement conformal and area-preserving maps |
| Medium | Add Gaussian curvature display |
| Low | Export experiment results to CSV/PDF |
| Low | Add an animation of the mapping being applied |
