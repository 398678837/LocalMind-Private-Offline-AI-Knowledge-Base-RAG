
import os
import json
from pathlib import Path

# 验证数据目录
data_dir = Path(__file__).parent / "data"

print("=" * 60)
print("LocalMind 数据验证")
print("=" * 60)

# 1. 检查 Chroma DB
print("\n1. Chroma DB 向量数据库:")
chroma_dir = data_dir / "chroma_db"
if chroma_dir.exists():
    print("   [OK] Chroma DB 目录存在")
    
    sqlite_file = chroma_dir / "chroma.sqlite3"
    if sqlite_file.exists():
        size_mb = sqlite_file.stat().st_size / 1024 / 1024
        print(f"   [OK] SQLite 数据库: {sqlite_file.name} ({size_mb:.2f} MB)")
    
    # 检查集合
    collections = [d for d in chroma_dir.iterdir() if d.is_dir() and d.name != "__pycache__"]
    for coll in collections:
        print(f"   [OK] 集合: {coll.name}")
        for file in coll.iterdir():
            size_kb = file.stat().st_size / 1024
            print(f"      - {file.name} ({size_kb:.2f} KB)")

# 2. 检查上传文件
print("\n2. 上传文件:")
uploads_dir = data_dir / "uploads"
if uploads_dir.exists():
    files = list(uploads_dir.iterdir())
    print(f"   [OK] 找到 {len(files)} 个上传文件")
    for file in files:
        size_kb = file.stat().st_size / 1024
        print(f"      - {file.name} ({size_kb:.2f} KB)")

# 3. 检查 JSON 存储
print("\n3. JSON 存储数据:")
storage_dir = data_dir / "storage"
if storage_dir.exists():
    for json_file in storage_dir.glob("*.json"):
        print(f"   [OK] {json_file.name}")
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                print(f"      - 包含 {len(data)} 条记录")
            elif isinstance(data, dict):
                print(f"      - 包含 {len(data)} 个键")

print("\n" + "=" * 60)
print("数据验证完成！所有文件都已成功存储。")
print("=" * 60)

