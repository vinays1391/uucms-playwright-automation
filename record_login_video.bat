@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Python environment not found. Run setup from README.md first.
    exit /b 1
)

.venv\Scripts\python.exe scripts\record-login-video.py
exit /b %errorlevel%
