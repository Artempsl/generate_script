# N8N INTEGRATION GUIDE

## ✅ Статус готовности

**Код полностью готов** для интеграции с n8n через FastAPI + ngrok!

---

## 📋 Предварительные требования

1. ✅ **FastAPI сервер** - работает на `localhost:8000`
2. ✅ **ngrok** - установлен и настроен
3. ✅ **Windows Environment Variables** - API keys установлены как глобальные переменные Windows
4. ✅ **n8n** - установлен и запущен

### Проверка API ключей

Убедитесь, что следующие переменные установлены в Windows (User environment variables):

```powershell
# Проверить установленные переменные:
[System.Environment]::GetEnvironmentVariable('OPENAI_API_KEY', 'User')
[System.Environment]::GetEnvironmentVariable('PINECONE_API_KEY', 'User')
[System.Environment]::GetEnvironmentVariable('COHERE_API_KEY', 'User')
[System.Environment]::GetEnvironmentVariable('SERPAPI_API_KEY', 'User')  # опционально
```

**Если не установлены**, используйте PowerShell:

```powershell
# Установить переменные (замените на ваши ключи):
[System.Environment]::SetEnvironmentVariable('OPENAI_API_KEY', 'sk-...', 'User')
[System.Environment]::SetEnvironmentVariable('PINECONE_API_KEY', 'your-key', 'User')
[System.Environment]::SetEnvironmentVariable('COHERE_API_KEY', 'your-key', 'User')
[System.Environment]::SetEnvironmentVariable('SERPAPI_API_KEY', 'your-key', 'User')
```

⚠️ **После установки** перезапустите PowerShell/IDE

---

## 🚀 Шаг 1: Запуск FastAPI сервера

### Команда запуска:

**Рекомендуемый способ** (экспорт переменных вручную):

```powershell
# Экспортировать переменные в текущую сессию PowerShell
$env:OPENAI_API_KEY = [System.Environment]::GetEnvironmentVariable('OPENAI_API_KEY', 'User')
$env:PINECONE_API_KEY = [System.Environment]::GetEnvironmentVariable('PINECONE_API_KEY', 'User')
$env:COHERE_API_KEY = [System.Environment]::GetEnvironmentVariable('COHERE_API_KEY', 'User')
$env:SERPAPI_API_KEY = [System.Environment]::GetEnvironmentVariable('SERPAPI_API_KEY', 'User')

# Запустить сервер
python -m uvicorn agent.api:app --host 0.0.0.0 --port 8000
```

⚠️ **Важно:** Windows User environment variables **не наследуются** Python subprocess автоматически. Нужно экспортировать их в текущую PowerShell сессию перед запуском uvicorn.

**Альтернативный способ** (через скрипт - может не работать):

```powershell
# В корневой папке проекта
.\start_server.ps1
```

⚠️ **Внимание:** Этот способ может быть заблокирован политикой выполнения PowerShell. Если получаете ошибку "running scripts is disabled", используйте рекомендуемый способ выше.

### Проверка запуска:

Откройте в браузере: **http://localhost:8000**

Вы должны увидеть:
```json
{
  "service": "Script Generation Agent Backend",
  "version": "2.0.0",
  "status": "operational",
  "endpoints": {
    "generate": "POST /generate-script",
    "test": "GET /test",
    "docs": "GET /docs",
    "health": "GET /health"
  }
}
```

### Health Check:

**GET** http://localhost:8000/health

```json
{
  "status": "healthy",
  "timestamp": "2026-03-04T18:00:00.000000+00:00",
  "database": {
    "connected": true,
    "total_executions": 5
  },
  "environment": {
    "OPENAI_API_KEY": "✓",
    "PINECONE_API_KEY": "✓",
    "COHERE_API_KEY": "✓",
    "SERPAPI_API_KEY": "✗ (optional)"
  }
}
```

---

## 🌐 Шаг 2: Запуск ngrok

### Команда:

```bash
ngrok http 8000
```

### Вывод ngrok:

```
Session Status                online
Account                       [Your Account]
Version                       3.x.x
Region                        [Your Region]
Forwarding                    https://abc123def456.ngrok-free.app -> http://localhost:8000
```

### ⚠️ ВАЖНО:

**Скопируйте URL:** `https://abc123def456.ngrok-free.app`

Это и есть ваш **публичный URL** для n8n.

### Проверка ngrok URL:

Откройте в браузере: **https://abc123def456.ngrok-free.app**

Должны увидеть тот же JSON ответ, что и на localhost:8000.

---

## 🎯 Шаг 3: Настройка n8n Execution Node

### Формат входных данных

