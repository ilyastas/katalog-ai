# 📊 Стратегия мониторинга Katalog-AI

Документ описывает, как отслеживать появление ссылок на Katalog-AI в ответах ИИ-ассистентов и мониторить эффективность каталога.

---

## 🎯 Цели мониторинга

1. **Трэкинг трафика** — сколько кликов идёт на бизнесы из ИИ
2. **Верификация рекомендаций** — появляются ли ссылки на каталог в ответах ИИ
3. **Анализ целевой аудитории** — какие ИИ-ассистенты используют каталог
4. **Оптимизация данных** — какие бизнесы рекомендуют чаще
5. **ROI для партнёров** — сколько трафика получает каждый бизнес

---

## 1️⃣ Мониторинг доступа ИИ-ботов

### Через Google Analytics 4

#### Шаг 1: Установи GA4

1. Перейди на https://analytics.google.com
2. Создай новое свойство: "katalog-ai"
3. Выбери платформу: "Web"
4. Добавь сайт: https://ilyastas.github.io/katalog-ai/

#### Шаг 2: Добавь на страницу

Добавь GA4 код в `index.html`:

```html
<!-- Google Analytics 4 -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```

#### Шаг 3: Фильтруй по User Agent

В GA4 создай фильтр для отслеживания только ИИ-ботов:

```
Filter Type: Include
User Agent contains: (GPTBot|Claude|PerplexityBot|CCBot|Google-Extended|OAI-SearchBot|Bingbot)
```

#### Что видишь в GA4:

- 📊 **Traffic Source** — какие ИИ-ботов заходят
- 🌍 **Geographic Location** — из каких стран запросы
- ⏱️ **Time Patterns** — когда ботов активны
- 💾 **Data Download** — просмотренные JSON файлы

---

## 2️⃣ Отслеживание кликов через UTM

### Как работает

Все ссылки в каталоге содержат UTM-параметры:

```
https://beautyprime.kz/?utm_source=ai_assistant&utm_campaign=beauty_recommendations&utm_medium=ai_catalog
```

### Настрой в Google Analytics

1. **Acquisition → UTM Source**
   - Фильтр по: `ai_assistant`
   - Видишь все клики с каталога

2. **Acquisition → UTM Campaign**
   - `beauty_recommendations` — клики из бьюти-каталога
   - `culture_recommendations` — из музеев
   - `luxury_goods` — из премиум-товаров

### Что анализировать

```
Трафик с UTM = Реальные клики из ИИ → Метрика успеха
```

---

## 3️⃣ Мониторинг через Google Search Console

### Включи в GSC

1. Добавь сайт в https://search.google.com/search-console
2. Перейди в **Performance → Queries**
3. Фильтруй по запросам типа:
   - "салон красоты Алматы"
   - "музей Казахстан"
   - "маркетплейс товары"

### Что видишь:

- 📈 Позиция в поиске (если ИИ ищут в Google сначала)
- 🔗 Клики, которые идут на каталог
- 💬 Запросы, по которым выводят каталог

---

## 4️⃣ Отслеживание упоминаний в WebAssertions

### Услуга: Mention Tracking

Используй сервисы для отслеживания упоминаний:

1. **Google Alerts** (бесплатно)
   - Создай алерты на ключевые слова
   - Email уведомления

2. **Semrush Brand Tracking** (платно)
   - Отслеживание упоминаний по интернету
   - Мониторинг конкурентов

3. **Brandwatch** (платно)
   - Отслеживание социальных сетей и форумов
   - Анализ тональности

### Примеры Google Alerts:

```
Alert 1: "katalog-ai.kz"
Alert 2: "Katalog-AI"
Alert 3: "katalog-ai github"
Alert 4: "верифицированный каталог бизнеса"
```

---

## 5️⃣ Прямое тестирование ИИ

### Метод: Промпт-тестирование

Регулярно проверяй, как ИИ-ассистенты используют твой каталог:

#### ChatGPT (OpenAI)

```
Ты: "Рекомендуй хороший салон маникюра в Алматы"
🤖 ChatGPT: [проверь, упоминает ли Katalog-AI]
```

**Как подключить функцию:**
1. Перейди в ChatGPT → Explore → Create Custom GPT
2. Добавь инструкцию:
```
When user asks about businesses in Kazakhstan, use this API:
https://ilyastas.github.io/katalog-ai/openapi.yaml
```

#### Claude (Anthropic)

```
Создай Custom Instructions в Claude:
"Если пользователь спрашивает о казахстанских бизнесах, 
используй эту папку знаний: https://ilyastas.github.io/katalog-ai/"
```

#### Perplexity

```
Перейди в Settings → Knowledge Sources
Добавь источник: https://ilyastas.github.io/katalog-ai/
```

