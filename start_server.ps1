# start_server.ps1
# Startup script for FastAPI server with environment variables

Write-Host "=" * 80
Write-Host "FASTAPI SERVER STARTUP SCRIPT"
Write-Host "=" * 80

# Export User environment variables to current PowerShell session
Write-Host "`nExporting Windows User environment variables..."
$env:OPENAI_API_KEY = [System.Environment]::GetEnvironmentVariable('OPENAI_API_KEY', 'User')
$env:PINECONE_API_KEY = [System.Environment]::GetEnvironmentVariable('PINECONE_API_KEY', 'User')
$env:COHERE_API_KEY = [System.Environment]::GetEnvironmentVariable('COHERE_API_KEY', 'User')
$env:SERPAPI_API_KEY = [System.Environment]::GetEnvironmentVariable('SERPAPI_API_KEY', 'User')

# Verify variables
Write-Host "`nEnvironment variables loaded:"
Write-Host "  OPENAI_API_KEY: $(if ($env:OPENAI_API_KEY) { '✓ SET (' + $env:OPENAI_API_KEY.Length + ' chars)' } else { '✗ NOT SET' })"
Write-Host "  PINECONE_API_KEY: $(if ($env:PINECONE_API_KEY) { '✓ SET (' + $env:PINECONE_API_KEY.Length + ' chars)' } else { '✗ NOT SET' })"
Write-Host "  COHERE_API_KEY: $(if ($env:COHERE_API_KEY) { '✓ SET (' + $env:COHERE_API_KEY.Length + ' chars)' } else { '✗ NOT SET' })"
Write-Host "  SERPAPI_API_KEY: $(if ($env:SERPAPI_API_KEY) { '✓ SET (' + $env:SERPAPI_API_KEY.Length + ' chars)' } else { '✗ NOT SET (optional)' })"

# Check if all required variables are set
if (-not $env:OPENAI_API_KEY -or -not $env:PINECONE_API_KEY -or -not $env:COHERE_API_KEY) {
    Write-Host "`n✗ ERROR: Missing required environment variables!" -ForegroundColor Red
    Write-Host "Please set them using:" -ForegroundColor Yellow
    Write-Host "  [System.Environment]::SetEnvironmentVariable('VAR_NAME', 'value', 'User')" -ForegroundColor Yellow
    exit 1
}

Write-Host "`n✓ All required variables set!`n"
Write-Host "=" * 80
Write-Host "Starting FastAPI server on http://localhost:8000"
Write-Host "=" * 80
Write-Host ""

# Start server
python -m uvicorn agent.api:app --host 0.0.0.0 --port 8000
