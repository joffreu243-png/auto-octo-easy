# 🔴 Recorder Module

Модуль записи действий пользователя в браузере и конвертации их в workflow.

## 📁 Структура

```
recorder/
├── __init__.py          # Экспорты
├── recorder.py          # ✅ Основной класс рекордера
├── event_listener.py    # TODO: Прослушивание browser events
├── action_analyzer.py   # TODO: Анализ и оптимизация действий
└── selector_generator.py# TODO: Генерация селекторов
```

## 🎯 Назначение

Запись действий пользователя и конвертация в workflow узлы:

```python
from src.recorder.recorder import ActionRecorder

recorder = ActionRecorder()

# Начать запись
recorder.start_recording()

# Пользователь выполняет действия в браузере...
recorder.record_action("navigate", url="https://example.com")
recorder.record_action("click", selector="#button")
recorder.record_action("type", selector="#input", value="text")

# Остановить запись
recorder.stop_recording()

# Получить узлы workflow
nodes = recorder.convert_to_workflow()
print(f"Recorded {len(nodes)} actions")
```

## 🎯 Типы действий

- **navigate** - переход по URL
- **click** - клик
- **type** - ввод текста
- **select** - выбор из списка
- **hover** - наведение
- **scroll** - прокрутка
- **wait** - ожидание

## 📝 TODO
- [ ] Browser event listeners (CDP)
- [ ] Smart selector generation
- [ ] Action deduplication
- [ ] Action optimization
- [ ] Screenshot capture on each action
- [ ] Assertions recording
