@echo off
echo ==========================================
echo OCP RAG Chatbot - ngrok 배포
echo ==========================================

:: 1. 서버 실행 (백그라운드)
echo [1/2] 챗봇 서버 시작 중...
call venv\Scripts\activate
start /B uvicorn src.api:app --host 0.0.0.0 --port 8000 > nul 2>&1

:: 서버 기동 대기
timeout /t 3 /nobreak > nul
echo [1/2] 챗봇 서버 시작 완료 (http://localhost:8000)

:: 2. ngrok 실행
echo [2/2] ngrok 터널 시작 중...
echo.
echo ※ 아래 Forwarding URL을 공유하세요
echo ==========================================
ngrok.exe http 8000
pause
