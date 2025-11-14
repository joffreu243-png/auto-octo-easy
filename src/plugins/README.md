# 🔌 Plugins Module

Система плагинов для расширения функционала OctoMaster Pro.

## 📁 Структура

```
plugins/
├── __init__.py   # Экспорты (Plugin class from core)
├── base.py       # TODO: Дополнительные базовые классы
├── loader.py     # TODO: Загрузчик плагинов
└── registry.py   # TODO: Реестр плагинов
```

## 🎯 Типы плагинов

### Block Plugin
Добавление новых типов блоков в workflow:

```python
from src.core.plugin_manager import Plugin

class CustomBlockPlugin(Plugin):
    def initialize(self) -> bool:
        # Register new block type
        return True

    def shutdown(self) -> None:
        # Cleanup
        pass
```

### Integration Plugin
Интеграция со сторонними сервисами

### Theme Plugin
Кастомные темы оформления

### Tool Plugin
Дополнительные инструменты

## 📝 TODO
- [ ] Plugin API documentation
- [ ] Plugin template generator
- [ ] Plugin marketplace
- [ ] Hot reload
- [ ] Sandboxing
