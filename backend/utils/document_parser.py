

from backend.models.schemas import FileType


class DocumentParser:
    """文档解析工具类 - 简单版"""
    
    def __init__(self):
        self.chunk_size = 500
        self.chunk_overlap = 50
        self.encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030', 'latin-1']
    
    def parse_document(self, file_path, file_type):
        """文档解析主函数"""
        try:
            if file_type == FileType.PDF:
                return self._parse_pdf(file_path)
            elif file_type == FileType.DOCX:
                return self._parse_docx(file_path)
            else:
                return self._parse_text(file_path)
        except Exception as e:
            print("[ERROR] 解析文档失败:", e)
            return None
    
    def _parse_text(self, file_path):
        """解析纯文本文件 - 简单版"""
        for encoding in self.encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    text = f.read()
                print(f"[INFO] 成功用 {encoding} 编码读取文件")
                return text
            except UnicodeDecodeError:
                continue
            except Exception as e:
                print(f"[ERROR] 用 {encoding} 编码读取失败:", e)
                continue
        print("[ERROR] 所有编码尝试失败")
        return None
    
    def _parse_pdf(self, file_path):
        """解析 PDF 文件"""
        try:
            import pdfplumber
            text_parts = []
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
            return '\n\n'.join(text_parts)
        except ImportError:
            print("[INFO] pdfplumber 未安装，PDF 解析跳过")
            return "PDF 文件内容"
        except Exception as e:
            print("[ERROR] 解析 PDF 失败:", e)
            return "PDF 文件内容"
    
    def _parse_docx(self, file_path):
        """解析 Word DOCX 文件"""
        try:
            from docx import Document
            doc = Document(file_path)
            text_parts = []
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text_parts.append(paragraph.text)
            return '\n\n'.join(text_parts)
        except ImportError:
            print("[INFO] python-docx 未安装，DOCX 解析跳过")
            return "Word 文件内容"
        except Exception as e:
            print("[ERROR] 解析 DOCX 失败:", e)
            return "Word 文件内容"
    
    def clean_text(self, text):
        """简单的文本清洗"""
        return text.strip()
    
    def split_into_chunks(self, text, chunk_size=None, chunk_overlap=None):
        """简单的分块"""
        if not text:
            return []
        chunks = []
        for i in range(0, len(text), 500):
            chunk = text[i:i+500].strip()
            if chunk:
                chunks.append(chunk)
        return chunks


document_parser = DocumentParser()

