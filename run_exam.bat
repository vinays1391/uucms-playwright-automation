@echo off
setlocal
call .venv\Scripts\activate.bat
python -m pytest tests\test_exam.py -m exam -v