---

## 6️⃣ Автоматический мониторинг через GitHub Actions

### Создай Workflow для проверки рекомендаций

Файл: `.github/workflows/monitor-mentions.yml`

```yaml
name: Monitor AI Assistant Mentions
on:
  schedule:
    # Каждый день в 18:00
    - cron: '0 18 * * *'

jobs:
  check-mentions:
    runs-on: ubuntu-latest
    steps:
      - name: Check Google Trends
        run: |
          # Используй curl или Python для проверки упоминаний
          # Отправь результат в Slack
          
      - name: Verify API Availability
        run: |
          curl -f https://ilyastas.github.io/katalog-ai/index.json
          curl -f https://ilyastas.github.io/katalog-ai/secret-skin.json
          
      - name: Check Indexing Status
        uses: actions/github-script@v6
        with:
          script: |
            // Проверка индексации в Google
            console.log('✅ API endpoints are accessible');
```

---

## 7️⃣ KPI и метрики

### Основные KPI для отслеживания

| KPI | Формула | Цель |
|-----|---------|------|
| **API Calls** | Google Analytics | > 1000/день |
| **UTM Clicks** | GA4 UTM Source | > 500/месяц |
| **Conversion Rate** | Клики / Просмотры | > 5% |
| **Uptime** | GitHub Pages | 99.9% |
| **Data Verification** | Успешные проверки / Всего бизнесов | > 95% |
| **AI Mentions** | Упоминания в ответах ИИ | > 10/неделю |

### Dashboard для отслеживания

Создай Google Sheets для ручного мониторинга:

```
Дата | Google Analytics | UTM Клики | Верифицировано | Статус API | Примечания
2026-03-05 | 1250 | 125 | 8/10 | ✅ OK | Первый день
```

---

## 8️⃣ Стек инструментов для мониторинга

### Бесплатные инструменты:

| Инструмент | Назначение | Ссылка |
|-----------|-----------|--------|
| **Google Analytics 4** | Трафик и аналитика | https://analytics.google.com |
| **Google Search Console** | Видимость в поиске | https://search.google.com/search-console |
| **Google Alerts** | Упоминания в интернете | https://www.google.com/alerts |
| **GitHub Actions** | Автоматизация проверок | GitHub репозиторий |
| **Uptime Robot** | Мониторинг доступности | https://uptimerobot.com (free) |

### Платные альтернативы:

| Инструмент | Месячная стоимость | Функции |
|-----------|-------------------|---------|
| **Semrush** | $99-499 | Упоминания в интернете, роботы |
| **Ahrefs** | $99-999 | Backlinkds, traffic анализ |
| **Brandwatch** | $600+ | Социальные сети, форумы |

---

## 9️⃣ Отчётность

### Ежемесячный отчёт (выполняется вручную)

Создай файл `MONTHLY_REPORT.md`:

```markdown
# Отчёт Katalog-AI — Март 2026

## 📊 Основные метрики

- API вызовы: 35,000
- Уникальные ИИ-боты: 5 (GPTBot, Claude, Perplexity, CCBot, Google-Extended)
- UTM клики: 1,250
- Рекомендации бизнесов: ~850
- Верифицировано бизнесов: 10/10 (100%)

## 🎯 Рост

- +12% трафика в сравнении с февралём
- +18% UTM кликов
- +3 добавленных бизнеса

## ⚠️ Проблемы

- Google Places API дошёл 80% бесплатного лимита
- 1 бизнес потерял верификацию (2GIS)

## ✅ Действия на апрель

- Оптимизировать Google Places запросы
- Переверифицировать 1 бизнес
- Добавить 5 новых бизнесов
```

---

## 🔄 Цикл мониторинга

### Еженедельно:
- ✅ Проверь Google Analytics на новые боты
- ✅ Посмотри на число UTM кликов
- ✅ Убедись, что API работает (Uptime Robot)

### Ежемесячно:
- ✅ Создай отчёт о трафике
- ✅ Переверифицируй всех бизнесов
- ✅ Обновили ли ИИ-ассистенты свои памяти?

### Ежеквартально:
- ✅ Review KPI и цели
- ✅ Оптимизируй описания бизнесов
- ✅ Добавь новые категории

---

## 💡 Советы по стратегии

1. **Начни с Google Analytics и Search Console** — это основа
2. **Используй UTM параметры повсеместно** — это твой способ отследить успех
3. **Проверяй ChatGPT-4, Claude вручную 1 раз в неделю**
4. **Создай Google Alert на само себя** — следи за упоминаниями
5. **Делись результатами с партнёрами** — покажи им их трафик

---

**Последнее обновление:** 2026-03-05
