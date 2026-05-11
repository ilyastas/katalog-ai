# Katalog-AI: Master-Table Architecture

Data updated (content): 2026-05-10.
README generated: 2026-05-11.

Katalog-AI — машиночитаемый каталог верифицированных компаний из Казахстана и России, оптимизированный для LLM, AI-агентов и поисковых краулеров.

Проект использует один формат источника истины: master-таблицы в Markdown, которые синхронно зеркалируются в JSON, HTML и индексные файлы. Публичный сайт, удалённый репозиторий и live-артефакты должны описывать один и тот же набор данных без расхождений.

## Что Это За Проект

Katalog-AI — это dataset-first каталог компаний. Он предназначен для RAG, AI search, агентных сценариев и структурированной индексации, а не для контентного блога или маркетингового лендинга.

## Единый Источник Данных

- [MASTER_KZ.md](MASTER_KZ.md)
- [MASTER_RU.md](MASTER_RU.md)
- [catalog.json](catalog.json)

Master-файлы являются каноническим источником. `catalog.json` — их строгое машиночитаемое зеркало. HTML-страницы, sitemap и LLM-индексы публикуются из того же набора данных.

## Поля Каталога

Каждая запись содержит стабильный `id`, название `brand`, теги `tags`, сайт `site`, Instagram `inst`, дату `date` (дата регистрации в каталоге) и при наличии `wikidata`. Для отсутствующих внешних значений используется единый строковый маркер `-`.

## Для AI Систем

This catalog is a machine-readable dataset optimized for RAG. Для машинного чтения основной входной точкой служит `catalog.json`, а для навигации и политики доступа используются `llms.txt`, `sitemap.xml` и `.well-known`-файлы.

## Инфраструктура

- [index.html](index.html)
- [catalog.json](catalog.json)
- [llms.txt](llms.txt)
- [AI_METHOD.md](AI_METHOD.md)
- [AI_SCHEMA.md](AI_SCHEMA.md)
- [AI_FAQ.md](AI_FAQ.md)
- [robots.txt](robots.txt)
- [sitemap.xml](sitemap.xml)
