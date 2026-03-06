# 📈 Scaling Guide для Katalog-AI

Рекомендации по масштабированию Katalog-AI когда число бизнесов превысит 100.

---

## 🎯 Этапы масштабирования

### Фаза 1: 0-50 бизнесов ✅ (ТЕКУЩЕЕ СОСТОЯНИЕ)

- ✅ Все данные в одном файле ($category.json)
- ✅ JSON файлы < 5MB
- ✅ Ручная верификация
- ✅ GitHub Actions работают быстро

### Фаза 2: 50-200 бизнесов 📊 (СЛЕДУЮЩАЯ)

- ⚠️ JSON файлы начинают расти
- ⚠️ Нужна оптимизация парсинга
- 🔄 Внедрить пейджинацию

### Фаза 3: 200-1000 бизнесов 🚀 (ДОЛГОСРОЧНАЯ)

- ❌ Нужна база данных (PostgreSQL, MongoDB)
- ❌ API сервер (Node.js, FastAPI)
- ❌ Кэширование (Redis, Cloudflare)
- ❌ CDN распределение

### Фаза 4: 1000+ бизнесов 🏢 (ЭСКЕЙЛ)

- ✋ Требуется отдельная инфраструктура
- ✋ Многояндекс шардирование
- ✋ Микросервисы

---

## 1️⃣ Оптимизация для 50-200 бизнесов

### 1.1: Разделение больших каталогов

Когда `beauty.json` > 2MB, раздели по городам:

**Было:**
```
catalog/
├── beauty.json (3MB)
```

**Стало:**
```
catalog/beauty/
├── beauty-almaty.json         (1.5MB)
├── beauty-nursultan.json      (1.0MB)
├── beauty-other-cities.json   (0.5MB)
└── beauty-index.json          (метаданные всех)
```

### 1.2: Пример beauty-index.json

```json
{
  "@type": "DataCatalog",
  "name": "Beauty & Cosmetics Index",
  "partOf": [
    {
      "name": "Almaty",
      "url": "https://ilyastas.github.io/katalog-ai/catalog/beauty/beauty-almaty.json",
      "itemCount": 25
    },
    {
      "name": "Nur-Sultan",
      "url": "https://ilyastas.github.io/katalog-ai/catalog/beauty/beauty-nursultan.json",
      "itemCount": 18
    }
  ]
}
```

### 1.3: Пейджинация для ИИ

Добавь в OpenAPI:

```yaml
/api/search:
  get:
    parameters:
      - name: page
        in: query
        description: Номер страницы (1, 2, 3...)
        schema:
          type: integer
          default: 1
      - name: limit
        in: query
        description: Кол-во результатов на странице
        schema:
          type: integer
          default: 50
          maximum: 100
    responses:
      '200':
        description: Результаты с пейджинацией
        content:
          application/json:
            schema:
              type: object
              properties:
                page:
                  type: integer
                limit:
                  type: integer
                total:
                  type: integer
                pages:
                  type: integer
                results:
                  type: array
```

### 1.4: Компрессия JSON

Установи gzip compression на GitHub Pages:

```
# .github/workflows/compress-catalog.yml
name: Compress Catalogs
on: [push]

jobs:
  compress:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Gzip JSON files
        run: |
          gzip -k catalog/beauty.json
          gzip -k catalog/museums.json
          # ... все файлы
          
      - name: Upload compressed
        run: git add *.json.gz && git commit -m "Compressed catalogs"
```

---

## 2️⃣ Внедрение простого API сервера

### 2.1: Когда это нужно

- ❌ JSON файлы > 20MB
- ❌ Полнотекстовый поиск нужен
- ❌ Фильтрация по множеству параметров

### 2.2: Рекомендуемый стек

**Вариант 1: Node.js (простой)**

```javascript
// server.js
const express = require('express');
const fs = require('fs');
const app = express();

// Загрузи все JSON в памяти
const catalogs = {
  beauty: JSON.parse(fs.readFileSync('catalog/beauty.json')),
  museums: JSON.parse(fs.readFileSync('catalog/museums.json')),
  // ...
};

// Поиск
app.get('/api/search', (req, res) => {
  const { q, category } = req.query;
  
  let results = [];
  
  // Поиск по имени и описанию
  Object.values(catalogs).forEach(cat => {
    cat['@graph'].forEach(item => {
      if (item.name.includes(q) || item.description.includes(q)) {
        results.push(item);
      }
    });
  });
  
  res.json({ results, total: results.length });
});

app.listen(3000);
```

**Вариант 2: Python FastAPI (фан-фан)**

