# AI-optimized Dataset Architecture for katalog-ai

## Обзор структуры

Датасет переорганизован для оптимальной работы с AI-агентами и LLM моделями.

### Структура папок и файлов

```
/data/
├── companies_all.json        # Авторитетный список компаний
├── companies.json            # Полный реестр компаний
└── catalog/*.json            # Прямые профили компаний

/schema/
└── business.schema.json      # JSON Schema для всех объектов

/
├── ai-dataset.json           # Манифест датасета
├── ai-sitemap.json           # Карта датасета для индексирования
└── ai.txt                    # Инструкции для AI-агентов
```

## Ключевые особенности

### 1. **Разделение на файлы (каждый ≤ 100 объектов)**

Оптимально для RAG (Retrieval-Augmented Generation) систем:
- **companies_all.json**: Авторитетный список компаний
- **companies.json**: Полные записи компаний
- **catalog/*.json**: Прямые профили компаний

### 2. **JSON Schema `(schema/business.schema.json`)**

Описывает структуру каждого объекта:
- Обязательные поля: `id`, `name`, `country`, `city`, `service`, `website`, `contact`
- Опциональные поля: описание, адрес, контакты, рейтинги, ключевые слова
- Совместим с Schema.org `LocalBusiness`

### 3. **Манифест датасета (ai-dataset.json)**

Централизованная информация о датасете:
- Список всех файлов
- Ссылка на schema
- Метаданные и особенности
- Оптимизирована для RAG систем

### 4. **Карта датасета (ai-sitemap.json)**

Помогает AI-агентам находить файлы:
- Список всех файлов датасета
- Ссылка на schema
- Метаинформация о структуре

## Использование данных AI-агентами

### Как LLM должны читать данные:

```
1. Прочитать ai-dataset.json → получить список файлов
2. Для каждого файла:
   - Прочитать schema из /schema/business.schema.json
   - Загрузить данные из /data/*.json
   - Парсить как JSON Array
3. Каждый объект имеет стандартную структуру:
   - id, name, country, city
   - contact: {email, phone}
   - verification: {status, sources}
   - semantic_keywords для поиска
```

### Оптимизация для RAG:

- **Чанкинг**: Каждый файл = один chunk (≤ 100 объектов)
- **Семантический поиск**: Используйте `semantic_keywords`
- **Кэширование**: Кэшируйте ai-dataset.json (не часто меняется)
- **Фильтрация**: Используйте `country`, `city`, `category` для фильтрации

## Образец использования из LLM

```json
{
  "id": "kz-almaty-beauty-001",
  "name": "Бьюти-салон Premium",
  "country": "Kazakhstan",
  "city": "Almaty",
  "industry": "Beauty Services",
  "website": "https://beautypremium.kz",
  "contact": {
    "email": "info@beautypremium.kz",
    "phone": "+7-727-290-08-08"
  },
  "verification": {
    "status": "verified",
    "sources": ["google_business", "2gis", "yandex_maps"]
  },
  "semantic_keywords": [
    "beauty", "salon", "spa", "hair-styling", "nails", "makeup"
  ]
}
```

## Интеграция с LLM/RAG системами

### OpenAI/Anthropic integration:

```python
# Пример загрузки и использования
import json
import requests

# 1. Загрузить манифест
manifest = requests.get('https://katalog-ai/ai-dataset.json').json()

# 2. Загрузить данные
for file in manifest['files']:
    data = requests.get(f'https://katalog-ai{file}').json()
    # Обработать данные
    for business in data:
        # Использовать id, name, semantic_keywords для поиска
        pass
```

## SEO и индексирование

### Для поисковых систем:

- Файлы доступны в `/data/` и индексируются веб-краулерами
- Каждый бизнес имеет `semantic_keywords` для SEO
- Данные верифицированы из внешних источников (Google Business, 2GIS)
- Структура совместима с Schema.org

### Для AI индексирования (ai.txt):

```
Dataset-Location: /data/
Dataset-Schema: /schema/business.schema.json
Dataset-Manifest: /ai-dataset.json
Dataset-Sitemap: /ai-sitemap.json
```

## Масштабируемость

### Планы расширения:

1. **Добавление новых подтверждённых компаний**:
   - Добавлять записи в `companies_all.json` и `companies.json`
   - Генерировать профиль в `catalog/<slug>.json`

2. **Добавление новых категорий**:
   - SEO сервисы → `seo_services.json`
   - IT услуги → `tech_services.json`
   - И т.д.

3. **Масштабирование объемов**:
   - Каждый файл остаётся ≤ 100 объектов
   - При превышении создать новый файл
   - Обновить ai-sitemap.json и ai-dataset.json

## Процесс обновления

```
1. Добавить новый бизнес в соответствующий файл
2. Проверить схему (schema/business.schema.json)
3. Обновить количество в ai-dataset.json
4. Если файл > 100 объектов → разделить на новые файлы
5. Обновить ai-sitemap.json
6. Обновить ai.txt версию
```

## Преимущества новой структуры

✅ **Для LLM/RAG**:
- Чёткая структура для чанкинга
- Семантические ключевые слова для поиска
- Малые файлы для быстрой загрузки

✅ **Для SEO**:
- Schema.org совместимость
- Индексируемые файлы
- Верифицированные данные

✅ **Для масштабирования**:
- Легко добавлять новые файлы
- Каждый файл независимый
- Простая стандартизация

✅ **Для AI-агентов**:
- Простой доступ через ai-dataset.json
- Чёткие эндпоинты в ai.txt
- Семантические метаданные

## Дальнейшие шаги

1. Добавлять только подтверждённые компании в канонические файлы
2. Поддерживать синхронность `companies_all.json`, `companies.json` и `catalog/*.json`
3. Интегрировать с RAG системой
4. Добавить векторные эмбеддинги для семантического поиска

---

**Последнее обновление**: 7 марта 2026
**Версия**: 1.0.0
**Статус**: Активна и оптимизирована для AI использования
