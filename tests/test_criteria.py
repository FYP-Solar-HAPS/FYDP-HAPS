"""Schema checks for acceptance/criteria.yaml (card T-W0.04).

These tests do not judge any model. They make sure every pre-registered criterion is complete
enough to be reviewed and tagged: it has a check, a pass rule, a tolerance type, a gate, a source
and a rationale (PLAN.md §2 rule 2, §11).
"""

from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")

CRITERIA = Path(__file__).resolve().parents[1] / "acceptance" / "criteria.yaml"
REQUIRED = {"category", "check", "pass_rule", "tolerance", "applies_to", "gate", "source",
            "rationale", "open_items"}
PLAN_KEYS = {"V-ISA", "V-SUN", "V-LL", "V-BEAM", "V-ENERGY", "VAL-A", "VAL-B", "VAL-AF",
             "VER-GCI", "H1", "H3", "OPT", "SURR", "MC"}  # PLAN.md §11
GATES = {"G0", "G1", "G2", "G3", "G4", "G5"}
TOLERANCE_TYPES = {"absolute", "relative", "probability", "rule", "TBD"}


@pytest.fixture(scope="module")
def doc():
    return yaml.safe_load(CRITERIA.read_text(encoding="utf-8"))


def test_header(doc):
    assert doc["schema_version"] == 1
    assert doc["criteria_version"].startswith("v")
    assert doc["status"] in {"DRAFT", "TAGGED"}


def test_every_plan_criterion_is_registered(doc):
    assert PLAN_KEYS <= set(doc["criteria"])


@pytest.mark.parametrize("key", sorted(PLAN_KEYS | {"H2", "H4"}))
def test_criterion_is_complete(doc, key):
    item = doc["criteria"][key]
    assert REQUIRED <= set(item), f"{key} missing {REQUIRED - set(item)}"
    assert item["gate"] in GATES
    assert item["tolerance"]["type"] in TOLERANCE_TYPES
    sources = item["source"] if isinstance(item["source"], list) else [item["source"]]
    assert all(s.get("ref") for s in sources), f"{key} has a source without ref"
    assert len(item["rationale"].strip()) > 20, f"{key} rationale too short"


def test_tbd_tolerances_are_flagged_as_open(doc):
    for key, item in doc["criteria"].items():
        if "TBD" in str(item["tolerance"]):
            assert item["open_items"], f"{key} has a TBD tolerance but no open item"
