# ============================================================================
# MULTI-SERVER LAUNCHER - FastAPI + Cloudflared Tunnels
# ============================================================================
# Этот скрипт запускает несколько FastAPI серверов и создает туннели для n8n
# ============================================================================

Write-Host "🚀 Запуск FastAPI серверов и туннелей..." -ForegroundColor Cyan
Write-Host ""

# ----------------------------------------------------------------------------
# КОНФИГУРАЦИЯ СЕРВЕРОВ
# ----------------------------------------------------------------------------
# Добавьте свои серверы в этот массив:
$servers = @(
    @{
        Name = "generate_script"
        Path = "C:\Users\kupit\w5\generate_script"
        Port = 8000
        Command = "python -m uvicorn agent.api:app --host 0.0.0.0 --port 8000"
        EnvVars = @{
            OPENAI_API_KEY = [System.Environment]::GetEnvironmentVariable('OPENAI_API_KEY', 'User')
            PINECONE_API_KEY = [System.Environment]::GetEnvironmentVariable('PINECONE_API_KEY', 'User')
            COHERE_API_KEY = [System.Environment]::GetEnvironmentVariable('COHERE_API_KEY', 'User')
            SERPAPI_API_KEY = [System.Environment]::GetEnvironmentVariable('SERPAPI_API_KEY', 'User')
        }
    },
    @{
        Name = "server_2"
        Path = "C:\path\to\server2"  # ← ИЗМЕНИТЕ НА РЕАЛЬНЫЙ ПУТЬ
        Port = 8001
        Command = "python -m uvicorn main:app --host 0.0.0.0 --port 8001"  # ← ИЗМЕНИТЕ КОМАНДУ
        EnvVars = @{
            # Добавьте переменные окружения для сервера 2
            OPENAI_API_KEY = [System.Environment]::GetEnvironmentVariable('OPENAI_API_KEY', 'User')
        }
    },
    @{
        Name = "server_3"
        Path = "C:\path\to\server3"  # ← ИЗМЕНИТЕ НА РЕАЛЬНЫЙ ПУТЬ
        Port = 8002
        Command = "python -m uvicorn main:app --host 0.0.0.0 --port 8002"  # ← ИЗМЕНИТЕ КОМАНДУ
        EnvVars = @{
            # Добавьте переменные окружения для сервера 3
            OPENAI_API_KEY = [System.Environment]::GetEnvironmentVariable('OPENAI_API_KEY', 'User')
        }
    }
)

# ----------------------------------------------------------------------------
# ПУТЬ К CLOUDFLARED
# ----------------------------------------------------------------------------
$cloudflaredPath = "$env:USERPROFILE\cloudflared.exe"

if (-not (Test-Path $cloudflaredPath)) {
    Write-Host "❌ Cloudflared не найден: $cloudflaredPath" -ForegroundColor Red
    Write-Host "Скачайте: https://github.com/cloudflare/cloudflared/releases" -ForegroundColor Yellow
    exit 1
}

# ----------------------------------------------------------------------------
# ЗАПУСК СЕРВЕРОВ
# ----------------------------------------------------------------------------
Write-Host "📦 Запуск FastAPI серверов..." -ForegroundColor Green
Write-Host ""

$serverProcesses = @()

foreach ($server in $servers) {
    Write-Host "  → Запуск: $($server.Name) (Port: $($server.Port))" -ForegroundColor Yellow
    
    # Проверка порта
    $portInUse = Get-NetTCPConnection -LocalPort $server.Port -ErrorAction SilentlyContinue
    if ($portInUse) {
        Write-Host "    ⚠️  Порт $($server.Port) уже занят. Освобождаю..." -ForegroundColor Yellow
        Get-NetTCPConnection -LocalPort $server.Port | ForEach-Object {
            Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue
        }
        Start-Sleep -Seconds 1
    }
    
    # Формирование команды с переменными окружения
    $envVarsString = ""
    foreach ($key in $server.EnvVars.Keys) {
        $value = $server.EnvVars[$key]
        if ($value) {
            $envVarsString += "`$env:$key = '$value'; "
        }
    }
    
    $fullCommand = "$envVarsString cd '$($server.Path)'; $($server.Command)"
    
    # Запуск сервера в новом окне PowerShell
    $process = Start-Process powershell -ArgumentList @(
        "-NoExit",
        "-Command",
        $fullCommand
    ) -PassThru
    
    $serverProcesses += @{
        Name = $server.Name
        Port = $server.Port
        ProcessId = $process.Id
    }
    
    Write-Host "    ✓ PID: $($process.Id)" -ForegroundColor Green
}

Write-Host ""
Write-Host "⏳ Ожидание запуска серверов (10 секунд)..." -ForegroundColor Cyan
Start-Sleep -Seconds 10

# ----------------------------------------------------------------------------
# ПРОВЕРКА СЕРВЕРОВ
# ----------------------------------------------------------------------------
Write-Host ""
Write-Host "🔍 Проверка серверов..." -ForegroundColor Green
Write-Host ""

