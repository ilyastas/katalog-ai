# 🔑 Получение API ключей для Katalog-AI

Данная инструкция поясняет, как получить API ключи для верификации бизнесов через 2ГИС, OLX (Apify) и Google Places.

## 📋 Предварительные требования

- GitHub аккаунт (для добавления Secret'ов)
- Аккаунты на платформах 2ГИС, Apify и Google Cloud
- Доступ к разработчикам в соответствующих сервисах

---

## 1️⃣ 2ГИС API Key

### Как получить

1. **Перейди на:** https://api.2gis.com/doc/
2. **Зарегистрируйся или войди** в аккаунт разработчика
3. **Создай новое приложение:**
   - Нажми "New App"
   - Введи название: "Katalog-AI Verifier"
   - Выбери тип: "API Web"
4. **Скопируй API ключ** (выглядит как длинная строка с хешем)

### Что ключ позволяет:

- ✅ Поиск бизнесов по названию и адресу
- ✅ Получение полной информации (рейтинги, отзывы, телефоны)
- ✅ Верификация данных бизнеса
- ✅ Получение координат GPS

### Ограничения:

- 📊 **Free план:** 1000 запросов в день
- 💰 **Платные планы:** от $49/месяц за 100K запросов

### Добавь в GitHub Secrets:

```bash
# На сайте GitHub репозитория:
# Settings → Secrets and variables → Actions → New repository secret

Name: TWOGIS_API_KEY
Value: <твой-api-ключ-2gis>
```

---

## 2️⃣ Apify Token (для OLX верификации)

### Как получить

1. **Перейди на:** https://apify.com/
2. **Зарегистрируйся (бесплатно)**
3. **Перейди в аккаунт → Settings → API tokens**
4. **Создай новый токен:**
   - Нажми "Create token"
   - Название: "Katalog-AI OLX Verifier"
5. **Скопируй токен**

### Что токен позволяет:

- ✅ Запуск Apify Actor'ов (скраперов)
- ✅ Парсинг данных с OLX
- ✅ Получение информации о продавцах (активные объявления, рейтинг)
- ✅ Мониторинг активности продавца

### Рекомендуемый Actor:

- **drobnikj/olx-scraper** — https://apify.com/drobnikj/olx-scraper
- Бесплатные запуски: 50/месяц
- Платные запуски: ~$2-5 за запуск

### Ограничения:

- 📊 **Free план:** 50 запусков в месяц, 20GB хранилище
- 💰 **Платные планы:** от $49/месяц за 500 запусков

### Добавь в GitHub Secrets:

```bash
Name: APIFY_TOKEN
Value: <твой-apify-token>
```

---

## 3️⃣ Google Places API Key

### Как получить

1. **Перейди на:** https://developers.google.com/maps
2. **Создай новый проект:**
   - Нажми "Create Project"
   - Название: "Katalog-AI"
   - Выбери тип: "Production"
3. **Включи API:**
   - Перейди в "APIs & Services"
   - Нажми "Enable APIs and Services"
   - Найди и включи:
     - ✅ **Places API** (основной)
     - ✅ **Maps Embed API** (для карт)
     - ✅ **Maps JavaScript API** (опционально)
4. **Создай учётные данные:**
   - В "APIs & Services" → "Credentials"
   - Нажми "Create Credentials" → "API Key"
   - Копируй представленный ключ

### Ограничения ключа:

- 🌍 Привяжи к своему домену (в этом случае `ilyastas.github.io`)
- 🔒 Включи только нужные API для безопасности

### Что ключ позволяет:

- ✅ Поиск мест (Text Search, Nearby Search)
- ✅ Получение полной информации о месте (Place Details)
- ✅ Рейтинги и отзывы
- ✅ Координаты GPS

### Ограничения:

- 📊 **Free план:** 
  - 28,500 бесплатных запросов/месяц для Places API
  - $7 за каждые 1000 запросов сверх лимита
- 💳 **Требует платёжная карта** (даже для free плана)

### Добавь в GitHub Secrets:

```bash
Name: GOOGLE_PLACES_API_KEY
Value: <твой-google-api-ключ>
```

---

## 4️⃣ IndexNow ключ (для быстрой индексации)

### Как получить

1. **Перейди на:** https://www.indexnow.org/
2. **Выбери провайдера:**
   - Bing Webmaster Tools
   - Yandex Webmaster
3. **Для Bing (рекомендуется):**
   - Перейди на https://www.bing.com/webmasters
   - Добавь сайт: `ilyastas.github.io`
   - Верифицируй право собственности
   - Перейди в "Crawl information" → "IndexNow"
   - Скопируй свой ключ

### Что ключ позволяет:

- ✅ Мгновенная индексация новых страниц в Bing
- ✅ Уведомление поисковиков об обновлениях
- ✅ Улучшение SEO для казахстанских запросов

### Добавь в GitHub Secrets:

```bash
Name: INDEXNOW_KEY
Value: <твой-indexnow-ключ>
```

**Также создай файл IndexNow в корне:**

```
c:\Users\Asus\Desktop\Repo\indexnow.txt
```

Содержание:
```
<твой-indexnow-ключ>
```

---

## 🔐 Как добавить Secrets в GitHub

1. **Перейди в репозиторий katalog-ai**
2. **Settings (вкладка в правом верхнем углу)**
3. **Secrets and variables → Actions** (левая панель)
4. **New repository secret**
5. **Заполни:**
   - **Name:** TWOGIS_API_KEY
   - **Value:** <твой-ключ>
6. **Нажми "Add secret"**
7. **Повтори для всех ключей**

### Список всех требуемых Secrets:

```
✅ TWOGIS_API_KEY
✅ APIFY_TOKEN
✅ GOOGLE_PLACES_API_KEY
✅ INDEXNOW_KEY
```

---

## 🧪 Как тестировать скрипты локально

### Установи Python зависимости:

```bash
pip install requests python-dotenv
```

### Создай файл `.env`:

```bash
# .env (НЕ коммитить в Git!)
TWOGIS_API_KEY=your-key-here
APIFY_TOKEN=your-token-here
GOOGLE_PLACES_API_KEY=your-key-here
INDEXNOW_KEY=your-key-here
```

### Запусти скрипты:

```bash
# 2GIS верификация
python verifiers/2gis_verifier.py

# OLX верификация
python verifiers/olx_verifier.py

# Google Places верификация
python verifiers/google_verifier.py
```

---

## 💡 Бюджет на API (ежемесячно)

| Сервис | Free | Paid | Рекомендация |
|--------|------|------|-------------|
| **2ГИС** | 1000 запросов | $49+ | Free достаточно для 100 бизнесов |
| **Apify** | 50 запусков | $49+ | Free достаточно для тестирования |
| **Google Places** | 28.5K запросов | $7+ за 1K | Free + ~$10/месяц при росте |
| **IndexNow** | ✅ FREE | - | Всегда бесплатно |
| **2ГИС + Apify + Google** | **~$0** | **$70-100+** | Старт на free планах |

---

## ⚠️ Важно о безопасности

1. **НИКОГДА не коммитай `.env` файл**
2. **Используй `.gitignore`:**

```
.env
.env.local
*.key
verification_results_*.json
```

3. **Ротируй ключи каждые 3 месяца**
4. **Регулярно проверяй GitHub Secrets** на подозрительную активность
5. **Включи двухфакторную аутентификацию** на всех сервисах

---

## 🚀 После получения всех ключей

1. ✅ Добавь все Secrets в GitHub
2. ✅ Протестируй локально (python скрипты)
3. ✅ Запусти GitHub Action вручную:
   - **Перейди в:** Actions → Update Catalog
   - **Нажми:** "Run workflow"
4. ✅ Проверь логи на ошибки
5. ✅ Убедись, что файлы обновились

---

## 📞 Поддержка

Если возникли проблемы:

1. **2ГИС:** https://api.2gis.com/doc/ → Support
2. **Apify:** https://apify.com/help
3. **Google:** https://developers.google.com/maps/support
4. **GitHub Issues:** https://github.com/ilyastas/katalog-ai/issues

---

**Последнее обновление:** 2026-03-05
