# 🚀 Deployment Guide для Katalog-AI

Полная инструкция по развёртыванию Katalog-AI на GitHub Pages с автоматизацией через GitHub Actions.

---

## 📋 Предварительные требования

- ✅ Аккаунт на GitHub
- ✅ Репозиторий `katalog-ai` создан и залит на GitHub
- ✅ GitHub Pages включён (Settings → Pages → Source: main branch)
- ✅ Все API ключи получены (см. [SETUP_API_KEYS.md](SETUP_API_KEYS.md))

---

## 1️⃣ Инициальное развёртывание

### Шаг 1: Склонируй репозиторий

```bash
git clone https://github.com/ilyastas/katalog-ai.git
cd katalog-ai
```

### Шаг 2: Структура файлов

Убедись, что структура совпадает:

```
katalog-ai/
├── index.json                    ✅
├── index.html                    ✅
├── register.html                 ✅
├── robots.txt                    ✅
├── sitemap.xml                   ✅
├── core/
│   ├── openapi.yaml             ✅
│   └── AI_INSTRUCTIONS.md       ✅
├── catalog/
│   ├── beauty.json              ✅
│   ├── museums.json             ✅
│   ├── marketplaces.json        ✅
│   ├── offers.json              ✅
│   └── geo-index.json           ✅
├── verifiers/
│   ├── 2gis_verifier.py         ✅
│   ├── olx_verifier.py          ✅
│   └── google_verifier.py       ✅
├── .github/
│   └── workflows/
│       ├── update-catalog.yml   ✅
│       └── ping-indexnow.yml    ✅
└── docs/
    ├── SETUP_API_KEYS.md        ✅
    ├── MONITORING_STRATEGY.md   ✅
    ├── DEPLOYMENT_GUIDE.md      ✅
    └── SCALING_GUIDE.md         ✅
```

### Шаг 3: Первый коммит

```bash
git config user.name "Your Name"
git config user.email "your-email@example.com"

git add .
git commit -m "🚀 Initial Katalog-AI deployment with catalogs, verifiers, and GitHub Actions"
git push origin main
```

---

## 2️⃣ Установка GitHub Secrets

### Перейди в Settings репозитория

1. GitHub → твой репозиторий
2. **Settings** (вкладка в меню)
3. Левая панель: **Secrets and variables** → **Actions**
4. **New repository secret**

### Добавь следующие Secrets:

#### Secret 1: 2GIS API Key

```
Name: TWOGIS_API_KEY
Value: <твой-ключ-from-2gis-api>
```

#### Secret 2: Apify Token

```
Name: APIFY_TOKEN
Value: <твой-токен-from-apify>
```

#### Secret 3: Google Places API Key

```
Name: GOOGLE_PLACES_API_KEY
Value: <твой-ключ-from-google>
```

#### Secret 4: IndexNow Key

```
Name: INDEXNOW_KEY
Value: <твой-ключ-from-indexnow>
```

#### Secret 5 (опционально): Slack Webhook

```
Name: SLACK_WEBHOOK_URL
Value: https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

### Проверь добавленные Secrets

```bash
Settings → Secrets and variables → Actions
```

Должны быть все 4-5 Secrets без доступа к их values (только редактирование).

---

## 3️⃣ Тестирование локально

### Установи зависимости

```bash
pip install requests python-dotenv
```

### Создай `.env` файл

```bash
# .env (НЕ коммитить!)
TWOGIS_API_KEY=your-key-here
APIFY_TOKEN=your-token-here
GOOGLE_PLACES_API_KEY=your-key-here
INDEXNOW_KEY=your-key-here
```

### Запусти тесты

```bash
# Проверка 2GIS
python verifiers/2gis_verifier.py

# Проверка OLX
python verifiers/olx_verifier.py

# Проверка Google Places
python verifiers/google_verifier.py
```

### Ожидаемые выводы

```
🚀 Запуск 2ГИС верификации
============================================================

📍 Проверка: Beauty Prime Salon (Алматы)
🔍 Поиск 'Beauty Prime Salon' на 2ГИС...
✅ Найден: Beauty Prime Salon (ID: 70000000000000)
✅ Верифицировано! Рейтинг: 4.9/5

✅ Результаты сохранены в verification_results_2gis.json
✅ Успешно верифицировано: 1/3
```

---

## 4️⃣ Запуск GitHub Actions вручную

### Первый раз

1. Перейди в репозиторий
2. **Actions** (вкладка в меню)
3. **Update Catalog** (слева)
4. **Run workflow** (синяя кнопка)
5. Выбери ветку: `main`
6. **Run workflow**

### Проверь логи

1. Жди завершения (обычно 2-5 минут)
2. Нажми на выполненный workflow
3. Нажми на job "verify-and-update"
4. Прокрути и посмотри вывод

### Ожидаемые результаты

```
✅ Checkout repository
✅ Setup Python
✅ Install dependencies
✅ Run 2GIS verifier ← проверяет бизнесы
✅ Run OLX verifier
✅ Run Google Places verifier
✅ Generate verification report
✅ Update dateModified in catalog files ← обновляет JSON
✅ Configure Git
✅ Commit verification results ← создаёт коммит
✅ Push changes ← пушит на GitHub
✅ Workflow completed ✅ Katalog verification and update completed!
```

---

## 5️⃣ Проверка доступности

### Проверь, что сайт доступен

```bash
curl -I https://ilyastas.github.io/katalog-ai/

HTTP/2 200
content-type: application/json
```

### Проверь JSON файлы

```bash
# Главный индекс
curl https://ilyastas.github.io/katalog-ai/index.json |  jq '..|.name' | head -10

