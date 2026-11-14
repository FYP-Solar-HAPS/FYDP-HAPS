"""Smoke test: the package installs and imports (keeps CI meaningful before real tests exist)."""

import importlib

import haps

SUBPACKAGES = [
    "atmosphere", "solar", "pv", "aero", "propulsion", "mass", "structures",
    "energy", "stability", "cost", "space", "evaluation", "optimisation", "uq", "io",
]


def test_version_defined():
    assert isinstance(haps.__version__, str)


def test_subpackages_import():
    for name in SUBPACKAGES:
        importlib.import_module(f"haps.{name}")
