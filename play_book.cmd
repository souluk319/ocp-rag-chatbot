@echo off
setlocal

set "ROOT=%~dp0"
set "VENV_PY=%ROOT%.venv\Scripts\python.exe"

if exist "%VENV_PY%" (
  "%VENV_PY%" "%ROOT%scripts\play_book.py" %*
) else (
  python "%ROOT%scripts\play_book.py" %*
)
