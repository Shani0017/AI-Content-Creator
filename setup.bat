@echo off
cd /d "%~dp0"
echo ===== AI Content Creator - one-time setup =====
where py >nul 2>nul
if %errorlevel%==0 (set PY=py -3) else (set PY=python)
%PY% --version >nul 2>nul
if errorlevel 1 (
  echo Python 3.10 or newer is required. Install it from https://www.python.org/downloads/ ^(tick "Add python.exe to PATH"^) and run this again.
  pause
  exit /b 1
)
if not exist ".venv\Scripts\python.exe" %PY% -m venv .venv
".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
  echo Install failed. Check your internet connection and run setup.bat again.
  pause
  exit /b 1
)
echo.
echo Setup finished. Start the app with start.bat
echo The voice files ^(about 340 MB^) can be downloaded from the Settings page inside the app.
pause
