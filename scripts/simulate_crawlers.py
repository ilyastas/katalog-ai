"""Симуляция краулеров, поисковиков и LLM-ботов для katalogai.io"""
import urllib.request
import json
import re
from datetime import date

TODAY = date.today().isoformat()
errors: list[str] = []
warns: list[str] = []


def fetch(url: str, ua: str = "Mozilla/5.0") -> str:
    req = urllib.request.Request(url, headers={"User-Agent": ua})
    with urllib.request.urlopen(req, timeout=10) as r:
        return r.read().decode("utf-8", errors="replace")


def ok(msg: str) -> None:
    print(f"[OK] {msg}")


def fail(msg: str) -> None:
    errors.append(msg)


def warn(msg: str) -> None:
    warns.append(msg)


# ── robots.txt ────────────────────────────────────────────────────────────────
print("\n── robots.txt ──")
robots = fetch("https://katalogai.io/robots.txt")
ok("fetched") if robots else fail("empty")
if "User-agent: *" in robots and "Allow: /" in robots:
    ok("open AI policy found via User-agent: * and Allow: /")
else:
    fail("open AI policy MISSING in robots.txt")
if "llms.txt" in robots:           ok("llms.txt referenced")
else:                              warn("llms.txt not referenced")
if TODAY in robots:                ok(f"date {TODAY} found")
else:                              fail(f"date {TODAY} MISSING")

# ── sitemap.xml ───────────────────────────────────────────────────────────────
print("\n── sitemap.xml ──")
sitemap = fetch("https://katalogai.io/sitemap.xml")
for u in ["katalogai.io/", "catalog.json", "llms.txt", "README.md"]:
    if u in sitemap: ok(f"{u} listed")
    else:            fail(f"{u} MISSING")
lastmods = re.findall(r"<lastmod>(.+?)</lastmod>", sitemap)
stale = [d for d in lastmods if d != TODAY]
if not stale: ok(f"all lastmod = {TODAY}")
else:         fail(f"stale lastmods: {stale}")

# ── llms.txt (Claude-User) ────────────────────────────────────────────────────
print("\n── llms.txt (Claude-User) ──")
llms = fetch("https://katalogai.io/llms.txt", ua="Claude-User/1.0")
if "katalogai.io" in llms:    ok("canonical URL present")
else:                         fail("canonical URL MISSING")
if "catalog.json" in llms:    ok("catalog.json linked")
else:                         fail("catalog.json MISSING")
if "github" in llms.lower():  ok("GitHub notice present")
else:                         warn("GitHub notice missing")
if TODAY in llms:             ok(f"date {TODAY} found")
else:                         fail(f"date {TODAY} MISSING")

# ── catalog.json (GPTBot) ─────────────────────────────────────────────────────
print("\n── catalog.json (GPTBot) ──")
cat_raw = fetch("https://katalogai.io/catalog.json", ua="GPTBot/1.0")
cat = json.loads(cat_raw)
ok(f"{len(cat)} entries parsed")
stale_entries = [e["id"] for e in cat if e.get("date") != TODAY]
if not stale_entries: ok(f"all entry dates = {TODAY}")
else:                 fail(f"stale entry dates: {stale_entries}")
required_fields = ["id", "brand", "tags", "site", "date", "counter"]
for e in cat:
    for field in required_fields:
        if field not in e:
            fail(f"entry {e.get('id')} missing field '{field}'")
ok("all required fields present") if not errors else None

# ── index.html (GPTBot — no JS) ───────────────────────────────────────────────
print("\n── index.html (GPTBot, no JS) ──")
html = fetch("https://katalogai.io/", ua="GPTBot/1.0")
if "<noscript>" in html:      ok("<noscript> block present (GPTBot-safe)")
else:                         fail("<noscript> MISSING — GPTBot blind!")
if "datePublished" in html:   ok("JSON-LD datePublished present")
else:                         fail("datePublished MISSING in JSON-LD")
if "dateModified" in html:    ok("JSON-LD dateModified present")
else:                         fail("dateModified MISSING in JSON-LD")
if TODAY in html:             ok(f"date {TODAY} found")
else:                         fail(f"date {TODAY} MISSING")
if 'rel="canonical"' in html: ok("canonical link present")
else:                         fail("canonical link MISSING")
if "ai-instructions" in html: ok("ai-instructions link present")
else:                         warn("ai-instructions link missing")

# ── .well-known/ai-plugin.json ────────────────────────────────────────────────
print("\n── ai-plugin.json ──")
try:
    plugin = json.loads(fetch("https://katalogai.io/.well-known/ai-plugin.json"))
    ok(f"accessible — name_for_human={plugin.get('name_for_human')}")
    for key in ["name_for_human", "description_for_model", "api"]:
        if key in plugin: ok(f"field '{key}' present")
        else:             warn(f"field '{key}' missing")
except Exception as e:
    fail(f"ai-plugin.json error: {e}")

# ── AI_METHOD / AI_FAQ / AI_SCHEMA ───────────────────────────────────────────
print("\n── Semantic docs (AI_*.md) ──")
for doc in ["AI_METHOD.md", "AI_FAQ.md", "AI_SCHEMA.md"]:
    try:
        content = fetch(f"https://katalogai.io/{doc}")
        if TODAY in content: ok(f"{doc}: date {TODAY} present")
        else:                fail(f"{doc}: date {TODAY} MISSING")
    except Exception as e:
        fail(f"{doc}: {e}")

# ── Итог ─────────────────────────────────────────────────────────────────────
print("\n" + "=" * 55)
if not errors:
    print(f"ALL CHECKS PASSED  (today={TODAY})")
else:
    print(f"FAILED — {len(errors)} error(s):")
    for e in errors:
        print(f"  [FAIL] {e}")
if warns:
    print(f"\nWARNINGS — {len(warns)}:")
    for w in warns:
        print(f"  [WARN] {w}")
