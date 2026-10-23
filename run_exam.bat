@echo off
setlocal
call .venv\Scripts\activate.bat
python -m pytest tests\ui\exam -m exam -v
