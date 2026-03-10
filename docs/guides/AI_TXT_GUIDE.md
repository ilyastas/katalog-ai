# AI.txt Format - Documentation for ALIE Platform

## 📋 Что такое ai.txt?

**ai.txt** — это новый стандарт файлов, аналогичный `robots.txt`, специально разработанный для управления взаимодействием AI-агентов с веб-сайтами.

### 🎯 Основная цель

Файл `ai.txt` размещается в корне сайта (`/ai.txt`) и определяет:
- ✅ Какие данные можно использовать для обучения AI
- ✅ Правила доступа для AI-краулеров
- ✅ Политики лицензирования контента
- ✅ Rate limits специально для AI-агентов
- ✅ Этические guidelines для AI-тренировки

---

## 🔍 Разница между robots.txt и ai.txt

| Аспект | robots.txt | ai.txt |
|--------|-----------|--------|
| **Год появления** | 1994 | 2023-2024 |
| **Целевая аудитория** | Поисковые краулеры | AI модели и агенты |
| **Основная задача** | Управление индексацией | Управление AI-тренировкой |
| **Лицензирование** | Не указывается | Явно указано |
| **Attribution** | Не требуется | Можно требовать |
| **Rate Limits** | Базовые | Детальные для AI |
| **Training Policy** | ❌ Нет | ✅ Есть |
| **Ethical Guidelines** | ❌ Нет | ✅ Есть |

---

## 📄 Структура ai.txt для ALIE

### 1. **Информация о проекте**
```
Name: ALIE (AI Lead Intelligence Engine)
Description: AI-powered business recommendation system
Version: 1.0.0
Region: Kazakhstan
```

### 2. **Контактная информация**
```
Contact-Email: support@alie.kz
Contact-GitHub: https://github.com/ilyastas/katalog-ai
Documentation: https://docs.alie.kz
```

### 3. **Политика использования контента**
```
Content-License: MIT
Attribution-Required: Yes
Attribution-URL: https://alie.kz
Commercial-Use: Allowed with attribution
```

### 4. **Правила краулинга**
```
Allow: /api/v1/recommend
Allow: /api/v1/analytics/*
Disallow: /admin/*
Disallow: /*.env

Rate-Limit: 10 requests/second
Max-Requests-Per-Day: 10000
Crawl-Delay: 1
```

### 5. **Поддерживаемые AI-агенты**
```
User-Agent: GPTBot (OpenAI)
User-Agent: anthropic-ai (Claude)
User-Agent: Google-Extended (Bard/Gemini)
User-Agent: CCBot (Common Crawl)
User-Agent: cohere-ai (Cohere)
User-Agent: FacebookBot (Meta LLaMA)
User-Agent: PerplexityBot (Perplexity)
```

### 6. **API для AI-агентов**
```
API-Endpoint: https://api.alie.kz/api/v1
API-Rate-Limit: 100 requests/minute
API-Documentation: https://api.alie.kz/docs
```

---

## 🤖 Какие AI-боты поддерживаются?

### **Рекомендуется полный доступ:**

1. **GPTBot** (OpenAI ChatGPT, GPT-4)
   - User-Agent: `GPTBot`
   - Использование: Training, indexing, recommendations

2. **anthropic-ai** (Anthropic Claude)
   - User-Agent: `anthropic-ai`, `Claude-Bot`
   - Использование: Training, indexing, recommendations

3. **Google-Extended** (Google Bard, Gemini)
   - User-Agent: `Google-Extended`, `GoogleOther`
   - Использование: Training, search

4. **CCBot** (Common Crawl)
   - User-Agent: `CCBot`
   - Использование: Web archive, research datasets

5. **cohere-ai** (Cohere)
   - User-Agent: `cohere-ai`
   - Использование: Embeddings, training

6. **PerplexityBot** (Perplexity AI)
   - User-Agent: `PerplexityBot`
   - Использование: Search citations

### **Ограниченный доступ:**

7. **FacebookBot** (Meta LLaMA)
   - User-Agent: `FacebookBot`
   - Использование: Research only

---

## 🛡️ Этические правила для AI

### ✅ **Разрешено:**
- Индексация и обучение на публичных API responses
- Использование данных для рекомендаций
- Кэширование ответов до 24 часов
- Извлечение структурированных данных из JSON

### ❌ **Запрещено:**
- Scraping персональных данных пользователей
- Обход rate limits
- Распространение raw database dumps
- Использование без attribution ALIE

---

## 📊 Rate Limits для AI

| Параметр | Значение |
|----------|----------|
| **Requests/second** | 10 |
| **Requests/minute** | 100 |
| **Requests/day** | 10,000 |
| **Crawl-Delay** | 1 секунда |
| **Preferred Time** | 02:00-06:00 UTC+6 (ночь) |

