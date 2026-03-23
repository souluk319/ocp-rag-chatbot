@echo off
echo ==========================================
echo OCP RAG Chatbot - Stopping Server
echo ==========================================
taskkill /F /IM uvicorn.exe /T 2>nul
if %errorlevel% equ 0 (
    echo Server stopped successfully.
) else (
    echo No running server found.
)
pause
