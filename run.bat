@echo off
echo ==========================================
echo OCP RAG Chatbot - Running Server
echo ==========================================
call venv\Scripts\activate
uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
pause
