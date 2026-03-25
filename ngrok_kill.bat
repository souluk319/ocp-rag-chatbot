@echo off
chcp 65001 >nul 2>&1
echo ==========================================
echo OCP RAG Chatbot - Kill All
echo ==========================================
taskkill /F /IM ngrok.exe /T 2>nul
if %errorlevel% equ 0 (
    echo ngrok stopped
) else (
    echo ngrok not running
)
taskkill /F /IM uvicorn.exe /T 2>nul
if %errorlevel% equ 0 (
    echo server stopped
) else (
    echo server not running
)
echo ==========================================
echo All processes terminated.
pause
