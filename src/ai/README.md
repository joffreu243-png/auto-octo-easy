# 🤖 AI Module

AI-ассистент для генерации и оптимизации workflow с использованием GPT-4/Claude.

## 📁 Структура

```
ai/
├── __init__.py           # Экспорты
├── assistant.py          # ✅ Главный AI ассистент
├── intent_recognition.py # TODO: Распознавание намерений
├── workflow_generator.py # TODO: Генерация workflow из текста
├── optimizer.py          # TODO: Оптимизация workflow
└── prompts/              # TODO: Промпты для AI
    ├── __init__.py
    ├── generation.py     # Промпты для генерации
    └── optimization.py   # Промпты для оптимизации
```

## 🎯 Использование

```python
from src.ai.assistant import AIAssistant

assistant = AIAssistant()
await assistant.initialize()

# Генерация workflow из текста
description = """
Зайди на Amazon, найди iPhone 15,
собери цены всех вариантов и сохрани в CSV
"""
nodes = await assistant.generate_workflow(description)

# Оптимизация существующего workflow
optimized = await assistant.optimize_workflow(existing_nodes)

# Подсказка следующего действия
next_node = await assistant.suggest_next_action(
    current_nodes=nodes,
    context="user wants to extract prices"
)
```

## 🎯 Возможности

- ✅ Инициализация OpenAI/Anthropic клиента
- 🔄 Генерация workflow из текстового описания (TODO)
- 🔄 Оптимизация существующего workflow (TODO)
- 🔄 Подсказки следующих действий (TODO)
- 🔄 Intent recognition (TODO)

## 📝 TODO
- [ ] Prompt engineering для генерации
- [ ] Парсинг AI response в узлы
- [ ] Context management (история)
- [ ] Few-shot examples
- [ ] Chain-of-thought prompting
- [ ] Streaming responses
