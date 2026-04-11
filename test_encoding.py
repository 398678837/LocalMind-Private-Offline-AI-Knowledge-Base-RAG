
import chardet

file_path = r"h:\AI Projects\LocalMind\LocalMind-Private-Offline-AI-Knowledge-Base-RAG-\data\uploads\73b54012-c95f-4c33-9fca-94f503f4840b.txt"

print("=" * 60)
print("正在检测文件编码...")
print("=" * 60)

with open(file_path, 'rb') as f:
    raw_data = f.read()

print(f"文件大小: {len(raw_data)} 字节")
print()

result = chardet.detect(raw_data)
print("chardet 检测结果:")
print(f"  编码: {result.get('encoding')}")
print(f"  置信度: {result.get('confidence')}")
print(f"  语言: {result.get('language')}")
print()

encodings = [
    'utf-8', 'gbk', 'gb2312', 'gb18030', 
    'latin-1', 'big5', 'shift_jis', 'euc-kr',
    'cp1252', 'iso-8859-1', 'utf-16', 'utf-16-le', 'utf-16-be'
]

print("=" * 60)
print("尝试所有编码:")
print("=" * 60)

success_encoding = None
success_text = None

for enc in encodings:
    try:
        text = raw_data.decode(enc)
        print(f"\n编码 {enc} 读取成功！")
        print(f"前 150 字符:\n{text[:150]}")
        print()
        print("-" * 60)
        success_encoding = enc
        success_text = text
        break
    except Exception as e:
        print(f"编码 {enc} 失败")

if success_encoding:
    print("\n" + "=" * 60)
    print(f"成功编码: {success_encoding}")
    print("=" * 60)
else:
    print("\n" + "=" * 60)
    print("所有编码都失败了")
    print("=" * 60)

