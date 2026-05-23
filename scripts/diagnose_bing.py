"""Диагностика: почему Bing не индексирует katalogai.io"""
import urllib.request
import re
from datetime import date

TODAY = date.today().isoformat()


def fetch(url: str, ua: str = "Mozilla/5.0") -> tuple[str, int]:
    req = urllib.request.Request(url, headers={"User-Agent": ua})
    with urllib.request.urlopen(req, timeout=10) as r:
        return r.read().decode("utf-8", errors="replace"), r.status


# ── Что видит Bingbot/msnbot ─────────────────────────────────────────────────
print("\n=== Bingbot видит index.html ===")
html, status = fetch(
    "https://katalogai.io/",
    ua="msnbot/2.0b (+http://search.microsoft.com/msnbot.htm)"
)
print(f"HTTP status: {status}")

m = re.search(r'<link rel=["\']canonical["\'][^>]+href=["\']([^"\'> ]+)', html)
print(f"canonical: {m.group(1) if m else 'NOT FOUND'}")

m = re.search(r"<title>(.+?)</title>", html)
print(f"title: {m.group(1) if m else 'NOT FOUND'}")

m = re.search(r'<meta\s+name=["\']description["\'][^>]+content=["\']([^"\']+)', html)
if not m:
    m = re.search(r'content=["\']([^"\']+)["\'][^>]+name=["\']description["\']', html)
print(f"meta description: {m.group(1)[:80] if m else 'NOT FOUND'}")

print(f"JSON-LD: {'PRESENT' if 'application/ld+json' in html else 'MISSING'}")
print(f"noscript: {'PRESENT' if '<noscript>' in html else 'MISSING'}")

# ── robots.txt для Bingbot ───────────────────────────────────────────────────
print("\n=== robots.txt (Bingbot/msnbot секция) ===")
robots, _ = fetch("https://katalogai.io/robots.txt", ua="Bingbot/2.0")
for line in robots.splitlines():
    if any(x in line.lower() for x in ["bingbot", "msnbot", "user-agent", "disallow", "allow", "sitemap"]):
        print(f"  {line}")

# ── IndexNow ключи ───────────────────────────────────────────────────────────
print("\n=== IndexNow ключи ===")
for key in ["7f559c9f7d60484fa802ab03c9328995", "9a1f3247e0e9496aa35d6b290e5862bb"]:
    try:
        content, s = fetch(f"https://katalogai.io/{key}.txt")
        match = content.strip() == key
        print(f"[{s}] {key}.txt → content='{content.strip()}' → match={match}")
    except Exception as e:
        print(f"[ERR] {key}.txt: {e}")

# ── sitemap.xml ──────────────────────────────────────────────────────────────
print("\n=== sitemap.xml ===")
sitemap, _ = fetch("https://katalogai.io/sitemap.xml")
urls = re.findall(r"<loc>(.+?)</loc>", sitemap)
lastmods = re.findall(r"<lastmod>(.+?)</lastmod>", sitemap)
for u, lm in zip(urls, lastmods):
    print(f"  {lm}  {u}")

# ── CNAME ────────────────────────────────────────────────────────────────────
print("\n=== CNAME ===")
try:
    cname, _ = fetch("https://katalogai.io/CNAME")
    print(f"CNAME содержит: {cname.strip()}")
except Exception as e:
    print(f"CNAME недоступен (допустимо для CDN-only): {e}")

# ── Известные причины проблем с Bing ─────────────────────────────────────────
print("\n=== Чек-лист причин непопадания в Bing ===")
checks = {
    "IndexNow активен в daily-sync.yml": True,  # мы добавляли
    "Sitemap отправлен в Bing Webmaster Tools": None,  # требует ручной проверки
    "Bing Webmaster Tools: сайт добавлен": None,  # требует ручной проверки
    "robots.txt: Bingbot разрешён (wildcard или явно)": (
        ("User-agent: *" in robots and "Allow: /" in robots)
        or ("Bingbot" in robots and "Allow: /" in robots)
    ),
    "sitemap.xml: catalog.json указан": "catalog.json" in sitemap,
    "canonical указывает на katalogai.io": m is not None if (m := re.search(r'rel=["\']canonical["\'][^>]+href=["\']([^"\'> ]+)', html)) else False,
}
for check, result in checks.items():
    if result is True:   print(f"  [OK]  {check}")
    elif result is False: print(f"  [!!]  {check}")
    else:                print(f"  [??]  {check}  ← нужна ручная проверка")
