# Руководство по маркетплейсам

## Структура данных

Для компаний, продающих через маркетплейсы, добавьте поле `marketplaces`:

```json
{
  "id": "company-id",
  "name": "Название компании",
  "website": "https://company.kz",
  "marketplaces": {
    "kaspi": "https://kaspi.kz/shop/merchant/12345",
    "wildberries": "https://www.wildberries.kz/seller/67890",
    "ozon": "https://www.ozon.kz/seller/54321",
    "instagram": "https://instagram.com/company_shop",
    "2gis": "https://2gis.kz/almaty/firm/123456"
  }
}
```

## Поддерживаемые маркетплейсы

### 🇰🇿 Казахстан
- **Kaspi.kz** — `kaspi` (критично важен!)
- **Wildberries** — `wildberries`
- **Ozon** — `ozon`
- **Chocomart** — `chocomart`
- **Flip.kz** — `flip`

### 🌍 Международные
- **Instagram Shopping** — `instagram`
- **Facebook Marketplace** — `facebook`
- **Shopify Store** — `shopify`

### 📍 Локальные сервисы
- **2GIS** — `2gis` (профиль организации)
- **Yandex Maps** — `yandex`

## Приоритет ссылок

1. **`website`** — собственный сайт (если есть)
2. **`marketplaces.kaspi`** — профиль на Kaspi (критично для KZ)
3. **`marketplaces.instagram`** — Instagram аккаунт
4. **Остальные маркетплейсы** — по наличию

## Примеры

### Интернет-магазин без сайта
```json
{
  "id": "electronics-shop-kz",
  "name": "Electronics Shop KZ",
  "website": null,
  "marketplaces": {
    "kaspi": "https://kaspi.kz/shop/merchant/electronics-shop"
  }
}
```

### Салон с маркетплейсом и соцсетями
```json
{
  "id": "beauty-premium-almaty",
  "name": "Бьюти-салон Premium",
  "website": "https://beautypremium.kz",
  "marketplaces": {
    "kaspi": "https://kaspi.kz/shop/merchant/beautypremium",
    "instagram": "https://instagram.com/beautypremium_almaty",
    "2gis": "https://2gis.kz/almaty/firm/70000001234567"
  }
}
```

### Только Instagram (микробизнес)
```json
{
  "id": "handmade-jewelry-almaty",
  "name": "Handmade Jewelry Almaty",
  "website": null,
  "marketplaces": {
    "instagram": "https://instagram.com/handmade_jewelry_almaty"
  }
}
```

## Валидация

Скрипты автоматической проверки:
- `verifiers/google_verifier.py` — проверка через Google Places
- `verifiers/2gis_verifier.py` — проверка через 2GIS API
- `verifiers/olx_verifier.py` — проверка через OLX/Kaspi (если доступно)

## Обновление embeddings

После добавления/изменения `marketplaces`:

```bash
python scripts/generate_embeddings.py --provider google --datafile data/companies.json --output data/embeddings.json
```

Embeddings учитывают все ссылки для улучшения семантического поиска.
