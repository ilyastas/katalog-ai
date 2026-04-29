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
        
        # Strip UTF-8 BOM if present
        if content.startswith('\ufeff'):
            content = content[1:]
            
        needs_write = False
            
        # check if mojibake present
        if 'Р' in content or 'С' in content or 'В' in content or 'Р”' in content:
            try:
                content = content.encode('cp1251').decode('utf-8')
                print(f"Fixed mojibake in {os.path.basename(path)}")
                needs_write = True
            except Exception as e:
                pass
                
        # we still want to save uniformly as utf-8 without BOM
        with open(path, 'w', encoding='utf-8', newline='') as f:
            f.write(content)
            print(f"Saved {os.path.basename(path)} without BOM")
            
    except Exception as e:
        print(f"Error {path}: {e}")
