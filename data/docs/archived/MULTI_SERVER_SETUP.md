# MULTI-SERVER SETUP GUIDE

## 🎯 Быстрый старт

Для запуска всех 3 FastAPI серверов + туннелей одной командой:

```powershell
cd C:\Users\kupit\w5\generate_script
.\launch_all_servers.ps1
```

---

## ⚙️ Конфигурация серверов

### Шаг 1: Откройте `launch_all_servers.ps1`

### Шаг 2: Настройте массив `$servers`

```powershell
$servers = @(
    @{
        Name = "generate_script"           # Имя проекта
        Path = "C:\Users\kupit\w5\generate_script"  # Путь к проекту
        Port = 8000                        # Порт сервера
        Command = "python -m uvicorn agent.api:app --host 0.0.0.0 --port 8000"
        EnvVars = @{                       # Переменные окружения
            OPENAI_API_KEY = [System.Environment]::GetEnvironmentVariable('OPENAI_API_KEY', 'User')
            PINECONE_API_KEY = [System.Environment]::GetEnvironmentVariable('PINECONE_API_KEY', 'User')
            COHERE_API_KEY = [System.Environment]::GetEnvironmentVariable('COHERE_API_KEY', 'User')
        }
    },
    
    # СЕРВЕР 2 - НАСТРОЙТЕ ЗДЕСЬ
    @{
        Name = "server_2"                  # ← ИЗМЕНИТЕ НА РЕАЛЬНОЕ ИМЯ
        Path = "C:\path\to\server2"        # ← ИЗМЕНИТЕ НА РЕАЛЬНЫЙ ПУТЬ
        Port = 8001
        Command = "python -m uvicorn main:app --host 0.0.0.0 --port 8001"  # ← ПРОВЕРЬТЕ КОМАНДУ
        EnvVars = @{
            OPENAI_API_KEY = [System.Environment]::GetEnvironmentVariable('OPENAI_API_KEY', 'User')
            # Добавьте другие переменные если нужны
        }
    },
    
    # СЕРВЕР 3 - НАСТРОЙТЕ ЗДЕСЬ
    @{
        Name = "server_3"                  # ← ИЗМЕНИТЕ НА РЕАЛЬНОЕ ИМЯ
        Path = "C:\path\to\server3"        # ← ИЗМЕНИТЕ НА РЕАЛЬНЫЙ ПУТЬ
        Port = 8002
        Command = "python -m uvicorn main:app --host 0.0.0.0 --port 8002"  # ← ПРОВЕРЬТЕ КОМАНДУ
        EnvVars = @{
            OPENAI_API_KEY = [System.Environment]::GetEnvironmentVariable('OPENAI_API_KEY', 'User')
        }
    }
)
```

---

## 🚀 Запуск

### Вариант 1: Автоматический (рекомендуется)

```powershell
.\launch_all_servers.ps1
```

**Скрипт автоматически:**
- ✅ Проверит занятые порты и освободит их
- ✅ Экспортирует переменные окружения
- ✅ Запустит все FastAPI серверы в отдельных окнах
- ✅ Проверит health check каждого сервера
- ✅ Создаст cloudflared туннель для каждого сервера
- ✅ Выведет финальный отчет с PID и портами

### Вариант 2: Ручной (для отладки)

```powershell
# Запуск сервера 1
$env:OPENAI_API_KEY = [System.Environment]::GetEnvironmentVariable('OPENAI_API_KEY', 'User')
$env:PINECONE_API_KEY = [System.Environment]::GetEnvironmentVariable('PINECONE_API_KEY', 'User')
$env:COHERE_API_KEY = [System.Environment]::GetEnvironmentVariable('COHERE_API_KEY', 'User')
python -m uvicorn agent.api:app --host 0.0.0.0 --port 8000

# В другом терминале - туннель 1
& "$env:USERPROFILE\cloudflared.exe" tunnel --url http://localhost:8000

# Повторить для серверов 2 и 3 с портами 8001, 8002
```

---

## 📋 Результат запуска

После запуска скрипта вы увидите:

