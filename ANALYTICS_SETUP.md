# 📊 Настройка мониторинга ИИ-ботов

## 1️⃣ GitHub Traffic (Встроенный)
**Как проверить:**
1. Откройте: https://github.com/ilyastas/katalog-ai/insights/traffic
2. Там увидите:
   - 📈 Views (просмотры)
   - 👥 Unique visitors (уникальные посетители)
   - 📦 Clones (клонирования репозитория)
   - ⭐ Popular content (популярные файлы)

**Минусы:** Хранит данные только 14 дней

---

## 2️⃣ JS-трекер (Встроен в index.html)
**Что делает:**
- Определяет User-Agent посетителя
- Распознает ИИ-ботов: GPTBot, Claude-bot, PerplexityBot и др.
- Логирует визиты в консоль браузера

**Как использовать:**
```javascript
// Для отправки данных на ваш сервер раскомментируйте в index.html:
fetch('https://your-logger-service.com/log', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify(visitData)
});
```

**Рекомендуемые бесплатные сервисы для логов:**
- [Webhook.site](https://webhook.site) - временный URL для тестов
- [RequestBin](https://requestbin.com) - логирование запросов
- [Pipedream](https://pipedream.com) - 100 запросов/день бесплатно

---

## 3️⃣ GoatCounter (Бесплатная аналитика)
**Настройка:**
1. Зарегистрируйтесь: https://www.goatcounter.com/
2. Создайте сайт с кодом `katalog-ai`
3. Скрипт уже добавлен в `index.html`
4. Дашборд: https://katalog-ai.goatcounter.com/

**Преимущества:**
- ✅ Бесплатно для некоммерческих проектов
- ✅ Не требует cookies
- ✅ Показывает User-Agent (определите ИИ-ботов)
- ✅ Конфиденциально (без Google Analytics)
- ✅ Хранит данные бесконечно

**Что увидите:**
- Количество визитов по дням
- User-Agent каждого посетителя
- Популярные страницы
- Источники переходов

---

## 4️⃣ Альтернатива: Plausible Analytics
**Если нужна более мощная аналитика:**
1. Зарегистрируйтесь: https://plausible.io
2. Замените в `index.html`:
```html
<script defer data-domain="ilyastas.github.io" 
        src="https://plausible.io/js/script.js"></script>
```

**Бесплатный тариф:** 10,000 визитов/месяц

---

## 🔍 Как определить конкретных ИИ-ботов

### User-Agent ИИ-помощников:
| Бот | User-Agent |
|-----|------------|
| ChatGPT | `Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko); compatible; GPTBot/1.0` |
| Claude | `Claude-Bot` |
| Perplexity | `PerplexityBot` |
| Google Bard | `Google-Extended` |
| OpenAI Search | `OAI-SearchBot` |
| Common Crawl | `CCBot` |

### В GoatCounter/Plausible:
Фильтруйте логи по ключевым словам: `GPTBot`, `Claude`, `CCBot`, `Perplexity`

---

## 🚀 Следующие шаги

1. **Закоммитьте изменения:**
```bash
git add index.html ANALYTICS_SETUP.md
git commit -m "Add AI bot tracking and analytics"
git push
```

2. **Зарегистрируйтесь в GoatCounter:**
   - https://www.goatcounter.com/signup

3. **Проверьте GitHub Traffic через неделю:**
   - https://github.com/ilyastas/katalog-ai/insights/traffic

4. **Проверьте работу сайта:**
   - https://ilyastas.github.io/katalog-ai/

---

## 📌 Быстрые ссылки

- 🌐 Ваш сайт: https://ilyastas.github.io/katalog-ai/
- 📊 GitHub Traffic: https://github.com/ilyastas/katalog-ai/insights/traffic
- 📈 GoatCounter: https://katalog-ai.goatcounter.com/ (после регистрации)
- 📝 Данные для ИИ: https://ilyastas.github.io/katalog-ai/data.json

---

*Обновлено: 3 марта 2026*
