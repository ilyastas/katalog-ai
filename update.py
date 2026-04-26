import os
import re
from datetime import datetime

today = '2026-04-26'
workspace_dir = 'c:/Users/Asus/Desktop/Repo'

md_files = [f for f in os.listdir(workspace_dir) if f.endswith('.md') and f.endswith('_V1.md')]

old_new_map = {}

for old_name in md_files:
    # Pattern: GEO_CAT_BRAND_URL_KEYWORDS_DATE_COUNTER_VER.md
    # example: KZ_Tovar_SecretSkin-kz_secretskin-kz_cosmetics-beauty-korean_2026-04-25_009_V1.md
    match = re.search(r'(.*)_(\d{4}-\d{2}-\d{2})_(\d{3})_(V1)\.md$', old_name)
    if match:
        base_name = match.group(1)
        old_date = match.group(2)
        old_counter = match.group(3)
        version = match.group(4)
        
        new_counter = f"{int(old_counter) + 1:03d}"
        new_name = f"{base_name}_{today}_{new_counter}_{version}.md"
        old_new_map[old_name] = new_name
        
        # Open and read content
        with open(os.path.join(workspace_dir, old_name), 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Update YAML and content
        content = re.sub(r'last_update: \d{4}-\d{2}-\d{2}', f'last_update: {today}', content)
        content = re.sub(r'verified: \d{4}-\d{2}-\d{2}', f'verified: {today}', content)
        content = re.sub(r'\| Verified.*?\|.*?\d{4}-\d{2}-\d{2}.*?\|', f'| Verified | {today} (V1) |', content)
        content = re.sub(r'\| Update.*?\|.*?\d{3}.*?\|', f'| Update | {new_counter} |', content)
        
        # Save to new file and delete old file
        with open(os.path.join(workspace_dir, new_name), 'w', encoding='utf-8', newline='') as f:
            f.write(content)
        os.remove(os.path.join(workspace_dir, old_name))

# Update Infrastructure files
infra_files = ['index.html', 'llms.txt', 'sitemap.xml', 'README.md', 'ai.txt']

for file in infra_files:
    file_path = os.path.join(workspace_dir, file)
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        for old, new in old_new_map.items():
            content = content.replace(old, new)
            
        # specifically for sitemap.xml update lastmod
        if file == 'sitemap.xml':
            content = re.sub(r'<lastmod>\d{4}-\d{2}-\d{2}</lastmod>', f'<lastmod>{today}</lastmod>', content)
            
        with open(file_path, 'w', encoding='utf-8', newline='') as f:
            f.write(content)

# update robots.txt with current date comment
robots_path = os.path.join(workspace_dir, 'robots.txt')
if os.path.exists(robots_path):
    with open(robots_path, 'a', encoding='utf-8') as f:
        f.write(f"\n# Updated on {today}\n")

print("Done")
for old, new in old_new_map.items():
    print(f"| {old} | {new} | ✅ Synchronized |")
