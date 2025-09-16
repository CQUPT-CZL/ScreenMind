# 🧠 ScreenMind

智能截图答题助手 - AI驱动的Web版题目识别和解答系统

## ✨ 功能特色

- 🤖 **多AI模型支持**: 支持 Google Gemini、通义千问、OpenAI GPT 等主流AI模型
- 📸 **图片智能分析**: 自动识别题目类型，提供详细解答和解析
- 🌐 **完整Web应用**: 前后端一体化，无需安装客户端
- 🎯 **高精度识别**: 支持选择题、填空题、判断题等多种题型
- 📱 **响应式设计**: 支持拖拽上传，适配各种设备
- ⚙️ **灵活配置**: 支持在线切换AI模型和配置API密钥

## 🚀 快速开始

### 环境要求
- Python 3.8+
- 现代Web浏览器

### 安装依赖
```bash
cd screenmind-web
pip install -r backend/requirements.txt
```

### 配置API密钥
```bash
# 通义千问（推荐，国内访问稳定）
export QWEN_API_KEY="your-qwen-api-key"

# 或者使用其他AI服务
export GEMINI_API_KEY="your-gemini-api-key"
export OPENAI_API_KEY="your-openai-api-key"
```

### 启动服务
```bash
python start.py
```

### 访问应用
- **Web应用**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/api/v1/health

## 📖 API接口

### 图片分析
```http
POST /api/v1/analyze
Content-Type: multipart/form-data

参数:
- image: 图片文件
- model_provider: AI模型提供商 (可选)
- model_name: 模型名称 (可选)

响应:
{
  "success": true,
  "data": {
    "question_type": "选择题",
    "question_content": "题目内容",
    "answer": "正确答案",
    "explanation": "详细解析",
    "analysis_time": 2.3
  }
}
```

### 健康检查
```http
GET /api/v1/health

响应:
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00",
  "service": "ScreenMind API",
  "version": "1.0.0"
}
```

### 获取可用模型
```http
GET /api/v1/analyze/models

响应:
{
  "success": true,
  "data": {
    "gemini": {
      "name": "Google Gemini",
      "models": ["gemini-1.5-flash", "gemini-1.5-pro"]
    },
    "qwen": {
      "name": "通义千问",
      "models": ["qwen-vl-plus", "qwen-vl-max"]
    }
  }
}
```

## 🔧 配置管理

### 设置API密钥
```http
POST /api/v1/config/api-key
Content-Type: application/json

{
  "provider": "qwen",
  "api_key": "your-api-key"
}
```

### 切换AI模型
```http
POST /api/v1/config/model
Content-Type: application/json

{
  "provider": "qwen",
  "model": "qwen-vl-plus"
}
```

### 获取当前设置
```http
GET /api/v1/config/settings
```

## 🌐 部署方案

### Docker部署
```bash
# 构建镜像
docker build -t screenmind-api .

# 运行容器
docker run -p 8000:8000 -e QWEN_API_KEY=your-key screenmind-api
```

### 云服务器部署
```bash
# 使用 systemd 管理服务
sudo cp screenmind.service /etc/systemd/system/
sudo systemctl enable screenmind
sudo systemctl start screenmind
```

### Nginx反向代理
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📁 项目结构

```
screenmind-web/
├── backend/                 # 后端API
│   ├── app/
│   │   ├── main.py         # FastAPI应用 + Web界面
│   │   ├── api/            # API路由模块
│   │   │   ├── analyze.py  # 图片分析接口
│   │   │   ├── config.py   # 配置管理接口
│   │   │   └── health.py   # 健康检查接口
│   │   └── core/           # 核心模块
│   │       └── ai_service.py # AI服务集成
│   ├── requirements.txt    # Python依赖
│   └── static/            # 静态文件目录
├── start.py               # 启动脚本
└── README.md              # 说明文档
```

## 💡 使用说明

### 基础使用
1. 启动服务后，打开浏览器访问 http://localhost:8000
2. 点击或拖拽图片到上传区域
3. 点击"开始分析"按钮，等待AI分析结果
4. 查看题目类型、内容、答案和详细解析

### 技术栈
- **后端**: FastAPI + Python
- **AI服务**: Google Gemini、通义千问、OpenAI
- **图片处理**: Pillow
- **前端**: 原生HTML/CSS/JavaScript
- **部署**: Docker、云服务器

### 开发模式
```bash
# 使用启动脚本（推荐）
python start.py

# 或手动启动开发服务器
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```