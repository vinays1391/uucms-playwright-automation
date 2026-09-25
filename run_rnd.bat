@echo off
setlocal
call .venv\Scripts\activate.bat
python -m pytest tests -k rnd -v
