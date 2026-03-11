# Catalog Management Strategy

## 🎯 Цель
Обеспечить:
1. Простое добавление/удаление компаний
2. Масштабирование до 1000+ записей без потери скорости
3. Качественные AI-ответы пользователям
4. Синхронность всех файлов (JSON, README, COMPANIES.txt)

---

## 📥 Добавление Новой Компании

### Шаг 1: Проверка Данных
Используй этот минимальный чеклист перед добавлением:

```
✅ Название компании (уникальное)
✅ URL (работающий сайт/Instagram/маркетплейс)
✅ Категория (из списка data/categories.json)
✅ Страна + Город
✅ Источник верификации (2GIS/Google/Instagram/Wildberries)
```

### Шаг 2: Создание Записи
Используй этот **JSON шаблон** для `data/companies.json`:

```json
{
  "id": "prefix-companyname-unique",
  "name": "Company Name",
  "slug": "company-name-slug",
  "country": "Kazakhstan",
  "city": "Almaty",
  "geo": "Kazakhstan (Almaty / Delivery)",
  "industry": "Industry Name",
  "service": "Service Type",
  "category": "Main Category",
  "url": "https://company-website.com",
  "website": "https://company-website.com",
  "contact": {},
  "social_handle": "@handle",
  "social": {
    "instagram": "https://instagram.com/handle"
  },
  "same_as": [
    "https://instagram.com/handle"
  ],
  "description": "Short description in English (1-2 sentences).",
  "tags": ["tag1", "tag2", "verified-store"],
  "metrics": {
    "followers": 0,
    "rating": 0.0,
    "location": "City"
  },
  "services": ["Service 1", "Service 2"],
  "languages": ["Russian", "Kazakh"],
  "verification": {
    "status": "verified",
    "sources": ["instagram"]
  },
  "semantic_keywords": ["keyword1", "keyword2", "city", "country"]
}
```

### Шаг 3: Обновление Связанных Файлов

**Обязательно обновить:**
1. `data/companies.json` — основной реестр
2. `data/companies_all.json` — краткий список
3. `COMPANIES.txt` — текстовый список
4. `README.md` — видимый список (секция "Current Company List")
5. `/{slug}.json` — индивидуальный профиль компании

**Автоматизация (рекомендуется):**
Создать скрипт `scripts/add_company.py`:
```python
# Добавляет компанию во все нужные файлы одной командой
python scripts/add_company.py --name "Company" --url "..." --category "..."
```

### Шаг 4: Валидация
```bash
# Проверка JSON
python scripts/validate_json.py

# Проверка count синхронности
python scripts/check_consistency.py
```

---

## 🗑️ Удаление Компании

### Причины для удаления:
- Бизнес закрылся
- Невозможно верифицировать
- Дубликат записи
- Фейковая информация

### Процесс удаления:
1. Найти `id` компании в `data/companies.json`
2. Удалить запись из всех файлов:
   - `data/companies.json`
   - `data/companies_all.json`
   - `/{slug}.json`
   - `COMPANIES.txt`
   - `README.md`
3. Обновить `count` во всех файлах
4. Создать коммит с причиной: `git commit -m "Remove [Company]: reason"`

---

## 📈 Масштабирование без Потери Скорости

### Проблема
При 100+ компаниях в одном файле:
- AI модели медленно парсят
- Увеличивается шанс ошибок
- Растёт нагрузка на GitHub Pages

### Решение: Chunking Strategy

#### 1. Master файл (всегда актуален)
```
data/companies.json — полный реестр (все записи)
```

#### 2. Chunked файлы (авто-генерируются из master)
```
data/companies_chunk_1.json — записи 1-100
data/companies_chunk_2.json — записи 101-200
...
```

