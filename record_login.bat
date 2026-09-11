@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Python environment not found.
    echo Run: py -m venv .venv
    echo Then install dependencies with: .venv\Scripts\python.exe -m pip install -e .
    exit /b 1
)

if not exist "recordings" mkdir recordings
.venv\Scripts\python.exe -m playwright codegen --target=python --output=recordings\login_codegen.py http://123.63.4.210:5010/
exit /b %errorlevel%
