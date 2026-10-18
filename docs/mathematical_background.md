# Mathematical Background

## 1. What Is a Surface?

In mathematics, a **surface** is a 2-dimensional manifold — a shape that locally looks like a flat plane but may be curved globally.  Surfaces are usually described by a **parametrisation**: a function

$$\mathbf{r}: U \subseteq \mathbb{R}^2 \to \mathbb{R}^3, \quad \mathbf{r}(u, v) = (x(u,v),\, y(u,v),\, z(u,v))$$

that maps a 2-D parameter domain into 3-D space.

### Examples implemented in this project

| Surface | Parametrisation | Domain |
|---------|----------------|--------|
| Flat plane | $\mathbf{r}(x, y) = (x, y, 0)$ | $x, y \in [-L, L]$ |
| Cylinder (lateral surface) | $\mathbf{r}(\theta, z) = (r\cos\theta,\, r\sin\theta,\, z)$ | $\theta \in [0, 2\pi),\; z \in [0, h]$ |
| Circle (1-D curve) | $\mathbf{r}(\theta) = (r\cos\theta,\, r\sin\theta,\, 0)$ | $\theta \in [0, 2\pi)$ |

---

## 2. The Metric Tensor

The **first fundamental form** (or metric tensor) $g$ encodes how arc lengths are measured on a surface.  For a parametrisation $\mathbf{r}(u, v)$:

$$g_{ij} = \frac{\partial \mathbf{r}}{\partial u^i} \cdot \frac{\partial \mathbf{r}}{\partial u^j}$$

The infinitesimal arc length element is:

$$ds^2 = g_{11}\,du^2 + 2g_{12}\,du\,dv + g_{22}\,dv^2$$

### Metric of the cylinder

For $\mathbf{r}(\theta, z) = (r\cos\theta, r\sin\theta, z)$:

$$\frac{\partial \mathbf{r}}{\partial \theta} = (-r\sin\theta,\, r\cos\theta,\, 0), \qquad
  \frac{\partial \mathbf{r}}{\partial z} = (0,\, 0,\, 1)$$

$$g = \begin{pmatrix} r^2 & 0 \\ 0 & 1 \end{pmatrix}$$

So: $ds^2 = r^2 d\theta^2 + dz^2$.

### Metric of the flat plane

$$g = \begin{pmatrix} 1 & 0 \\ 0 & 1 \end{pmatrix}, \qquad ds^2 = dx^2 + dy^2$$

---

## 3. Geodesics

A **geodesic** is a curve on a surface that locally minimises arc length — the surface analogue of a straight line.

### Cylinder geodesic (unroll method)

A cylinder can be **unrolled** (developed) onto a flat rectangle without distortion.  Under this development:

$$\theta \mapsto s = r\theta \quad \text{(arc-length coordinate)}$$

The geodesic distance between $(\theta_1, z_1)$ and $(\theta_2, z_2)$ becomes the straight-line distance in the unrolled rectangle:

$$d_{\text{geo}} = \sqrt{(r\,\Delta\theta_{\min})^2 + (\Delta z)^2}$$

where $\Delta\theta_{\min} = \min(|\theta_2 - \theta_1|,\; 2\pi - |\theta_2 - \theta_1|)$.

### Circle arc length

The intrinsic distance between two points on a circle of radius $r$ is:

$$d_{\text{arc}} = r\,\Delta\theta_{\min}$$

---

## 4. Mappings Between Surfaces

A **smooth map** $f: S_1 \to S_2$ is a function between surfaces.  Key types:

| Type | Definition |
|------|-----------|
| **Continuous map** | $f$ is continuous |
| **Smooth map** | $f$ has continuous derivatives of all orders |
| **Homeomorphism** | bijective and bicontinuous — preserves topology |
| **Diffeomorphism** | bijective smooth map with smooth inverse |
| **Isometry** | distance-preserving: $d(f(p), f(q)) = d(p, q)$ for all $p, q$ |
| **Conformal map** | angle-preserving (but not necessarily distance-preserving) |

### Cylinder → Circle projection

$$f: \text{Cylinder} \to \text{Circle}, \quad
  f(r\cos\theta,\, r\sin\theta,\, z) = (r\cos\theta,\, r\sin\theta,\, 0)$$

- This map is **not injective** (many-to-one): all points at the same $\theta$ but different $z$ map to the same point.
- It is **not an isometry**: pairs with different $z$ but equal $\theta$ have distance compressed to 0.
- It is **not a diffeomorphism**: it has no inverse (information is lost).

### Plane → Cylinder wrapping

$$f: \text{Plane} \to \text{Cylinder}, \quad
  f(x, y, 0) = (r\cos(x/r),\, r\sin(x/r),\, y)$$

- This map **preserves arc lengths in the $x$ direction** (they become arc lengths along the cylinder's base circle).
- It is **not globally isometric**: distances in the $y$ direction are preserved, but diagonal distances are generally distorted relative to the original straight-line distance.
- It is a **local isometry** in the sense that the metric tensors are pulled back correctly: the development of a cylinder onto a plane is a classical example in differential geometry.

---

## 5. Ambient vs Intrinsic Distance

| Term | Meaning | Formula |
|------|---------|---------|
| **Ambient Euclidean** | Straight line through 3-D space | $d_E = \|\mathbf{p} - \mathbf{q}\|_2$ |
| **Intrinsic geodesic** | Shortest path *on the surface* | $d_{\text{geo}} = \int_\gamma ds$ |

For a flat plane these are equal.  For curved surfaces, $d_{\text{geo}} \geq d_E$ always.

---

## 6. Differential Geometry — Broader Context

This project implements toy examples of the following concepts from differential geometry:

- **Parametric surfaces and coordinate charts**
- **First fundamental form (Riemannian metric)**
- **Geodesics and intrinsic distance**
- **Smooth maps and their differential**
- **Isometries and distance distortion**

These concepts appear in:
- Riemannian Geometry (curvature, geodesics)
- General Relativity (spacetime as a 4-D Lorentzian manifold)
- Computer Graphics (UV-mapping, mesh parameterisation)
- Machine Learning (manifold learning, dimensionality reduction)
