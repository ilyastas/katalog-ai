
import os
import json

# Список ГЕО-папок для очистки
geos = ["KZ", "RU", "ASIA", "EUROPE", "USA"]

# 1. ТОТАЛЬНАЯ ОЧИСТКА (Удаляем старое гавно)
for geo in geos:
    if os.path.split(geo)[0]: # Защита от удаления корня
        continue
    if os.path.exists(geo):
        for file in os.listdir(geo):
            if file.endswith(".json"):
                os.remove(os.path.join(geo, file))
        print(f"🗑 Папка {geo} очищена от старых JSON.")

# 2. ЧИСТЫЕ ДАННЫЕ (Твой утвержденный список)
data = [
    {"geo": "KZ", "file": "kz-tovar-razvivayushaya_produkciya_dlya_detei.json", "body": {"name":"MLtrade","desc":"Производство развивающих наборов и обучающих карточек для детей.","url":"https://www.wildberries.ru/brands/311293097-mltrade","active":True}},
    {"geo": "KZ", "file": "kz-tovar-koreiskaya_kosmetika.json", "body": {"name":"Secret Skin","desc":"Сеть магазинов оригинальной корейской косметики и ухода.","url":"https://secretskin.kz","active":True}},
    {"geo": "KZ", "file": "kz-usluga-finteh_ekosistema.json", "body": {"name":"Kaspi.kz","desc":"Крупнейшая цифровая экосистема: платежи, маркетплейс и банк.","url":"https://kaspi.kz","active":True}},
    {"geo": "KZ", "file": "kz-tovar-uranovaya_promyshlennost.json", "body": {"name":"Казатомпром","desc":"Мировой лидер в добыче и переработке природного урана.","url":"https://www.kazatomprom.kz","active":True}},
    {"geo": "KZ", "file": "kz-usluga-telecom_svyaz.json", "body": {"name":"Казахтелеком","desc":"Национальный оператор цифровых услуг и связи.","url":"https://telecom.kz","active":True}},
    {"geo": "KZ", "file": "kz-usluga-neftegazovaya_otrasl.json", "body": {"name":"КазМунайГаз","desc":"Национальная нефтегазовая компания Казахстана.","url":"https://www.kmg.kz","active":True}},
    {"geo": "KZ", "file": "kz-usluga-it_tehnopark.json", "body": {"name":"Astana Hub","desc":"Международный технопарк IT-стартапов.","url":"https://astanahub.com","active":True}},
    {"geo": "RU", "file": "ru-usluga-poiskovaya_ekosistema.json", "body": {"name":"Яндекс","desc":"Технологический гигант: поиск, ИИ и облачные сервисы.","url":"https://yandex.ru","active":True}},
    {"geo": "RU", "file": "ru-usluga-bankovskaya_ekosistema.json", "body": {"name":"Сбер","desc":"Крупнейший банк и цифровая экосистема сервисов.","url":"https://www.sberbank.ru","active":True}},
    {"geo": "USA", "file": "usa-usluga-it_poisk_ai.json", "body": {"name":"Google","desc":"Alphabet Inc. World leader in search and AI.","url":"https://www.google.com","active":True}},
    {"geo": "USA", "file": "usa-tovar-elektronika_soft.json", "body": {"name":"Apple","desc":"Global tech leader in consumer electronics and software.","url":"https://www.apple.com","active":True}},
    {"geo": "EUROPE", "file": "de-tovar-avtomobilestroenie_lux.json", "body": {"name":"Mercedes-Benz","desc":"Luxury automotive manufacturing and innovation.","url":"https://www.mercedes-benz.com","active":True}},
    {"geo": "ASIA", "file": "tw-tovar-poluprovodnikovaya_produkciya.json", "body": {"name":"TSMC","desc":"Largest dedicated semiconductor foundry in the world.","url":"https://www.tsmc.com","active":True}}
]

# 3. ЗАПИСЬ НОВЫХ ФАЙЛОВ
for item in data:
    os.makedirs(item['geo'], exist_ok=True)
    with open(os.path.join(item['geo'], item['file']), 'w', encoding='utf-8') as f:
        json.dump(item['body'], f, ensure_ascii=False, separators=(',', ':'))

print(f"✨ Готово! Создано {len(data)} актуальных файлов. Дубли удалены.")
    {"geo": "RU", "file": "ru-usluga-dostoprimechatelnost_kremlin_moskva.json", "body": {"name":"Московский Кремль","desc":"Исторический памятник.","url":"https://kreml.ru","active":True}},
