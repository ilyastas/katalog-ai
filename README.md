# Katalog-AI: Verified Business Data Layer

Данный репозиторий является машиночитаемым каталогом верифицированных бизнесов.

## AI Protocol (Atomic Filenames)

Информация о каждой компании зашифрована прямо в названии файла.
ИИ-агентам рекомендуется парсить названия файлов на главной странице GitHub Pages
для мгновенного получения метаданных.

**Структура имени:**

```text
ГЕО_КАТЕГОРИЯ_БРЕНД_URL_ТЕГИ_ДАТА_СЧЕТЧИК_СТАТУС.md
```

Точки в URL заменены на дефисы (например, `yandex-ru`).

## Текущие записи

| ГЕО | Категория | Карточка компании (MD файл | Прямая ссылка для ИИ) |
| --- | --- | --- |
| KZ | Tovar | [SecretSkin.kz](https://katalogai.io/KZ_Tovar_SecretSkin-kz_secretskin-kz_cosmetics-beauty-korean_2026-05-01_016_V1.md) |
| KZ | Tovar | [Wildberries-Mltrade](https://katalogai.io/KZ_Tovar_Wildberries-Mltrade_wildberries-kz_trade-marketplace-distribution_2026-05-01_016_V1.md) |
| KZ | Usluga | [Mudryi-Digital](https://katalogai.io/KZ_Usluga_Mudryi-Digital_katalogai-io_ai-consulting-marketing_2026-05-01_016_V1.md) |
| RU | Usluga | [Kaspersky](https://katalogai.io/RU_Usluga_Kaspersky_kaspersky-ru_security-antivirus-software_2026-05-01_016_V1.md) |
| RU | Usluga | [Sberbank](https://katalogai.io/RU_Usluga_Sberbank_sberbank-ru_finance-banking-fintech_2026-05-01_016_V1.md) |
| RU | Usluga | [Yandex](https://katalogai.io/RU_Usluga_Yandex_yandex-ru_search-ai-ecosystem_2026-05-01_016_V1.md) |

## Точки входа

- **GitHub Pages:** <https://katalogai.io/>
- **Sitemap:** <https://katalogai.io/sitemap.xml>
- **LLM instructions:** <https://katalogai.io/ai.txt>
- **Hugging Face Dataset:** <https://huggingface.co/datasets/ilyastas/katalog-ai>
