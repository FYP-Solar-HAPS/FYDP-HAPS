"""Environment smoke test (card T-W0.02, PLAN.md §3.3 and §5.1).

Checks that every Python package in env/environment.yml imports, records its version,
reports whether PyTorch sees the GPU, and runs "hello" cases of the external tools:
XFOIL, AVL, the OpenVSP Python API and (optionally, it is slow) ANSYS Fluent in batch mode.
The result is written to env/machines/<machine>.json and summarised on screen.

Run from the repository root with the ``haps`` environment active::

    python -m haps.io.envcheck                 # packages + XFOIL + AVL + OpenVSP
    python -m haps.io.envcheck --fluent        # also launch Fluent once (licence check)

Where the tools are found (first match wins):

* XFOIL:   environment variable ``HAPS_XFOIL`` (full path to xfoil.exe), else ``xfoil`` on PATH
* AVL:     ``HAPS_AVL`` (full path to avl.exe), else ``avl`` on PATH
* OpenVSP: ``HAPS_VSP_PYTHON`` (python.exe of the separate ``haps-vsp`` environment, because
           OpenVSP's Windows Python API is only built for Python 3.11 and 3.13), else
           ``%USERPROFILE%/.conda/envs/haps-vsp/python.exe``
* Fluent:  ``HAPS_FLUENT`` (full path to fluent.exe), else ``fluent`` on PATH

The card's acceptance test is this script passing on both laptops (PLAN.md §5.1).
"""

from __future__ import annotations

import argparse
import importlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path

# import name -> distribution name used in the report (same as environment.yml)
PACKAGES: dict[str, str] = {
    "numpy": "numpy",
    "scipy": "scipy",
    "pandas": "pandas",
    "xarray": "xarray",
    "netCDF4": "netcdf4",
    "pyarrow": "pyarrow",
    "numba": "numba",
    "matplotlib": "matplotlib",
    "pytest": "pytest",
    "hypothesis": "hypothesis",
    "pydantic": "pydantic",
    "pint": "pint",
    "yaml": "pyyaml",
    "rich": "rich",
    "pvlib": "pvlib-python",
    "cdsapi": "cdsapi",
    "earthaccess": "earthaccess",
    "requests": "requests",
    "sklearn": "scikit-learn",
    "statsmodels": "statsmodels",
    "torch": "pytorch",
    "gpytorch": "gpytorch",
    "botorch": "botorch",
    "ax": "ax-platform",
    "SALib": "salib",
    "chaospy": "chaospy",
    "openmdao": "openmdao",
    "pymupdf": "pymupdf",
    "docx": "python-docx",
    "aerosandbox": "aerosandbox",
    "neuralfoil": "neuralfoil",
    "openaerostruct": "openaerostruct",
    "pymoo": "pymoo",
    "smt": "smt",
}

XFOIL_SCRIPT = "NACA 0012\nOPER\nVISC 1e6\nITER 200\nALFA 2\n\nQUIT\n"
AVL_SCRIPT = "QUIT\n"
FLUENT_JOURNAL = "/exit yes\n"


@dataclass
class Check:
    name: str
    ok: bool
    version: str = ""
    detail: str = ""


@dataclass
class Report:
    machine: str
    created_utc: str
    python: str
    platform: str
    checks: list[Check] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return all(c.ok for c in self.checks)


# --------------------------------------------------------------------------
# Output parsers (unit-tested without the external programs)
# --------------------------------------------------------------------------
def parse_xfoil_cl(output: str) -> float | None:
    """Return the last lift coefficient XFOIL printed (``CL = 0.2345``), or None."""
    matches = re.findall(r"CL\s*=\s*(-?\d+\.\d+)", output)
    return float(matches[-1]) if matches else None


def parse_xfoil_version(output: str) -> str:
    """Return the XFOIL version from its banner (``XFOIL Version 6.99``), or ''."""
    match = re.search(r"XFOIL\s+Version\s+([\d.]+)", output, re.IGNORECASE)
    return match.group(1) if match else ""


