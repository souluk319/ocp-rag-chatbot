@echo off
echo ==========================================
echo OCP RAG Chatbot - Demo Preflight
echo ==========================================
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
call venv\Scripts\activate
python scripts/check_fixture_integrity.py
if errorlevel 1 goto :fail
python scripts/check_submission_contract.py
if errorlevel 1 goto :fail
python scripts/check_demo_preflight.py
if errorlevel 1 goto :fail
echo.
echo Preflight checks passed.
pause
exit /b 0

:fail
echo.
echo Preflight checks failed.
pause
exit /b 1
