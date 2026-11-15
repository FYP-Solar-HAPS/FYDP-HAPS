@echo off
REM ==========================================================================
REM  HAPS FYDP: one-click environment set-up for Windows (card T-W0.02)
REM  Double-click this file, or run it from any Command Prompt.
REM  Optional: env\setup_env.bat --fluent   (also launches Fluent once)
REM
REM  What it does:
REM   1. finds Miniforge (MINIFORGE below, or the usual install folders)
REM   2. installs conda-lock into a small "haps-tools" environment (base is never modified)
REM   3. creates env\conda-lock.yml from env\environment.yml if it does not exist yet
REM   4. (re)creates the "haps" environment from the lock file
REM   5. installs this repository's package, runs the tests and the smoke test
REM  Uses Miniforge only (conda-forge). Do not mix with Anaconda.
REM ==========================================================================
setlocal
set "MINIFORGE=D:\Miniforge"
if not exist "%MINIFORGE%\Scripts\activate.bat" set "MINIFORGE=%USERPROFILE%\miniforge3"
if not exist "%MINIFORGE%\Scripts\activate.bat" set "MINIFORGE=%LOCALAPPDATA%\miniforge3"
if not exist "%MINIFORGE%\Scripts\activate.bat" (
  echo Miniforge not found. Edit the MINIFORGE line at the top of this file.
  goto :fail
)

REM Keep environments and the package cache in the user's folder, because Miniforge's own folder
REM may be read-only for this Windows user (installed "for all users").
set "CONDA_ENVS_DIRS=%USERPROFILE%\.conda\envs"
set "CONDA_PKGS_DIRS=%USERPROFILE%\.conda\pkgs"
set "HAPS_PREFIX=%USERPROFILE%\.conda\envs\haps"

REM Go to the repository root (this file lives in env\)
cd /d "%~dp0.."
echo Repository: %CD%
echo Miniforge:  %MINIFORGE%
call "%MINIFORGE%\Scripts\activate.bat" "%MINIFORGE%" || goto :fail

echo.
echo [1/5] Preparing conda-lock in a small tools environment "haps-tools"...
REM Miniforge's base folder may be read-only for your Windows user (installed "for all users").
REM Nothing is written there: new environments go to your user folder automatically.
call conda env list | findstr /r /c:"^haps-tools " >nul
if errorlevel 1 (
  call conda create -n haps-tools -c conda-forge --override-channels --yes conda-lock || goto :fail
)
call conda activate haps-tools || goto :fail

echo.
if exist "env\conda-lock.yml" (
  echo [2/5] env\conda-lock.yml already exists: using it.
) else (
  echo [2/5] Creating env\conda-lock.yml for win-64 and linux-64. This takes several minutes...
  call conda-lock lock -f env\environment.yml -p win-64 -p linux-64 --lockfile env\conda-lock.yml || goto :fail
  echo Lock file created. Commit env\conda-lock.yml on a branch and open a pull request.
)

echo.
call conda env list | findstr /r /c:"^haps " >nul
if not errorlevel 1 (
  echo [3/5] An environment called "haps" already exists.
  choice /M "Remove it and rebuild it from the lock file"
  if errorlevel 2 goto :skip_rebuild
  call conda env remove -n haps --yes || goto :fail
)
echo [3/5] Creating the "haps" environment from the lock file. Large download (PyTorch)...
REM Plain conda (not mamba) does the install: it handles a read-only Miniforge folder correctly.
call conda-lock install --conda "%MINIFORGE%\Scripts\conda.exe" --log-level DEBUG -p "%HAPS_PREFIX%" env\conda-lock.yml || goto :fail
:skip_rebuild

echo.
echo [4/5] Installing the haps package and running the tests...
call conda activate haps || goto :fail
python -m pip install --no-deps -e ".[dev,literature]" || goto :fail
python -m pytest -q || goto :fail

echo.
echo [5/5] Smoke test (packages and external tools)...
python -m haps.io.envcheck %*
echo.
echo Done. Commit env\machines\*.json (and env\conda-lock.yml if it was created).
pause
exit /b 0

:fail
echo.
echo FAILED at the step above. Copy the last 30 lines of this window into the chat.
pause
exit /b 1