def parse_avl_version(output: str) -> str:
    """Return the AVL version from its banner (``Athena Vortex Lattice  Program  Version 3.40``)."""
    match = re.search(r"Vortex\s+Lattice.*?Version\s+([\d.]+)", output, re.IGNORECASE | re.DOTALL)
    return match.group(1) if match else ""


# --------------------------------------------------------------------------
# Individual checks
# --------------------------------------------------------------------------
def find_tool(env_var: str, exe: str) -> str | None:
    """Path from an environment variable, else the executable on PATH, else None."""
    configured = os.environ.get(env_var, "").strip().strip('"')
    if configured:
        return configured if Path(configured).is_file() else None
    return shutil.which(exe)


def run(cmd: list[str], stdin: str = "", timeout: float = 120.0, cwd: Path | None = None
        ) -> tuple[int, str]:
    """Run a command with text on stdin; return (exit code, combined output)."""
    proc = subprocess.run(  # fixed argument lists, never a shell
        cmd, check=False, input=stdin, capture_output=True, text=True, timeout=timeout, cwd=cwd,
    )
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def check_package(module: str, dist: str) -> Check:
    try:
        mod = importlib.import_module(module)
    except Exception as exc:  # noqa: BLE001  (report any import failure, do not crash)
        return Check(dist, False, detail=f"import failed: {exc.__class__.__name__}: {exc}")
    version = str(getattr(mod, "__version__", getattr(mod, "VERSION", "")))
    return Check(dist, True, version=version)


def check_torch_gpu() -> Check:
    try:
        import torch
    except Exception as exc:  # noqa: BLE001
        return Check("torch GPU", False, detail=f"torch not importable: {exc}")
    if torch.cuda.is_available():
        name = torch.cuda.get_device_name(0)
        return Check("torch GPU", True, version=str(torch.version.cuda), detail=name)
    # Not a failure: CPU-only PyTorch works, just slower. Recorded so the team knows.
    return Check("torch GPU", True, detail="CUDA not available: running on CPU (see env/README.md)")


def check_xfoil() -> Check:
    exe = find_tool("HAPS_XFOIL", "xfoil")
    if exe is None:
        return Check("XFOIL", False, detail="not found: set HAPS_XFOIL or add xfoil to PATH")
    try:
        with tempfile.TemporaryDirectory() as tmp:  # XFOIL may write files in its cwd
            code, out = run([exe], XFOIL_SCRIPT, timeout=60, cwd=Path(tmp))
    except (OSError, subprocess.TimeoutExpired) as exc:
        return Check("XFOIL", False, detail=f"run failed: {exc}")
    cl = parse_xfoil_cl(out)
    if cl is None:
        return Check("XFOIL", False, version=parse_xfoil_version(out),
                     detail=f"no CL in output (exit {code})")
    return Check("XFOIL", True, version=parse_xfoil_version(out),
                 detail=f"NACA 0012, Re 1e6, alpha 2 deg: CL = {cl:.4f}")


def check_avl() -> Check:
    exe = find_tool("HAPS_AVL", "avl")
    if exe is None:
        return Check("AVL", False, detail="not found: set HAPS_AVL or add avl to PATH")
    try:
        code, out = run([exe], AVL_SCRIPT, timeout=30)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return Check("AVL", False, detail=f"run failed: {exc}")
    version = parse_avl_version(out)
    return Check("AVL", bool(version), version=version,
                 detail="banner read" if version else f"banner not recognised (exit {code})")


VSP_HELLO = (
    "import openvsp as vsp\n"
    "print('VSPVERSION', vsp.GetVSPVersion())\n"
    "vsp.VSPRenew()\n"
    "vsp.AddGeom('WING')\n"
    "print('NGEOMS', len(vsp.FindGeoms()))\n"
)


def parse_vsp_hello(output: str) -> tuple[str, int | None]:
    """Return (version text, number of geometries) printed by the OpenVSP hello script."""
    version = re.search(r"VSPVERSION\s+(.+)", output)
    count = re.search(r"NGEOMS\s+(\d+)", output)
    return (version.group(1).strip() if version else "",
            int(count.group(1)) if count else None)


