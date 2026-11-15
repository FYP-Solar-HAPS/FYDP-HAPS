# External programs (card T-W0.02)

Required versions are from PLAN.md §3.3. Fill in the installed version per laptop from
`env/machines/<laptop>.json` after running `python -m haps.io.envcheck --fluent`. A tool that is
not installed is written `not installed` with the reason; it is never left blank.

| Program | Used for (PLAN section) | Required | Laptop 1 (AR) | Laptop 2 | Variable | Official source |
|---|---|---|---|---|---|---|
| XFOIL | Airfoil polars, NeuralFoil check (§7.4, §12.5) | 6.99 | 6.99 ✓ | | `HAPS_XFOIL` | web.mit.edu/drela/Public/web/xfoil |
| AVL | Trim, stability derivatives, modes (§7.8, §10.1) | 3.40 or later | 3.52 ✓ | | `HAPS_AVL` | web.mit.edu/drela/Public/web/avl |
| OpenVSP (+ Python API, in `haps-vsp`, Python 3.13) | Parametric geometry, VSPAERO (§10.1, §12.7) | 3.56.0 (Python3.13 build) | 3.56.0 (Py 3.13 build) installed; API check fails: `haps-vsp` not set up (open) | | `HAPS_VSP_PYTHON` | openvsp.org |
| ANSYS Fluent | L2 RANS, E387 validation (§10.2) | record release | 2026 ✓ (batch start, licence) | | `HAPS_FLUENT` | university licence |
| ANSYS Mechanical | L2 FEA (§10.3) | record release | not checked | | — | university licence |
| VORLAX | Non-planar VLM check (§12.5) | record | not checked | | — | NASA (source to record) |
| XFLR5 / flow5 | Manual cross-checks (§12.5) | record | not checked | | — | xflr5.tech |
| OpenFOAM | Independent CFD code check (§10.2) | v2406+ or .org 12 | not checked | | — | openfoam.com / openfoam.org |
| Tecplot | Post-processing (§12.5) | record | not checked | | — | university licence |
| SolidWorks | Detail CAD after G3 (§12.7) | record | not checked | | — | university licence |
| nTop | Optional lattice parts (§12.7) | record | not checked | | — | educational licence |
| ArduPilot SITL | Needed after G3 (P9) | — | not checked | | — | ardupilot.org |

Laptop 1 = DESKTOP-LVTUQF4 (Windows 11, Python 3.12.16, CPU-only PyTorch), report `env/machines/DESKTOP-LVTUQF4.json` (15 Nov 2026): 38/39 checks pass.

Machine notes (CPU, RAM, GPU, OS) go in the JSON reports; do not repeat them here.
