# Katalog-AI: Master-Table Architecture

Last updated: 2026-05-06.

Репозиторий переведен в формат единого организма:

- Источник истины для контента: таблицы в `MASTER_KZ.md` и `MASTER_RU.md`
- Машиночитаемое зеркало: `catalog.json`

## Master-файлы

- [MASTER_KZ.md](MASTER_KZ.md)
- [MASTER_RU.md](MASTER_RU.md)

## Синхронизация

- Любые изменения в компаниях вносятся только в таблицы MASTER-файлов.
- `catalog.json` должен быть зеркалом строк из таблиц MASTER-файлов.
- Перед коммитом обязательно запускать `python validate_sync.py`.

## Инфраструктура

- [catalog.json](catalog.json)
- [llms.txt](llms.txt)
- [SCHEMA.md](SCHEMA.md)
- [SYNC_PROTOCOL.md](SYNC_PROTOCOL.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [robots.txt](robots.txt)
- [sitemap.xml](sitemap.xml)