def vsp_python() -> str | None:
    """python.exe of the haps-vsp environment (OpenVSP API), or None if not found."""
    configured = os.environ.get("HAPS_VSP_PYTHON", "").strip().strip('"')
    if configured:
        return configured if Path(configured).is_file() else None
    default = Path(os.environ.get("USERPROFILE", str(Path.home()))) / ".conda" / "envs" / "haps-vsp"
    for candidate in (default / "python.exe", default / "bin" / "python"):
        if candidate.is_file():
            return str(candidate)
    return None


def check_openvsp() -> Check:
    exe = vsp_python()
    if exe is None:
        return Check("OpenVSP API", False,
                     detail="haps-vsp environment not found: see env/README.md section 3")
    try:
        code, out = run([exe, "-c", VSP_HELLO], timeout=120)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return Check("OpenVSP API", False, detail=f"run failed: {exc}")
    version, n = parse_vsp_hello(out)
    if code != 0 or n is None:
        last = out.strip().splitlines()[-1] if out.strip() else "no output"
        return Check("OpenVSP API", False, version=version, detail=f"exit {code}: {last[:120]}")
    return Check("OpenVSP API", n == 1, version=version,
                 detail=f"created {n} wing geometry (haps-vsp environment)")


def check_fluent() -> Check:
    exe = find_tool("HAPS_FLUENT", "fluent")
    if exe is None:
        return Check("Fluent", False, detail="not found: set HAPS_FLUENT or add fluent to PATH")
    with tempfile.TemporaryDirectory() as tmp:
        journal = Path(tmp) / "hello.jou"
        journal.write_text(FLUENT_JOURNAL, encoding="ascii")
        try:
            code, out = run([exe, "2d", "-g", "-t1", "-i", str(journal)], timeout=600,
                            cwd=Path(tmp))
        except (OSError, subprocess.TimeoutExpired) as exc:
            return Check("Fluent", False, detail=f"run failed: {exc}")
    version = ""
    if match := re.search(r"Fluent\s+([\d.]+)|Release\s+([\d.]+)", out):
        version = match.group(1) or match.group(2) or ""
    return Check("Fluent", code == 0, version=version,
                 detail="batch start and exit OK (licence checked out)" if code == 0
                 else f"exit code {code}; see Fluent output")


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------
def build_report(tools: bool, packages: bool, fluent: bool) -> Report:
    report = Report(
        machine=platform.node() or "unknown",
        created_utc=datetime.now(UTC).isoformat(timespec="seconds"),
        python=sys.version.split()[0],
        platform=platform.platform(),
    )
    if not sys.version.startswith("3.12."):
        report.checks.append(Check("python 3.12", False, version=report.python,
                                   detail="wrong interpreter: activate the haps environment"))
    if packages:
        report.checks += [check_package(m, d) for m, d in PACKAGES.items()]
        report.checks.append(check_torch_gpu())
    if tools:
        report.checks += [check_xfoil(), check_avl(), check_openvsp()]
        if fluent:
            report.checks.append(check_fluent())
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m haps.io.envcheck",
                                     description="Environment smoke test (T-W0.02).")
    parser.add_argument("--packages-only", action="store_true", help="skip external tools")
    parser.add_argument("--tools-only", action="store_true", help="skip Python packages")
    parser.add_argument("--fluent", action="store_true", help="also launch Fluent once (slow)")
    parser.add_argument("--out", type=Path, default=None,
                        help="report path (default env/machines/<machine>.json)")
    args = parser.parse_args(argv)

    report = build_report(tools=not args.packages_only, packages=not args.tools_only,
                          fluent=args.fluent)
    safe_name = re.sub(r"[^A-Za-z0-9_-]+", "_", report.machine)
    out = args.out or Path("env") / "machines" / f"{safe_name}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = asdict(report) | {"ok": report.ok}
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    width = max(len(c.name) for c in report.checks)
    for c in report.checks:
        print(f"{'PASS' if c.ok else 'FAIL'}  {c.name:<{width}}  {c.version:<12} {c.detail}")
    failed = [c.name for c in report.checks if not c.ok]
    print(f"\n{len(report.checks) - len(failed)}/{len(report.checks)} checks passed. Report: {out}")
    if failed:
        print("Failed: " + ", ".join(failed))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
