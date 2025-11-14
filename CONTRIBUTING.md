# 🤝 Руководство по участию в разработке OctoMaster Pro

Спасибо за интерес к участию в разработке OctoMaster Pro! Это руководство поможет вам начать.

## 📋 Содержание

- [Кодекс поведения](#-кодекс-поведения)
- [Как внести вклад](#-как-внести-вклад)
- [Настройка окружения](#-настройка-окружения)
- [Стандарты кода](#-стандарты-кода)
- [Процесс разработки](#-процесс-разработки)
- [Тестирование](#-тестирование)
- [Отправка Pull Request](#-отправка-pull-request)
- [Структура коммитов](#-структура-коммитов)

## 📜 Кодекс поведения

### Наши стандарты

- 🤝 Будьте уважительны к другим участникам
- 💬 Используйте вежливый и инклюзивный язык
- 🎯 Фокусируйтесь на том, что лучше для сообщества
- 🙏 Принимайте конструктивную критику
- 🌟 Показывайте эмпатию к другим участникам

### Неприемлемое поведение

- 🚫 Оскорбительные комментарии
- 🚫 Троллинг и провокации
- 🚫 Публичные или приватные домогательства
- 🚫 Публикация чужой личной информации
- 🚫 Другое профессионально неэтичное поведение

## 🚀 Как внести вклад

### Виды вкладов

Мы приветствуем различные виды вкладов:

#### 🐛 Сообщения об ошибках

- Используйте шаблон issue для багов
- Укажите версию Python и OS
- Предоставьте минимальный воспроизводимый пример
- Опишите ожидаемое и фактическое поведение

#### ✨ Предложения новых функций

- Используйте шаблон issue для feature request
- Опишите зачем нужна эта функция
- Предложите возможную реализацию
- Обсудите с мейнтейнерами перед началом работы

#### 📝 Улучшение документации

- Исправление опечаток
- Улучшение формулировок
- Добавление примеров
- Перевод на другие языки

#### 💻 Код

- Исправление багов
- Реализация новых функций
- Оптимизация производительности
- Рефакторинг

## 🛠️ Настройка окружения

### 1. Fork и клонирование

```bash
# Fork репозитория через GitHub UI
# Затем клонируйте свой fork

git clone https://github.com/YOUR_USERNAME/octomaster-pro.git
cd octomaster-pro

# Добавьте upstream remote
git remote add upstream https://github.com/octomaster/octomaster-pro.git
```

### 2. Установка зависимостей

#### Через Poetry (рекомендуется)

```bash
# Установите Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Установите зависимости включая dev
poetry install --with dev

# Активируйте окружение
poetry shell
```

#### Через pip

```bash
# Создайте виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows

# Установите зависимости
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 3. Установка pre-commit hooks

```bash
# Установите pre-commit hooks
pre-commit install

# Проверьте что всё работает
pre-commit run --all-files
```

### 4. Установка браузеров

```bash
# Для Playwright
playwright install chromium firefox webkit

# Для Selenium (если нужно)
# Драйверы установятся автоматически через selenium-manager
```

### 5. Настройка IDE

#### VS Code

Установите расширения:
- Python
- Pylance
- Black Formatter
- Ruff
- PyQt6 Snippets

Настройки (`.vscode/settings.json`):

```json
{
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.formatting.provider": "black",
  "python.testing.pytestEnabled": true,
  "editor.formatOnSave": true
}
```

#### PyCharm

- Включите Poetry integration
- Настройте Black как форматтер
- Включите Type Checking (mypy)
- Настройте pytest как test runner

## 📏 Стандарты кода

### Python Style Guide

Проект следует:

- **PEP 8** - базовый стиль кода Python
- **PEP 484** - Type Hints
- **PEP 257** - Docstring Conventions
- **Black** - автоматическое форматирование
- **Ruff** - быстрый линтер

### Type Hints

**Обязательны** для всех функций и методов:

```python
from typing import Optional, List

def process_workflow(
    workflow_id: str,
    nodes: List[Node],
    timeout: Optional[int] = None
) -> bool:
    """
    Process workflow with given nodes.

    Args:
        workflow_id: Unique workflow identifier
        nodes: List of workflow nodes
        timeout: Optional timeout in seconds

    Returns:
        True if processing successful, False otherwise

    Raises:
        WorkflowError: If workflow validation fails
    """
    pass
```

### Docstrings

Используем **Google Style**:

```python
def calculate_total(items: List[Item], tax_rate: float = 0.1) -> float:
    """
    Calculate total price including tax.

    This function sums up all item prices and applies the specified
    tax rate to calculate the final total.

    Args:
        items: List of items to calculate total for
        tax_rate: Tax rate as decimal (default: 0.1 for 10%)

    Returns:
        Total price including tax

    Raises:
        ValueError: If tax_rate is negative

    Examples:
        >>> items = [Item(price=100), Item(price=200)]
        >>> calculate_total(items, tax_rate=0.2)
        360.0

    Note:
        Tax is rounded to 2 decimal places
    """
    if tax_rate < 0:
        raise ValueError("Tax rate cannot be negative")

    subtotal = sum(item.price for item in items)
    return round(subtotal * (1 + tax_rate), 2)
```

### Именование

```python
# Классы - PascalCase
class WorkflowExecutor:
    pass

# Функции и методы - snake_case
def execute_workflow():
    pass

# Константы - UPPER_SNAKE_CASE
MAX_RETRY_COUNT = 3

# Приватные члены - префикс _
class MyClass:
    def __init__(self):
        self._private_value = 0

    def _private_method(self):
        pass
```

### Imports

```python
# Стандартная библиотека
import os
import sys
from pathlib import Path
from typing import Optional, List

# Сторонние библиотеки
import httpx
from loguru import logger
from PyQt6.QtWidgets import QWidget

# Локальные imports
from src.core.config import get_config
from src.core.exceptions import WorkflowError
```

Порядок:
1. Стандартная библиотека
2. Сторонние библиотеки
3. Локальные модули

Используйте `isort` для автоматической сортировки.

## 🔄 Процесс разработки

### 1. Создание ветки

```bash
# Обновите main
git checkout main
git pull upstream main

# Создайте feature branch
git checkout -b feature/your-feature-name
# или для багфикса
git checkout -b fix/bug-description
```

### 2. Разработка

```bash
# Делайте изменения
# Коммитьте часто с понятными сообщениями

git add .
git commit -m "feat: add new awesome feature"

# Синхронизируйтесь с upstream регулярно
git fetch upstream
git rebase upstream/main
```

### 3. Код-ревью инструменты

```bash
# Форматирование
black src/ tests/

# Линтинг
ruff src/ tests/

# Type checking
mypy src/

# Проверка всего сразу
pre-commit run --all-files
```

## 🧪 Тестирование

### Написание тестов

**Обязательно** пишите тесты для:
- Новых функций
- Исправлений багов
- Изменений API

#### Пример Unit теста

```python
# tests/unit/test_workflow.py

import pytest
from src.nodes.node import Node, NodeType

def test_node_creation():
    """Test node can be created with correct parameters."""
    node = Node(type=NodeType.NAVIGATE, name="Test Node")

    assert node.type == NodeType.NAVIGATE
    assert node.name == "Test Node"
    assert node.parameters == {}

def test_node_parameter_set():
    """Test node parameters can be set."""
    node = Node(type=NodeType.CLICK)
    node.set_parameter("selector", "#button")

    assert node.get_parameter("selector") == "#button"

@pytest.mark.asyncio
async def test_async_operation():
    """Test async functionality."""
    result = await some_async_function()
    assert result is not None
```

#### Пример Integration теста

```python
# tests/integration/test_browser_workflow.py

import pytest
from src.browser.controller import BrowserController
from src.nodes.editor import NodeEditor
from src.nodes.node import Node, NodeType

@pytest.mark.integration
async def test_workflow_execution():
    """Test complete workflow execution."""
    # Setup
    controller = BrowserController()
    editor = NodeEditor()

    # Create workflow
    nav_node = Node(type=NodeType.NAVIGATE)
    nav_node.set_parameter("url", "https://example.com")
    editor.add_node(nav_node)

    # Execute
    await controller.start()
    success = await controller.navigate(nav_node.get_parameter("url"))

    # Verify
    assert success is True

    # Cleanup
    await controller.stop()
```

### Запуск тестов

```bash
# Все тесты
pytest

# Только unit тесты
pytest tests/unit/

# С покрытием
pytest --cov=src --cov-report=html

# Быстрые тесты (без медленных)
pytest -m "not slow"

# Конкретный файл
pytest tests/unit/test_workflow.py

# Конкретный тест
pytest tests/unit/test_workflow.py::test_node_creation
```

### Требования к покрытию

- **Минимум 80%** общее покрытие
- **90%+** для критических модулей (core, browser)
- **100%** для utility функций

## 📤 Отправка Pull Request

### 1. Подготовка

```bash
# Убедитесь что все тесты проходят
pytest

# Проверьте код
black src/ tests/
ruff src/ tests/
mypy src/

# Обновите main и rebase
git fetch upstream
git rebase upstream/main
```

### 2. Создание PR

1. Push вашей ветки в fork
```bash
git push origin feature/your-feature-name
```

2. Откройте PR через GitHub UI

3. Заполните шаблон PR:
   - Описание изменений
   - Связанные issues
   - Скриншоты (для UI изменений)
   - Checklist

### 3. Шаблон PR

```markdown
## Описание
Краткое описание что делает этот PR

## Тип изменений
- [ ] Исправление бага (non-breaking change)
- [ ] Новая функция (non-breaking change)
- [ ] Breaking change (изменения ломающие обратную совместимость)
- [ ] Документация

## Связанные issues
Fixes #123
Related to #456

## Как протестировано
Опишите как вы тестировали изменения

## Checklist
- [ ] Код следует style guide проекта
- [ ] Написаны тесты для изменений
- [ ] Все тесты проходят
- [ ] Обновлена документация
- [ ] Добавлены type hints
- [ ] Pre-commit hooks проходят

## Скриншоты (если применимо)
Добавьте скриншоты для UI изменений
```

### 4. Код-ревью

- Отвечайте на комментарии оперативно
- Будьте открыты к предложениям
- Вносите запрошенные изменения
- Обновляйте PR после изменений

## 📝 Структура коммитов

### Conventional Commits

Используем [Conventional Commits](https://www.conventionalcommits.org/) спецификацию:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Типы коммитов

- **feat**: Новая функция
- **fix**: Исправление бага
- **docs**: Изменения документации
- **style**: Форматирование кода (не влияющие на логику)
- **refactor**: Рефакторинг кода
- **perf**: Улучшение производительности
- **test**: Добавление или изменение тестов
- **build**: Изменения системы сборки
- **ci**: Изменения CI конфигурации
- **chore**: Другие изменения (обновление зависимостей и т.д.)

### Примеры

```bash
# Новая функция
git commit -m "feat(recorder): add action recording functionality"

# Исправление бага
git commit -m "fix(browser): resolve memory leak in controller"

# Breaking change
git commit -m "feat!: change workflow API structure

BREAKING CHANGE: workflow.execute() now returns WorkflowResult instead of bool"

# С scope и телом
git commit -m "feat(ai): integrate GPT-4 for workflow generation

- Add OpenAI client integration
- Create prompt templates
- Implement workflow parsing from AI response

Closes #123"
```

### Scope

Рекомендуемые scopes:
- `core` - ядро приложения
- `gui` - пользовательский интерфейс
- `browser` - автоматизация браузера
- `recorder` - записыватель действий
- `ai` - AI ассистент
- `scheduler` - планировщик
- `plugins` - система плагинов
- `tests` - тесты
- `docs` - документация

## 🎯 Советы для контрибьюторов

### Начните с малого

Для первого вклада выбирайте:
- 🏷️ Issues с меткой `good first issue`
- 📝 Улучшение документации
- 🐛 Простые баг-фиксы

### Общайтесь

- 💬 Задавайте вопросы в issues
- 📞 Присоединяйтесь к Discord
- 🤝 Обсуждайте идеи перед реализацией

### Качество важнее скорости

- ✅ Пишите качественный код
- 📚 Документируйте изменения
- 🧪 Покрывайте тестами
- 🔍 Тщательно тестируйте

## 📞 Получение помощи

Если у вас вопросы:

1. 📖 Проверьте [документацию](docs/)
2. 🔍 Поищите существующие issues
3. 💬 Спросите в [Discord](https://discord.gg/octomaster)
4. 📧 Напишите на support@octomaster.pro

## 🙏 Спасибо!

Спасибо что вносите вклад в OctoMaster Pro! Ваша помощь делает проект лучше для всех. 🎉

---

**Happy Coding! 🚀**
