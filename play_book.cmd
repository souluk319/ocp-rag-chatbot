@echo off
setlocal

set "ROOT=%~dp0"
set "VENV_PY=%ROOT%.venv\Scripts\python.exe"
set "PREFLIGHT=%ROOT%scripts\codex_preflight.ps1"
set "PWSH=C:\Program Files\PowerShell\7\pwsh.exe"
set "COMMAND=%~1"
set "ARTIFACTS_SCOPE_ROOT=%ROOT%artifacts"
set "ARTIFACTS_DIR_OVERRIDE="

cd /d "%ROOT%"

if not exist "%VENV_PY%" (
  echo Missing required virtual environment: "%VENV_PY%"
  exit /b 1
)

if not exist "%PWSH%" (
  echo Missing required PowerShell 7: "%PWSH%"
  exit /b 1
)

if exist "%ROOT%.env" (
  for /f "usebackq eol=# tokens=1,* delims==" %%A in ("%ROOT%.env") do (
    if /I "%%A"=="ARTIFACTS_DIR" set "ARTIFACTS_DIR_OVERRIDE=%%B"
  )
)

if defined ARTIFACTS_DIR_OVERRIDE (
  for %%I in ("%ARTIFACTS_DIR_OVERRIDE%") do set "ARTIFACTS_SCOPE_ROOT=%%~fI"
)

if "%COMMAND%"=="" set "COMMAND=unknown"
set "PLAY_BOOK_WRITE_SCOPE=runtime:%COMMAND%"
if /I "%COMMAND%"=="ui" set "PLAY_BOOK_WRITE_SCOPE=read-only:ui-runtime"
if /I "%COMMAND%"=="ask" set "PLAY_BOOK_WRITE_SCOPE=%ARTIFACTS_SCOPE_ROOT%\answering\answer_log.jsonl"
if /I "%COMMAND%"=="eval" set "PLAY_BOOK_WRITE_SCOPE=%ARTIFACTS_SCOPE_ROOT%\answering\answer_eval_report.json"
if /I "%COMMAND%"=="ragas" set "PLAY_BOOK_WRITE_SCOPE=%ARTIFACTS_SCOPE_ROOT%\answering\ragas_eval_report.json;%ARTIFACTS_SCOPE_ROOT%\answering\ragas_eval_dataset_preview.json"
if /I "%COMMAND%"=="runtime" set "PLAY_BOOK_WRITE_SCOPE=%ARTIFACTS_SCOPE_ROOT%\runtime\runtime_report.json"
set "PLAY_BOOK_VERIFY_CMD=%ROOT%play_book.cmd %*"

"%PWSH%" -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%PREFLIGHT%" -WriteScope "%PLAY_BOOK_WRITE_SCOPE%" -VerifyCmd "%PLAY_BOOK_VERIFY_CMD%" %*
if errorlevel 1 (
  exit /b 1
)

set "PLAY_BOOK_LAUNCHER=play_book.cmd"
"%VENV_PY%" "%ROOT%scripts\play_book.py" %*
