# fydp-haps

**Modular Solar-Electric UAV for Emergency Telecommunications: A Low-Altitude Proof-of-Concept for Energy-Optimised, Multi-Payload HALE Platforms**

Final Year Design Project, Department of Aerospace Engineering, School of Mechanical and Manufacturing Engineering (SMME), National University of Sciences and Technology (NUST), Islamabad.

| Role | Name |
|---|---|
| Team lead | Syed Shah Umer |
| Team member | Ateeq-ur-Rehman |
| Team member | Muhammad Hayat Arain |
| Supervisor | Mr. Aun Haider, Lecturer, NUST SMME |

This repository is private. It holds all code, data summaries, requirements, analyses, reports and task records for the project. It is a purely academic project.

---

## 1. What the project does

The project designs two linked aircraft:

- **Full scale (FS):** a solar-electric high-altitude platform at 20 km over Islamabad. It is analysed only, never built.
- **Demonstrator (DM):** a low-altitude solar-electric aircraft (under 10 kg, at or below 1,000 ft AGL, visual line of sight) that is built, instrumented, ground-tested and flown in February–April 2027.

The design is chosen by exploring linked requirement, design and cost spaces with models of increasing fidelity (L0 analytic → L1 panel/VLM → L2 CFD/FEA). It is verified and validated against published data and our own measurements, and carries uncertainty at every step. Demonstrator measurements then feed back into the full-scale prediction.

The full method and schedule are in **[PLAN.md](PLAN.md)**. The live task board is **[TASKS.md](TASKS.md)**.

---

## 2. Current phase

| Item | Status |
|---|---|
| Phase | W0 set-up (12–15 Nov 2026) |
| Next gate | G0: requirement register and spaces defined (target Thu 19 Nov 2026) |
| Configuration freeze (G3) | Target Thu 10 Dec 2026, latest Sun 13 Dec 2026 |
| Mid-defence | Date to be announced (expected 14–23 Dec 2026) |

Update this table at every gate.

---

## 3. Repository map

| Folder | Contents |
|---|---|
| `acceptance/` | `criteria.yaml`: every pass rule and tolerance, registered **before** the run it judges |
| `cards/` | One Markdown file per task card (template in PLAN.md §3.5) |
| `requirements/` | Stakeholder needs, requirement register, AHP weights, constraints, traceability matrix |
| `src/haps/` | The Python package: atmosphere, solar, PV, aerodynamics, propulsion, mass, structures, energy, stability, cost, design space, evaluation, optimisation, uncertainty, input/output |
| `tests/` | Automated tests: unit, limiting-case, regression and validation |
| `data/raw/` | Downloaded or measured data, never edited by hand |
| `data/external/` | Published datasets used for validation (Sky-Sailor, AtlantikSolar, Selig, NASA TM-4062), each with a source note |
| `data/processed/` | Data derived by scripts, with the script that made it |
| `literature/` | Reading rules (`README.md`, binding for people and agents), `SOURCES_INDEX.md`, `index.csv`, `library.bib`, text copies of AI files, `ai_leads.csv`, `gap_register.csv`, `evidence_register.csv`. PDFs and other originals are on the shared drive |
| `runs/` | One folder per analysis run: `manifest.json`, inputs, small outputs, logs |
| `cfd/` | CFD case set-ups, journals/scripts, post-processing (meshes and solutions on the shared drive) |
| `fea/` | FEA set-ups and result summaries |
| `cad/` | Exported geometry and CAD notes (native CAD files on the shared drive) |
| `hardware/` | Test procedures, raw logs and analyses for cells, battery, MPPT and later flight hardware |
| `reports/` | Gate reports, figures, mid-defence material |
| `env/` | Environment definition, lock files, external tool versions |
| `docs/` | How-to guides for the team |
| `.github/workflows/` | Continuous integration: tests and lint on every push and pull request |

Large files (PDFs, meshes, CFD/FEA results, native CAD, NetCDF downloads, photos) live on the shared drive in `fydp-haps-data/`, which mirrors this layout. Each folder that has large files contains a `LOCATION.md` giving the drive path.

---

## 4. Getting started (each team member, once)

1. Install **Git** (git-scm.com) and **GitHub Desktop** (desktop.github.com).
2. Install **Miniforge** (conda-forge Python distribution). Use **Python 3.12**, not 3.14.
3. Clone this repository with GitHub Desktop to a short path **outside** OneDrive/Google Drive sync folders, e.g. `C:\work\fydp-haps`.
4. Open *Miniforge Prompt* in that folder and run:
   ```
   conda create -n haps python=3.12 -y
   conda activate haps
   pip install -e .
   pip install pytest ruff
   pytest
   ```
   All tests should pass. The full environment (`env/environment.yml` and lock file) arrives with task T-W0.02.

---

## 5. How work is done

All rules are in PLAN.md §2–3. In short:

1. **One task card = one branch.** Name it `card/T-P2.07-short-name`.
2. Build on the branch. Commit small, clear steps (`T-P2.07: add Glauert series solver`).
3. Push the branch and open a **pull request** into `main`. Attach evidence: test output, plots, run manifests.
4. The named reviewer checks it against the review checklist (PLAN.md §3.6). Gate-critical work also needs an independent checker.
5. Merge only after approval **and** green CI. Update the card's status in `TASKS.md` in the same pull request.
6. `main` contains only `VERIFIED` work. Nobody pushes to `main` directly.

**Non-negotiables:** acceptance criteria are written before the run; every number has a source; verification is never reported as validation; nothing generated or predicted is presented as measured; every result carries its uncertainty.

---

## 6. For AI agents

Read `PLAN.md` §2 and §3 and `AGENTS.md` (added in T-W0.03) before taking a card. Never start a card whose dependencies in `TASKS.md` are not `VERIFIED`, except in the paired mode of PLAN.md §3.7. Never mark your own work `VERIFIED`.

---

## 7. Licence and use

Private academic work of the team named above. Not for redistribution without the team's and supervisor's permission. Third-party data and software keep their own licences; see source notes in `data/external/` and `env/tools.md`.
