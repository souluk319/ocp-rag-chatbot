@echo off
echo ==========================================
echo OCP RAG Chatbot - Running Server
echo ==========================================
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
call venv\Scripts\activate
uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
pause
