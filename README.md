# OctoMaster Pro

![Version](https://img.shields.io/badge/version-0.1.0--alpha-blue)
![Python](https://img.shields.io/badge/python-3.11+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

**Революционная платформа для автоматизации браузеров**

> Создавайте сложные сценарии автоматизации без программирования - просто покажите компьютеру что нужно делать!

## ✨ Особенности

- 🎨 **Визуальный конструктор** - собирайте скрипты как LEGO
- 🎬 **Запись действий** - делайте что хотите, программа запомнит
- 🤖 **AI-ассистент** - понимает что вы хотите и помогает
- 🌐 **Встроенный браузер** - всё в одном окне
- 📚 **Библиотека шаблонов** - тысячи готовых решений
- 🔧 **Интеграция с Octo Browser** - полный контроль над профилями
- ⚡ **Нулевой порог входа** - начните через 30 секунд

## 🚀 Быстрый старт

### Установка

```bash
# Клонировать репозиторий
git clone https://github.com/yourusername/octomaster-pro.git
cd octomaster-pro

# Создать виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows

# Установить зависимости
pip install -r requirements.txt

# Запустить приложение
python main.py
```

### Первый скрипт за 30 секунд

1. Запустите OctoMaster Pro
2. Нажмите кнопку **"🔴 Запись"**
3. Сделайте действия в браузере (откройте сайт, кликните, введите текст)
4. Нажмите **"⏹️ Стоп"**
5. Готово! Ваш скрипт создан

## 📖 Документация

- [Руководство пользователя](docs/user-guide.md)
- [API документация](docs/api.md)
- [Архитектура проекта](docs/architecture.md)
- [Создание плагинов](docs/plugins.md)

## 🎯 Use Cases

### Скрапинг данных
```python
# Сбор товаров с интернет-магазина
workflow = Workflow()
workflow.add_block(OpenURL("https://example.com"))
workflow.add_block(ExtractData("h2.product-title"))
workflow.add_block(SaveToCSV("products.csv"))
workflow.run()
```

### Автоматизация тестирования
```python
# Тест регистрации пользователя
workflow = Workflow()
workflow.add_block(OpenURL("https://example.com/signup"))
workflow.add_block(TypeText("#email", "test@example.com"))
workflow.add_block(TypeText("#password", "SecurePass123"))
workflow.add_block(Click("button[type='submit']"))
workflow.add_block(Assert("h1", "Welcome!"))
workflow.run()
```

## 🏗️ Архитектура

```
OctoMaster Pro
├── Frontend (PyQt6)
│   ├── Visual Builder (Node Editor)
│   ├── Code Editor
│   ├── Browser View
│   ├── Recorder
│   └── Debugger
├── Core Engine (Python)
│   ├── Automation Engine
│   ├── Script Executor
│   ├── State Manager
│   └── AI Agent
├── Browser Layer
│   ├── Playwright
│   ├── Selenium
│   └── CDP Protocol
└── Integrations
    ├── Octo Browser API
    ├── Cloud Storage
    └── Notifications
```

## 🛠️ Технологии

- **GUI:** PyQt6, QtWebEngine
- **Automation:** Playwright, Selenium, Puppeteer
- **AI/ML:** OpenAI API, Anthropic Claude, Local LLMs
- **Data:** Pandas, SQLAlchemy, BeautifulSoup4
- **Web:** FastAPI, HTTPX, Requests

## 📦 Модули

- **Visual Builder** - Визуальный node-based редактор
- **Action Recorder** - Запись действий пользователя
- **Browser View** - Встроенный Chromium браузер
- **AI Assistant** - Интеллектуальный помощник
- **Template Library** - Библиотека готовых скриптов
- **Scraping Tools** - Инструменты для сбора данных
- **Scheduler** - Планировщик задач
- **Debugger** - Отладчик и профайлер
- **Octo Integration** - Интеграция с Octo Browser
- **Team Collaboration** - Командная работа

## 🎨 Скриншоты

*(Будут добавлены после реализации GUI)*

## 🗺️ Roadmap

### Phase 1: MVP (Q1 2025)
- [x] Базовая архитектура проекта
- [ ] Базовый GUI
- [ ] Node-based редактор
- [ ] 20 основных блоков
- [ ] Рекордер действий
- [ ] Встроенный браузер
- [ ] Интеграция с Octo API
- [ ] Экспорт в Python код

### Phase 2: Core Features (Q2 2025)
- [ ] AI ассистент
- [ ] Библиотека шаблонов (50 шаблонов)
- [ ] Планировщик задач
- [ ] Отладчик
- [ ] Инструменты скрапинга
- [ ] Multi-browser support

### Phase 3: Advanced (Q3 2025)
- [ ] Командная работа
- [ ] Cloud sync
- [ ] Маркетплейс плагинов
- [ ] Mobile app (viewer)
- [ ] Advanced AI features
- [ ] 100+ готовых шаблонов

### Phase 4: Enterprise (Q4 2025)
- [ ] Self-hosted версия
- [ ] SSO integration
- [ ] Advanced analytics
- [ ] White-label решение
- [ ] Enterprise support

## 🤝 Участие в разработке

Мы приветствуем вклад в проект! Пожалуйста, прочитайте [CONTRIBUTING.md](CONTRIBUTING.md) для деталей.

## 📄 Лицензия

Этот проект лицензирован под MIT License - см. [LICENSE](LICENSE) для деталей.

## 👥 Авторы

- **OctoMaster Team** - *Initial work*

## 🙏 Благодарности

- Octo Browser за вдохновение
- Playwright команда за отличный фреймворк
- Сообщество open source

## 📧 Контакты

- Website: https://octomaster.pro (в разработке)
- Email: support@octomaster.pro
- Discord: https://discord.gg/octomaster
- Telegram: https://t.me/octomaster

---

**⭐ Если проект вам нравится, поставьте звезду на GitHub!**
