@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo First run: setting things up. This takes a few minutes...
  call setup.bat
)
".venv\Scripts\python.exe" app.py
pause
