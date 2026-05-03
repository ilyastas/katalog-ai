import os

kz_files = sorted([f for f in os.listdir('.') if f.startswith('KZ_') and f.endswith('.md')])
ru_files = sorted([f for f in os.listdir('.') if f.startswith('RU_') and f.endswith('.md')])

rename_map = {}

kz_counter = 10
for f in kz_files:
    rename_map[f] = f'{kz_counter}_{f}'
    kz_counter += 1

ru_counter = 50
for f in ru_files:
    rename_map[f] = f'{ru_counter}_{f}'
    ru_counter += 1

# Files to update
targets = ['sitemap.xml', 'llms.txt', 'README.md']

for target in targets:
    if os.path.exists(target):
        with open(target, 'r', encoding='utf-8') as file:
            content = file.read()
        
        for old, new in rename_map.items():
            content = content.replace(old, new)
            
        with open(target, 'w', encoding='utf-8') as file:
            file.write(content)
            print(f'Updated {target}')

# Rename files on disk
for old, new in rename_map.items():
    os.rename(old, new)
    print(f'Renamed {old} -> {new}')
