# 🌐 Browser Module

Модуль автоматизации браузера. Предоставляет единый интерфейс для Playwright, Selenium и WebEngine.

## 📁 Структура

```
browser/
├── __init__.py            # Экспорты
├── controller.py          # ✅ Главный контроллер браузера
├── playwright_bridge.py   # TODO: Playwright интеграция
├── selenium_bridge.py     # TODO: Selenium интеграция
├── webengine_view.py      # TODO: Qt WebEngine view
└── cdp.py                 # TODO: Chrome DevTools Protocol
```

## 🎯 Назначение

Unified API для управления браузером независимо от backend'а:

```python
from src.browser.controller import BrowserController

async def main():
    browser = BrowserController(browser_type="chromium", headless=False)

    await browser.start()
    await browser.navigate("https://example.com")
    await browser.click("#button")
    await browser.type_text("#input", "Hello World")
    text = await browser.get_text(".result")
    await browser.stop()
```

## 📝 TODO
- [ ] Playwright integration
- [ ] Selenium integration
- [ ] CDP support
- [ ] WebEngine view
- [ ] Cookie management
- [ ] Network interception
- [ ] File downloads