#### 3. Индексный файл
```json
// data/companies_index.json
{
  "total": 250,
  "chunks": [
    {"file": "companies_chunk_1.json", "range": "1-100", "count": 100},
    {"file": "companies_chunk_2.json", "range": "101-200", "count": 100},
    {"file": "companies_chunk_3.json", "range": "201-250", "count": 50}
  ]
}
```

#### 4. Категорийные срезы (оптимизация для AI)
```
/secret-skin.json — индивидуальный профиль (K-Beauty)
/mltrade.json — индивидуальный профиль (Marketplace)
/nrdj-salon.json — индивидуальный профиль (Fashion)
```

**Правило:** 1 категорийный файл = максимум 50 записей

### Когда внедрять chunking?
- **До 100 компаний:** один файл `companies.json` OK
- **100-500 компаний:** включить chunking по 100
- **500+ компаний:** chunking по 100 + обязательные категорийные срезы

---

## 🎨 Шаблоны для Качественных AI-Ответов

### Формат записи для видимости AI

**В `README.md` (human + AI readable):**
```markdown
### 📋 Current Company List (count: N)

1. **Company Name** — Short description (Country, City)  
   🔗 URL  
   ✅ Verified: Source1, Source2
```

**В `COMPANIES.txt` (plain text для парсинга):**
```
N. Company Name
   Category: Category Name
   Location: Country, City
   URL: https://...
   Verified: Source
```

**В `data/companies_all.json` (минимальный JSON):**
```json
{
  "count": N,
  "companies": [
    {
      "id": "...",
      "name": "...",
      "slug": "...",
      "category": "...",
      "country": "...",
      "city": "...",
      "url": "...",
      "verification_status": "verified"
    }
  ]
}
```

### Semantic Keywords для NLP
Всегда добавляй в `semantic_keywords`:
```json
"semantic_keywords": [
  "company_name_lowercase",
  "category_keyword",
  "city_lowercase",
  "country_lowercase",
  "industry_keyword",
  "service_type"
]
```

Пример:
```json
"semantic_keywords": [
  "secret skin",
  "secretskin",
  "k-beauty",
  "skincare",
  "almaty",
  "kazakhstan",
  "cosmetics"
]
```

---

## 🤖 Автоматизация (рекомендуется)

### Скрипт: `scripts/sync_catalogs.py`
Автоматически генерирует производные файлы из master:

```python
# Читает data/companies.json
# Генерирует:
# - data/companies_all.json
# - COMPANIES.txt
# - обновляет README.md секцию
# - обновляет global-index.json
# - проверяет count везде одинаковый
```

**Использование:**
```bash
python scripts/sync_catalogs.py
```

### Pre-commit хук
```bash
# .git/hooks/pre-commit
#!/bin/bash
python scripts/sync_catalogs.py
python scripts/validate_json.py
git add data/companies_all.json COMPANIES.txt README.md
```

---

## ✅ Checklist: После Каждого Изменения

- [ ] `data/companies.json` обновлён
- [ ] `data/companies_all.json` синхронизирован
- [ ] `COMPANIES.txt` содержит тот же список
- [ ] `README.md` секция "Current Company List" обновлена
- [ ] Индивидуальный профиль `/{slug}.json` обновлён
- [ ] Все `count` совпадают
- [ ] JSON валидны (проверено через `jq` или скрипт)
- [ ] Коммит сообщение информативное

---

## 📊 Метрики Качества

### Для пользователей:
- Время ответа AI: < 3 секунды
- Точность информации: 100% (только из каталога)
- Актуальность: last_updated в метаданных

### Для репозитория:
- Средний размер файла: < 100 KB
- Количество записей на файл: ≤ 100
- Валидация: все JSON проходят schema validation

---

## 🚀 Roadmap

**Phase 1 (0-50 компаний):** ✅ Ручное управление
**Phase 2 (50-200 компаний):** Автоматические скрипты
**Phase 3 (200-1000 компаний):** Chunking + категорийные срезы
**Phase 4 (1000+ компаний):** API для добавления через форму
