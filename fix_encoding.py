
import os
import re

def fix_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 替换 HTML 实体编码
        original_content = content
        content = content.replace('&gt;', '>')
        content = content.replace('&lt;', '<')
        content = content.replace('&amp;', '&')
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f'Fixed: {file_path}')
        else:
            print(f'OK: {file_path}')
    except Exception as e:
        print(f'Error fixing {file_path}: {e}')

def fix_directory(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                fix_file(file_path)

if __name__ == '__main__':
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    print('Fixing backend files...')
    fix_directory(backend_dir)
    print('Done!')

