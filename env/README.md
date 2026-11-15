# env/ — software environment (card T-W0.02)

Everything needed to reproduce results on both laptops and in CI (PLAN.md §3.3, rule 7 of §2).

| File | What it is | Edited by |
|---|---|---|
| `environment.yml` | List of Python packages (conda-forge, Python 3.12) | Pull request only |
| `conda-lock.yml` | Exact versions for Windows (`win-64`) and Linux (`linux-64`), generated from `environment.yml` | Generated (never by hand) |
| `tools.md` | External programs (XFOIL, AVL, OpenVSP, Fluent, …): required version, installed version per laptop, where to get them | Team |
| `machines/<laptop>.json` | Smoke-test report from each laptop (`python -m haps.io.envcheck`) | Generated |

## 0. Quickest way (Windows): `env\setup_env.bat`

Double-click `env\setup_env.bat` (or run it in Command Prompt). It does sections 1–4 below in
order: installs conda-lock (into a small `haps-tools` environment, so Miniforge's base folder is
never written to, even if it is read-only), creates `env\conda-lock.yml` if missing, builds the `haps`
environment from it, installs the package, runs the tests and the smoke test. It looks for
Miniforge in `D:\Miniforge` and the default install folders; edit the `MINIFORGE` line if yours
is elsewhere. Use Miniforge only; do not mix with Anaconda.

**Why `conda` "is not recognised" or "environment.yml not found":** a normal terminal does not
know about conda unless Miniforge was added to PATH (use Miniforge Prompt, or run
`D:\Miniforge\Scripts\conda.exe init cmd.exe powershell` once and reopen the terminal). Miniforge
Prompt starts in your user folder, so first change to the repository: on another drive this needs
`/d` and quotes, e.g. `cd /d "D:\ATEEQ\Ateeq work\FYP\FYDP-HAPS"`.

## 1. One-time: create the lock file (maintainer, once)

In **Miniforge Prompt**, from the repository folder:

```
conda env create -f env/environment.yml
conda activate haps
conda-lock lock -f env/environment.yml -p win-64 -p linux-64 --lockfile env/conda-lock.yml
```

Commit `env/conda-lock.yml` on a branch and open a pull request. Repeat only when
`environment.yml` changes (a new package is a pull request that changes both files).

## 2. Every laptop: install from the lock file

```
conda install -n base -c conda-forge conda-lock
conda-lock install -n haps env/conda-lock.yml
conda activate haps
pip install --no-deps -e ".[dev,literature]"
pytest -q
```

`--no-deps` stops pip replacing the locked versions. If an environment called `haps` already
exists, remove it first with `conda env remove -n haps`.

## 3. External programs

Install each program listed in `tools.md`, then tell the project where it is. In Command Prompt
(once per laptop; close and reopen the prompt afterwards):

```
setx HAPS_XFOIL "C:\Tools\XFOIL6.99\xfoil.exe"
setx HAPS_AVL "C:\Tools\AVL\avl.exe"
setx HAPS_FLUENT "C:\Program Files\ANSYS Inc\v<release>\fluent\ntbin\win64\fluent.exe"
setx HAPS_DATA "D:\ATEEQ\Ateeq work\Google Drive\FYDP-HAPS-data"
```

Use your own paths. `HAPS_DATA` is the mirrored shared-drive data folder; code and agents read
large files from there and never from paths typed into code.

## 4. Smoke test (the card's acceptance test)

```
conda activate haps
python -m haps.io.envcheck --fluent
```

It imports every package, reports whether PyTorch sees the GPU, runs XFOIL (NACA 0012,
Re = 10⁶, α = 2°), starts AVL, creates a wing through the OpenVSP API and starts and exits Fluent
in batch mode (licence check). The report goes to `env/machines/<laptop>.json`: commit it.
T-W0.02 passes when both laptops show every check `PASS` and `tools.md` records the versions.

**GPU.** The lock file pins the CPU build of PyTorch, which is enough at this project's scale.
If a surrogate job later needs the RTX 3050, open a card to add a CUDA build to the lock
(conda-lock virtual-package specification); do not `pip install` a different torch into `haps`.

**OpenVSP (separate environment).** OpenVSP's Windows Python API is built only for Python 3.11
and 3.13 (OpenVSP 3.56.0 has no 3.12 build), so it lives in its own small environment
`haps-vsp` (`env/vsp-environment.yml`, Python 3.13). Geometry scripts run there and write
files that the `haps` environment reads. Once per laptop, in Miniforge Prompt (use your own
OpenVSP folder; download the **Python 3.13** Windows build from openvsp.org):

```
conda env create -f env\vsp-environment.yml
conda activate haps-vsp
pip install -e "D:\OpenVSP\OpenVSP-3.56.0-win64-Python3.13\OpenVSP-3.56.0-win64\python\openvsp_config"
pip install -e "D:\OpenVSP\OpenVSP-3.56.0-win64-Python3.13\OpenVSP-3.56.0-win64\python\openvsp"
conda deactivate
```

The smoke test finds `haps-vsp` in `%USERPROFILE%\.conda\envs\` automatically; if it is elsewhere,
`setx HAPS_VSP_PYTHON "<path>\python.exe"`. Never install `openvsp` into `haps`.

