@echo off
echo ===================================
echo  Starting AgriTech AI (Python 3.11)
echo ===================================
call "%~dp0.venv\Scripts\activate.bat"
python -m streamlit run "%~dp0main.py"
pause
