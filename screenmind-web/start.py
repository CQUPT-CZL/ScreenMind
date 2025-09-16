#!/usr/bin/env python3
"""
ScreenMind Web版本启动脚本
"""
import os
import sys
import subprocess

def check_requirements():
    """检查依赖是否已安装"""
    try:
        import fastapi
        import uvicorn
        import PIL
        print("✅ 依赖检查通过")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        return False

def check_api_keys():
    """检查API密钥配置"""
    keys_status = {
        "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY"),
        "QWEN_API_KEY": os.getenv("QWEN_API_KEY"),
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY")
    }

    configured_keys = [k for k, v in keys_status.items() if v]

    if configured_keys:
        print(f"✅ 已配置API密钥: {', '.join(configured_keys)}")
        return True
    else:
        print("⚠️  未检测到API密钥配置")
        print("请设置至少一个API密钥:")
        print("  export GEMINI_API_KEY='your-key'")
        print("  export QWEN_API_KEY='your-key'")
        print("  export OPENAI_API_KEY='your-key'")
        print("或在启动后通过设置页面配置")
        return False

def start_server():
    """启动Web服务器"""
    print("🚀 启动ScreenMind Web服务器...")

    # 切换到backend目录
    backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")

    # 启动命令
    cmd = [
        sys.executable, "-m", "uvicorn",
        "app.main:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--reload"
    ]

    try:
        # 在backend目录中启动
        subprocess.run(cmd, cwd=backend_dir)
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

def main():
    """主函数"""
    print("=" * 50)
    print("🧠 ScreenMind Web版本 - 启动器")
    print("=" * 50)

    # 检查依赖
    if not check_requirements():
        return

    # 检查API密钥
    check_api_keys()

    print("\n📝 准备启动服务器...")
    print("启动后请访问: http://localhost:8000")
    print("API文档: http://localhost:8000/docs")
    print("按 Ctrl+C 停止服务器")
    print()

    # 启动服务器
    start_server()

if __name__ == "__main__":
    main()