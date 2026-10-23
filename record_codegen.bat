@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Python environment not found. Run setup from README.md first.
    exit /b 1
)

.venv\Scripts\python.exe scripts\record-codegen.py %*
exit /b %errorlevel%
