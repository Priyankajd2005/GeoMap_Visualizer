# GeoMap Visualizer 🗺️

**Interactive Geometric Mapping and Distance Analysis**

> An educational, interactive web application that visualises mappings between geometric surfaces and analyses how those mappings distort distances — an introductory computational exploration of Differential Geometry concepts.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Features](#2-features)
3. [Folder Structure](#3-folder-structure)
4. [Mathematical Concepts](#4-mathematical-concepts)
5. [Installation (Windows)](#5-installation-windows)
6. [Running the Application](#6-running-the-application)
7. [Running Tests](#7-running-tests)
8. [Expected Behaviour](#8-expected-behaviour)
9. [Limitations and Future Improvements](#9-limitations-and-future-improvements)
10. [Uploading to GitHub](#10-uploading-to-github)
11. [VS Code Quick-Start](#11-vs-code-quick-start)

---

## 1. Project Overview

GeoMap Visualizer lets you:

- **Visualise** a flat plane, a cylinder, and a circle as interactive 3-D surfaces.
- **Map** points from one surface to another using mathematically defined functions.
- **Measure** how Euclidean distances change (or fail to be preserved) through a mapping.
- **Experiment** with multiple point pairs and see distortion statistics in a table and chart.
- **Learn** the underlying mathematics through a built-in educational section.

This project is aimed at second-year B.Tech Computer Science students and provides a hands-on introduction to ideas from Differential Geometry and Riemannian Geometry.

---

## 2. Features

| # | Feature | Description |
|---|---------|-------------|
| 1 | Surface Visualisation | Plane, cylinder, and circle rendered as 3-D Plotly figures |
| 2 | Geometric Mapping | Cylinder → circle mapping shown with connecting lines |
| 3 | Distance Analysis | Euclidean distances before/after mapping, with delta table |
| 4 | Interactive Dashboard | Streamlit sidebar with dropdowns and sliders |
| 5 | Educational Section | Plain-English explanations and key equations |
| 6 | Research Experiment | Deterministic multi-pair distance comparison with chart |
| 7 | Unit Tests | pytest suite for mapping functions and distance utilities |

---

## 3. Folder Structure

```
GeoMap_Visualizer/
├── app.py                   # Streamlit entry point
├── config.py                # Central configuration constants
├── requirements.txt         # Pinned dependencies
├── README.md                # This file
├── .gitignore
│
├── src/
│   ├── __init__.py
│   ├── surfaces.py          # Surface geometry generators
│   ├── mappings.py          # Mapping functions between surfaces
│   ├── distance_analysis.py # Distance calculation helpers
│   └── experiments.py       # Reproducible multi-pair experiment
│
├── components/
│   ├── __init__.py
│   ├── plots.py             # Plotly figure builders
│   └── metrics.py           # Streamlit metric / table rendering
│
├── tests/
│   ├── test_mappings.py
│   └── test_distance_analysis.py
│
├── docs/
│   ├── mathematical_background.md
│   ├── methodology.md
│   └── limitations.md
│
├── data/
│   └── README.md
│
└── outputs/
    └── .gitkeep
```

---

## 4. Mathematical Concepts

| Term | Plain explanation |
|------|------------------|
| **Surface** | A 2-D shape embedded in 3-D space (e.g. a cylinder, a sphere) |
| **Mapping / Map** | A function f: S₁ → S₂ that sends every point on surface S₁ to a point on S₂ |
| **Euclidean distance** | Straight-line distance through 3-D space: d = √((x₂−x₁)²+(y₂−y₁)²+(z₂−z₁)²) |
| **Intrinsic distance** | Shortest path *along the surface* between two points |
| **Isometry** | A distance-preserving map where d(f(p),f(q)) = d(p,q) for every pair |
| **Projection** | A mapping that reduces dimension (e.g. cylinder → circle) — generally *not* an isometry |

---

## 5. Installation (Windows)

> **Prerequisites**: Python 3.11 (or 3.10+) installed and added to `PATH`.

### Step-by-step

```powershell
# 1 – Navigate to the project folder
cd path\to\GeoMap_Visualizer

# 2 – Create a virtual environment
python -m venv .venv

# 3 – Activate it
.venv\Scripts\activate

# 4 – Upgrade pip (recommended)
python -m pip install --upgrade pip

# 5 – Install dependencies
python -m pip install -r requirements.txt
```

You should see all packages installed without errors.

---

## 6. Running the Application

```powershell
# Make sure the virtual environment is active
.venv\Scripts\activate

streamlit run app.py
```

Streamlit will print a local URL such as `http://localhost:8501`. Open it in your browser.

---

## 7. Running Tests

```powershell
# From the project root (virtual env active)
python -m pytest
```

All tests are in the `tests/` folder and run automatically. Expect output like:

```
collected 12 items
...........
12 passed in 0.45s
```

---

## 8. Expected Behaviour

1. The sidebar lets you choose a **surface** and a **mapping**.
2. A 3-D plot of the selected surface appears in the main panel.
3. Move the **Point A** and **Point B** sliders to place two points on the surface.
4. The app shows:
   - Euclidean distance on the original surface
   - Euclidean distance on the mapped surface
   - Difference (distortion)
5. The **Research Experiment** tab runs a fixed 20-pair distance comparison and shows a chart.
6. The **Math Background** tab explains the concepts in plain English.

---

## 9. Limitations and Future Improvements

**Current limitations**

- Only three surfaces are implemented (plane, cylinder, circle).
- Only one mapping is implemented (cylinder → circle angular projection).
- Intrinsic geodesic distances are approximated numerically, not solved analytically for all surfaces.
- The app has not been scientifically peer-reviewed; it is an educational tool only.

**Future improvements**

- Add sphere, torus, and Möbius strip surfaces.
- Implement conformal and area-preserving maps.
- Compute exact geodesics using the `geomstats` library.
- Export results as CSV or PDF.

---

## 10. Uploading to GitHub

```powershell
# Initialise a local git repository
git init

# Stage all files
git add .

# First commit
git commit -m "Initial commit: GeoMap Visualizer v1.0"

# Create a new repository on github.com, then link it:
git remote add origin https://github.com/<your-username>/GeoMap_Visualizer.git

# Push
git branch -M main
git push -u origin main
```

Make sure `.gitignore` is present (it excludes `.venv/`, `__pycache__/`, and `outputs/`).

---

## 11. VS Code Quick-Start

1. Open VS Code → **File ▸ Open Folder** → select `GeoMap_Visualizer/`.
2. Open the integrated terminal (**Ctrl + `**).
3. Run the activation and startup commands from Section 5 and 6 above.
4. Install the recommended extensions: **Python**, **Pylance**, **Streamlit Snippets**.
5. Set the Python interpreter to `.venv\Scripts\python.exe` (**Ctrl+Shift+P → "Python: Select Interpreter"**).

---

*GeoMap Visualizer v1.0 — for educational purposes only.*
