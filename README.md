# LocalMind - 本地私有化 AI 知识库问答助手

🚀 **本地私有化、隐私优先**的 AI 知识库问答助手，基于 RAG（检索增强生成）+ AI Agents 技术，100% 本地离线运行！

## ✨ 核心特性

- 🔒 **完全本地离线**：无任何云端请求，不上传任何用户数据
- 📚 **多文档支持**：PDF、Word、TXT、Markdown、代码文件等
- 🤖 **AI Agents**：智能任务规划、工具调用、多知识库路由
- 🧠 **COT 可视化**：清晰展示 AI 思考过程
- 🔐 **安全特性**：AES 文件加密、敏感信息检测、本地日志审计
- 🌐 **多语言支持**：中文、英文、日文、韩文界面
- 💻 **跨平台**：支持 Windows、MacOS

## 🛠️ 技术栈

### 前端
- React 18 + TypeScript
- Tailwind CSS / ShadCN UI
- Axios + React Router

### 后端
- Python 3.10+ + FastAPI
- Pydantic + Uvicorn

### AI 核心
- LangChain（含 Agents 模块）
- Ollama（本地大模型）
- Chroma DB（本地向量库）
- sentence-transformers（向量化模型）

### 文档解析
- PyPDF2 / pdfplumber（PDF）
- python-docx（Word）
- Unstructured（通用文本/代码）
- MarkdownIt（MD）

## 📁 项目结构

```
LocalMind/
├── backend/              # FastAPI 后端
│   ├── api/             # API 接口层
│   ├── core/            # 核心业务逻辑
│   ├── models/          # Pydantic 数据模型
│   ├── services/        # 服务层
│   ├── utils/           # 工具函数
│   └── config/          # 配置文件
├── frontend/            # React 前端
│   └── src/
│       ├── pages/       # 页面组件
│       ├── components/  # 通用组件
│       ├── api/         # API 调用
│       ├── utils/       # 工具函数
│       ├── types/       # TypeScript 类型
│       └── store/       # 状态管理
├── ai_core/             # AI 核心模块
│   ├── rag/            # RAG 检索
│   ├── agents/         # AI Agents
│   ├── embeddings/     # 向量化
│   └── vector_db/      # 向量数据库
├── document_parser/     # 文档解析模块
├── security/            # 安全模块
├── scripts/             # 启动脚本
├── docker/              # Docker 配置
└── docs/                # 文档
```

## 🚀 快速开始

### 前置要求
1. **Python 3.10+**
2. **Node.js 18+**
3. **Ollama** - [下载安装](https://ollama.ai/)

### 安装 Ollama 模型
```bash
# 拉取对话模型
ollama pull qwen2:7b

# 拉取向量化模型
ollama pull nomic-embed-text:latest
```

### 后端部署

#### 1. 创建虚拟环境
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

#### 2. 安装依赖
```bash
pip install -r requirements.txt
```

#### 3. 启动后端
```bash
cd backend
python main.py
```

后端将运行在：http://127.0.0.1:8000

API 文档：http://127.0.0.1:8000/docs

### 前端部署

#### 1. 安装依赖
```bash
cd frontend
npm install
```

#### 2. 启动前端
```bash
npm run dev
```

前端将运行在：http://localhost:5173

### 使用说明
1. 打开 http://localhost:5173
2. 创建知识库
3. 上传文档（支持 PDF/DOCX/TXT/MD/PY/JAVA）
4. 开始对话！

## ✨ 已实现功能
- ✅ 创建、编辑、删除知识库
- ✅ 文件上传与管理
- ✅ 文档自动解析与向量化
- ✅ RAG 问答系统
- ✅ 对话会话管理
- ✅ 多语言支持（中文/英文/日语/韩语）
- ✅ 100% 本地私有化，无云端请求

## 📖 文档

- [环境部署指南](./docs/deployment.md)
- [API 文档](./docs/api.md)
- [使用教程](./docs/tutorial.md)
- [常见问题](./docs/faq.md)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

---

**LocalMind - 让 AI 在您的设备上安全运行** 🔒
