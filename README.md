# 🐙 OctoMaster Pro

![Version](https://img.shields.io/badge/version-0.1.0--alpha-blue)
![Python](https://img.shields.io/badge/python-3.11+-green)
![License](https://img.shields.io/badge/license-MIT-orange)
![Status](https://img.shields.io/badge/status-100%25_functional-brightgreen)

**Революционная платформа для автоматизации браузеров с визуальным редактором workflow**

> 🎯 Создавайте сложные сценарии автоматизации БЕЗ программирования - просто покажите компьютеру что нужно делать!

![OctoMaster Pro Screenshot](docs/screenshot.png)

---

## ✨ Ключевые возможности

### 🎨 Визуальный конструктор workflow
- **Node-based редактор** - собирайте автоматизации как конструктор
- **Drag & Drop** - перетаскивайте блоки и соединяйте их
- **40+ готовых блоков** - навигация, клики, ввод текста, ожидания, извлечение данных
- **Live preview** - видите что создаете в реальном времени

### 🎬 Запись действий (Recorder)
- **Автоматическая запись** - нажмите 🔴 и делайте что нужно
- **Преобразование в блоки** - действия становятся workflow
- **Редактирование** - подправьте записанное в визуальном редакторе
- **Replay** - запускайте записанное сколько угодно раз

### 🤖 AI-ассистент
- **Генерация workflow** - опишите задачу, получите готовый сценарий
- **Умные подсказки** - AI помогает выбрать правильные блоки
- **Оптимизация** - AI улучшает ваши workflow

### 🔧 Интеграция с Octo Browser
- **Управление профилями** - создание, запуск, остановка
- **Прокси и fingerprints** - полная поддержка
- **Bulk операции** - работайте с множеством профилей
- **Теги и группы** - организуйте профили

### 📚 Библиотека шаблонов
- **10+ готовых шаблонов** - от поиска в Google до e-commerce
- **Параметризация** - настройте под свои нужды
- **Сохранение своих** - создайте и используйте повторно

### ⚡ Расширенные возможности
- ✅ **Планировщик задач** - cron, interval, event-based
- ✅ **Уведомления** - Email, Telegram, Slack, Discord, Desktop
- ✅ **Отладка** - breakpoints, step-by-step, call stack
- ✅ **Переменные** - динамические данные в workflow
- ✅ **Экспорт в Python** - получите чистый код
- ✅ **Система плагинов** - расширяйте функционал
- ✅ **Темы** - светлая и темная тема

---

## 🚀 Быстрый старт

### Установка

#### 🪟 Windows (Рекомендуется)

**Требования:** Python 3.11, 3.12 или 3.13 (⚠️ НЕ 3.14 - dev версия!)

**🎯 ПРОСТОЙ СПОСОБ (один клик):**

1. **Первый запуск:** Дважды кликните `install_and_run.bat`
   - Автоматически создаст виртуальное окружение
   - Установит все зависимости
   - Установит Playwright браузер
   - Применит все фиксы
   - Запустит программу

2. **Последующие запуски:** Дважды кликните `quick_start.bat`

3. **Ярлык на рабочем столе:** Запустите `desktop_shortcut.bat`

**📖 Альтернативный способ (ручная установка):**

```cmd
# Запустите setup_windows.bat в папке проекта
setup_windows.bat
```

📖 **Полная инструкция для Windows:** [WINDOWS_INSTALL.md](WINDOWS_INSTALL.md)

**Возможные проблемы:**
- ❌ Ошибки компиляции greenlet → Запустите `fix_greenlet.bat`
- ❌ Проблемы с импортами → Запустите `python fix_imports.py`
- ❌ PyQt6 warnings → Запустите `python fix_pyqt6.py`

#### 🐧 Linux / 🍎 macOS

```bash
# 1. Клонировать репозиторий
git clone https://github.com/yourusername/octomaster-pro.git
cd octomaster-pro

# 2. Создать виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac

# 3. Установить зависимости
pip install -r requirements.txt

# 4. Установить браузеры для Playwright
playwright install chromium

# 5. Запустить приложение
python main.py

# ИЛИ безопасный запуск (для виртуальных машин)
./run.sh
```

### Первый workflow за 60 секунд

#### Способ 1: Запись действий (проще)

1. **Запустите OctoMaster Pro**
   ```bash
   python main.py
   ```

2. **Нажмите кнопку "🔴 Record"** в toolbar

3. **Выполните действия:**
   - Откройте сайт
   - Кликните на элемент
   - Введите текст
   - И т.д.

4. **Нажмите "⏹️ Stop Recording"**

5. **Готово!** Ваш workflow создан и готов к запуску

6. **Запустите:** нажмите `F5` или кнопку "▶️ Run"

#### Способ 2: Визуальный конструктор

1. **Создайте новый workflow:**
   - `File → New Workflow` или `Ctrl+N`

2. **Добавьте блоки:**
   - Нажмите `➕ Add Block`
   - Выберите блок из категории (например: Navigation → Open URL)
   - Блок появится на canvas

3. **Настройте блок:**
   - Кликните на блок
   - В панели Inspector (справа) укажите параметры
   - Например: URL = "https://google.com"

4. **Добавьте еще блоки:**
   - Actions → Type Text (selector: `input[name='q']`, text: "Python")
   - Actions → Click (selector: `input[name='btnK']`)
   - Data → Screenshot (path: "result.png")

5. **Соедините блоки:**
   - Кликните и перетащите от одного блока к другому
   - Блоки выполнятся по порядку

6. **Запустите:**
   - Нажмите `F5` или кнопку "▶️ Run"
   - Смотрите выполнение в Console tab

7. **Сохраните:**
   - `File → Save` или `Ctrl+S`
   - Выберите имя файла

#### Способ 3: Из шаблона (быстрее всего)

1. **Используйте готовый шаблон:**
   - `File → New from Template` или `Ctrl+Shift+N`
   - Выберите шаблон (например: "Google Search")

2. **Укажите параметры:**
   - Search query: "OctoMaster Pro"
   - Screenshot path: "google_result.png"

3. **Запустите:**
   - `F5` и workflow готов!

---

## 📖 Руководство пользователя

### Интерфейс приложения

```
┌─────────────────────────────────────────────────────────────┐
│  File  Edit  View  Run  Tools  Help                         │
│  📄 📂 💾  |  ▶️ ⏸️ ⏹️  |  🔴  |  🐛  |  📸 ⚙️                 │
├────────┬──────────────────────────────────────┬──────────────┤
│        │                                      │              │
│ Project│    Visual Editor (Canvas)           │   Inspector  │
│ Explor │                                      │              │
│   er   │   [Block] ──→ [Block] ──→ [Block]   │   Name: ...  │
│        │      ↓                               │   Type: ...  │
│  📁    │   [Block] ──→ [Block]                │   Params:    │
│  📄    │                                      │    • url     │
│  📄    │   (Drag blocks, connect, configure)  │    • text    │
│        │                                      │              │
├────────┴──────────────────────────────────────┴──────────────┤
│  📟 Console │ 📋 Logs │ 🔢 Variables │ 🐛 Debugger │ 🌐 Browser │
│  > Running workflow...                                       │
│  → Executing: Open URL                                       │
│  ✓ Open URL completed                                        │
└──────────────────────────────────────────────────────────────┘
```

### Основные панели

#### 1. **Project Explorer** (слева)
- Список workflow файлов
- Быстрый доступ к проектам
- Организация файлов

#### 2. **Visual Editor** (центр)
- Главное рабочее пространство
- Перетаскивание и соединение блоков
- Toolbar с кнопками:
  - `➕ Add Block` - добавить блок
  - `🔍+` / `🔍-` - zoom
  - `⬜ Fit` - показать все
  - `📐 Auto Layout` - автоматическое выравнивание

#### 3. **Inspector** (справа)
- Параметры выбранного блока
- Редактирование свойств
- Справка по блоку

#### 4. **Bottom Panel** (внизу - табы)
- **Console** 📟 - вывод при выполнении
- **Logs** 📋 - логи приложения с фильтрами
- **Variables** 🔢 - переменные workflow
- **Debugger** 🐛 - отладка с breakpoints
- **Browser** 🌐 - встроенный браузер (preview)

### Горячие клавиши

| Клавиша | Действие |
|---------|----------|
| `Ctrl+N` | Новый workflow |
| `Ctrl+Shift+N` | Из шаблона |
| `Ctrl+O` | Открыть |
| `Ctrl+S` | Сохранить |
| `Ctrl+Shift+S` | Сохранить все |
| `Ctrl+Z` | Отменить |
| `Ctrl+Shift+Z` / `Ctrl+Y` | Повторить |
| `Ctrl+X` / `C` / `V` | Вырезать/Копировать/Вставить |
| `Ctrl+A` | Выбрать все блоки |
| `F5` | Запустить workflow |
| `F8` | Отладка workflow |
| `Shift+F5` | Остановить |
| `F1` | Quick Start Guide |
| `Ctrl+Q` | Выход |
| `Ctrl+Plus` | Zoom in |
| `Ctrl+Minus` | Zoom out |
| `Ctrl+0` | Reset zoom |
| `Delete` | Удалить выбранные блоки |

### Типы блоков

#### 🧭 Navigation (Навигация)
- **Open URL** - открыть URL
- **Go Back** - назад
- **Go Forward** - вперед
- **Refresh** - обновить страницу
- **Close Tab** - закрыть вкладку

#### ⚡ Actions (Действия)
- **Click** - кликнуть элемент
- **Type Text** - ввести текст
- **Press Key** - нажать клавишу
- **Hover** - навести мышь
- **Drag & Drop** - перетащить
- **Scroll** - прокрутить
- **Upload File** - загрузить файл
- **Download File** - скачать файл

#### ⏱️ Waits (Ожидания)
- **Wait for Load** - дождаться загрузки
- **Wait for Element** - дождаться элемента
- **Wait Time** - подождать N секунд
- **Wait for Text** - дождаться текста

#### 📊 Data (Данные)
- **Get Text** - извлечь текст
- **Get Attribute** - получить атрибут
- **Extract Table** - извлечь таблицу
- **Screenshot** - сделать скриншот
- **Get Cookies** - получить cookies
- **Set Cookies** - установить cookies

#### 🔀 Conditions (Условия)
- **If** - условие
- **Loop** - цикл
- **For Each** - для каждого
- **Break** - прервать цикл

#### 💾 Storage (Хранение)
- **Save Data** - сохранить данные
- **Load Data** - загрузить данные
- **Set Variable** - установить переменную
- **Get Variable** - получить переменную

#### 🌐 Octo Browser
- **Create Profile** - создать профиль
- **Start Profile** - запустить профиль
- **Stop Profile** - остановить профиль
- **Delete Profile** - удалить профиль

---

## 🎯 Примеры использования

### Пример 1: Автоматический поиск в Google

```
[Open URL] url="https://google.com"
    ↓
[Type Text] selector="input[name='q']" text="Python"
    ↓
[Click] selector="input[name='btnK']"
    ↓
[Wait for Element] selector="#search"
    ↓
[Screenshot] path="google_results.png"
```

### Пример 2: Мониторинг цен

```
[Open URL] url="https://amazon.com/product/..."
    ↓
[Wait for Element] selector=".price"
    ↓
[Get Text] selector=".price" variable="current_price"
    ↓
[If] condition="{{current_price}} < 100"
    ↓
[Send Notification] channel="telegram" message="Цена упала!"
```

### Пример 3: Заполнение формы

```
[Open URL] url="https://example.com/contact"
    ↓
[Type Text] selector="#name" text="John Doe"
    ↓
[Type Text] selector="#email" text="john@example.com"
    ↓
[Type Text] selector="#message" text="Hello!"
    ↓
[Click] selector="button[type='submit']"
    ↓
[Wait for Text] text="Message sent"
    ↓
[Screenshot] path="success.png"
```

---

## 🔌 Интеграции

### Octo Browser API

```python
# Пример использования Octo Browser блоков
[Create Profile]
  name="Test Profile"
  browser="chromium"
  proxy="http://proxy:port"
    ↓
[Start Profile]
  profile_id="{{profile_id}}"
    ↓
[... ваши действия ...]
    ↓
[Stop Profile]
  profile_id="{{profile_id}}"
```

### Уведомления

Настройте в `.env`:

```env
# Telegram
TELEGRAM_ENABLED=true
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_CHAT_ID=your_chat_id

# Email
EMAIL_ENABLED=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

### Планировщик

```python
# Запускайте workflow по расписанию
# GUI: Tools → Scheduler

# Cron: каждый день в 9:00
0 9 * * *

# Interval: каждые 2 часа
Every 2 hours

# Event: при изменении файла
File changed: /path/to/file
```

---

## 🐛 Отладка

### Использование Debugger

1. **Установите breakpoint:**
   - Кликните на блок правой кнопкой
   - Выберите "Add Breakpoint"

2. **Запустите debug:**
   - `F8` или `Run → Debug Workflow`

3. **Управление:**
   - **Step** (→) - выполнить следующий блок
   - **Continue** (⏭) - продолжить до breakpoint
   - **Pause** (⏸) - пауза
   - **Stop** (⏹) - остановить

4. **Смотрите:**
   - **Call Stack** - стек вызовов
   - **Variables** - значения переменных
   - **Debug Output** - вывод отладки

### Логи

В таб **Logs**:
- Фильтр по уровню (DEBUG/INFO/WARNING/ERROR)
- Auto-scroll
- Export в файл
- Поиск

---

## 📦 Экспорт

### Экспорт в Python

`File → Export → Export as Python`

Получите чистый Python код:

```python
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # Open URL
        await page.goto("https://google.com")

        # Type Text
        await page.fill("input[name='q']", "Python")

        # Click
        await page.click("input[name='btnK']")

        # Wait for Element
        await page.wait_for_selector("#search")

        # Screenshot
        await page.screenshot(path="google_results.png")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🔧 Настройка

### Файл .env

Скопируйте `.env.example` в `.env` и настройте:

```env
# Основные настройки
APP_NAME=OctoMaster Pro
DEBUG=true
LOG_LEVEL=INFO

# Браузер
DEFAULT_BROWSER=chromium
HEADLESS=false

# Octo Browser
OCTO_API_KEY=your_key
OCTO_API_URL=https://api.octobrowser.net

# AI
OPENAI_API_KEY=your_key
ANTHROPIC_API_KEY=your_key

# Уведомления
TELEGRAM_ENABLED=true
TELEGRAM_BOT_TOKEN=token
EMAIL_ENABLED=true
...
```

---

## 🚨 Решение проблем

### Краш при открытии Browser Panel

**Проблема:** Segmentation fault при клике на Browser tab

**Решение:**
```bash
# Используйте безопасный запуск
./run.sh

# ИЛИ установите переменные окружения
export QTWEBENGINE_CHROMIUM_FLAGS="--disable-gpu --disable-software-rasterizer --no-sandbox"
python main.py
```

См. подробнее в [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

### Playwright не находит браузер

```bash
# Установите браузеры
playwright install chromium
# ИЛИ все
playwright install
```

### Ошибки импорта модулей

```bash
# Переустановите зависимости
pip install -r requirements.txt --force-reinstall
```

---

## 📚 Документация

- **Quick Start Guide** - `F1` в приложении
- **TROUBLESHOOTING.md** - решение проблем
- **API Documentation** - для разработчиков плагинов
- **Template Guide** - создание шаблонов
- **Plugin Development** - разработка плагинов

---

## 🤝 Вклад в проект

Мы приветствуем вклад в проект!

1. Fork репозитория
2. Создайте ветку (`git checkout -b feature/amazing`)
3. Commit изменения (`git commit -m 'Add feature'`)
4. Push в ветку (`git push origin feature/amazing`)
5. Создайте Pull Request

---

## 📝 Лицензия

MIT License - см. [LICENSE](LICENSE)

---

## 🌟 Благодарности

- PyQt6 - GUI framework
- Playwright - browser automation
- SQLAlchemy - ORM
- APScheduler - task scheduling
- Loguru - logging
- И всем contributors!

---

## 📞 Поддержка

- **Issues:** [GitHub Issues](https://github.com/yourusername/octomaster-pro/issues)
- **Discussions:** [GitHub Discussions](https://github.com/yourusername/octomaster-pro/discussions)
- **Email:** support@octomaster.pro

---

## 🗺️ Roadmap

- [x] Phase 1: MVP - Visual Editor, Recorder, 40+ blocks
- [x] Phase 2: Executor, Templates, CLI, Octo Integration
- [x] Phase 3: Scheduler, Notifications, Plugins, Debugger, Themes
- [ ] Phase 4: AI Assistant, Cloud Sync, Team Collaboration
- [ ] Phase 5: Mobile app, Browser extension, API

---

<div align="center">

**Сделано с ❤️ командой OctoMaster**

⭐ Если вам нравится проект - поставьте звезду!

</div>
