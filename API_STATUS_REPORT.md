# 🔍 API Status Report — Статус ключей и endpoints

> 📅 Создано: 10 марта 2026 г.  
> 📦 Репозиторий: katalog-ai  
> 🔐 Источник secrets: GitHub Actions Secrets

---

## 🔑 Статус API ключей

### ✅ Настроены в GitHub Secrets

| Ключ | Провайдер | Статус | Использование |
|------|-----------|--------|---------------|
| `GOOGLE_AI_API_KEY` | Google AI Studio (Gemini) | ✅ Работает | Генерация embeddings (бесплатный tier) |
| `GOOGLE_PLACES_KEY` | Google Places API | ✅ Работает | Верификация компаний + enrichment |
| `OPENAI_API_KEY` | OpenAI | ⚠️ **Неоплаченный** | Чат, embeddings (НЕ работает) |
| `OPENAI_ASSISTANT_ID` | OpenAI Assistants | ⚠️ **Неоплаченный** | Ассистент ALIE (НЕ работает) |
| `TWOGIS_API_KEY` | 2ГИС API | ❓ | Верификация (Казахстан) |
| `APIFY_TOKEN` | Apify | ❓ | Scraping OLX/Kaspi |

### ❌ НЕ настроены локально

- Нет `.env` или `.env.local` файла в репозитории
- Для локальной разработки нужно создать `.env.local` (есть пример в [.env.example](.env.example))

---

## 🧠 Генерация Embeddings (Семантический поиск)

### Статус скрипта: ✅ Готов к работе

**Файл:** [scripts/generate_embeddings.py](scripts/generate_embeddings.py)

**Провайдеры:**
- 🥇 **Предпочитаемый:** Google AI (Gemini) — `models/gemini-embedding-001` (БЕСПЛАТНО)
- 🥈 **Fallback:** OpenAI — `text-embedding-3-small` (платно, сейчас недоступен)

**Auto-режим:**
```bash
python scripts/generate_embeddings.py --provider auto --datafile data/companies.json --output data/embeddings.json
```

Скрипт автоматически выберет Google AI если ключ `GOOGLE_AI_API_KEY` доступен.

### ✅ Где работает:

#### 1. GitHub Actions (CI/CD) — ✅ РАБОТАЕТ

