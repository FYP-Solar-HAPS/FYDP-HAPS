"""Create the fydp-haps folder skeleton (task T-W0.01).

Run once from the repository root:

    python setup_repo.py

It creates every folder listed in PLAN.md section 3.2. Git does not track
empty folders, so each folder receives a short README.md describing what
belongs there. Python package folders receive an __init__.py instead.
Existing files are never overwritten, so the script is safe to run again.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent

# Folder -> one-line description written into that folder's README.md
FOLDERS: dict[str, str] = {
    "acceptance": "Pre-registered pass rules (criteria.yaml). Edited only by pull request; tagged criteria-vN before the runs they judge.",
    "cards": "One Markdown file per task card, named <ID>.md (e.g. T-P2.07.md), using the template in PLAN.md section 3.5.",
    "requirements": "P0 outputs: needs.csv, register.csv, ahp.json, constraints.yaml, trace.csv.",
    "data/raw": "Downloaded or measured data, exactly as received. Never edit by hand. Large files (>20 MB, NetCDF, GRIB) go to the shared drive; record their location in LOCATION.md.",
    "data/external": "Published datasets used for validation (Sky-Sailor, AtlantikSolar, Selig, NASA TM-4062, UIUC propellers). Each dataset has a SOURCE.md with full reference and access date.",
    "data/processed": "Data produced by scripts. Each file is reproducible from a script in src/ or a run in runs/.",
    "literature": "Reading rules and literature registers. See literature/README.md (shipped with the starter kit).",
    "literature/notes": "Human-checked notes on individual papers, one Markdown file per citekey (e.g. Noth2008.md).",
    "runs": "One sub-folder per analysis run: manifest.json, inputs, small outputs, logs. Large outputs go to the shared drive.",
    "cfd": "CFD case set-ups, Fluent journals, OpenFOAM dictionaries, post-processing scripts. Meshes and solution files go to the shared drive.",
    "cfd/e387": "E387 airfoil validation case (T-CFD.01, T-CFD.02).",
    "cfd/pipeline": "Automated L2 pipeline: geometry export, meshing, run and post-processing scripts (T-CFD.03).",
    "fea": "FEA set-ups (ANSYS Mechanical) and result summaries. Result files go to the shared drive.",
    "cad": "Exported geometry (STEP/STL, small) and CAD notes. Native CAD files go to the shared drive.",
    "hardware/cells": "Solar-cell incoming inspection and I-V test procedures, raw logs and analyses (T-HW.01 to T-HW.03).",
    "reports": "Gate reports (G0-G3), figures, analysis write-ups.",
    "reports/mid_defence": "Mid-defence deck sources and progress report form (T-DOC.01).",
    "env": "environment.yml, lock files and tools.md (versions of external programs) (T-W0.02).",
    "docs": "How-to guides for the team: setup, Git workflow, conventions.",
    "tests": "pytest tests: unit, limiting-case, regression and validation.",
}

# Python package folders under src/haps (PLAN.md section 7)
PACKAGES = [
    "atmosphere", "solar", "pv", "aero", "propulsion", "mass", "structures",
    "energy", "stability", "cost", "space", "evaluation", "optimisation", "uq", "io",
]


def write_if_missing(path: Path, text: str) -> bool:
    """Write text to path only if the file does not exist yet."""
    if path.exists():
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return True


def main() -> None:
    created = 0
    for folder, description in FOLDERS.items():
        target = ROOT / folder
        target.mkdir(parents=True, exist_ok=True)
        if folder != "tests":  # tests/ already holds test files
            created += write_if_missing(
                target / "README.md", f"# {folder}/\n\n{description}\n"
            )

    package_root = ROOT / "src" / "haps"
    created += write_if_missing(
        package_root / "__init__.py",
        '"""HAPS/solar-UAV design analysis package (fydp-haps)."""\n\n__version__ = "0.0.1"\n',
    )
    for name in PACKAGES:
        created += write_if_missing(
            package_root / name / "__init__.py",
            f'"""haps.{name}: see PLAN.md section 7 for the module specification."""\n',
        )

    print(f"Done. {created} new files created; existing files left untouched.")


if __name__ == "__main__":
    main()
