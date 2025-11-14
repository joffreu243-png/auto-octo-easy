# 🌐 Octo Browser Integration Guide

## Обзор

OctoMaster Pro теперь полностью интегрирован с **Octo Browser** - анти-детект браузером для автоматизации. Вы можете создавать workflow в визуальном редакторе, а затем экспортировать их как Python скрипты, которые автоматически запускают профили Octo Browser.

## Что нового

### ✅ Реализованные возможности:

1. **Octo API Client** - полноценный клиент для работы с Local API Octo Browser
2. **Диалог настроек Octo** - удобная настройка API токена
3. **Диалог экспорта с Octo** - выбор профиля и генерация готового скрипта
4. **Автоматическая генерация скриптов** - Playwright (async/sync) и Selenium

### 🎯 Основные преимущества:

- **Визуальное создание автоматизации** - используйте Inspector Mode для записи действий
- **Автоматический выбор профилей** - выбирайте нужный профиль из списка
- **Готовые скрипты** - экспортированный Python код готов к запуску
- **Поддержка прокси и fingerprints** - все настройки профиля сохраняются
- **Работа с тегами** - фильтрация профилей по тегам

## Быстрый старт

### Шаг 1: Настройка Octo Browser API

1. **Откройте Octo Browser**
2. **Перейдите в Settings → Additional**
3. **Скопируйте API Token**
4. **В OctoMaster Pro:**
   - Откройте `Tools → 🌐 Octo Browser Settings...` (или нажмите `Ctrl+Alt+O`)
   - Вставьте API Token
   - Нажмите "🔍 Test Connection" для проверки
   - Нажмите "💾 Save"

### Шаг 2: Создание workflow

