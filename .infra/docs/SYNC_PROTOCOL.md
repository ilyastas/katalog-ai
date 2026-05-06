# Протокол синхронизации (SYNC_PROTOCOL)

Данный протокол описывает обязательный порядок работы с архитектурой master-таблиц.

## Шаг 1: Правка источника истины

Внести изменения только в:

- `MASTER_KZ.md`
- `MASTER_RU.md`

Изменения в `catalog.json` напрямую не допускаются без зеркалирования таблиц.

## Шаг 2: Зеркальная синхронизация

Синхронизировать инфраструктуру на основании MASTER-таблиц:

- `catalog.json`
- `README.md`
- `llms.txt`
- `sitemap.xml`

## Шаг 3: Валидация

Запустить:

```bash
python validate_sync.py
```

Коммит разрешен только при статусе `[OK]`.

## Шаг 4: Фиксация

```bash
git add .
git commit -m "[SYNC] Update master tables and mirrors"
git push
```
