@echo off
cd /d "%~dp0"
echo ===== AI Content Creator - one-time setup =====
set PY=
py -3.11 --version >nul 2>nul && set PY=py -3.11
if "%PY%"=="" py -3.12 --version >nul 2>nul && set PY=py -3.12
if "%PY%"=="" (
  echo Python 3.11 or 3.12 is required ^(newer versions such as 3.14 / 3.15 do not have the speech packages yet^).
  echo Easiest: run the one-line installer from the README, it installs Python 3.11 for you.
  echo Or install it from https://www.python.org/downloads/release/python-3119/ and run setup.bat again.
  pause
  exit /b 1
)
echo Using %PY%
if not exist ".venv\Scripts\python.exe" %PY% -m venv .venv
".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\python.exe" -m pip install --prefer-binary --only-binary=:all: -r requirements.txt
if errorlevel 1 (
  echo Install failed. Check your internet connection and run setup.bat again.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" -m forge.setup_models
echo.
echo Setup finished. Start the app with start.bat
pause
