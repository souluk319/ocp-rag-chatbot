@echo off
echo ==========================================
echo OCP RAG Chatbot - Indexing
echo ==========================================
call venv\Scripts\activate
python scripts/build_index.py
pause
