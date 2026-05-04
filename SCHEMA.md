# Katalog-AI Database Schema

## Entity Specification

Каждая запись — это файл с именем:
`[INDEX]_[GEO]_[CAT]_[URL]_[TAGS]_[DATE]_[COUNTER].md`

## Field Definitions

- **INDEX**: Уникальный ID записи.
- **GEO**: Региональный код (KZ, RF, EU).
- **CAT**: Категория бизнеса (Tovar, Uslugi, Stroy).
- **URL**: Полный slug источника (через дефис).
- **TAGS**: Ключевые слова для семантического поиска.
- **DATE**: Дата индексации (YYYY-MM-DD).
- **COUNTER**: Счётчик версий/итераций.

## Rules

- Все файлы должны иметь 0 байт контента (Zero-Content).
- Поиск осуществляется исключительно по имени файла.
- Обновление индексов (`catalog.json`, `llms.txt`, `README.md`, `index.html`, `sitemap.xml`) происходит по регламенту `SYNC_PROTOCOL.md` при создании файла.