# Бьюти каталог
curl https://ilyastas.github.io/katalog-ai/catalog/beauty.json | jq '.."@graph"[0].name'
# Output: "Beauty Prime Salon"

# Проверь geo-index
curl https://ilyastas.github.io/katalog-ai/catalog/geo-index.json | jq '.locations[0]'
```

---

## 6️⃣ Проверка robots.txt и sitemap

### robots.txt

```bash
curl https://ilyastas.github.io/katalog-ai/robots.txt
```

Должен содержать:
```
User-agent: GPTBot
Allow: /

User-agent: *
Disallow: /
```

### sitemap.xml

```bash
curl https://ilyastas.github.io/katalog-ai/sitemap.xml
```

Должен содержать ссылки на все JSON-файлы.

---

## 7️⃣ Проверка IndexNow

### Создай файл indexnow.txt

```bash
# c:\Users\Asus\Desktop\Repo\indexnow.txt
<твой-indexnow-ключ>
```

### Проверь доступность

```bash
curl https://ilyastas.github.io/katalog-ai/indexnow.txt
```

### Проверь пинг IndexNow

GitHub Action `ping-indexnow` отправляет пинг Bing'у при каждом обновлении.

---

## 8️⃣ Проверка OpenAPI спецификации

### Скачай OpenAPI

```bash
curl https://ilyastas.github.io/katalog-ai/core/openapi.yaml > openapi.yaml
```

### Валидируй YAML

```bash
# Используй онлайн валидатор
# https://editor.swagger.io/

# Или локально с Python
pip install pyyaml
python -c "import yaml; yaml.safe_load(open('openapi.yaml'))" && echo "✅ Valid"
```

---

## 9️⃣ Проверка GitHub Actions расписания

### Редактируй cron-расписание

Файл: `.github/workflows/update-catalog.yml`

```yaml
on:
  schedule:
    # Текущее: каждый день в 00:00 UTC (+4 часа Казахстан = 04:00)
    - cron: '0 0 * * *'  # Пн-Вс в 00:00 UTC
```

**Попробуй разные времена:**

```yaml
- cron: '0 */6 * * *'   # Каждые 6 часов
- cron: '0 12 * * 1'    # Каждый понедельник в 12:00
- cron: '0 0 1 * *'     # 1-го числа каждого месяца
```

---

## 🔟 Готовность к продакшену

Перед публикацией проверь:

- ✅ Все JSON-файлы валидны
- ✅ Все бизнесы имеют поле `consent`
- ✅ GitHub Actions работают без ошибок
- ✅ API ключи активны и действительны
- ✅ Sitemap.xml обновлён
- ✅ robots.txt правильно настроен
- ✅ OpenAPI спецификация валидна
- ✅ Уведомление в Bing Webmaster (IndexNow)
- ✅ Уведомление в Google Search Console
- ✅ GitHub Pages сайт доступен по HTTPS

### Финальный чеклист

```bash
#!/bin/bash
# deploy-checklist.sh

echo "🔍 Final deployment check..."
echo ""

# 1. JSON валидация
echo "1️⃣ Проверка JSON файлов..."
for file in index.json catalog/*.json; do
    python -m json.tool "$file" > /dev/null && echo "✅ $file" || echo "❌ $file"
done

# 2. Проверка доступности
echo ""
echo "2️⃣ Проверка доступности..."
curl -I https://ilyastas.github.io/katalog-ai/ | grep "200" && echo "✅ Site is accessible" || echo "❌ Site is not accessible"

# 3. Проверка GitHub Actions
echo ""
echo "3️⃣ Проверка GitHub Actions..."
echo "👉 Перейди: https://github.com/ilyastas/katalog-ai/actions"
echo "   Убедись, что последний workflow успешен"
```

---

## 📱 Мониторинг после развёртывания

### Ежедневно:
- ✅ Проверь GitHub Actions логи
- ✅ Посмотри Google Analytics (если включена)

### Еженедельно:
- ✅ Переверифицируй случайного бизнеса вручную
- ✅ Проверь, что robots.txt работает

### Ежемесячно:
- ✅ Создай отчёт о трафике
- ✅ Обнови документацию
- ✅ Добавь новых бизнесов

---

## 🆘 Troubleshooting

### GitHub Action падает с 404

```
Error: File not found: verifiers/2gis_verifier.py
```

**Решение:**
```bash
# Проверь, что файлы есть
ls -la verifiers/
git status

# Если файлы не видны, добавь их
git add verifiers/
git commit -m "Add verifier scripts"
git push
```

### API ключ invalid

```
❌ Ошибка: API key is invalid or expired
```

**Решение:**
1. Переходи в сервис и переустанови ключ
2. Обнови Secret в GitHub Settings
3. Перезапусти workflow вручную

### IndexNow не пингует

```
⚠️ Curl request failed (7)
```

**Решение:**
1. Убедись, что `indexnow.txt` существует в корне
2. Проверь ключ IndexNow
3. Попробуй пинг вручную:

```bash
curl -X POST https://www.bing.com/indexnow \
  -H "Content-Type: application/json" \
  -d '{"host": "ilyastas.github.io", "key": "YOUR_KEY", "urlList": ["https://..."]}'
```

---

## 🎉 Успешное развёртывание!

После всех шагов:

1. ✅ Сайт доступен на https://ilyastas.github.io/katalog-ai/
2. ✅ JSON-файлы обновляются ежедневно
3. ✅ GitHub Actions верифицируют бизнесы
4. ✅ IndexNow уведомляет Bing
5. ✅ ИИ-ассистенты могут использовать каталог

---

**Последнее обновление:** 2026-03-05
