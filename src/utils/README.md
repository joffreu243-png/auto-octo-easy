# 🛠️ Utils Module

Утилиты и вспомогательные функции общего назначения.

## 📁 Структура

```
utils/
├── __init__.py       # Экспорты
├── helpers.py        # ✅ Вспомогательные функции
├── validators.py     # ✅ Валидаторы данных
├── crypto.py         # TODO: Шифрование/дешифрование
├── file_utils.py     # TODO: Работа с файлами
└── network_utils.py  # TODO: Сетевые утилиты
```

## 🎯 Реализовано

### Helpers (`helpers.py`)
```python
from src.utils.helpers import generate_id, format_duration, retry

# Генерация ID
id = generate_id()  # UUID4 string

# Форматирование времени
duration = format_duration(2500)  # "2.5s"

# Retry декоратор
@retry(max_attempts=3, delay=1.0)
def unstable_function():
    pass
```

### Validators (`validators.py`)
```python
from src.utils.validators import validate_url, validate_email, validate_selector

assert validate_url("https://example.com") == True
assert validate_email("user@example.com") == True
assert validate_selector("#button") == True
```

## 📝 TODO
- [ ] Crypto utils (encrypt/decrypt credentials)
- [ ] File utils (path management, temp files)
- [ ] Network utils (retry with backoff, proxy)
- [ ] String utils (sanitize, slugify)
- [ ] Date utils (parsing, formatting)