n8n отправляет **прямой массив**:

```json
[
  {
    "isValid": true,
    "projectName": "My Project Name",
    "genre": "Thriller",
    "storyIdea": "A detective realizes the killer is someone they've been talking to all along",
    "duration": 1
  }
]
```

### Настройки HTTP Request Node в n8n:

#### 1. **Method:** `POST`

#### 2. **URL:** 
```
https://YOUR_NGROK_URL.ngrok-free.app/generate-script
```

**Пример:**
```
https://abc123def456.ngrok-free.app/generate-script
```

#### 3. **Authentication:** `None`

#### 4. **Headers:**

| Header Name | Value |
|-------------|-------|
| `Content-Type` | `application/json` |

#### 5. **Body Content Type:** `JSON`

#### 6. **JSON Body:**

##### Вариант A: Использовать данные из предыдущих узлов (рекомендуется)

Если у вас есть предыдущий узел, который генерирует данные:

```javascript
// В n8n Expression
[
  {
    "isValid": true,
    "projectName": "{{ $json.projectName }}",
    "genre": "{{ $json.genre }}",
    "storyIdea": "{{ $json.storyIdea }}",
    "duration": {{ $json.duration }}
  }
]
```

##### Вариант B: Статические тестовые данные

```json
[
  {
    "isValid": true,
    "projectName": "Test Project",
    "genre": "Thriller",
    "storyIdea": "A detective realizes the killer is someone they've been talking to all along",
    "duration": 1
  }
]
```

#### 7. **Options:**

- **Timeout:** `360000` (6 минут - больше чем MAX_TIMEOUT_SECONDS в API)
- **Response Format:** `JSON`
- **Redirect:** `Follow Redirect`

---

## 📤 Формат ответа от API

### Успешный ответ (HTTP 200):

```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "success",
  "project_name": "Test Project",
  "genre": "Thriller",
  "duration": 1,
  "language": "en",
  "script": "Detective Sarah sat in her cluttered office, case files sprawled across the desk like a chaotic mosaic. The killer had eluded her for months, leaving only cryptic messages and a trail of violence. Her phone buzzed—a text from Mark, her confidant, offering support...",
  "outline": "ACT I - SETUP (30%)...",
  "char_count": 1080,
  "target_chars": 1000,
  "iteration_count": 1,
  "tokens_used_total": 15281,
  "retrieved_sources_count": 5,
  "validation_passed": true,
  "created_at": "2026-03-04T18:00:00.000000+00:00"
}
```

### Ошибка валидации (HTTP 422):

```json
{
  "detail": [
    {
      "loc": ["body", 0, "duration"],
      "msg": "Duration must be between 1 and 60 minutes",
      "type": "value_error"
    }
  ]
}
```

### Ошибка выполнения (HTTP 500):

```json
{
  "detail": "Agent execution failed: OpenAI API rate limit exceeded"
}
```

---

## 🧪 Тестирование интеграции

### Тест 1: Health Check

**GET** `https://YOUR_NGROK_URL.ngrok-free.app/health`

**Ожидаемый результат:** HTTP 200 + JSON со статусом "healthy"

### Тест 2: Direct API Call (PowerShell)

```powershell
# Замените YOUR_NGROK_URL на ваш реальный URL
$url = "https://YOUR_NGROK_URL.ngrok-free.app/generate-script"

$body = @"
[
  {
    "isValid": true,
    "projectName": "API Test",
    "genre": "Sci-Fi",
    "storyIdea": "A scientist discovers time travel but realizes every change creates a darker timeline",
    "duration": 1
  }
]
"@

$response = Invoke-RestMethod -Uri $url -Method POST -Body $body -ContentType "application/json"

Write-Host "Status: $($response.status)"
Write-Host "Script Length: $($response.char_count) chars"
Write-Host "Tokens Used: $($response.tokens_used_total)"
Write-Host "`nScript Preview:"
Write-Host $response.script.Substring(0, [Math]::Min(200, $response.script.Length))
```

### Тест 3: Full n8n Workflow

1. **Создайте новый workflow в n8n**

2. **Добавьте Manual Trigger Node**

3. **Добавьте HTTP Request Node:**
   - Method: POST
   - URL: `https://YOUR_NGROK_URL.ngrok-free.app/generate-script`
   - Body:
   ```json
   [
     {
       "isValid": true,
       "projectName": "n8n Test",
       "genre": "Horror",
       "storyIdea": "A family moves into a house where mirrors show reflections from the past",
       "duration": 1
     }
   ]
   ```

