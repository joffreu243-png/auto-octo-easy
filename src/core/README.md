# 🎯 Core Module

Ядро приложения OctoMaster Pro. Содержит базовую инфраструктуру и общие компоненты.

## 📁 Структура

```
core/
├── __init__.py           # Экспорты модуля
├── app.py               # Главный класс приложения
├── config.py            # Управление конфигурацией
├── logger.py            # Система логирования
├── events.py            # Event bus (pub/sub)
├── state.py             # Управление состоянием
├── exceptions.py        # Кастомные исключения
└── plugin_manager.py    # Менеджер плагинов
```

## 🎯 Назначение

### Application (`app.py`)
- **Что делает**: Главный класс приложения, управляет жизненным циклом
- **Использование**:
```python
from src.core.app import Application

app = Application()
exit_code = app.run()
```

### Configuration (`config.py`)
- **Что делает**: Управление конфигурацией через Pydantic
- **Особенности**:
  - Поддержка `.env` файлов
  - Валидация настроек
  - Type hints для всех параметров
  - Иерархическая структура (database, browser, ai, etc.)

```python
from src.core.config import get_config

config = get_config()
print(config.browser.timeout)  # 30000
print(config.ai.enabled)       # False
```

### Logger (`logger.py`)
- **Что делает**: Настройка логирования с Loguru
- **Особенности**:
  - Цветной вывод в консоль
  - Ротация файлов логов
  - Уровни логирования
  - Backtrace для ошибок

```python
from src.core.logger import setup_logger, get_logger

setup_logger(log_level="DEBUG", log_file="app.log")
logger = get_logger(__name__)

logger.info("Application started")
logger.error("Something went wrong")
```

### Events (`events.py`)
- **Что делает**: Event bus для pub/sub архитектуры
- **Особенности**:
  - Decoupled communication между модулями
  - 30+ предопределённых типов событий
  - Wildcard подписки
  - История событий

```python
from src.core.events import get_event_bus, EventType

bus = get_event_bus()

# Подписка на событие
def on_workflow_started(event):
    print(f"Workflow {event.get('workflow_id')} started!")

bus.subscribe(EventType.WORKFLOW_STARTED, on_workflow_started)

# Публикация события
bus.emit(EventType.WORKFLOW_STARTED, {"workflow_id": "123"})
```

### State (`state.py`)
- **Что делает**: Централизованное управление состоянием приложения
- **Содержит**:
  - Workflow state
  - Browser state
  - Recorder state
  - Execution stats

```python
from src.core.state import get_app_state

state = get_app_state()
state.workflow.is_executing = True
state.browser.current_url = "https://example.com"

print(state.workflow.stats.success_rate)  # 95.5
```

### Exceptions (`exceptions.py`)
- **Что делает**: Иерархия кастомных исключений
- **Типы**:
  - `OctoMasterError` - базовое
  - `ConfigurationError` - ошибки конфигурации
  - `WorkflowError` - ошибки workflow
  - `BrowserError` - ошибки браузера
  - `PluginError` - ошибки плагинов
  - И другие...

```python
from src.core.exceptions import WorkflowError

raise WorkflowError(
    "Node validation failed",
    workflow_id="workflow_123",
    block_id="block_456"
)
```

### Plugin Manager (`plugin_manager.py`)
- **Что делает**: Динамическая загрузка и управление плагинами
- **Особенности**:
  - Auto-discovery плагинов
  - Enable/disable плагинов
  - Изоляция плагинов
  - Hot reload

```python
from src.core.plugin_manager import get_plugin_manager

pm = get_plugin_manager()
pm.load_all_plugins()
pm.enable_plugin("my_custom_plugin")

plugin = pm.get_plugin("my_custom_plugin")
```

## 🔗 Зависимости

- **Pydantic** - конфигурация и валидация
- **Loguru** - логирование
- **PyQt6** - GUI framework (только для Application)

## 🧪 Тестирование

```bash
# Unit тесты для core модуля
pytest tests/unit/core/

# Конкретный тест
pytest tests/unit/core/test_config.py
```

## 📝 TODO

- [ ] Добавить hot reload для конфигурации
- [ ] Реализовать distributed events (Redis pub/sub)
- [ ] Добавить metrics сбор (Prometheus)
- [ ] Реализовать crash recovery
- [ ] Добавить профилирование производительности

## 🤝 Contributing

При добавлении нового компонента в core:

1. Создайте файл с соответствующим именем
2. Добавьте docstrings (Google style)
3. Добавьте type hints везде
4. Экспортируйте в `__init__.py`
5. Напишите unit тесты
6. Обновите этот README