$healthyServers = @()

foreach ($serverInfo in $serverProcesses) {
    $port = $serverInfo.Port
    $name = $serverInfo.Name
    
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:$port/health" -Method GET -TimeoutSec 5 -ErrorAction Stop
        Write-Host "  ✓ $name (Port: $port) - HEALTHY" -ForegroundColor Green
        $healthyServers += $serverInfo
    } catch {
        try {
            # Попробовать корневой endpoint если /health не существует
            $response = Invoke-RestMethod -Uri "http://localhost:$port/" -Method GET -TimeoutSec 5 -ErrorAction Stop
            Write-Host "  ✓ $name (Port: $port) - RUNNING" -ForegroundColor Green
            $healthyServers += $serverInfo
        } catch {
            Write-Host "  ⚠️  $name (Port: $port) - НЕ ОТВЕЧАЕТ" -ForegroundColor Yellow
            Write-Host "      Проверьте окно PowerShell для логов" -ForegroundColor Gray
        }
    }
}

if ($healthyServers.Count -eq 0) {
    Write-Host ""
    Write-Host "❌ Ни один сервер не запустился успешно" -ForegroundColor Red
    Write-Host "Проверьте логи в окнах PowerShell" -ForegroundColor Yellow
    exit 1
}

# ----------------------------------------------------------------------------
# ЗАПУСК ТУННЕЛЕЙ
# ----------------------------------------------------------------------------
Write-Host ""
Write-Host "🌐 Запуск Cloudflared туннелей..." -ForegroundColor Green
Write-Host ""

$tunnelProcesses = @()

foreach ($serverInfo in $healthyServers) {
    $port = $serverInfo.Port
    $name = $serverInfo.Name
    
    Write-Host "  → Создание туннеля для $name (localhost:$port)..." -ForegroundColor Yellow
    
    $process = Start-Process powershell -ArgumentList @(
        "-NoExit",
        "-Command",
        "Write-Host '🌐 Туннель для: $name (Port: $port)' -ForegroundColor Cyan; & '$cloudflaredPath' tunnel --url http://localhost:$port"
    ) -PassThru
    
    $tunnelProcesses += @{
        Name = $name
        Port = $port
        ProcessId = $process.Id
    }
    
    Write-Host "    ✓ PID: $($process.Id)" -ForegroundColor Green
}

Write-Host ""
Write-Host "⏳ Ожидание установки туннелей (15 секунд)..." -ForegroundColor Cyan
Start-Sleep -Seconds 15

# ----------------------------------------------------------------------------
# ФИНАЛЬНЫЙ ОТЧЕТ
# ----------------------------------------------------------------------------
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "✅ ВСЕ СЕРВЕРЫ И ТУННЕЛИ ЗАПУЩЕНЫ!" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

Write-Host "📋 Запущенные серверы:" -ForegroundColor Yellow
Write-Host ""
foreach ($serverInfo in $healthyServers) {
    Write-Host "  • $($serverInfo.Name)" -ForegroundColor White
    Write-Host "    Local:  http://localhost:$($serverInfo.Port)" -ForegroundColor Gray
    Write-Host "    PID:    $($serverInfo.ProcessId)" -ForegroundColor Gray
    Write-Host ""
}

Write-Host "🌐 Туннели (проверьте окна PowerShell для URL):" -ForegroundColor Yellow
Write-Host ""
foreach ($tunnelInfo in $tunnelProcesses) {
    Write-Host "  • $($tunnelInfo.Name) (Port: $($tunnelInfo.Port))" -ForegroundColor White
    Write-Host "    PID:    $($tunnelInfo.ProcessId)" -ForegroundColor Gray
    Write-Host "    URL:    Смотрите окно туннеля ↑" -ForegroundColor Magenta
    Write-Host ""
}

Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

Write-Host "📝 ИНСТРУКЦИИ ДЛЯ N8N:" -ForegroundColor Green
Write-Host ""
Write-Host "  1. Откройте окна туннелей (PowerShell)" -ForegroundColor White
Write-Host "  2. Скопируйте URL вида: https://xxx-yyy-zzz.trycloudflare.com" -ForegroundColor White
Write-Host "  3. В n8n HTTP Request Node используйте:" -ForegroundColor White
Write-Host "     URL: https://xxx-yyy-zzz.trycloudflare.com/generate-script" -ForegroundColor Cyan
Write-Host "  4. Method: POST" -ForegroundColor White
Write-Host "  5. Body: JSON с вашими данными" -ForegroundColor White
Write-Host ""

Write-Host "⚠️  ВАЖНО:" -ForegroundColor Yellow
Write-Host "  • Не закрывайте окна PowerShell с серверами и туннелями" -ForegroundColor Gray
Write-Host "  • Cloudflared URL меняется при каждом перезапуске" -ForegroundColor Gray
Write-Host "  • Для остановки: закройте окна PowerShell или Ctrl+C" -ForegroundColor Gray
Write-Host ""

Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