4. **Добавьте Code Node** (для обработки ответа):
   ```javascript
   // Extract script text
   const script = $input.first().json.script;
   const char_count = $input.first().json.char_count;
   const tokens = $input.first().json.tokens_used_total;
   
   return [
     {
       json: {
         script: script,
         length: char_count,
         tokens: tokens,
         success: true
       }
     }
   ];
   ```

5. **Запустите workflow**

6. **Проверьте результат** (должен появиться сгенерированный скрипт)

---

## 🔧 Параметры запроса

### Обязательные поля:

| Поле | Тип | Описание | Валидация |
|------|-----|----------|-----------|
| `isValid` | boolean | Флаг валидации | Должен быть `true` |
| `projectName` | string | Название проекта | 1-200 символов |
| `genre` | string | Жанр | 1-100 символов |
| `storyIdea` | string | Идея сценария | 10-5000 символов |
| `duration` | integer | Длительность (минуты) | 1-60 |

### Опциональные поля:

| Поле | Тип | Описание | По умолчанию |
|------|-----|----------|--------------|
| `request_id` | string | UUID для идемпотентности | Автогенерация |

---

## 🎨 Поддерживаемые жанры

- **Horror** - Ужасы
- **Thriller** - Триллер
- **Drama** - Драма
- **Noir Detective** - Нуар/Детектив
- **Sci-Fi** - Научная фантастика
- **Comedy** - Комедия
- **Fantasy** - Фэнтези
- **Romance** - Романтика
- **Action** - Боевик

---

## 🌍 Поддерживаемые языки

### Автоопределение языка:

API автоматически определяет язык по тексту `storyIdea`:

- **English:** Если идея на английском
- **Russian (Русский):** Если идея на русском

### Примеры:

**English:**
```json
{
  "storyIdea": "A detective realizes the killer is someone they've been talking to",
  // → language: "en"
}
```

**Russian:**
```json
{
  "storyIdea": "Детектив понимает что убийца это тот с кем он разговаривал",
  // → language: "ru"
}
```

---

## ⚙️ Расчет длительности

### Целевая длина скрипта:

```
target_chars = duration * char_rate
```

**Char rates:**
- **English:** 1000 символов/минута
- **Russian:** 1450 символов/минута

### Примеры:

| Duration | Language | Target Chars |
|----------|----------|--------------|
| 1 min | English | 1,000 chars |
| 1 min | Russian | 1,450 chars |
| 3 min | English | 3,000 chars |
| 5 min | Russian | 7,250 chars |
| 10 min | English | 10,000 chars |

### Допустимое отклонение:

API принимает скрипты в диапазоне **90-110%** от целевой длины.

---

## 🔄 Идемпотентность

### Request ID

Если вы передаете тот же `request_id`, API вернет **кэшированный результат** из базы данных:

```json
[
  {
    "isValid": true,
    "projectName": "Test",
    "genre": "Thriller",
    "storyIdea": "...",
    "duration": 1,
    "request_id": "my-unique-id-123"  // ← Фиксированный ID
  }
]
```

**Повторный запрос с тем же `request_id`:**
- ✅ Мгновенный ответ (из БД)
- ✅ Не тратит tokens
- ✅ Идентичный результат

**Использование:**
- Защита от дублирующих запросов
- Retry logic без повторной генерации
- Cost optimization

---

## 📊 Метрики производительности

### Типичное время выполнения:

| Duration | Avg Time | Max Time |
|----------|----------|----------|
| 1 min | 60-90s | 120s |
| 3 min | 90-120s | 180s |
| 5 min | 120-180s | 240s |
| 10 min | 180-240s | 300s |

### Token usage:

| Duration | Avg Tokens | Cost (GPT-4o-mini) |
|----------|------------|---------------------|
| 1 min | ~15,000 | $0.0062 |
| 3 min | ~16,500 | $0.0067 |
| 5 min | ~24,000 | $0.0098 |

---

## 🚨 Troubleshooting

### Проблема 1: "Connection refused"

**Причина:** FastAPI сервер не запущен

**Решение:**
```powershell
python -m uvicorn agent.api:app --host 0.0.0.0 --port 8000
```

### Проблема 2: "Timeout after 300s"

**Причина:** Агент не успел выполниться за 5 минут

**Решение:**
- Проверьте API keys в `.env`
- Уменьшите `duration` (попробуйте 1-2 минуты)
- Проверьте логи сервера на ошибки

### Проблема 3: "No module named 'pinecone'"

**Причина:** Отсутствует зависимость

**Решение:**
```powershell
pip install pinecone==8.1.0
# Перезапустите сервер
```

### Проблема 4: "Environment validation failed"