```
═══════════════════════════════════════════════════════════════
✅ ВСЕ СЕРВЕРЫ И ТУННЕЛИ ЗАПУЩЕНЫ!
═══════════════════════════════════════════════════════════════

📋 Запущенные серверы:

  • generate_script
    Local:  http://localhost:8000
    PID:    12345

  • server_2
    Local:  http://localhost:8001
    PID:    12346

  • server_3
    Local:  http://localhost:8002
    PID:    12347

🌐 Туннели (проверьте окна PowerShell для URL):

  • generate_script (Port: 8000)
    PID:    12348
    URL:    Смотрите окно туннеля ↑

  • server_2 (Port: 8001)
    PID:    12349
    URL:    Смотрите окно туннеля ↑

  • server_3 (Port: 8002)
    PID:    12350
    URL:    Смотрите окно туннеля ↑
```

### Где найти URL туннелей:

**Откройте окна PowerShell** с туннелями и найдите строку:

```
Your quick Tunnel: https://abc-def-ghi-location.trycloudflare.com
```

---

## 🎯 Настройка n8n

### Для каждого сервера создайте HTTP Request Node:

#### Server 1 (generate_script):
- **URL:** `https://xxx-yyy-zzz.trycloudflare.com/generate-script`
- **Method:** POST
- **Body:** 
```json
{
  "project_name": "Test Project",
  "genre": "Thriller",
  "story_idea": "Your story idea",
  "duration": 1
}
```

#### Server 2:
- **URL:** `https://aaa-bbb-ccc.trycloudflare.com/your-endpoint`
- **Method:** POST
- **Body:** Ваш формат данных

#### Server 3:
- **URL:** `https://ddd-eee-fff.trycloudflare.com/your-endpoint`
- **Method:** POST
- **Body:** Ваш формат данных

---

## 🔧 Управление процессами

### Проверить запущенные серверы:

```powershell
# Проверить процессы на портах
Get-NetTCPConnection -LocalPort 8000,8001,8002 | Select-Object LocalPort, State, OwningProcess
```

### Остановить все серверы:

```powershell
# Остановить процессы на портах 8000-8002
8000..8002 | ForEach-Object {
    Get-NetTCPConnection -LocalPort $_ -ErrorAction SilentlyContinue | 
    ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
}
```

### Остановить конкретный сервер:

```powershell
# Остановить сервер на порту 8001
Get-NetTCPConnection -LocalPort 8001 | ForEach-Object {
    Stop-Process -Id $_.OwningProcess -Force
}
```

### Перезапустить все:

```powershell
# Остановить все
8000..8002 | ForEach-Object {
    Get-NetTCPConnection -LocalPort $_ -ErrorAction SilentlyContinue | 
    ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
}

# Подождать 2 секунды
Start-Sleep -Seconds 2

# Запустить заново
.\launch_all_servers.ps1
```

---

## 📊 Архитектура

```
┌─────────────────────────────────────────────────────────────┐
│                          N8N WORKFLOW                        │
└────────────┬──────────────┬──────────────┬──────────────────┘
             │              │              │
             ▼              ▼              ▼
    ┌────────────────┐ ┌────────────────┐ ┌────────────────┐
    │ HTTP Request 1 │ │ HTTP Request 2 │ │ HTTP Request 3 │
    └────────┬───────┘ └────────┬───────┘ └────────┬───────┘
             │                  │                  │
             │ HTTPS            │ HTTPS            │ HTTPS
             │                  │                  │
             ▼                  ▼                  ▼
    ┌────────────────┐ ┌────────────────┐ ┌────────────────┐
    │  Cloudflared   │ │  Cloudflared   │ │  Cloudflared   │
    │   Tunnel 1     │ │   Tunnel 2     │ │   Tunnel 3     │
    └────────┬───────┘ └────────┬───────┘ └────────┬───────┘
             │                  │                  │
             │ HTTP             │ HTTP             │ HTTP
             │                  │                  │
             ▼                  ▼                  ▼
    ┌────────────────┐ ┌────────────────┐ ┌────────────────┐
    │ FastAPI:8000   │ │ FastAPI:8001   │ │ FastAPI:8002   │
    │ generate_script│ │   server_2     │ │   server_3     │
    └────────────────┘ └────────────────┘ └────────────────┘
```

---

## ⚠️ Важные замечания

### 1. Cloudflared URL меняются

**Проблема:** При каждом перезапуске cloudflared генерирует новый URL

