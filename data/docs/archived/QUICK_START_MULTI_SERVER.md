# 🎬 Multi-Server Launcher - Быстрый старт

## Что это?

Автоматический запуск **3 FastAPI серверов + 3 туннелей** для интеграции с n8n одной командой.

---

## 🚀 Запуск

```powershell
cd C:\Users\kupit\w5\generate_script
.\launch_all_servers.ps1
```

---

## ⚙️ Первоначальная настройка

### 1. Установите cloudflared (один раз)

```powershell
# Скачать
Invoke-WebRequest -Uri "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe" -OutFile "$env:USERPROFILE\cloudflared.exe"

# Проверить
Test-Path "$env:USERPROFILE\cloudflared.exe"
```

### 2. Настройте серверы в `launch_all_servers.ps1`

Откройте файл и измените:

```powershell
$servers = @(
    @{
        Name = "generate_script"  # ✅ Уже настроен
        Path = "C:\Users\kupit\w5\generate_script"
        Port = 8000
        # ...
    },
    @{
        Name = "server_2"         # ⚠️ НАСТРОЙТЕ ЗДЕСЬ
        Path = "C:\path\to\server2"  # ← ИЗМЕНИТЕ
        Port = 8001
        Command = "python -m uvicorn main:app --host 0.0.0.0 --port 8001"
        # ...
    },
    @{
        Name = "server_3"         # ⚠️ НАСТРОЙТЕ ЗДЕСЬ
        Path = "C:\path\to\server3"  # ← ИЗМЕНИТЕ
        Port = 8002
        # ...
    }
)
```

---

## 📋 После запуска

### Вы увидите:

```
✅ ВСЕ СЕРВЕРЫ И ТУННЕЛИ ЗАПУЩЕНЫ!

📋 Запущенные серверы:
  • generate_script - http://localhost:8000
  • server_2        - http://localhost:8001
  • server_3        - http://localhost:8002

🌐 Туннели:
  Проверьте окна PowerShell для URL
```

### Откройте окна туннелей и найдите URL:

```
Your quick Tunnel: https://xxx-yyy-zzz.trycloudflare.com
```

### Используйте URL в n8n:

```
Server 1: https://xxx-yyy-zzz.trycloudflare.com/generate-script
Server 2: https://aaa-bbb-ccc.trycloudflare.com/your-endpoint
Server 3: https://ddd-eee-fff.trycloudflare.com/your-endpoint
```

---

## 🔧 Управление

### Остановить все серверы:

```powershell
8000..8002 | ForEach-Object {
    Get-NetTCPConnection -LocalPort $_ -ErrorAction SilentlyContinue | 
    ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
}
```

### Проверить статус:

```powershell
Get-NetTCPConnection -LocalPort 8000,8001,8002 | 
    Select-Object LocalPort, State, OwningProcess
```

### Перезапустить:

```powershell
# Остановить
8000..8002 | ForEach-Object {
    Get-NetTCPConnection -LocalPort $_ -ErrorAction SilentlyContinue | 
    ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
}

# Запустить
.\launch_all_servers.ps1
```

---

## 📖 Полная документация

- **[MULTI_SERVER_SETUP.md](MULTI_SERVER_SETUP.md)** - Детальное руководство
- **[N8N_INTEGRATION_GUIDE.md](N8N_INTEGRATION_GUIDE.md)** - Интеграция с n8n
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Архитектура проекта

---

## ❓ Troubleshooting

### "Cloudflared not found"
```powershell
Invoke-WebRequest -Uri "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe" -OutFile "$env:USERPROFILE\cloudflared.exe"
```

### "Port already in use"
Скрипт автоматически освобождает порты. Если не помогло:
```powershell
Get-NetTCPConnection -LocalPort 8000 | 
    ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
```

### Сервер не запустился
Откройте окно PowerShell с логами сервера и проверьте ошибки.

---

## 🤖 Команды для VS Code Copilot

**Запустить все серверы:**
> Запусти все серверы

**Остановить:**
> Останови все серверы

**Проверить статус:**
> Покажи статус серверов на портах 8000-8002

**Перезапустить:**
> Перезапусти все серверы

---

**Версия:** 1.0  
**Дата:** 2026-03-05
