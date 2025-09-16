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
from .api import analyze, config, health, screenshot
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

# 注册API路由
app_logger.info("注册API路由...")
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(analyze.router, prefix="/api/v1", tags=["analyze"])
app.include_router(config.router, prefix="/api/v1", tags=["config"])
app.include_router(screenshot.router, prefix="/api/v1", tags=["screenshot"])
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
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                text-align: center; 
                padding: 20px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                margin: 0;
                color: white;
            }
            .container { 
                max-width: 900px; 
                margin: 0 auto; 
                background: rgba(255, 255, 255, 0.95);
                border-radius: 20px;
                padding: 40px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                color: #333;
            }
            .shortcut-tips {
                background: linear-gradient(45deg, #ff6b6b, #feca57);
                color: white;
                padding: 20px;
                border-radius: 15px;
                margin: 20px 0;
                box-shadow: 0 8px 16px rgba(0,0,0,0.1);
                animation: pulse 2s infinite;
            }
            @keyframes pulse {
                0% { transform: scale(1); }
                50% { transform: scale(1.02); }
                100% { transform: scale(1); }
            }
            .shortcut-key {
                background: rgba(255,255,255,0.2);
                padding: 8px 12px;
                border-radius: 8px;
                font-weight: bold;
                font-family: 'Courier New', monospace;
                margin: 0 5px;
                display: inline-block;
                border: 2px solid rgba(255,255,255,0.3);
            }
            .upload-area {
                border: 3px dashed #007bff;
                padding: 40px;
                margin: 30px 0;
                border-radius: 15px;
                background: linear-gradient(45deg, #f8f9fa, #e9ecef);
                transition: all 0.3s ease;
                cursor: pointer;
            }
            .upload-area:hover { 
                border-color: #0056b3; 
                background: linear-gradient(45deg, #e3f2fd, #bbdefb);
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(0,123,255,0.15);
            }
            .screenshot-btn {
                background: linear-gradient(45deg, #28a745, #20c997);
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 25px;
                cursor: pointer;
                font-size: 18px;
                font-weight: bold;
                margin: 10px;
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3);
            }
            .screenshot-btn:hover { 
                background: linear-gradient(45deg, #218838, #1ea085);
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(40, 167, 69, 0.4);
            }
            .analyze-btn {
                background: linear-gradient(45deg, #007bff, #6610f2);
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 25px;
                cursor: pointer;
                font-size: 18px;
                font-weight: bold;
                margin: 10px;
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(0, 123, 255, 0.3);
            }
            .analyze-btn:hover { 
                background: linear-gradient(45deg, #0056b3, #520dc2);
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(0, 123, 255, 0.4);
            }
            .analyze-btn:disabled {
                background: #6c757d;
                cursor: not-allowed;
                transform: none;
                box-shadow: none;
            }
            .result {
                margin-top: 30px;
                padding: 25px;
                background: linear-gradient(45deg, #f8f9fa, #ffffff);
                border-radius: 15px;
                text-align: left;
                border-left: 5px solid #007bff;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            }
            .hidden { display: none; }
            .status-indicator {
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 10px 20px;
                border-radius: 25px;
                background: rgba(40, 167, 69, 0.9);
                color: white;
                font-weight: bold;
                z-index: 1000;
                transition: all 0.3s ease;
            }
            .status-indicator.processing {
                background: rgba(255, 193, 7, 0.9);
                animation: blink 1s infinite;
            }
            @keyframes blink {
                0%, 50% { opacity: 1; }
                51%, 100% { opacity: 0.5; }
            }
            .feature-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin: 30px 0;
            }
            .feature-card {
                background: linear-gradient(45deg, #ffffff, #f8f9fa);
                padding: 20px;
                border-radius: 15px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                transition: transform 0.3s ease;
            }
            .feature-card:hover {
                transform: translateY(-5px);
            }
        </style>
    </head>
    <body>
        <div class="status-indicator" id="statusIndicator">🟢 就绪</div>
        
        <div class="container">
            <h1>🧠 ScreenMind</h1>
            <h2>智能截图答题助手 - 网页版</h2>
            <p>AI驱动的智能答题助手，支持快捷键截屏分析！</p>

            <div class="shortcut-tips">
                <h3>⚡ 快捷操作指南</h3>
                <p>按下 <span class="shortcut-key">Ctrl + Shift + S</span> (Windows/Linux) 或 <span class="shortcut-key">Cmd + Shift + S</span> (Mac) 快速截屏</p>
                <p>截屏后图片将自动上传并进行AI分析 🚀</p>
            </div>

            <div class="feature-grid">
                <div class="feature-card">
                    <h4>📸 快捷截屏</h4>
                    <p>使用快捷键或点击按钮快速截取屏幕内容</p>
                </div>
                <div class="feature-card">
                    <h4>🤖 AI分析</h4>
                    <p>智能识别题目内容并提供详细解答</p>
                </div>
                <div class="feature-card">
                    <h4>⚡ 实时处理</h4>
                    <p>快速响应，秒级完成图片分析</p>
                </div>
            </div>

            <div style="margin: 30px 0;">
                <button onclick="startScreenCapture()" class="screenshot-btn" id="screenshotBtn">
                    📸 开始截屏
                </button>
            </div>

            <div class="upload-area" onclick="document.getElementById('fileInput').click()">
                <p>📁 或者点击这里上传图片文件</p>
                <p style="font-size: 14px; color: #666; margin-top: 10px;">支持 JPG、PNG、GIF 等格式</p>
                <input type="file" id="fileInput" accept="image/*" class="hidden">
            </div>

            <button onclick="analyzeImage()" id="analyzeBtn" class="analyze-btn" disabled>🤖 开始分析</button>

            <div id="result" class="result hidden"></div>
        </div>

        <script>
            let selectedFile = null;
            let isCapturing = false;

            // 更新状态指示器
            function updateStatus(status, isProcessing = false) {
                const indicator = document.getElementById('statusIndicator');
                indicator.textContent = status;
                if (isProcessing) {
                    indicator.classList.add('processing');
                } else {
                    indicator.classList.remove('processing');
                }
            }

            // 文件选择处理
            document.getElementById('fileInput').addEventListener('change', function(e) {
                selectedFile = e.target.files[0];
                if (selectedFile) {
                    document.querySelector('.upload-area p').textContent = '✅ 已选择: ' + selectedFile.name;
                    document.getElementById('analyzeBtn').disabled = false;
                    updateStatus('📁 文件已选择');
                }
            });

            // 截屏功能 - 使用后端API
            async function startScreenCapture() {
                if (isCapturing) return;
                
                try {
                    isCapturing = true;
                    updateStatus('📸 正在截屏...', true);
                    document.getElementById('screenshotBtn').textContent = '📸 截屏中...';
                    document.getElementById('screenshotBtn').disabled = true;

                    // 调用后端截屏API
                    const response = await fetch('/api/v1/screenshot', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        }
                    });
                    
                    if (!response.ok) {
                        const errorData = await response.json();
                        throw new Error(errorData.detail || `截屏失败: ${response.status}`);
                    }
                    
                    const result = await response.json();
                    
                    if (result.success) {
                        updateStatus('✅ 截屏完成');
                        
                        // 将base64图片数据转换为Blob
                        const base64Data = result.data.image;
                        const byteCharacters = atob(base64Data);
                        const byteNumbers = new Array(byteCharacters.length);
                        for (let i = 0; i < byteCharacters.length; i++) {
                            byteNumbers[i] = byteCharacters.charCodeAt(i);
                        }
                        const byteArray = new Uint8Array(byteNumbers);
                        const blob = new Blob([byteArray], { type: 'image/png' });
                        
                        // 创建文件对象
                        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
                        selectedFile = new File([blob], `screenshot-${timestamp}.png`, { type: 'image/png' });
                        
                        document.querySelector('.upload-area p').innerHTML = '✅ 截屏完成: ' + selectedFile.name + '<br><small>图片已准备好进行分析</small>';
                        document.getElementById('analyzeBtn').disabled = false;
                        
                        // 自动开始分析
                        setTimeout(() => {
                            analyzeImage();
                        }, 500);
                    } else {
                        throw new Error(result.message || '截屏失败');
                    }
                    
                } catch (error) {
                    console.error('截屏失败:', error);
                    updateStatus('❌ 截屏失败');
                    
                    let errorMsg = '截屏失败';
                    if (error.message) {
                        errorMsg = error.message;
                    }
                    
                    document.getElementById('result').innerHTML = `
                        <h3>❌ 截屏失败</h3>
                        <p><strong>错误信息：</strong>${errorMsg}</p>
                        <p><small>提示：请确保系统支持截屏功能</small></p>
                    `;
                    document.getElementById('result').classList.remove('hidden');
                } finally {
                    isCapturing = false;
                    document.getElementById('screenshotBtn').textContent = '📸 开始截屏';
                    document.getElementById('screenshotBtn').disabled = false;
                }
            }

            // 快捷键监听
            document.addEventListener('keydown', function(e) {
                // Ctrl+Shift+S (Windows/Linux) 或 Cmd+Shift+S (Mac)
                if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'S') {
                    e.preventDefault();
                    startScreenCapture();
                }
            });

            // 分析图片功能
            async function analyzeImage() {
                if (!selectedFile) return;

                const formData = new FormData();
                formData.append('image', selectedFile);

                document.getElementById('analyzeBtn').textContent = '🔄 分析中...';
                document.getElementById('analyzeBtn').disabled = true;
                updateStatus('🤖 AI分析中...', true);

                try {
                    const response = await fetch('/api/v1/analyze', {
                        method: 'POST',
                        body: formData
                    });

                    if (response.ok) {
                        const result = await response.json();
                        updateStatus('✅ 分析完成');
                        document.getElementById('result').innerHTML = `
                            <h3>📝 分析结果</h3>
                            <div style="background: linear-gradient(45deg, #e8f5e8, #f0f8f0); padding: 15px; border-radius: 10px; margin: 10px 0;">
                                <p><strong>🏷️ 题目类型：</strong><span style="color: #28a745; font-weight: bold;">${result.data.question_type}</span></p>
                            </div>
                            <div style="background: linear-gradient(45deg, #e3f2fd, #f0f8ff); padding: 15px; border-radius: 10px; margin: 10px 0;">
                                <p><strong>📋 题目内容：</strong></p>
                                <div style="background: white; padding: 10px; border-radius: 5px; margin-top: 5px;">${result.data.question_content}</div>
                            </div>
                            <div style="background: linear-gradient(45deg, #fff3cd, #fefefe); padding: 15px; border-radius: 10px; margin: 10px 0;">
                                <p><strong>✅ 正确答案：</strong></p>
                                <div style="background: #28a745; color: white; padding: 10px; border-radius: 5px; margin-top: 5px; font-weight: bold;">${result.data.answer}</div>
                            </div>
                            <div style="background: linear-gradient(45deg, #f8f9fa, #ffffff); padding: 15px; border-radius: 10px; margin: 10px 0;">
                                <p><strong>💡 详细解析：</strong></p>
                                <div style="background: white; padding: 10px; border-radius: 5px; margin-top: 5px; line-height: 1.6;">${result.data.explanation}</div>
                            </div>
                            <p style="text-align: center; color: #666; font-size: 14px; margin-top: 15px;">
                                ⏱️ 分析耗时：${result.data.analysis_time}秒 | 🚀 ScreenMind AI
                            </p>
                        `;
                        document.getElementById('result').classList.remove('hidden');
                    } else {
                        // 处理HTTP错误状态码
                        const errorData = await response.json();
                        const errorMsg = errorData.detail || '分析失败';
                        updateStatus('❌ 分析失败');
                        document.getElementById('result').innerHTML = `
                            <h3>❌ 分析失败</h3>
                            <p><strong>错误信息：</strong>${errorMsg}</p>
                            <p><small>状态码：${response.status}</small></p>
                        `;
                        document.getElementById('result').classList.remove('hidden');
                    }
                } catch (error) {
                    updateStatus('❌ 网络错误');
                    document.getElementById('result').innerHTML = `
                        <h3>❌ 网络错误</h3>
                        <p><strong>错误信息：</strong>${error.message}</p>
                    `;
                    document.getElementById('result').classList.remove('hidden');
                }

                document.getElementById('analyzeBtn').textContent = '🤖 开始分析';
                document.getElementById('analyzeBtn').disabled = false;
            }

            // 页面加载完成后的初始化
            document.addEventListener('DOMContentLoaded', function() {
                updateStatus('🟢 就绪');
                
                // 显示快捷键提示
                setTimeout(() => {
                    if (!selectedFile) {
                        updateStatus('⌨️ 按 Ctrl+Shift+S 截屏');
                    }
                }, 3000);
            });
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    app_logger.info("启动FastAPI服务器...")
    uvicorn.run(app, host="0.0.0.0", port=8000)