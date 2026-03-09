# Automation Scripts

Набор скриптов для управления каталогом компаний.

## 📝 Доступные скрипты

### 1. `add_company.py` — Добавление новой компании

Интерактивный скрипт для добавления компании в каталог с валидацией.

**Использование:**
```bash
python scripts/add_company.py
```

**Что делает:**
- Запрашивает все необходимые данные интерактивно
- Генерирует уникальный ID и slug
- Валидирует URL, email и другие поля
- Добавляет компанию в `data/companies.json`
- Обновляет счётчик компаний

**После запуска:**
1. Запустите `sync_catalogs.py` для обновления производных файлов
2. Проверьте изменения
3. Сделайте коммит

---

### 2. `sync_catalogs.py` — Синхронизация файлов

Автоматически генерирует производные файлы из мастер-файла `data/companies.json`.

**Использование:**
```bash
python scripts/sync_catalogs.py
```

**Что делает:**
- Генерирует `data/companies_all.json` (минималистичная версия)
- Генерирует `COMPANIES.txt` (текстовый формат)
- Создаёт секцию для `README.md` (нужно вставить вручную)
- Проверяет согласованность счётчиков

**Когда использовать:**
- После добавления/удаления компании
- После изменения данных в `data/companies.json`
- Перед коммитом изменений

---

### 3. `validate_json.py` — Валидация данных

Проверяет корректность всех JSON файлов каталога.

**Использование:**
```bash
python scripts/validate_json.py
```

**Что проверяет:**
- ✅ Корректность JSON синтаксиса
- ✅ Наличие обязательных полей
- ✅ Согласованность счётчиков между файлами
- ✅ Отсутствие дублирующихся ID и slug
- ✅ Корректность URL форматов
- ✅ Согласованность `COMPANIES.txt` с master файлом

**Когда использовать:**
- Перед каждым коммитом
- После ручных изменений JSON файлов
- При настройке CI/CD

---

## 🔄 Типичный рабочий процесс

### Добавление новой компании

```bash
# 1. Добавить компанию интерактивно
python scripts/add_company.py

# 2. Синхронизировать производные файлы
python scripts/sync_catalogs.py

# 3. Обновить README.md (скопировать секцию из вывода скрипта)
# (откройте README.md и вставьте новую секцию компаний)

# 4. Валидировать всё
python scripts/validate_json.py

# 5. Коммит
git add data/ COMPANIES.txt README.md
git commit -m "Add: Новая компания XYZ"
git push
```

### Удаление компании

```bash
# 1. Вручную удалить из data/companies.json
# (откройте файл и удалите объект компании)

# 2. Синхронизировать
python scripts/sync_catalogs.py

# 3. Обновить README.md

# 4. Валидировать
python scripts/validate_json.py

# 5. Коммит
git add data/ COMPANIES.txt README.md
git commit -m "Remove: Компания XYZ"
git push
```

### Обновление данных компании

```bash
# 1. Отредактировать data/companies.json
# (изменить нужные поля)

# 2. Синхронизировать
python scripts/sync_catalogs.py

# 3. Валидировать
python scripts/validate_json.py

# 4. Коммит
git add data/ COMPANIES.txt
git commit -m "Update: Компания XYZ - обновлены контакты"
git push
```

---

## ⚙️ Настройка CI/CD

### GitHub Actions (рекомендуется)

Создайте `.github/workflows/validate.yml`:

```yaml
name: Validate Catalog

on:
  pull_request:
    paths:
      - 'data/**'
      - 'COMPANIES.txt'
  push:
    branches:
      - main
    paths:
      - 'data/**'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.x'
      - name: Validate JSON files
        run: python scripts/validate_json.py
```

### Pre-commit Hook (локально)

Создайте `.git/hooks/pre-commit`:

```bash
#!/bin/sh
echo "🔍 Validating catalog files..."
python scripts/validate_json.py
if [ $? -ne 0 ]; then
    echo "❌ Validation failed! Commit aborted."
    exit 1
fi
echo "✅ Validation passed!"
```

Сделайте исполняемым:
```bash
chmod +x .git/hooks/pre-commit
```

---

## 📊 Требования

- **Python 3.6+** (используются только стандартные библиотеки)
- Никаких внешних зависимостей

---

## 🐛 Troubleshooting

### Ошибка "Module not found"
Убедитесь, что запускаете из корня репозитория:
```bash
cd /path/to/katalog-ai
python scripts/validate_json.py
```

### Ошибка валидации после sync
Проверьте, что `data/companies.json` корректен:
```bash
python -m json.tool data/companies.json
```

### Count не совпадает
Запустите sync с автофиксом:
```bash
python scripts/sync_catalogs.py
```

---

## 📚 Связанная документация

- [CATALOG_MANAGEMENT.md](../CATALOG_MANAGEMENT.md) — полная стратегия управления каталогом
- [CONTRIBUTING.md](../CONTRIBUTING.md) — гайд для контрибьюторов
- [README.md](../README.md) — основная документация проекта

---

**Последнее обновление:** 2025-01-28
