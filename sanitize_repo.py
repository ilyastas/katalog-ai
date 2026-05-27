import os
from pathlib import Path

# Список папок и расширений для зачистки (исключая скрытые и папки билда)
TARGET_EXTENSIONS = {'.md', '.txt', '.json', '.html', '.xml'}
EXCLUDE_DIRS = {'node_modules', '.git', '.github', 'public-site', '.venv', 'env'}

def sanitize_file(file_path):
    try:
        # Читаем как бинарник, чтобы перехватить реальные байты BOM
        raw_data = file_path.read_bytes()
        # Проверяем и срезаем BOM (\xef\xbb\xbf)
        if raw_data.startswith(b'\xef\xbb\xbf'):
            raw_data = raw_data[3:]
            print(f"[BOM REMOVED] -> {file_path}")
        # Декодируем строго в utf-8
        content = raw_data.decode('utf-8')
        # Нормализуем переводы строк: CRLF (\r\n) -> LF (\n) чтобы pre-commit не бесился
        content = content.replace('\r\n', '\n')
        # Пишем обратно как чистый UTF-8 без BOM и с LF строками
        file_path.write_text(content, encoding='utf-8', newline='\n')
    except UnicodeDecodeError:
        # Если упало тут — значит исходный файл уже был сохранен в битой cp1251
        try:
            content = file_path.read_text(encoding='cp1251')
            file_path.write_text(content, encoding='utf-8', newline='\n')
            print(f"[RECOVERED FROM CP1251] -> {file_path}")
        except Exception as e:
            print(f"[SKIP/FAILED] -> {file_path}: {e}")

for root, dirs, files in os.walk('.'):
    # Фильтруем папки на лету
    dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
    for file in files:
        fp = Path(root) / file
        if fp.suffix in TARGET_EXTENSIONS:
            sanitize_file(fp)

print("✅ Глобальная зачистка завершена!")
