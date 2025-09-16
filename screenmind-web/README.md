# 🧠 ScreenMind Web版本

智能截图答题助手 - 网页版，让任何人都能轻松使用AI来分析题目！

## ✨ 功能特色

- 📸 **简单易用**: 拖拽图片即可分析，无需安装任何软件
- 🤖 **多AI支持**: 支持Google Gemini、通义千问、OpenAI GPT等多种AI模型
- 🎯 **智能分析**: 自动识别题目类型，提供详细解答和解析
- 📱 **响应式设计**: 支持手机、平板、电脑等各种设备
- 🔒 **安全可靠**: API密钥加密存储，图片不会被保存

## 🚀 快速开始

### 方法1: 使用启动脚本（推荐）

1. **安装依赖**
   ```bash
   cd screenmind-web
   pip install -r backend/requirements.txt
   ```

2. **配置API密钥**（至少配置一个）
   ```bash
   # 通义千问（推荐，国内访问稳定）
   export QWEN_API_KEY="your-qwen-api-key"

   # Google Gemini
   export GEMINI_API_KEY="your-gemini-api-key"

   # OpenAI GPT
   export OPENAI_API_KEY="your-openai-api-key"
   ```

3. **启动服务**
   ```bash
   python start.py
   ```

4. **访问网站**
   - 打开浏览器访问: http://localhost:8000
   - API文档: http://localhost:8000/docs

### 方法2: 手动启动

```bash
cd screenmind-web/backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 🔧 API密钥获取

### 通义千问 (推荐)
1. 访问 [阿里云DashScope](https://dashscope.aliyuncs.com/)
2. 注册账号并创建API Key
3. 每月有免费额度，适合个人使用

### Google Gemini
1. 访问 [Google AI Studio](https://makersuite.google.com/)
2. 创建API Key
3. 免费额度丰富，功能强大

### OpenAI GPT
1. 访问 [OpenAI Platform](https://platform.openai.com/)
2. 创建API Key
3. 需要付费使用，但效果最佳

## 📖 使用说明

### 基础使用
1. 打开网页后，点击或拖拽图片到上传区域
2. 选择图片后，点击"开始分析"按钮
3. 等待AI分析完成，查看结果

### 设置管理
- 可以在设置页面切换不同的AI模型
- 支持实时配置API密钥
- 可以查看当前使用的模型信息

### 支持的图片格式
- PNG、JPG、JPEG、WEBP
- 文件大小限制: 10MB
- 建议图片清晰，文字易于识别

## 🌐 部署到服务器

### Docker部署

1. **创建Dockerfile**
   ```dockerfile
   FROM python:3.9-slim

   WORKDIR /app
   COPY backend/requirements.txt .
   RUN pip install -r requirements.txt

   COPY backend/ .

   EXPOSE 8000
   CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

2. **构建和运行**
   ```bash
   docker build -t screenmind-web .
   docker run -p 8000:8000 -e QWEN_API_KEY=your-key screenmind-web
   ```

### Vercel部署

1. **安装Vercel CLI**
   ```bash
   npm i -g vercel
   ```

2. **配置vercel.json**
   ```json
   {
     "builds": [
       {
         "src": "backend/app/main.py",
         "use": "@vercel/python"
       }
     ],
     "routes": [
       {
         "src": "/(.*)",
         "dest": "/backend/app/main.py"
       }
     ]
   }
   ```

3. **部署**
   ```bash
   vercel --prod
   ```

### 云服务器部署

1. **使用systemd管理服务**
   ```ini
   [Unit]
   Description=ScreenMind Web
   After=network.target

   [Service]
   Type=simple
   User=www-data
   WorkingDirectory=/opt/screenmind-web/backend
   Environment=PATH=/opt/screenmind-web/venv/bin
   Environment=QWEN_API_KEY=your-key
   ExecStart=/opt/screenmind-web/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

2. **使用Nginx反向代理**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

## 📝 API文档

### 分析图片
```http
POST /api/v1/analyze
Content-Type: multipart/form-data

Body:
- image: 图片文件

Response:
{
  "success": true,
  "data": {
    "question_type": "选择题",
    "question_content": "题目内容",
    "answer": "正确答案",
    "explanation": "详细解析",
    "analysis_time": 2.3,
    "model_used": "qwen-vl-plus"
  }
}
```

### 获取可用模型
```http
GET /api/v1/analyze/models

Response:
{
  "success": true,
  "data": {
    "gemini": {
      "name": "Google Gemini",
      "models": ["gemini-1.5-flash", "gemini-1.5-pro"]
    }
  }
}
```

### 设置API密钥
```http
POST /api/v1/config/api-key

Body:
{
  "provider": "qwen",
  "api_key": "your-api-key"
}
```

## 🛠️ 开发相关

### 项目结构
```
screenmind-web/
├── backend/                 # 后端API
│   ├── app/
│   │   ├── main.py         # FastAPI应用
│   │   ├── api/            # API路由
│   │   ├── core/           # 核心模块
│   │   └── models/         # 数据模型
│   └── requirements.txt    # Python依赖
├── frontend/               # 前端界面（待开发）
├── start.py               # 启动脚本
└── README.md              # 说明文档
```

### 技术栈
- **后端**: FastAPI + Python
- **AI服务**: Google Gemini、通义千问、OpenAI
- **图片处理**: Pillow
- **部署**: Docker、Vercel、云服务器

### 开发模式
```bash
# 启动开发服务器
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 运行测试
pytest tests/

# 代码格式化
black app/
isort app/
```

## 🤝 贡献指南

1. Fork项目
2. 创建功能分支: `git checkout -b feature/your-feature`
3. 提交代码: `git commit -am 'Add some feature'`
4. 推送分支: `git push origin feature/your-feature`
5. 提交Pull Request

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 💡 推广建议

### 目标用户
- 中学生、大学生
- 在线教育机构
- 培训班老师
- 家长辅导

### 推广策略
1. **社交媒体**: 在微博、知乎、B站等平台分享使用教程
2. **教育论坛**: 在各大教育论坛介绍工具优势
3. **口碑传播**: 鼓励用户分享给同学朋友
4. **SEO优化**: 优化关键词，提高搜索排名
5. **合作推广**: 与教育博主、老师合作推广

### 商业化方向
- **免费版**: 每日10次免费分析
- **付费版**: 无限制使用 + 高级AI模型
- **教育版**: 面向学校和机构的批量授权
- **API服务**: 为其他应用提供AI分析接口

---

🎉 **恭喜！现在你有了一个完整的网页版ScreenMind！**

用户只需要打开网页就能使用，再也不用担心安装问题了！