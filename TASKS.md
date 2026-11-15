# Task board

Single source of truth for task status. Full card details live in `cards/<ID>.md` (template: PLAN.md §3.5). Week, gate and acceptance details: PLAN.md §5–6.

**Status values:** `BLOCKED` (a dependency is not `VERIFIED`) · `READY` · `IN-PROGRESS` · `SUBMITTED` · `VERIFIED` · `REWORK` · `DESCOPED`
**Reviewers:** SU = Syed Shah Umer · AR = Ateeq-ur-Rehman · HA = Muhammad Hayat Arain · Team = all three (+ supervisor at gates)

**Rules**
- Change a status only in the same pull request that delivers the work, or when a dependency becomes `VERIFIED` (`BLOCKED` → `READY`).
- `VERIFIED` is set only by the named reviewer, with the date.
- Set-up exception (PLAN.md §3.4, W0 only, ends at G0 at the latest): the maintainer may merge set-up pull requests after CI passes; the named reviewer reviews them after the merge and only then sets `VERIFIED`.
- A card may run in paired mode (PLAN.md §3.7) before its dependencies are `VERIFIED`, but stays unverifiable until they are.
- Never delete a row. Descoped work is marked `DESCOPED` with the reason in its card.

Last updated: 15 Nov 2026

---

## Gates

| Gate | Meaning | Target date | Requires | Status | Signed (date) |
|---|---|---|---|---|---|
| G0 | Requirement register, weights and spaces defined | Thu 19 Nov | T-P0.01–05, T-P1.01–05, T-W0.04 | BLOCKED | |
| G1 | Models verified and validated | Thu 26 Nov | All T-P2, T-COST.02, T-CFD.02 | BLOCKED | |
| G2 | L1-verified shortlist with U1 robustness | Wed 2 Dec | T-P3.01–04, T-P4.01–05 | BLOCKED | |
| G3 | Configuration frozen | Thu 10 Dec (latest Sun 13 Dec) | T-P5, T-P6, T-FEA.01, T-P7.01–03 | BLOCKED | |

---

## W0 — Set-up (Thu 12 – Sun 15 Nov)

