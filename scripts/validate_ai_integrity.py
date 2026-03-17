
import json
import os
import sys

def validate_integrity():
    # Путь к нашему единственному мастер-файлу
    master_file = 'data/companies_all.json'
    
    print(f"🔍 Запуск финальной валидации: {master_file}...")

    if not os.path.exists(master_file):
        print(f"❌ ОШИБКА: Файл {master_file} не найден!")
        sys.exit(1)

    try:
        with open(master_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Проверка формата: это должен быть список []
        if not isinstance(data, list):
            print("❌ ОШИБКА: Формат данных неверный. Ожидался массив [], а получен объект.")
            sys.exit(1)

        # Проверка качества данных
        count = len(data)
        if count < 40:
            print(f"⚠️ ПРЕДУПРЕЖДЕНИЕ: В базе всего {count} компаний. Для 'Золотого фонда' нужно больше.")
        
        for entry in data:
            # Обязательные поля для RAG и AI
            required_fields = ['id', 'name', 'category', 'city', 'metadata']
            for field in required_fields:
                if field not in entry:
                    print(f"❌ ОШИБКА: У компании {entry.get('id', 'Unknown')} отсутствует поле '{field}'")
                    sys.exit(1)
            
            # Проверка верификации
            if not entry['metadata'].get('verified', False):
                print(f"⚠️ ВНИМАНИЕ: Компания {entry['id']} не верифицирована.")

        print(f"✅ УСПЕХ! Валидация пройдена. Всего объектов: {count}")
        print(f"🚀 Проект готов к деплою в Hugging Face и GitHub.")

    except json.JSONDecodeError:
        print(f"❌ ОШИБКА: Файл {master_file} содержит невалидный JSON!")
        sys.exit(1)

if __name__ == "__main__":
    validate_integrity()