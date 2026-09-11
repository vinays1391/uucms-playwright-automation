@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Python environment not found.
    echo Run: py -m venv .venv
    echo Then install dependencies with: .venv\Scripts\python.exe -m pip install -e .
    exit /b 1
)

if not exist ".env" (
    echo Missing .env. Copy .env.example to .env and configure the login values.
    exit /b 1
)

.venv\Scripts\python.exe -c "from dotenv import dotenv_values; import subprocess; browser = dotenv_values('.env').get('UUCMS_BROWSER', 'chromium').strip().lower(); valid = {'chromium', 'firefox', 'webkit'}; raise SystemExit('UUCMS_BROWSER must be chromium, firefox, or webkit') if browser not in valid else subprocess.call(['.venv\\Scripts\\python.exe', '-m', 'playwright', 'install', browser])"
if errorlevel 1 exit /b %errorlevel%
.venv\Scripts\python.exe -c "from dotenv import dotenv_values; import subprocess; browser = dotenv_values('.env').get('UUCMS_BROWSER', 'chromium').strip().lower(); raise SystemExit(subprocess.call(['.venv\\Scripts\\python.exe', '-m', 'pytest', 'tests\\test_login.py', '-m', 'login', '--browser=' + browser]))"
exit /b %errorlevel%
