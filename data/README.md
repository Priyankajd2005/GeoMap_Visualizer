# data/README.md

## Data Directory

This folder is reserved for any external datasets used by the project.

Currently, GeoMap Visualizer generates all sample data programmatically inside
`src/experiments.py` using a fixed random seed (see `config.py → EXPERIMENT_SEED`).
No external files are required to run the application or the tests.

If you add your own datasets in future, place them here and document their source
and licence in this file.
