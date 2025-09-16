"""
配置文件管理
"""
import os
from pathlib import Path
from typing import Dict, Any, List

class Config:
    """应用配置管理"""

    def __init__(self):
        self.app_name = "ScreenMind"
        self.version = "0.1.0"

        # 快捷键配置
        self.hotkey = "cmd+shift+q" if os.name == "posix" else "ctrl+shift+q"

        # AI模型配置
        self.available_models = {
            "gemini": {
                "name": "Google Gemini",
                "models": ["gemini-1.5-flash", "gemini-1.5-pro"],
                "api_key_env": "GEMINI_API_KEY",
                "requires_base_url": False
            },
            "qwen": {
                "name": "Qwen (通义千问)",
                "models": ["qwen-vl-plus", "qwen-vl-max"],
                "api_key_env": "QWEN_API_KEY",
                "requires_base_url": True,
                "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1"
            },
            "openai": {
                "name": "OpenAI GPT",
                "models": ["gpt-4o", "gpt-4o-mini"],
                "api_key_env": "OPENAI_API_KEY",
                "requires_base_url": False
            }
        }

        # 当前AI配置
        self.current_provider = os.getenv("AI_PROVIDER", "qwen")
        self.current_model = os.getenv("AI_MODEL", "qwen-vl-plus")

        # API密钥
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")
        self.qwen_api_key = os.getenv("QWEN_API_KEY", "")
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")

        # 文件路径
        self.config_dir = Path.home() / ".screenmind"
        self.config_dir.mkdir(exist_ok=True)

        # 截图设置
        self.screenshot_format = "PNG"
        self.screenshot_quality = 95

        # 界面设置
        self.window_width = 450
        self.window_height = 350

    def get_current_api_key(self) -> str:
        """获取当前模型的API密钥"""
        if self.current_provider == "gemini":
            return self.gemini_api_key
        elif self.current_provider == "qwen":
            return self.qwen_api_key
        elif self.current_provider == "openai":
            return self.openai_api_key
        return ""

    def get_current_model_config(self) -> Dict[str, Any]:
        """获取当前模型配置"""
        return self.available_models.get(self.current_provider, {})

    def set_model(self, provider: str, model: str):
        """设置当前使用的模型"""
        if provider in self.available_models:
            models = self.available_models[provider]["models"]
            if model in models:
                self.current_provider = provider
                self.current_model = model
                return True
        return False

    def get_ai_prompt(self) -> str:
        """获取AI提示词"""
        return """
Please carefully analyze the question in this image. If it's a multiple choice, fill-in-the-blank, or true/false question, please:

1. First identify the question type and content
2. Carefully analyze the requirements
3. Provide the correct answer
4. Give a brief explanation

Please respond in Chinese with the following format:
题目类型：[选择题/填空题/判断题/其他]
题目内容：[question text]
正确答案：[answer]
解析：[brief explanation]

If the image is unclear or not a question, please indicate that it cannot be recognized.
"""

config = Config()