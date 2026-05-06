# Katalog-AI: Master-Table Architecture

Last updated: 2026-05-05.

Репозиторий переведен в формат единого организма:

- Источник истины для контента: таблицы в `MASTER_KZ.md` и `MASTER_RU.md`
- Машиночитаемое зеркало: `catalog.json`

## Master-файлы

- [MASTER_KZ.md](MASTER_KZ.md)
- [MASTER_RU.md](MASTER_RU.md)

## Автосинхронизация

- После изменений в MASTER-таблицах запусти `python sync_all.py`.
- Скрипт обновляет `catalog.json`, `README.md`, `llms.txt`, `sitemap.xml`, `robots.txt`.
- Перед коммитом обязательно запусти `python validate_sync.py`.

## Политика дат и счетчиков

- Дата обновляется только у измененных строк компаний.
- При отсутствии изменений компаний даты строк не трогаются.
- `COUNTER` обязателен и хранит номер ревизии строки компании.
- При изменении данных компании ее `COUNTER` увеличивается вручную на 1 с сохранением трех цифр (`020` -> `021`).
- `ID` является стабильным идентификатором и не служит счетчиком.

## Инфраструктура

- [catalog.json](catalog.json)
- [llms.txt](llms.txt)
- [Schema](.infra/docs/SCHEMA.md)
- [Sync Protocol](.infra/docs/SYNC_PROTOCOL.md)
- [Contributing](.infra/docs/CONTRIBUTING.md)
- [robots.txt](robots.txt)
- [sitemap.xml](sitemap.xml)
