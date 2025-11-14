# ⏰ Scheduler Module

Планировщик задач для автоматического выполнения workflow по расписанию.

## 📁 Структура

```
scheduler/
├── __init__.py     # Экспорты
├── scheduler.py    # ✅ Главный планировщик (APScheduler)
├── executor.py     # TODO: Выполнение workflow
├── cron.py         # TODO: Cron парсер и валидатор
└── triggers.py     # TODO: Кастомные триггеры
```

## 🎯 Использование

```python
from src.scheduler.scheduler import TaskScheduler

scheduler = TaskScheduler()
scheduler.start()

# Cron расписание
scheduler.schedule_cron(
    task_id="daily_report",
    func=run_workflow,
    cron_expression="0 9 * * *"  # Каждый день в 9:00
)

# Интервал
scheduler.schedule_interval(
    task_id="check_prices",
    func=run_workflow,
    seconds=300  # Каждые 5 минут
)

# Одноразовая задача
scheduler.schedule_once(
    task_id="urgent_task",
    func=run_workflow,
    run_date=datetime(2024, 12, 31, 23, 59)
)
```

## 📝 TODO
- [ ] Workflow executor integration
- [ ] Job persistence (DB)
- [ ] Job history и logs
- [ ] Notification on completion/failure
- [ ] Max retries и error handling
- [ ] Job dependencies