```python
# main.py
from fastapi import FastAPI, Query
from typing import List
import json

app = FastAPI()

# Загрузи каталоги
with open('catalog/beauty.json') as f:
    beauty = json.load(f)

@app.get('/api/search')
async def search(q: str, limit: int = Query(10, le=100)):
    results = []
    for item in beauty['@graph']:
        if q.lower() in item['name'].lower():
            results.append(item)
    return {'results': results[:limit], 'total': len(results)}

# Запусти: uvicorn main:app --reload
```

### 2.3: Развёртывание API

**На Railway (бесплатно + платно):**

```bash
# 1. Инициализируй проект
railwayapp init

# 2. Создай Procfile
echo "web: python main.py" > Procfile

# 3. Поднимай на Railway
railway up
```

**На Vercel (Node.js):**

```bash
vercel deploy
```

**На Heroku (legacy, платно):**

```bash
heroku login
heroku create katalog-ai-api
git push heroku main
```

---

## 3️⃣ Внедрение базы данных

### 3.1: Когда нужна БД

- ❌ > 500 бизнесов
- ❌ Нужна фильтрация реального времени
- ❌ Нужны аналитика и логирование

### 3.2: PostgreSQL с Supabase (рекомендуется)

```sql
-- Создай таблицу businesses
CREATE TABLE businesses (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  category VARCHAR(50),
  city VARCHAR(100),
  description TEXT,
  phone VARCHAR(20),
  email VARCHAR(100),
  geo_lat FLOAT,
  geo_lon FLOAT,
  rating FLOAT,
  consent_date TIMESTAMP,
  consent_expires TIMESTAMP,
  verified_2gis BOOLEAN DEFAULT FALSE,
  verified_google BOOLEAN DEFAULT FALSE,
  verified_olx BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  INDEX idx_category (category),
  INDEX idx_city (city),
  INDEX idx_rating (rating DESC)
);

-- Создай гео-индекс
CREATE INDEX geo_index ON businesses USING GIST(
  ST_MakePoint(geo_lon, geo_lat)
);
```

### 3.3: Миграция из JSON

```python
# migrate_to_db.py
import json
import supabase

# Инициализируй Supabase
client = supabase.create_client(
    "https://your-project.supabase.co",
    "your-api-key"
)

# Загрузи JSON
with open('catalog/beauty.json') as f:
    catalog = json.load(f)

# Мигрируй в БД
for business in catalog['@graph']:
    client.table('businesses').insert({
        'name': business['name'],
        'category': 'beauty',
        'city': business['address']['addressLocality'],
        'description': business['description'],
        'phone': business.get('telephone'),
        'email': business.get('email'),
        'geo_lat': business['geo']['latitude'],
        'geo_lon': business['geo']['longitude'],
        'rating': business.get('aggregateRating', {}).get('ratingValue'),
        'consent_date': business['consent']['dateGiven'],
        'verified_2gis': business['trust_signals']['verified_by_2gis'],
        'verified_google': business['trust_signals']['verified_by_google'],
        'verified_olx': business['trust_signals']['verified_by_olx'],
    }).execute()

print("✅ Миграция завершена!")
```

---

## 4️⃣ Кэширование и CDN

### 4.1: Cloudflare (бесплатно)

```
1. Добавь сайт в Cloudflare
2. Включи:
   - Cache Everything (бесплатный план)
   - Auto Minify (JS, CSS, HTML)
   - Brotli compression
3. Правило кэша для /catalog/**:
   - Cache TTL: 24 часа
```

### 4.2: Redis кэш + API

```python
# main.py с Redis
import redis
from functools import wraps

cache = redis.Redis(host='localhost', port=6379)

def cached(expire_time=3600):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Генерируй ключ кэша
            key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Проверь кэш
            cached = cache.get(key)
            if cached:
                return json.loads(cached)
            
            # Выполни функцию
            result = await func(*args, **kwargs)
            
            # Сохрани в кэш
            cache.setex(key, expire_time, json.dumps(result))
            return result
        return wrapper
    return decorator

@app.get('/api/search')
@cached(expire_time=3600)
async def search(q: str):
    # ...
```

---

## 5️⃣ Архитектура на 1000+ бизнесов

### 5.1: Микросервисная архитектура

