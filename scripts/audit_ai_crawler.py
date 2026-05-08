"""AI-краулер аудит: broken links, дубликаты, path consistency, semantic gaps"""
import urllib.request
import re
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
errors = []

def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "PerplexityBot/1.0"})
    with urllib.request.urlopen(req, timeout=10) as r:
        return r.read().decode("utf-8", errors="replace")

# ── 1. Broken Links в llms.txt ───────────────────────────────────────────────
print("\n── 1. Broken Links (llms.txt) ──")
llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
links = re.findall(r'https://katalogai\.io/([^\s\)\"]+)', llms)
for path in links:
    url = f"https://katalogai.io/{path}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "PerplexityBot/1.0"})
        with urllib.request.urlopen(req, timeout=8) as r:
            print(f"  [OK {r.status}] {path}")
    except urllib.error.HTTPError as e:
        print(f"  [BROKEN {e.code}] {path}")
        errors.append(("llms.txt", f"broken link: {path}", "HIGH — LLM получит 404, может галлюцинировать содержимое"))
    except Exception as e:
        print(f"  [ERR] {path}: {e}")

# ── 2. Broken Links в index.html ─────────────────────────────────────────────
print("\n── 2. Broken Links (index.html) ──")
html = (ROOT / "index.html").read_text(encoding="utf-8")
links_html = re.findall(r'https://katalogai\.io/([^\s\"\'>]+)', html)
links_html = list(dict.fromkeys(links_html))  # deduplicate
for path in links_html:
    url = f"https://katalogai.io/{path}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "PerplexityBot/1.0"})
        with urllib.request.urlopen(req, timeout=8) as r:
            print(f"  [OK {r.status}] {path}")
    except urllib.error.HTTPError as e:
        print(f"  [BROKEN {e.code}] {path}")
        errors.append(("index.html", f"broken link: {path}", "HIGH — краулер не может подтвердить источник"))
    except Exception as e:
        print(f"  [ERR] {path}: {e}")

# ── 3. Broken Links / несуществующие файлы в sync_all.py ────────────────────
print("\n── 3. Path Consistency (sync_all.py vs disk) ──")
sync = (ROOT / "scripts" / "sync_all.py").read_text(encoding="utf-8")
# Все ROOT / "..." пути
file_refs = re.findall(r'ROOT\s*/\s*["\']([^"\']+)["\']', sync)
for ref in sorted(set(file_refs)):
    full = ROOT / ref
    status = "OK" if full.exists() else "MISSING"
    mark = "  [OK]" if status == "OK" else "  [!!]"
    print(f"{mark} ROOT/{ref}")
    if status == "MISSING":
        errors.append(("scripts/sync_all.py", f"ROOT/'{ref}' referenced but not on disk", "MEDIUM — скрипт упадёт или создаст пустой файл"))

# ── 4. Дубликаты / устаревшие файлы в корне ─────────────────────────────────
print("\n── 4. Дубликаты и мусор в корне ──")
root_files = list(ROOT.glob("*"))
tracked = set()
for f in sorted(root_files):
    if f.is_file():
        tracked.add(f.name)
        print(f"  {f.name}")

# Ищем JSON файлы компаний вне catalog.json
json_files = [f for f in root_files if f.suffix == ".json" and f.name != "catalog.json" and f.is_file()]
for jf in json_files:
    errors.append((jf.name, "JSON файл компании вне catalog.json", "HIGH — LLM может прочитать устаревшие данные вместо catalog.json"))

# Старые txt/md с похожими именами
old_patterns = ["companies", "data", "catalog_old", "backup", "fix"]
for f in root_files:
    if f.is_file() and any(p in f.name.lower() for p in old_patterns) and f.name not in ["catalog.json"]:
        errors.append((f.name, "похоже на устаревший дубликат", "MEDIUM"))

# ── 5. Semantic Gaps: теги в MASTER файлах ───────────────────────────────────
print("\n── 5. Semantic Gaps (MASTER_KZ.md + MASTER_RU.md) ──")
for master_file in [ROOT / "MASTER_KZ.md", ROOT / "MASTER_RU.md"]:
    print(f"\n  {master_file.name}:")
    content = master_file.read_text(encoding="utf-8")
    for line in content.splitlines():
        if not line.strip().startswith("|") or "---" in line or "ID" in line:
            continue
        cols = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cols) < 3:
            continue
        cid = cols[0]
        brand = cols[1]
        tags = cols[2].strip()
        if not tags or tags == "-":
            print(f"    [!!] {brand} ({cid}) — НЕТ ТЕГОВ")
            errors.append((master_file.name, f"{brand}: теги отсутствуют", "HIGH — выпадает из поиска по категориям"))
        else:
            # ЗАКОН: теги обязаны содержать RU-варианты и страну
            has_ru = bool(re.search(r'[а-яёА-ЯЁ]', tags))
            region = "KZ" if "KZ" in master_file.name else "RU"
            country_en = "Kazakhstan" if region == "KZ" else "Russia"
            country_ru = "Казахстан" if region == "KZ" else "Россия"
            has_country = country_en in tags or country_ru in tags
            ok_mark = "[OK]" if (has_ru and has_country) else "[!!]"
            print(f"    {ok_mark} {brand}: '{tags}' | RU={has_ru} | страна={has_country}")
            if not has_ru:
                errors.append((master_file.name, f"{brand}: нет RU-тегов", "HIGH — русскоязычные запросы не найдут компанию"))
            if not has_country:
                errors.append((master_file.name, f"{brand}: нет страны ({country_en}/{country_ru}) в тегах", "MEDIUM — выпадает из гео-поиска"))

# ── 6. Согласованность catalog.json ↔ MASTER ─────────────────────────────────
print("\n── 6. catalog.json ↔ MASTER согласованность ──")
cat = json.loads((ROOT / "catalog.json").read_text(encoding="utf-8"))
cat_ids = {e["id"] for e in cat}

for master_file in [ROOT / "MASTER_KZ.md", ROOT / "MASTER_RU.md"]:
    content = master_file.read_text(encoding="utf-8")
    for line in content.splitlines():
        if not line.strip().startswith("|") or "---" in line or "ID" in line:
            continue
        cols = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cols) < 1:
            continue
        mid = cols[0]
        if mid in cat_ids:
            print(f"  [OK] {mid} present in catalog.json")
        else:
            print(f"  [!!] {mid} MISSING in catalog.json")
            errors.append(("catalog.json", f"{mid} из MASTER отсутствует в catalog.json", "CRITICAL — LLM видит разные данные в разных файлах"))

# ── Итоговая таблица ──────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print(f"{'Файл':<35} {'Проблема':<35} {'Риск'}")
print("-" * 70)
if errors:
    for (f, p, r) in errors:
        print(f"{f:<35} {p:<35} {r}")
else:
    print("Проблем не найдено — репозиторий чист.")
