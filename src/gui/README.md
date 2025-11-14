# 🎨 GUI Module

Графический интерфейс пользователя на PyQt6. Содержит все компоненты UI приложения.

## 📁 Структура

```
gui/
├── __init__.py              # Экспорты модуля
├── main_window.py           # Главное окно приложения
├── widgets/                 # Пользовательские виджеты
│   ├── __init__.py
│   ├── visual_editor.py    # TODO: Визуальный редактор workflow
│   ├── browser_panel.py    # TODO: Панель браузера
│   ├── logs_widget.py      # TODO: Виджет логов
│   ├── variables_widget.py # TODO: Виджет переменных
│   └── debugger_widget.py  # TODO: Виджет отладки
├── dialogs/                 # Диалоговые окна
│   ├── __init__.py
│   ├── settings_dialog.py  # TODO: Настройки
│   ├── about_dialog.py     # TODO: О программе
│   └── plugin_dialog.py    # TODO: Менеджер плагинов
├── views/                   # Кастомные views
│   ├── __init__.py
│   └── workflow_view.py    # TODO: View для workflow
└── styles/                  # Стили и темы
    ├── __init__.py
    ├── dark_theme.qss      # TODO: Тёмная тема
    └── light_theme.qss     # TODO: Светлая тема
```

## 🎯 Главные компоненты

### MainWindow (`main_window.py`)
- **Статус**: ✅ Реализовано
- **Что делает**: Главное окно приложения со всеми меню и панелями
- **Особенности**:
  - Полное меню (File, Edit, View, Run, Tools, Help)
  - Toolbar с основными действиями
  - Tabbed interface (Browser, Console, Logs, etc.)
  - Dockable panels (Blocks, Properties)
  - Keyboard shortcuts
  - Event system integration

```python
from src.gui.main_window import MainWindow

window = MainWindow()
window.show()
```

### Visual Editor (TODO)
- **Файл**: `widgets/visual_editor.py`
- **Что нужно**: Node-based редактор workflow
- **Функции**:
  - Drag & drop блоков
  - Соединение узлов
  - Zoom и pan
  - Grid и snap
  - Undo/redo
  - Copy/paste блоков

### Browser Panel (TODO)
- **Файл**: `widgets/browser_panel.py`
- **Что нужно**: Встроенный браузер для preview
- **Функции**:
  - Qt WebEngine view
  - Navigation controls
  - DevTools integration
  - Screenshot capture
  - Element inspector

### Widgets (TODO)
- **LogsWidget**: Лог-консоль с фильтрацией
- **VariablesWidget**: Просмотр и редактирование переменных
- **DebuggerWidget**: Breakpoints и step debugging

### Dialogs (TODO)
- **SettingsDialog**: Настройки приложения
- **AboutDialog**: Информация о программе
- **PluginDialog**: Управление плагинами

## 🎨 Архитектура UI

```
┌─────────────────────────────────────────────────────────┐
│                     Main Window                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │                   Menu Bar                       │   │
│  │  File  Edit  View  Run  Tools  Help            │   │
│  └─────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────┐   │
│  │                   Tool Bar                       │   │
│  │  🆕 📁 💾 ▶️ ⏹️ 🔴 ...                        │   │
│  └─────────────────────────────────────────────────┘   │
│                                                          │
│  ┌────────┬──────────────────────────┬──────────────┐  │
│  │        │                          │              │  │
│  │ Blocks │   Visual Workflow        │  Properties  │  │
│  │ Library│   Editor (Canvas)        │  Panel       │  │
│  │        │                          │              │  │
│  │        │   [Drag & Drop Nodes]    │              │  │
│  │        │                          │              │  │
│  └────────┴──────────────────────────┴──────────────┘  │
│                                                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Tabs: Browser | Console | Logs | Variables     │   │
│  │  ┌───────────────────────────────────────────┐  │   │
│  │  │                                           │  │   │
│  │  │         Tab Content Area                  │  │   │
│  │  │                                           │  │   │
│  │  └───────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────┘   │
│                                                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Status Bar: Ready | Workflow: idle              │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## 🎨 Темы оформления

Поддерживаются темы через QSS (Qt Style Sheets):

- **Dark Theme**: Тёмная тема для работы ночью
- **Light Theme**: Светлая тема
- **Auto**: Автоматическая смена в зависимости от системы

```python
# Применение темы
from src.gui.styles import apply_theme

apply_theme(window, "dark")
```

## 🔗 Интеграция с Core

GUI тесно интегрирован с core модулем:

```python
from src.core.config import get_config
from src.core.events import get_event_bus, EventType
from src.core.state import get_app_state

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Получаем конфигурацию
        self.config = get_config()

        # Подписываемся на события
        self.event_bus = get_event_bus()
        self.event_bus.subscribe(EventType.WORKFLOW_STARTED, self.on_workflow_started)

        # Получаем состояние
        self.state = get_app_state()
```

## 🎯 Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+N` | New workflow |
| `Ctrl+O` | Open workflow |
| `Ctrl+S` | Save workflow |
| `Ctrl+Shift+S` | Save As |
| `Ctrl+Z` | Undo |
| `Ctrl+Y` | Redo |
| `Ctrl+X` | Cut |
| `Ctrl+C` | Copy |
| `Ctrl+V` | Paste |
| `Delete` | Delete selected |
| `F5` | Run workflow |
| `Shift+F5` | Stop execution |
| `F8` | Debug workflow |
| `Ctrl+R` | Start recording |
| `Ctrl++` | Zoom in |
| `Ctrl+-` | Zoom out |
| `Ctrl+0` | Reset zoom |
| `F1` | Help |

## 🧪 Тестирование

```bash
# GUI тесты с pytest-qt
pytest tests/gui/

# Тесты main window
pytest tests/gui/test_main_window.py

# С показом окна (для отладки)
pytest tests/gui/ --no-xvfb
```

## 📝 TODO

### Высокий приоритет
- [ ] Реализовать Visual Editor widget
- [ ] Добавить Browser Panel с WebEngine
- [ ] Создать LogsWidget с фильтрацией
- [ ] Реализовать VariablesWidget
- [ ] Добавить DebuggerWidget

### Средний приоритет
- [ ] Создать SettingsDialog
- [ ] Добавить AboutDialog
- [ ] Реализовать PluginDialog
- [ ] Добавить темы (dark/light)
- [ ] Создать custom виджеты для блоков

### Низкий приоритет
- [ ] Анимации переходов
- [ ] Tooltips на всех элементах
- [ ] Accessibility (a11y)
- [ ] Локализация (i18n)
- [ ] Custom title bar

## 🎨 Стандарты UI

### Цвета (Dark Theme)
```python
PRIMARY = "#3498db"      # Синий
SUCCESS = "#2ecc71"      # Зелёный
WARNING = "#f39c12"      # Оранжевый
DANGER = "#e74c3c"       # Красный
BACKGROUND = "#2c3e50"   # Тёмно-серый
FOREGROUND = "#ecf0f1"   # Светло-серый
```

### Spacing
- Padding: 8px
- Margin: 16px
- Border radius: 4px

### Typography
- Font family: "Segoe UI", "Arial", sans-serif
- Base size: 10pt
- Headers: 12pt bold

## 🤝 Contributing

При добавлении нового виджета:

1. Создайте файл в `widgets/`
2. Наследуйтесь от соответствующего Qt виджета
3. Добавьте docstrings
4. Используйте signals/slots для взаимодействия
5. Подписывайтесь на события из event bus
6. Напишите GUI тесты
7. Обновите этот README
