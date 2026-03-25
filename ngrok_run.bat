@echo off
chcp 65001 >nul 2>&1
echo ==========================================
echo OCP RAG Chatbot - ngrok Deploy
echo ==========================================

echo [1/2] Starting chatbot server...
call venv\Scripts\activate
start /B uvicorn src.api:app --host 0.0.0.0 --port 8000 > nul 2>&1

timeout /t 3 /nobreak > nul
echo [1/2] Server started (http://localhost:8000)

echo [2/2] Starting ngrok tunnel...
echo.
echo Share the Forwarding URL below
echo ==========================================
ngrok.exe http 8000
pause
