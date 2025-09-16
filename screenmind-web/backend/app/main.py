"""
ScreenMind Web版本 - FastAPI后端
"""
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
import os
from typing import Optional
import base64
import io
from PIL import Image
from dotenv import load_dotenv
# 导入API路由
from .api import analyze, config, health
from .core.ai_service import AIService, QuestionAnalyzer
# 导入日志配置
from .core.logger import app_logger, disable_uvicorn_console_logging

# 加载环境变量
load_dotenv()

# 配置日志
disable_uvicorn_console_logging()
app_logger.info("ScreenMind应用启动中...")

# 创建FastAPI应用
app = FastAPI(
    title="ScreenMind API",
    description="智能截图答题助手 - Web版本",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件目录 (如果存在)
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except RuntimeError:
    pass  # static目录不存在时忽略

# 全局AI服务实例
app_logger.info("初始化AI服务...")
ai_service = AIService()
question_analyzer = QuestionAnalyzer(ai_service)

# 将AI服务实例传递给analyze模块
analyze.question_analyzer = question_analyzer
app_logger.info("AI服务初始化完成")

# 注册路由
app_logger.info("注册API路由...")
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(analyze.router, prefix="/api/v1", tags=["analyze"])
app.include_router(config.router, prefix="/api/v1", tags=["config"])
app_logger.info("路由注册完成")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """根路径返回简单的欢迎页面"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>ScreenMind - 智能答题助手</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
            .container { max-width: 800px; margin: 0 auto; }
            .upload-area {
                border: 2px dashed #ccc;
                padding: 50px;
                margin: 20px 0;
                border-radius: 10px;
                background: #f9f9f9;
            }
            .upload-area:hover { border-color: #007bff; background: #f0f8ff; }
            button {
                background: #007bff;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
            }
            button:hover { background: #0056b3; }
            .result {
                margin-top: 20px;
                padding: 20px;
                background: #f8f9fa;
                border-radius: 10px;
                text-align: left;
            }
            .hidden { display: none; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🧠 ScreenMind</h1>
            <h2>智能截图答题助手 - 网页版</h2>
            <p>上传题目图片，AI帮你分析答案！</p>

            <div class="upload-area" onclick="document.getElementById('fileInput').click()">
                <p>📸 点击或拖拽图片到这里</p>
                <input type="file" id="fileInput" accept="image/*" class="hidden">
            </div>

            <button onclick="analyzeImage()" id="analyzeBtn" disabled>🤖 开始分析</button>

            <div id="result" class="result hidden"></div>
        </div>

        <script>
            let selectedFile = null;

            document.getElementById('fileInput').addEventListener('change', function(e) {
                selectedFile = e.target.files[0];
                if (selectedFile) {
                    document.querySelector('.upload-area p').textContent = '✅ 已选择: ' + selectedFile.name;
                    document.getElementById('analyzeBtn').disabled = false;
                }
            });

            async function analyzeImage() {
                if (!selectedFile) return;

                const formData = new FormData();
                formData.append('image', selectedFile);

                document.getElementById('analyzeBtn').textContent = '🔄 分析中...';
                document.getElementById('analyzeBtn').disabled = true;

                try {
                    const response = await fetch('/api/v1/analyze', {
                        method: 'POST',
                        body: formData
                    });

                    if (response.ok) {
                        const result = await response.json();
                        document.getElementById('result').innerHTML = `
                            <h3>📝 分析结果</h3>
                            <p><strong>题目类型：</strong>${result.data.question_type}</p>
                            <p><strong>题目内容：</strong>${result.data.question_content}</p>
                            <p><strong>正确答案：</strong>${result.data.answer}</p>
                            <p><strong>详细解析：</strong>${result.data.explanation}</p>
                            <p><small>分析耗时：${result.data.analysis_time}秒</small></p>
                        `;
                        document.getElementById('result').classList.remove('hidden');
                    } else {
                        // 处理HTTP错误状态码
                        const errorData = await response.json();
                        const errorMsg = errorData.detail || '分析失败';
                        document.getElementById('result').innerHTML = `
                            <h3>❌ 分析失败</h3>
                            <p><strong>错误信息：</strong>${errorMsg}</p>
                            <p><small>状态码：${response.status}</small></p>
                        `;
                        document.getElementById('result').classList.remove('hidden');
                    }
                } catch (error) {
                    document.getElementById('result').innerHTML = `
                        <h3>❌ 网络错误</h3>
                        <p><strong>错误信息：</strong>${error.message}</p>
                    `;
                    document.getElementById('result').classList.remove('hidden');
                }

                document.getElementById('analyzeBtn').textContent = '🤖 开始分析';
                document.getElementById('analyzeBtn').disabled = false;
            }
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    app_logger.info("启动FastAPI服务器...")
    uvicorn.run(app, host="0.0.0.0", port=8000)