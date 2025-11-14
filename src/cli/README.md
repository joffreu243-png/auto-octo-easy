# 💻 CLI Module

Command-line interface для OctoMaster Pro. Управление workflow из терминала.

## 📁 Структура

```
cli/
├── __init__.py   # Экспорты
└── main.py       # ✅ CLI entry point (stub)
```

## 🎯 Планируемые команды

```bash
# Запуск workflow
octomaster run workflow.json

# Запуск с параметрами
octomaster run workflow.json --headless --timeout=60

# Планирование
octomaster schedule workflow.json --cron "0 9 * * *"

# Список запланированных задач
octomaster schedule list

# Экспорт в Python
octomaster export workflow.json --format python > script.py

# Валидация workflow
octomaster validate workflow.json

# Список шаблонов
octomaster templates list

# Создание из шаблона
octomaster create --template google-search

# Информация
octomaster info
octomaster version
```

## 📝 TODO
- [ ] Click/Typer CLI framework
- [ ] Run command с опциями
- [ ] Schedule management
- [ ] Export commands
- [ ] Validation command
- [ ] Template management
- [ ] Config management через CLI
- [ ] Plugin management через CLI
