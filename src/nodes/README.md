# 🔗 Nodes Module

Система узлов для визуального редактора workflow. Управление графом выполнения.

## 📁 Структура

```
nodes/
├── __init__.py       # Экспорты
├── node.py           # ✅ Базовый класс Node (25+ типов)
├── connection.py     # ✅ Соединения между узлами
├── editor.py         # ✅ Редактор графа workflow
└── blocks/           # TODO: Реализации конкретных блоков
    ├── __init__.py
    ├── navigation.py # TODO: Navigate, Back, Forward
    ├── interaction.py# TODO: Click, Type, Select
    ├── waiting.py    # TODO: Wait, WaitForElement
    ├── data.py       # TODO: Extract, Transform
    └── logic.py      # TODO: If, Loop, Break
```

## 🎯 Типы узлов (NodeType)

### Navigation
- `NAVIGATE` - переход по URL
- `GO_BACK` - назад
- `GO_FORWARD` - вперёд
- `RELOAD` - перезагрузка

### Interaction
- `CLICK` - клик по элементу
- `TYPE` - ввод текста
- `SELECT` - выбор из dropdown
- `HOVER` - наведение
- `DRAG_DROP` - перетаскивание

### Waiting
- `WAIT` - ожидание времени
- `WAIT_FOR_ELEMENT` - ожидание элемента
- `WAIT_FOR_NAVIGATION` - ожидание навигации

### Data
- `EXTRACT_TEXT` - извлечение текста
- `EXTRACT_ATTRIBUTE` - извлечение атрибута
- `EXTRACT_HTML` - извлечение HTML

### Logic
- `CONDITION` - условие if/else
- `LOOP` - цикл
- `BREAK` - выход из цикла
- `CONTINUE` - продолжить цикл

## 🎯 Использование

```python
from src.nodes.editor import NodeEditor
from src.nodes.node import Node, NodeType

# Создаём редактор
editor = NodeEditor()

# Добавляем узлы
nav_node = Node(type=NodeType.NAVIGATE, name="Open Google")
nav_node.set_parameter("url", "https://google.com")
editor.add_node(nav_node)

click_node = Node(type=NodeType.CLICK)
click_node.set_parameter("selector", "#search-button")
editor.add_node(click_node)

# Соединяем
from src.nodes.connection import Connection
conn = Connection(nav_node.id, click_node.id)
editor.add_connection(conn)

# Сохраняем
editor.save_to_file(Path("my_workflow.json"))
```

## 📝 TODO
- [ ] Реализовать execute() для каждого типа узла
- [ ] Добавить валидацию параметров
- [ ] Cycle detection в графе
- [ ] Subgraphs (вложенные workflow)
