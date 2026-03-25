@echo off
echo ==========================================
echo OCP RAG Chatbot - ngrok + Server 종료
echo ==========================================
taskkill /F /IM ngrok.exe /T 2>nul
if %errorlevel% equ 0 (
    echo ngrok 종료 완료
) else (
    echo ngrok 프로세스 없음
)
taskkill /F /IM uvicorn.exe /T 2>nul
if %errorlevel% equ 0 (
    echo 서버 종료 완료
) else (
    echo 서버 프로세스 없음
)
echo ==========================================
echo 모두 종료되었습니다.
pause