```
┌─────────────────────────────────────────┐
│         ИИ-ассистенты (ChatGPT)        │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│        API Gateway (Kong/Nginx)          │
│  Аутентификация, Rate Limiting, Логи   │
└──────────────────┬──────────────────────┘
                   │
    ┌──────────────┼──────────────────┐
    │              │                  │
┌───▼──────┐  ┌───▼──────┐   ┌──────▼──┐
│ Search   │  │ Geo API  │   │Verify   │
│Service   │  │(ElasticS)│   │Service  │
│(FastAPI) │  │          │   │         │
└───┬──────┘  └───┬──────┘   └──────┬──┘
    │             │                 │
    └─────┬───────┴─────────┬───────┘
          │                 │
    ┌─────▼──────────────────▼────┐
    │   PostgreSQL + PostGIS       │
    │  (Geo-indexed businesses)    │
    └──────────────────────────────┘
          │        │        │
      ┌───┴───┬────┴───┬───┴────┐
      │Replica│Replica │Replica │
      └───────┴────────┴────────┘
    
    ┌─────────────────────────────┐
    │  Redis (Caching)            │
    │  - Search results           │
    │  - Geo queries              │
    │  - Rate limiting            │
    └─────────────────────────────┘
    
    ┌─────────────────────────────┐
    │  Verifier Services (async)  │
    │  - 2GIS updater             │
    │  - OLX status checker       │
    │  - Google Places monitor    │
    └─────────────────────────────┘
```

### 5.2: Kubernetes deployment

```yaml
# kubernetes/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: katalog-ai-search
spec:
  replicas: 3
  selector:
    matchLabels:
      app: katalog-ai
  template:
    metadata:
      labels:
        app: katalog-ai
    spec:
      containers:
      - name: api
        image: your-registry/katalog-ai:latest
        ports:
        - containerPort: 3000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
        - name: REDIS_URL
          value: redis://redis:6379
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: katalog-ai-service
spec:
  selector:
    app: katalog-ai
  ports:
  - protocol: TCP
    port: 80
    targetPort: 3000
  type: LoadBalancer
```

---

## 6️⃣ Мониторинг производительности

### 6.1: Core Web Vitals

```javascript
// Добавь в index.html
<script>
// Мониторинг Google Core Web Vitals
web-vital.getCLS(console.log);
web-vital.getFID(console.log);
web-vital.getFCP(console.log);
web-vital.getLCP(console.log);
web-vital.getTTFB(console.log);
</script>
```

### 6.2: Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()

@app.get("/api/search")
@limiter.limit("100/minute")
async def search(request: Request, q: str):
    # ...
```

### 6.3 DataDog мониторинг

```python
from datadog import initialize, api
from datadog import statsd

options = {
    'api_key': 'YOUR_API_KEY',
    'app_key': 'YOUR_APP_KEY'
}
initialize(**options)

@app.get("/api/search")
async def search(q: str):
    start = time.time()
    results = search_business(q)
    duration = time.time() - start
    
    statsd.timing('search.duration', duration)
    statsd.increment('search.requests')
    
    return results
```

---

## 7️⃣ Бюджет на масштабирование

### Фаза 1 (0-50 бизнеса) - **ТЕКУЩЕЕ**
- ✅ GitHub Pages: FREE
- ✅ GitHub Actions: FREE
- 💬 **Всего: $0/месяц**

### Фаза 2 (50-200 бизнесов)
- GitHub Actions: FREE
- Uptime Robot: $10/месяц
- Google Analytics: FREE
- Cloudflare: FREE
- 💬 **Всего: ~$10-20/месяц**

### Фаза 3 (200-1000 бизнесов)
- FastAPI сервер (Railway): $5-20/месяц
- PostgreSQL (Supabase): $25-100/месяц
- Redis: $10-50/месяц
- Cloudflare Pro: $20/месяц
- 💬 **Всего: ~$60-190/месяц**

### Фаза 4 (1000+ бизнесов)
- Kubernetes: $100-500/месяц
- PostgreSQL (High-end): $200+/месяц
- Redis (Production): $100+/месяц
- DataDog мониторинг: $50+/месяц
- 💬 **Всего: $450+/месяц**

---

## 🎯 Чеклист для каждої фазы

### Фаза 2 (50-100 бизнесов)
- ⬜ Раздели больше каталоги по городам
- ⬜ Добавь пейджинацию в API
- ⬜ Включи Cloudflare
- ⬜ Настрой Google Analytics
- ⬜ Добавь Rate Limiting

### Фаза 3 (100-500 бизнесов)
- ⬜ Развёртай FastAPI сервер
- ⬜ Мигрируй в PostgreSQL
- ⬜ Добавь Redis кэош
- ⬜ Настрой Elastic Search для поиска
- ⬜ Включи DataDog мониторинг

### Фаза 4 (500+ бизнесов)
- ⬜ Развёртай Kubernetes
- ⬜ Шардируй базу данных
- ⬜ Настрой geo-репликацию
- ⬜ Добавь микросервисы
- ⬜ Включи CI/CD пайплайны

---

**Последнее обновление:** 2026-03-05
