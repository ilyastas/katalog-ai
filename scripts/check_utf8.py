#!/usr/bin/env python3
# coding: utf-8
"""
Pre-commit hook: Проверка кодировки всех файлов на UTF-8 без BOM.
"""
import sys
from pathlib import Path

FAILED = False

def check_utf8(path):
    # Исключаем служебные и виртуальные директории
    skip_dirs = ['.venv', '.github']
    for skip in skip_dirs:
        if skip in path.parts:
            return True
    try:
        with open(path, 'rb') as f:
            raw = f.read()
        # UTF-8 BOM: 0xEF 0xBB 0xBF
        if raw.startswith(b'\xef\xbb\xbf'):
            print(f"[FAIL] BOM found: {path}")
            return False
        raw.decode('utf-8')
        return True
    except Exception as e:
        print(f"[FAIL] Not UTF-8: {path} ({e})")
        return False

if __name__ == "__main__":
    root = Path('.')
    exts = ['.md', '.json', '.html', '.txt', '.xml', '.yml', '.yaml']
    for ext in exts:
        for file in root.rglob(f'*{ext}'):
            if not check_utf8(file):
                FAILED = True
    if FAILED:
        print("\n[ERROR] Some files are not UTF-8 without BOM. Please fix encoding!")
        sys.exit(1)
    else:
        print("[OK] All files are UTF-8 without BOM.")
