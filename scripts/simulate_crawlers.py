"""Симуляция краулеров, поисковиков и LLM-ботов для katalogai.io"""
import urllib.request
import json
import re
from datetime import date

TODAY = date.today().isoformat()
ISO_DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")
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
robots_date_match = re.search(r"# Updated on (\d{4}-\d{2}-\d{2})", robots)
if not robots_date_match:
    fail("robots.txt updated marker MISSING")
else:
    robots_date = robots_date_match.group(1)
    ok(f"robots updated marker found: {robots_date}")
    if robots_date > TODAY:
        fail(f"robots updated marker is in the future: {robots_date}")

# ── sitemap.xml ───────────────────────────────────────────────────────────────
print("\n── sitemap.xml ──")
sitemap = fetch("https://katalogai.io/sitemap.xml")
for u in ["katalogai.io/", "catalog.json", "llms.txt"]:
    if u in sitemap: ok(f"{u} listed")
    else:            fail(f"{u} MISSING")
lastmods = re.findall(r"<lastmod>(.+?)</lastmod>", sitemap)
invalid_lastmods = [d for d in lastmods if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", d)]
if invalid_lastmods:
    fail(f"invalid lastmod values: {invalid_lastmods}")
else:
    ok("all sitemap lastmod values are ISO dates")
if any(d <= TODAY for d in lastmods):
    ok("sitemap lastmod markers are present and not in the future")
else:
    warn("sitemap lastmod markers look suspicious")

# ── llms.txt (Claude-User) ────────────────────────────────────────────────────
print("\n── llms.txt (Claude-User) ──")
llms = fetch("https://katalogai.io/llms.txt", ua="Claude-User/1.0")
if "katalogai.io" in llms:    ok("canonical URL present")
else:                         fail("canonical URL MISSING")
if "catalog.json" in llms:    ok("catalog.json linked")
else:                         fail("catalog.json MISSING")
if "github" in llms.lower():  ok("GitHub notice present")
else:                         warn("GitHub notice missing")
llms_date_match = re.search(r"Last updated: (\d{4}-\d{2}-\d{2})", llms)
if not llms_date_match:
    fail("llms.txt date marker MISSING")
else:
    llms_date = llms_date_match.group(1)
    ok(f"llms.txt date marker found: {llms_date}")
    if llms_date > TODAY:
        fail(f"llms.txt date is in the future: {llms_date}")

# ── catalog.json (GPTBot) ─────────────────────────────────────────────────────
print("\n── catalog.json (GPTBot) ──")
cat_raw = fetch("https://katalogai.io/catalog.json", ua="GPTBot/1.0")
cat = json.loads(cat_raw)
ok(f"{len(cat)} entries parsed")
invalid_entry_dates = [e.get("id", "?") for e in cat if not ISO_DATE_RE.fullmatch(e.get("date", ""))]
if invalid_entry_dates:
    fail(f"invalid entry date format: {invalid_entry_dates}")
else:
    ok("all entry dates are ISO dates")
future_entries = [e.get("id", "?") for e in cat if e.get("date", "") > TODAY]
if future_entries:
    fail(f"future entry dates detected: {future_entries}")
required_fields = ["id", "brand", "tags", "site", "inst", "date"]
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
if re.search(r"Page generated: (\d{4}-\d{2}-\d{2})", html):
    page_date = re.search(r"Page generated: (\d{4}-\d{2}-\d{2})", html).group(1)
    ok(f"page generated marker found: {page_date}")
    if page_date > TODAY:
        fail(f"page generated marker is in the future: {page_date}")
else:
    fail("page generated marker MISSING")
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
        date_match = re.search(r"Updated: (\d{4}-\d{2}-\d{2})", content)
        if not date_match:
            fail(f"{doc}: updated marker MISSING")
        else:
            doc_date = date_match.group(1)
            ok(f"{doc}: updated marker found: {doc_date}")
            if doc_date > TODAY:
                fail(f"{doc}: updated marker in the future: {doc_date}")
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
