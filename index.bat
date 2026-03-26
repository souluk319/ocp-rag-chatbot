@echo off
echo ==========================================
echo OCP RAG Chatbot - Indexing
echo ==========================================
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
call venv\Scripts\activate
python scripts/build_index.py
pause
