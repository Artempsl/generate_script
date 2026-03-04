@echo off
REM Quick test script with environment variables

REM Get API keys from User environment variables
for /f "tokens=*" %%i in ('powershell -command "[System.Environment]::GetEnvironmentVariable('PINECONE_API_KEY', 'User')"') do set PINECONE_API_KEY=%%i
for /f "tokens=*" %%i in ('powershell -command "[System.Environment]::GetEnvironmentVariable('OPENAI_API_KEY', 'User')"') do set OPENAI_API_KEY=%%i
for /f "tokens=*" %%i in ('powershell -command "[System.Environment]::GetEnvironmentVariable('COHERE_API_KEY', 'User')"') do set COHERE_API_KEY=%%i

echo Starting server with API keys from User environment...

REM Start server in background
start /B "AgentServer" .venv\Scripts\python.exe server.py

REM Wait for server to start
timeout /t 4 /nobreak >nul

REM Run test
.venv\Scripts\python.exe test_simple_script.py

REM Kill server
taskkill /FI "WINDOWTITLE eq AgentServer*" /F >nul 2>&1