| ID | Title | Depends on | Rev | Status | Notes |
|---|---|---|---|---|---|
| T-W0.01 | Repository, folder skeleton, CI, branch protection | — | AR; SU (post-merge) | SUBMITTED | Merged under set-up exception (initial commit, PR #1). Branch protection on `main` set; approvals at 0 until G0 |
| T-W0.02 | Python 3.12 environment, lock file, external tools installed and versions recorded | T-W0.01 | AR; SU (post-merge) | IN-PROGRESS | PR #2 (environment file, smoke test, `.gitattributes`). To do: generate `env/conda-lock.yml`; smoke test passing on both laptops; `env/tools.md` filled |
| T-W0.03 | Agent operating brief (`AGENTS.md` and tool-specific files) | T-W0.01 | SU | SUBMITTED | PR #3; acceptance = dry run per agent (`cards/T-W0.03-dry-run.md`) |
| T-W0.04 | Pre-registration v0 (`acceptance/criteria.yaml`, tag `criteria-v0`) | T-W0.01 | SU | SUBMITTED | PR #4 (draft); open items listed in the PR; tag `criteria-v0` after approval |
| T-LIT.00 | Literature intake: drive reorganised, index/copies/leads/gaps run, duplicates decided, `library.bib` exported | T-W0.01 | SU (post-merge) | IN-PROGRESS | Tooling and rules: PR #1, merged under set-up exception. Intake runs still to do. See `literature/README.md` §1, §4, §8 |
| T-LIT.01 | Literature index and bibliography (complete `index.csv`, check relevant leads) | T-LIT.00 | AR | BLOCKED | |
| T-LIT.02 | Evidence-register extraction (ongoing, on demand per module) | T-LIT.01 | AR | BLOCKED | Runs through W4 |
| T-LIT.03 | AI-claimed gap verification (`gap_register.csv`) | T-LIT.01 | SU | BLOCKED | Before any gap is stated in a report; runs through W4 |
| T-REG.01 | Permission application status (NUST/CAA) | — | SU | READY | |
| T-REG.02 | Compute access request (NUST machines) and Flow360 credit check | — | SU | READY | |

## W1 — P0 requirements, P1 design space, P2 modules start (Mon 16 – Sun 22 Nov)

| ID | Title | Depends on | Rev | Status | Notes |
|---|---|---|---|---|---|
| T-P0.01 | Stakeholder needs and source mapping | T-W0.03, T-LIT.01 | SU | BLOCKED | |
| T-P0.02 | Requirement register | T-P0.01 | SU | BLOCKED | |
| T-P0.03 | AHP weights (CR < 0.10) | T-P0.02 | SU | BLOCKED | |
| T-P0.04 | Constraint forms and filter order (`criteria-v1`) | T-P0.02, T-W0.04 | SU | BLOCKED | |
| T-P0.05 | Traceability skeleton | T-P0.02, T-P1.01 | AR | BLOCKED | |
| T-P1.01 | Morphological matrix schema (both scales) | T-W0.02 | AR | BLOCKED | |
| T-P1.02 | Compatibility rules and admissible set (exhaustive enumeration) | T-P1.01 | SU | BLOCKED | |
| T-P1.03 | Continuous sampling (scrambled Sobol) | T-P1.01, T-P1.02 | AR | BLOCKED | |
| T-P1.04 | Parametric geometry generator (AeroSandbox + OpenVSP) | T-P1.01 | SU | BLOCKED | |
| T-P1.05 | FS ↔ DM linkage rules | T-P1.01, T-P0.02 | AR | BLOCKED | |
| T-P2.01 | Atmosphere (ISA 0–25 km) | T-W0.02 | AR | BLOCKED | Paired mode before G0 |
| T-P2.02 | Solar geometry | T-W0.02 | AR | BLOCKED | Paired mode before G0 |
| T-P2.03 | Pipeline A (equations only) | T-P2.02 | AR | BLOCKED | Paired mode before G0 |
| T-P2.04 | Pipeline B (NASA POWER, ERA5, MERRA-2) | T-W0.02 | AR | BLOCKED | Paired mode before G0 |
| T-P2.05 | PV and array model | T-P2.03 | HA | BLOCKED | Paired mode before G0 |
| T-COST.01 | Price-point collection | T-W0.01 | HA | BLOCKED | |
| T-CFD.01 | E387 validation case set-up (mesh family) | T-W0.02 | SU | BLOCKED | |
| T-HW.01 | Solar-cell incoming inspection procedure | T-W0.01 | HA | BLOCKED | Before cells arrive |

## W2 — P2 completed and validated (G1); P3 screening (Mon 23 – Sun 29 Nov)

| ID | Title | Depends on | Rev | Status | Notes |
|---|---|---|---|---|---|
| T-P2.06 | Airfoil module (NeuralFoil + XFOIL, E387 check) | T-W0.02 | SU | BLOCKED | |
| T-P2.07 | Span efficiency / induced drag (lifting line, VLM) | T-P1.04 | AR | BLOCKED | |
| T-P2.08 | Parasite drag build-up | T-P1.04, T-P2.06 | SU | BLOCKED | |
| T-P2.09 | Propulsion (propeller, motor, ESC) | T-W0.02 | SU | BLOCKED | |
| T-P2.10 | Mass model (physics-based + Noth cross-check) | T-P1.04, T-P2.11 | AR | BLOCKED | |
| T-P2.11 | Beam structural model | T-W0.02 | SU | BLOCKED | |
| T-P2.12 | Stability (neutral point, static margin, tail sizing) | T-P1.04 | SU | BLOCKED | |
| T-P2.13 | Energy balance (SoC time-stepping, closure, DM endurance) | T-P2.01, T-P2.03, T-P2.04, T-P2.05 | AR | BLOCKED | |
| T-P2.14 | Sizing loop (both scales, both pipelines) | T-P2.06–T-P2.13, G0 | AR | BLOCKED | Needs G0 |
| T-P2.15 | Validation runs, Tier A and Tier B (gate-critical) | T-P2.14 | AR + checker | BLOCKED | |
| T-P2.16 | Pipeline A vs B comparison | T-P2.14 | AR | BLOCKED | |
| T-COST.02 | Cost model v0 (CERs, landed cost) | T-COST.01 | HA | BLOCKED | |
| T-CFD.02 | E387 2D RANS validation with GCI; method freeze | T-CFD.01 | SU | BLOCKED | |
| T-HW.02 | Cell incoming inspection on arrival | T-HW.01 + cells delivered | HA | BLOCKED | Report problems within 14 days |
| T-HW.03 | Outdoor I–V tests, translated to STC | T-HW.02 | HA | BLOCKED | |
| T-P3.01 | L0 screening, full admissible matrix | G1 | AR | BLOCKED | |
| T-P3.02 | Uncertainty-aware screening with calibration sample | T-P3.01 | AR + checker | BLOCKED | |
| T-P3.03 | Compliance matrix and three-direction queries | T-P3.01 | AR | BLOCKED | |
| T-P3.04 | Surrogates and active learning on L0 data | T-P3.01 | AR | BLOCKED | |
| T-CFD.03 | Automated L2 production pipeline (dry run on C0) | T-CFD.02, T-P1.04 | SU | BLOCKED | |

## W3 — P4 shortlist (G2); P5 optimisation; P6 starts (Mon 30 Nov – Sun 6 Dec)

| ID | Title | Depends on | Rev | Status | Notes |
|---|---|---|---|---|---|
| T-P4.01 | L1 analysis of the retained set | T-P3.02 | SU | BLOCKED | |
| T-P4.02 | Co-kriging L0/L1 | T-P4.01, T-P3.04 | AR | BLOCKED | |
| T-P4.03 | Ranking: weighted sum, TOPSIS, Pareto, Kendall τ | T-P3.03, T-P4.01, T-P0.03 | AR | BLOCKED | |
| T-P4.04 | U1 robustness (gate-critical) | T-P4.03 | AR + checker | BLOCKED | |
| T-P4.05 | Shortlist decision | T-P4.04 | Team | BLOCKED | |
| T-P5.01 | Multi-objective optimisation (NSGA-II/III) | G2 | AR | BLOCKED | |
| T-P5.02 | GA/PSO cross-checks | T-P5.01 | AR | BLOCKED | |
| T-P5.03 | Aerostructural wing refinement (OpenAeroStruct) | G2 | SU | BLOCKED | |
| T-P5.04 | Bayesian optimisation to allocate L2 runs | T-P5.01, T-P4.02 | AR | BLOCKED | |
| T-P5.05 | U2 robustness (gate-critical) | T-P5.01 | AR + checker | BLOCKED | |
| T-P6.01 | L2 RANS production runs start | T-P5.04, T-CFD.03 | SU | BLOCKED | |
| T-FEA.01 | FEA set-up, static and modal | G2 | SU | BLOCKED | |

## W4 — P6 complete, P7 freeze (G3), mid-defence (Mon 7 – Sun 13 Dec)

| ID | Title | Depends on | Rev | Status | Notes |
|---|---|---|---|---|---|
| T-P6.02 | L2 aerodynamics on finalists and benchmarks | T-P6.01 | SU | BLOCKED | |
| T-P6.03 | One-way aero → structure load mapping | T-P6.02, T-FEA.01 | SU | BLOCKED | |
| T-P6.04 | Aeroelastic screening | T-FEA.01, T-P4.01 | SU | BLOCKED | |
| T-P6.05 | Re-rank on L2-updated performance | T-P6.02, T-P5.05 | AR + checker | BLOCKED | |
| T-P7.01 | Final selection and freeze record (`freeze.yaml`) | T-P6.03, T-P6.04, T-P6.05 | Team + supervisor | BLOCKED | |
| T-P7.02 | Detail CAD start and interface control document v1 | T-P7.01 | SU | BLOCKED | |
| T-P7.03 | Forward-dependency package for P8–P11 | T-P7.01 | Team | BLOCKED | |
| T-DOC.01 | Mid-defence deck and progress report form | T-P7.01 | Team | BLOCKED | Draft slides from W2 in paired mode |

---

## Change log

| Date | Change | By |
|---|---|---|
| 14 Nov 2026 | Board created from PLAN.md v1.1 | |
| 15 Nov 2026 | OR-Tools removed (DLL clash on Windows); T-P1.02 uses exhaustive enumeration, SciPy `milp` for integer choices (PLAN.md §8, §9, §12.2) | |
| 15 Nov 2026 | T-W0.01 → SUBMITTED; T-W0.02 → IN-PROGRESS (PR #2); T-W0.03 → SUBMITTED (PR #3); T-W0.04 → SUBMITTED (PR #4) | |
| 15 Nov 2026 | Set-up exception added (PLAN.md §3.4): maintainer merges W0 set-up PRs after CI; named reviewer reviews after merge, before G0 | |
| 15 Nov 2026 | Added T-LIT.00 (literature intake) and T-LIT.03 (gap verification); T-LIT.01 now depends on T-LIT.00 (PLAN.md v1.2) | |
