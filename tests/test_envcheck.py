"""Unit tests for the output parsers of haps.io.envcheck (no external programs needed)."""

from haps.io.envcheck import (
    PACKAGES,
    parse_avl_version,
    parse_vsp_hello,
    parse_xfoil_cl,
    parse_xfoil_version,
)

XFOIL_OUT = """
 ===================================================
  XFOIL Version 6.99
 ===================================================
   a =  2.000      CL =  0.1987
  Cm = -0.0012     CD =  0.00602   =>   CDf =  0.00532    CDp =  0.00070
   a =  2.000      CL =  0.2214
"""

AVL_OUT = """
 ===================================================
  Athena Vortex Lattice  Program      Version  3.40
  Copyright (C) 2002   Mark Drela, Harold Youngren
"""


def test_xfoil_parsers_take_last_cl_and_version():
    assert parse_xfoil_cl(XFOIL_OUT) == 0.2214
    assert parse_xfoil_version(XFOIL_OUT) == "6.99"
    assert parse_xfoil_cl("no convergence") is None


def test_avl_version_from_banner():
    assert parse_avl_version(AVL_OUT) == "3.40"
    assert parse_avl_version("something else") == ""


def test_package_list_matches_environment_file():
    from pathlib import Path

    env = Path(__file__).resolve().parents[1] / "env" / "environment.yml"
    text = env.read_text(encoding="utf-8")
    missing = [dist for dist in PACKAGES.values() if dist not in text]
    assert not missing, f"in envcheck.PACKAGES but not in environment.yml: {missing}"


def test_vsp_hello_parser():
    out = "VSPVERSION OpenVSP 3.56.0\nNGEOMS 1\n"
    assert parse_vsp_hello(out) == ("OpenVSP 3.56.0", 1)
    assert parse_vsp_hello("Traceback ... ImportError") == ("", None)
