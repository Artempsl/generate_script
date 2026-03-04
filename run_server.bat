@echo off
REM =============================================================================
REM Agent Backend Server Startup Script (Windows)
REM =============================================================================
REM
REM This script launches the Agent Backend FastAPI server.
REM
REM Prerequisites:
REM   - Python virtual environment activated (.venv)
REM   - Environment variables set (OPENAI_API_KEY, PINECONE_API_KEY, etc.)
REM
REM Usage:
REM   run_server.bat
REM
REM =============================================================================

echo ================================================================================
echo AGENT BACKEND SERVER - STARTUP
echo ================================================================================
echo.

REM Check if virtual environment exists
if not exist ".venv\Scripts\python.exe" (
    echo ERROR: Virtual environment not found!
    echo Please run: python -m venv .venv
    echo Then install dependencies: .venv\Scripts\pip install -r requirements.txt
    pause
    exit /b 1
)

REM Check environment variables
echo Checking environment variables...
echo.

.venv\Scripts\python.exe -c "import os; print('  OPENAI_API_KEY:', 'SET' if os.getenv('OPENAI_API_KEY') else 'NOT SET')"
.venv\Scripts\python.exe -c "import os; print('  PINECONE_API_KEY:', 'SET' if os.getenv('PINECONE_API_KEY') else 'NOT SET')"
.venv\Scripts\python.exe -c "import os; print('  COHERE_API_KEY:', 'SET' if os.getenv('COHERE_API_KEY') else 'NOT SET')"
.venv\Scripts\python.exe -c "import os; print('  SERPAPI_API_KEY:', 'SET (optional)' if os.getenv('SERPAPI_API_KEY') else 'NOT SET (web search disabled)')"

echo.
echo ================================================================================
echo Starting server...
echo ================================================================================
echo.

REM Launch server
.venv\Scripts\python.exe server.py

REM Pause on exit to see any errors
pause