**Причина:** Не все API keys установлены как Windows environment variables

**Решение:**

Установите переменные через PowerShell:

```powershell
# Установите все необходимые ключи:
[System.Environment]::SetEnvironmentVariable('OPENAI_API_KEY', 'sk-your-key-here', 'User')
[System.Environment]::SetEnvironmentVariable('PINECONE_API_KEY', 'your-pinecone-key', 'User')
[System.Environment]::SetEnvironmentVariable('COHERE_API_KEY', 'your-cohere-key', 'User')

# Опционально (для веб-поиска):
[System.Environment]::SetEnvironmentVariable('SERPAPI_API_KEY', 'your-serpapi-key', 'User')

# Проверьте установку:
[System.Environment]::GetEnvironmentVariable('OPENAI_API_KEY', 'User')
```

⚠️ После установки **перезапустите PowerShell** и **FastAPI сервер**

### Проблема 5: ngrok требует авторизацию

**Причина:** Бесплатный план ngrok показывает warning page

**Решение:**
- Зарегистрируйтесь на ngrok.com
- Получите authtoken
- Запустите: `ngrok config add-authtoken YOUR_TOKEN`

### Проблема 6: "422 Unprocessable Entity"

**Причина:** Невалидные данные в запросе

**Решение:**
Проверьте:
- `isValid` = `true` (boolean, не string)
- `duration` = число от 1 до 60
- `storyIdea` = минимум 10 символов

---

## 📝 Пример полного workflow в n8n

```
┌─────────────────┐
│ Manual Trigger  │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ HTTP Request                        │
│ POST /generate-script               │
│                                     │
│ Body:                               │
│ [                                   │
│   {                                 │
│     "isValid": true,                │
│     "projectName": "n8n Demo",      │
│     "genre": "Sci-Fi",              │
│     "storyIdea": "Time travel...",  │
│     "duration": 1                   │
│   }                                 │
│ ]                                   │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ Code Node (Extract Script)          │
│                                     │
│ return [{                           │
│   json: {                           │
│     script: $input.first().json.    │
│              script,                │
│     length: $input.first().json.    │
│              char_count             │
│   }                                 │
│ }];                                 │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ Write to File / Database / Email    │
│ (Your choice)                       │
└─────────────────────────────────────┘
```

---

## ✅ Чек-лист готовности

- [x] Windows Environment Variables установлены (OPENAI_API_KEY, PINECONE_API_KEY, COHERE_API_KEY)
- [x] FastAPI сервер запущен на localhost:8000
- [x] Health check возвращает "healthy"
- [ ] ngrok запущен и URL получен
- [ ] ngrok URL открывается в браузере
- [ ] n8n установлен и запущен
- [ ] HTTP Request node настроен с правильным URL
- [ ] Тестовый запрос успешно выполнен

---

## 📞 Поддержка

**Логи сервера:**
Все запросы логируются в консоль, где запущен FastAPI.

**Database:**
Все выполнения сохраняются в `agent.db` для анализа.

**Документация API:**
http://localhost:8000/docs (Swagger UI)

---

## 🚀 Multi-Server Setup (3+ серверов)

Если вам нужно запустить **несколько FastAPI серверов** одновременно (например, для разных n8n workflows):

### Автоматический запуск всех серверов

```powershell
# Запустить все серверы + туннели одной командой
.\launch_all_servers.ps1
```

**Скрипт автоматически:**
- ✅ Запустит 3 FastAPI сервера на портах 8000, 8001, 8002
- ✅ Создаст cloudflared туннель для каждого
- ✅ Проверит health check
- ✅ Выведет все URL для n8n

### Конфигурация дополнительных серверов

Откройте `launch_all_servers.ps1` и настройте массив `$servers`:

```powershell
$servers = @(
    @{
        Name = "server_2"
        Path = "C:\path\to\server2"      # ← Ваш путь
        Port = 8001
        Command = "python -m uvicorn main:app --host 0.0.0.0 --port 8001"
        EnvVars = @{
            OPENAI_API_KEY = [System.Environment]::GetEnvironmentVariable('OPENAI_API_KEY', 'User')
        }
    }
    # ... добавьте больше серверов
)
```

### Детальная документация

📖 **См. полное руководство:** [MULTI_SERVER_SETUP.md](MULTI_SERVER_SETUP.md)

Включает:
- Конфигурация множественных серверов
- Управление процессами
- Архитектурная диаграмма
- Troubleshooting для мульти-сервер среды

---

**Создано:** 2026-03-04  
**Обновлено:** 2026-03-05  
**Версия:** 1.1  
**Проект:** generate_script
