@echo off
cd /d "%~dp0"
set PYTHONPATH=%~dp0
streamlit run app.py
