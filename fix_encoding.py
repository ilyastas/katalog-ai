import os
import glob

cwd = r'c:\Users\Asus\Desktop\Repo'
files = glob.glob(cwd + '/**/*.*', recursive=True)

for path in files:
    if not path.endswith('.md') and not path.endswith('.txt') and not path.endswith('.html') and not path.endswith('.xml'):
        continue
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # check if it looks like typical double-encoding
        if 'Р' in content or 'С' in content or 'В' in content or '' in content:
            try:
                # try to reverse mojibake
                fixed_content = content.encode('cp1251').decode('utf-8')
                print(f"Fixing {os.path.basename(path)}")
                with open(path, 'w', encoding='utf-8', newline='') as f:
                    f.write(fixed_content)
            except Exception as e:
                print(f"Skipping {os.path.basename(path)}: {e}")

    except Exception as e:
        pass
print("Done checking.")