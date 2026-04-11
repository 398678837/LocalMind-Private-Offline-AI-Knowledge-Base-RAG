
# LocalMind 启动指南

## 📋 前置要求

1. **Python 3.10+** - 后端运行环境
2. **Node.js 18+** - 前端运行环境
3. **Ollama** - 本地 LLM 服务（用于 RAG 对话）

## 🚀 快速启动

### 1. 启动 Ollama（可选但推荐）

如果要使用完整的 RAG 对话功能，需要先启动 Ollama：

```bash
# 下载并安装 Ollama
# Windows: https://ollama.ai/download

# 拉取模型（推荐 llama3:8b）
ollama pull llama3:8b

# 启动 Ollama 服务（通常安装后自动运行）
ollama serve
```

### 2. 启动后端服务

打开第一个终端窗口：

```bash
cd backend

# 激活虚拟环境
# Windows:
.\venv\Scripts\activate

# 安装依赖（首次运行）
pip install -r requirements.txt

# 启动后端服务
python main.py
```

后端将在 `http://127.0.0.1:8000` 启动

### 3. 启动前端服务

打开第二个终端窗口：

```bash
cd frontend

# 安装依赖（首次运行）
npm install

# 启动前端开发服务器
npm run dev
```

前端将在 `http://localhost:5173` 启动

## 🎯 使用流程

1. **打开浏览器** 访问 `http://localhost:5173`
2. **创建知识库** - 点击"新建知识库"按钮
3. **上传文档** - 选择知识库后点击"上传文件"
4. **开始对话** - 在输入框中提问，AI 将基于知识库内容回答

## 📁 数据存储

所有数据都存储在项目根目录的 `data` 文件夹中：
- `data/chroma_db/` - 向量数据库
- `data/uploads/` - 上传的文件
- `data/storage/` - JSON 格式的元数据

## ⚙️ 配置说明

修改 `backend/config/settings.py` 可以调整：
- 数据存储路径
- Ollama 地址和模型
- 向量化模型
- 服务器端口等