1. **Создайте новый workflow** (Ctrl+N или File → New Workflow)
2. **Добавьте блоки** через Inspector Mode или вручную:
   - Откройте вкладку "🌐 Browser"
   - Введите URL (например, https://web.telegram.org)
   - Нажмите "🎯 Inspector"
   - Правый клик на элементы → выберите действие
3. **Блоки автоматически добавятся** на канвас

### Шаг 3: Экспорт скрипта с Octo

1. **Откройте File → Export → Export with 🌐 Octo Browser...** (или нажмите `Ctrl+Shift+E`)
2. **Выберите профиль Octo Browser** из списка
3. **Настройте параметры:**
   - Script Type: Playwright (async/sync) или Selenium
   - Headless Mode: включить/выключить
   - Include Comments: комментарии в коде
4. **Нажмите "🔨 Generate Preview"** для предпросмотра
5. **Нажмите "💾 Export Script"** и сохраните файл

### Шаг 4: Запуск скрипта

```bash
# Убедитесь что Octo Browser запущен
python your_workflow_octo.py
```

Скрипт автоматически:
- Подключится к Octo Browser API
- Запустит выбранный профиль
- Подключит Playwright/Selenium
- Выполнит все действия из workflow

## Примеры использования

### Пример 1: Автоматизация для Telegram

```python
# Workflow: telegram_automation_octo.py
import asyncio
import httpx
from playwright.async_api import async_playwright

OCTO_API_TOKEN = 'your-api-token-here'
OCTO_API_URL = 'http://localhost:58888'
PROFILE_UUID = 'profile-uuid-here'

async def start_octo_profile():
    """Start Octo Browser profile and return WebSocket endpoint."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f'{OCTO_API_URL}/api/profiles/start',
            headers={'X-Octo-Api-Token': OCTO_API_TOKEN},
            json={'uuid': PROFILE_UUID, 'headless': False}
        )
        data = response.json()['data']
        return data['ws_endpoint']

async def main():
    """Main workflow execution."""
    # Start Octo profile
    ws_endpoint = await start_octo_profile()
    print(f'Connected to Octo profile: {ws_endpoint}')

    # Connect Playwright to Octo Browser
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(ws_endpoint)
        context = browser.contexts[0]
        page = context.pages[0]

        # Execute workflow blocks
        await page.goto('https://web.telegram.org')
        await page.click('.input-field-input')
        await page.fill('.input-field-input', '+1234567890')
        await page.click('.btn-primary')

        # Keep browser open for inspection
        await page.wait_for_timeout(5000)
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
```

### Пример 2: Selenium с Octo

```python
import httpx
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

OCTO_API_TOKEN = 'your-api-token-here'
OCTO_API_URL = 'http://localhost:58888'
PROFILE_UUID = 'profile-uuid-here'

def start_octo_profile():
    """Start Octo Browser profile and return debug port."""
    with httpx.Client() as client:
        response = client.post(
            f'{OCTO_API_URL}/api/profiles/start',
            headers={'X-Octo-Api-Token': OCTO_API_TOKEN},
            json={'uuid': PROFILE_UUID, 'headless': False}
        )
        data = response.json()['data']
        return data['debug_port']

def main():
    """Main workflow execution."""
    # Start Octo profile
    debug_port = start_octo_profile()
    print(f'Octo profile started on port: {debug_port}')

    # Connect Selenium to Octo Browser
    options = Options()
    options.add_experimental_option('debuggerAddress', f'127.0.0.1:{debug_port}')

    driver = webdriver.Chrome(options=options)

    # Execute workflow blocks
    driver.get('https://example.com')
    driver.find_element(By.CSS_SELECTOR, '.login-btn').click()

    # Keep browser open
    time.sleep(5)
    driver.quit()

if __name__ == '__main__':
    main()
```

## Архитектура

### Компоненты:

1. **OctoAPIClient** (`octomaster/integrations/octo/api_client.py`)
   - Полный клиент для Local API
   - Методы: `list_profiles()`, `start_profile()`, `stop_profile()`, etc.
   - Асинхронный (httpx + asyncio)

2. **OctoSettingsDialog** (`octomaster/gui/dialogs/octo_settings_dialog.py`)
   - Настройка API Token
   - Проверка подключения
   - Сохранение настроек в `.octo_settings`

3. **OctoExportDialog** (`octomaster/gui/dialogs/octo_export_dialog.py`)
   - Выбор профиля из списка
   - Настройка параметров экспорта
   - Генерация Python кода
   - Предпросмотр скрипта

4. **Интеграция в MainWindow**
   - Новые пункты меню
   - Автоматическое сохранение/загрузка настроек
   - Удобные диалоги

### API Endpoints (Local API)

```
Base URL: http://localhost:58888/api

GET    /profiles              - Список профилей
GET    /profiles/{uuid}       - Детали профиля
POST   /profiles/start        - Запуск профиля
POST   /profiles/stop         - Остановка профиля
POST   /profiles              - Создание профиля
DELETE /profiles/{uuid}       - Удаление профиля
```

### Формат запроса Start Profile:

```json
{
  "uuid": "profile-uuid-here",
  "headless": false,
  "debug_port": 9222  // optional
}
```

### Формат ответа:

```json
{
  "data": {
    "uuid": "profile-uuid-here",
    "ws_endpoint": "ws://127.0.0.1:9222/devtools/browser/...",
    "debug_port": 9222,
    "selenium_port": null
  }
}
```

## Устранение неполадок

### Проблема: "Cannot connect to Octo Browser"

**Решение:**
1. Убедитесь что Octo Browser запущен
2. Проверьте что Local API включен в настройках
3. Проверьте порт (по умолчанию 58888)

### Проблема: "Invalid API token"

**Решение:**
1. Откройте Octo Browser → Settings → Additional
2. Скопируйте новый API Token
3. Обновите настройки в OctoMaster Pro

### Проблема: "Profile not found"

**Решение:**
1. Нажмите "🔄 Refresh Profiles" в диалоге экспорта
2. Убедитесь что профиль существует в Octo Browser

### Проблема: Скрипт не запускается

**Решение:**
1. Проверьте что Octo Browser запущен
2. Проверьте API Token в скрипте
3. Установите зависимости: `pip install playwright selenium httpx`

## Требования

### Зависимости Python:

```bash
pip install -r requirements.txt
```

Главные:
- `httpx[http2]>=0.25.0` - для HTTP запросов
- `playwright>=1.40.0` - для автоматизации
- `selenium>=4.15.0` - для Selenium скриптов
- `qasync>=0.24.0` - для async в PyQt6

### Требования Octo Browser:

- **Octo Browser** должен быть установлен и запущен
- **API Token** из Settings → Additional
- **Local API** должен быть доступен на порту 58888
- **Подписка**: Base или выше (для API доступа)

## Rate Limits

| Plan | Requests/Minute | Requests/Hour |
|------|----------------|---------------|
| Base | 50 | 500 |
| Team | 100 | 1,500 |
| Advanced | 200+ | 3,000+ |

**Примечание:** Только запросы `Start Profile` учитываются в лимитах.

## FAQ

### Q: Можно ли использовать несколько профилей одновременно?

A: Да! Создайте отдельные workflow для разных профилей и запустите скрипты параллельно. Учитывайте лимиты вашей подписки.

### Q: Как передать переменные в скрипт?

A: Используйте аргументы командной строки или конфигурационные файлы. Пример:

```python
import sys

PROFILE_UUID = sys.argv[1] if len(sys.argv) > 1 else 'default-uuid'
```

### Q: Можно ли использовать headless mode?

A: Да! В диалоге экспорта включите "Headless Mode". Это полезно для серверного запуска.

### Q: Поддерживаются ли cookies и proxy?

A: Да! Все настройки профиля (cookies, proxy, fingerprint) используются автоматически при запуске через API.

### Q: Как отлаживать скрипты?

A: Используйте `print()` для вывода информации и запускайте с `headless=False` для визуального контроля.

## Roadmap

Планируется добавить:
- ✅ Поддержка Octo Browser API
- ✅ Выбор профилей из списка
- ✅ Генерация Playwright и Selenium скриптов
- 🔄 Массовый запуск профилей
- 🔄 Управление прокси через API
- 🔄 Автоматическое создание профилей
- 🔄 Интеграция с Cloud API Octo
- 🔄 Расписание запуска профилей

## Поддержка

- **Документация Octo Browser API:** https://docs.octobrowser.net/en/api/start-api/
- **OctoMaster Pro Issues:** https://github.com/octomaster/octomaster-pro/issues
- **Community:** Telegram, Discord

---

**Создано с ❤️ командой OctoMaster Pro**
