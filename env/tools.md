# External programs (card T-W0.02)

Required versions are from PLAN.md §3.3. Fill in the installed version per laptop from
`env/machines/<laptop>.json` after running `python -m haps.io.envcheck --fluent`. A tool that is
not installed is written `not installed` with the reason; it is never left blank.

| Program | Used for (PLAN section) | Required | Laptop 1 (AR) | Laptop 2 | Variable | Official source |
|---|---|---|---|---|---|---|
| XFOIL | Airfoil polars, NeuralFoil check (§7.4, §12.5) | 6.99 | | | `HAPS_XFOIL` | web.mit.edu/drela/Public/web/xfoil |
| AVL | Trim, stability derivatives, modes (§7.8, §10.1) | 3.40 or later | | | `HAPS_AVL` | web.mit.edu/drela/Public/web/avl |
| OpenVSP (+ Python API, in `haps-vsp`, Python 3.13) | Parametric geometry, VSPAERO (§10.1, §12.7) | 3.56.0 (Python3.13 build) | | | `HAPS_VSP_PYTHON` | openvsp.org |
| ANSYS Fluent | L2 RANS, E387 validation (§10.2) | record release | | | `HAPS_FLUENT` | university licence |
| ANSYS Mechanical | L2 FEA (§10.3) | record release | | | — | university licence |
| VORLAX | Non-planar VLM check (§12.5) | record | | | — | NASA (source to record) |
| XFLR5 / flow5 | Manual cross-checks (§12.5) | record | | | — | xflr5.tech |
| OpenFOAM | Independent CFD code check (§10.2) | v2406+ or .org 12 | | | — | openfoam.com / openfoam.org |
| Tecplot | Post-processing (§12.5) | record | | | — | university licence |
| SolidWorks | Detail CAD after G3 (§12.7) | record | | | — | university licence |
| nTop | Optional lattice parts (§12.7) | record | | | — | educational licence |
| ArduPilot SITL | Needed after G3 (P9) | — | | | — | ardupilot.org |

Machine notes (CPU, RAM, GPU, OS) go in the JSON reports; do not repeat them here.