**Workflow:** [.github/workflows/update.yml](.github/workflows/update.yml#L50-L60)

```yaml
env:
  OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  GOOGLE_AI_API_KEY: ${{ secrets.GOOGLE_AI_API_KEY }}
run: |
  python scripts/generate_embeddings.py --provider auto --datafile data/companies.json --output data/embeddings.json
```

- ✅ Использует `GOOGLE_AI_API_KEY` из secrets
- ✅ Автоматически запускается при изменении `data/**`
- ✅ Результат коммитится в репозиторий (файл `data/embeddings.json`)

#### 2. Локально — ❌ НЕ РАБОТАЕТ (нет .env файла)

**Чтобы запустить локально:**

```bash
# 1. Создать .env.local (не коммитится в git)
echo "GOOGLE_AI_API_KEY=AIza..." > .env.local

# 2. Установить зависимости
pip install google-generativeai python-dotenv

# 3. Запустить
python scripts/generate_embeddings.py --provider google
```

---

## 📡 Backend API Endpoints — Что работает?

### ✅ Работает БЕЗ API ключей

#### 1. `/api/v1/recommend` — Рекомендации бизнеса ✅

**Требования:** PostgreSQL + Neo4j (NO API KEYS)

**Что делает:**
- Поиск компаний по запросу (PostgreSQL)
- Семантический поиск через граф (Neo4j)
- Фильтрация по категории/городу
- Сортировка по trust_score

**Пример:**
```bash
POST /api/v1/recommend
{
  "query": "салон красоты Алматы",
  "category": "beauty",
  "limit": 5,
  "verified_only": true
}
```

**Зависимости:**
- ✅ PostgreSQL (локальная база)
- ✅ Neo4j (граф связей)
- ❌ НЕ требует OpenAI/Google

---

#### 2. `/api/v1/verify/{business_id}/verify` — Верификация ✅ (частично)

**Требования:** 2ГИС API, Google Places API (NO OpenAI)

**Что делает:**
- Проверяет существование компании в 2ГИС
- Проверяет в Google Places
- Обновляет trust_score

**Статус:**
- ✅ Код готов
- ⚠️ Требует `GOOGLE_PLACES_KEY` (есть в secrets)
- ⚠️ Требует `TWOGIS_API_KEY` (статус неизвестен)

---

#### 3. `/api/v1/analytics/daily` — Аналитика ✅

**Требования:** PostgreSQL ONLY

**Что делает:**
- Статистика по дням (клики, рекомендации, звонки)
- Revenue metrics
- Category breakdown

**Зависимости:**
- ✅ PostgreSQL (таблица `lead_events`)

---

### ❌ НЕ работает (требует оплаченный OpenAI)

#### 4. `/api/v1/openai/chat` — Чат с AI ассистентом ❌

**Требования:** OpenAI API ключ (PAID)

**Что делает:**
- Многораундовый чат (OpenAI Assistants)
- Function calling для рекомендаций
- Контекст из каталога

**Почему не работает:**
- ❌ `OPENAI_API_KEY` неоплаченный
- ❌ `OPENAI_ASSISTANT_ID` требует настройки

**Файл:** [backend/api/endpoints/openai_chat.py](backend/api/endpoints/openai_chat.py#L47-L79)

---

## 🚀 GitHub Actions Workflows — Где используются ключи

### 1. [update.yml](.github/workflows/update.yml) — Dataset Update

**Триггеры:**
- Push в `main` (пути: `data/**`, `website/**`, `index.html`)
- Manual dispatch

**Использует:**
- `OPENAI_API_KEY` — embeddings (fallback) ⚠️
- `GOOGLE_AI_API_KEY` — embeddings (primary) ✅

**Статус:** ✅ Работает через Google AI

---

### 2. [update-catalog.yml](.github/workflows/update-catalog.yml) — Catalog Enrichment

**Триггеры:**
- Webhook (новые компании)
- Schedule (раз в неделю)

**Использует:**
- `GOOGLE_PLACES_KEY` — enrichment ✅

**Статус:** ✅ Работает

---

### 3. [deploy-production.yml](.github/workflows/deploy-production.yml) — Kubernetes Deploy

**Использует:**
- `OPENAI_API_KEY` — передается в контейнер ⚠️
- `GOOGLE_PLACES_KEY` — передается в контейнер ✅

**Статус:** ⚠️ Частично работает (OpenAI endpoints не работают)

---

## 📊 Сводка — что работает прямо сейчас

| Компонент | Статус | Примечание |
|-----------|--------|------------|
| **Генерация embeddings (CI/CD)** | ✅ | Через Google AI (бесплатно) |
| **Генерация embeddings (локально)** | ❌ | Нет .env файла |
| **Recommend API** | ✅ | PostgreSQL + Neo4j |
| **Verification API** | ⚠️ | Требует проверки ключей 2ГИС |
| **Analytics API** | ✅ | PostgreSQL only |
| **OpenAI Chat API** | ❌ | Неоплаченный токен |
| **GitHub Pages** | ✅ | Статический каталог |
| **Auto-stats generation** | ✅ | Каждые 6 часов |

---

## 🔧 Рекомендации

### Чтобы ВСЁ работало локально:

1. Создать `.env.local`:
```bash
# Google AI (бесплатный tier)
GOOGLE_AI_API_KEY=AIzaSy...

# Google Places (платный, но есть free quota)
GOOGLE_PLACES_KEY=AIzaSy...

# 2ГИС (Казахстан)
TWOGIS_API_KEY=...

# OpenAI (только если оплачен)
# OPENAI_API_KEY=sk-proj-...
```

2. Установить зависимости:
```bash
pip install -r backend/requirements.txt
pip install google-generativeai
```

3. Запустить backend:
```bash
cd backend
uvicorn main:app --reload
```

### Чтобы активировать OpenAI чат:

1. Оплатить OpenAI токен
2. Зарегистрировать ассистента:
```bash
python backend/scripts/register_openai_assistant.py
```
3. Обновить `OPENAI_ASSISTANT_ID` в GitHub Secrets

---

## ✅ Итог

**Сейчас БЕЗ оплаты работает:**
- ✅ Семантический поиск (через Google AI Gemini embeddings)
- ✅ Рекомендации компаний (PostgreSQL + Neo4j)
- ✅ Аналитика
- ✅ Верификация (частично, через Google Places)
- ✅ GitHub Actions автоматизация

**НЕ работает без оплаты:**
- ❌ OpenAI чат-ассистент
- ❌ OpenAI embeddings (но есть бесплатный fallback на Gemini)

**Вывод:** Каталог и основные API **полностью функциональны** даже без оплаты OpenAI. OpenAI нужен только для чат-интерфейса.