**Решение А (бесплатное):**
- Запускайте туннели один раз утром
- Копируйте URL в n8n
- Не перезапускайте туннели без необходимости

**Решение Б (платное, постоянные URL):**
```powershell
# Зарегистрироваться на cloudflare.com
# Создать Named Tunnel с постоянным доменом
cloudflared tunnel login
cloudflared tunnel create my-tunnel
cloudflared tunnel route dns my-tunnel server1.yourdomain.com
```

### 2. Порты

**Текущая конфигурация:**
- Server 1: 8000
- Server 2: 8001
- Server 3: 8002

**Изменить порты:**
Отредактируйте `$servers` массив в `launch_all_servers.ps1`

### 3. Переменные окружения

**Каждый сервер может использовать разные API keys:**

```powershell
EnvVars = @{
    OPENAI_API_KEY = [System.Environment]::GetEnvironmentVariable('OPENAI_API_KEY', 'User')
    CUSTOM_KEY_1 = [System.Environment]::GetEnvironmentVariable('CUSTOM_KEY_1', 'User')
    CUSTOM_KEY_2 = "hardcoded-value"  # Не рекомендуется
}
```

### 4. Health Check

Скрипт проверяет endpoints:
1. `http://localhost:PORT/health`
2. `http://localhost:PORT/` (если /health не существует)

**Если ваш сервер использует другой endpoint:**

Отредактируйте секцию "ПРОВЕРКА СЕРВЕРОВ" в скрипте.

---

## 🐛 Troubleshooting

### Проблема: "Port already in use"

**Решение:**
```powershell
# Скрипт автоматически освобождает порты
# Если нужно вручную:
Get-NetTCPConnection -LocalPort 8000 | ForEach-Object {
    Stop-Process -Id $_.OwningProcess -Force
}
```

### Проблема: "Cloudflared not found"

**Решение:**
```powershell
# Скачать cloudflared
Invoke-WebRequest -Uri "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe" -OutFile "$env:USERPROFILE\cloudflared.exe"

# Проверить
Test-Path "$env:USERPROFILE\cloudflared.exe"
```

### Проблема: Сервер не отвечает на health check

**Причины:**
1. Сервер еще не запустился (подождите больше времени)
2. Ошибка в коде сервера (проверьте окно PowerShell с логами)
3. Неправильная команда запуска (проверьте `Command` в конфигурации)

**Решение:**
- Откройте окно PowerShell с сервером
- Проверьте логи на ошибки
- Запустите сервер вручную для отладки

### Проблема: n8n не может соединиться с туннелем

**Проверка:**
```powershell
# Проверить tunnel URL в браузере
# Должен открыться ответ от FastAPI
```

**Если не работает:**
1. Проверьте что туннель запущен (окно PowerShell)
2. Скопируйте точный URL из логов cloudflared
3. Проверьте что сервер отвечает локально: `http://localhost:8000/health`

---

## 📝 Пример workflow для VS Code

### Простые команды для ассистента:

**Запустить все серверы:**
```
Запусти все серверы
```

**Остановить все серверы:**
```
Останови все серверы
```

**Перезапустить:**
```
Перезапусти все серверы
```

**Проверить статус:**
```
Покажи статус серверов
```

Ассистент автоматически выполнит соответствующие PowerShell команды.

---

## ✅ Чек-лист готовности

### Перед первым запуском:

- [ ] Cloudflared скачан: `$env:USERPROFILE\cloudflared.exe`
- [ ] Windows environment variables установлены (OPENAI_API_KEY и др.)
- [ ] Конфигурация серверов в `launch_all_servers.ps1` обновлена
- [ ] Пути к проектам серверов 2 и 3 правильные
- [ ] Команды запуска серверов 2 и 3 правильные
- [ ] n8n установлен и запущен

### После запуска:

- [ ] Все серверы показывают "HEALTHY" или "RUNNING"
- [ ] Туннели показывают URL в окнах PowerShell
- [ ] Каждый сервер отвечает локально (localhost:8000/8001/8002)
- [ ] URL туннелей скопированы в n8n HTTP Request nodes
- [ ] Тестовый запрос из n8n успешен

---

**Создано:** 2026-03-05  
**Версия:** 1.0  
**Проект:** generate_script