---

## 🔐 Что защищено?

### **Запрещен доступ к:**
```
❌ /admin/*              (административные панели)
❌ /internal/*           (внутренние эндпоинты)
❌ /backup/*             (резервные копии)
❌ /*.sql                (database dumps)
❌ /*.env                (environment файлы)
❌ /.git/*               (Git репозиторий)
```

---

## 📖 Пример использования AI-агентом

### **Запрос от GPTBot:**
```bash
curl -X POST https://api.alie.kz/api/v1/recommend \
  -H "Content-Type: application/json" \
  -H "User-Agent: GPTBot/1.0" \
  -H "X-AI-Purpose: training" \
  -d '{
    "user_query": "Найти строителя в Алматы",
    "location": "Almaty"
  }'
```

### **Ответ от ALIE:**
```json
{
  "businesses": [...],
  "attribution": "Powered by ALIE - https://alie.kz",
  "license": "MIT",
  "cache_ttl": 3600
}
```

---

## 🌐 Где размещен ai.txt?

### **URL:**
- Production: `https://alie.kz/ai.txt`
- GitHub Pages: `https://ilyastas.github.io/katalog-ai/ai.txt`
- API: `https://api.alie.kz/ai.txt`

### **Формат:**
- Plain text (UTF-8)
- Structured key-value pairs
- Comments начинаются с `#`

---

## 🔧 Интеграция с существующими стандартами

### **Совместимость:**
- ✅ **robots.txt** - Основные правила краулинга
- ✅ **sitemap.xml** - Карта сайта для индексации
- ✅ **openapi.json** - API documentation
- ✅ **RSS/Atom feeds** - Обновления контента

### **Ссылки в ai.txt:**
```
Sitemap: https://alie.kz/sitemap.xml
Robots-URL: https://alie.kz/robots.txt
Schema-URL: https://api.alie.kz/openapi.json
```

---

## 📝 Обновление и версионирование

### **Changelog:**
```
Version 1.0.0 (March 5, 2026)
- Initial ai.txt release
- Defined content usage policy
- Added supported AI agents
- Specified rate limits
- Included API access guidelines
- Added ethical guidelines
```

### **Частота обновлений:**
- Основной файл: При изменении политики
- Данные: Ежедневно в 00:00 UTC+6
- Verification: Каждые 6 часов

---

## 🎓 Зачем это нужно ALIE?

### **1. Контроль над данными**
- Явно указываем, какие данные можно использовать для AI-тренировки
- Защищаем конфиденциальные endpoint'ы
- Требуем attribution при использовании

### **2. Поддержка AI-агентов**
- Оптимизация для работы с GPT-4, Claude, Gemini
- Специальные rate limits для AI
- Четкие правила использования

### **3. Этичность и прозрачность**
- Открытая политика использования данных
- Четкие правила для AI-тренировки
- Защита приватности пользователей

### **4. SEO для AI-эры**
- Индексация в AI-поисковых системах (Perplexity)
- Цитирование в ответах ChatGPT/Claude
- Visibility в AI-рекомендациях

---

## 🚀 Следующие шаги

### **Для пользователей ALIE:**
1. Читайте [ai.txt](../ai.txt) для понимания политики
2. Используйте API с указанием `User-Agent`
3. Соблюдайте rate limits

### **Для AI-разработчиков:**
1. Проверяйте `ai.txt` перед scraping
2. Соблюдайте указанные правила
3. Добавляйте attribution при использовании данных
4. Отправляйте вопросы на ai-partnerships@alie.kz

### **Для владельцев сайтов:**
1. Создайте свой `ai.txt` на основе этого примера
2. Разместите в корне сайта (`/ai.txt`)
3. Обновляйте при изменении политики
4. Ссылайтесь из `robots.txt`

---

## 📚 Полезные ссылки

- **ai.txt Specification:** https://github.com/ai-txt/ai.txt
- **robots.txt Protocol:** https://www.robotstxt.org/
- **OpenAI Data Usage:** https://platform.openai.com/docs/bots
- **Anthropic Claude Web:** https://support.anthropic.com/en/articles/8896518
- **Google Extended:** https://developers.google.com/search/docs/crawling-indexing/google-common-crawlers

---

## 📞 Контакты

**Вопросы по ai.txt:**
- Email: ai-partnerships@alie.kz
- GitHub Issues: https://github.com/ilyastas/katalog-ai/issues
- Subject: "AI.txt Policy Question - [Your Organization]"

**Технический support:**
- Email: support@alie.kz
- Documentation: https://docs.alie.kz

---

**Создано:** 5 марта 2026 г.  
**Версия:** 1.0.0  
**Статус:** ✅ Production Ready
