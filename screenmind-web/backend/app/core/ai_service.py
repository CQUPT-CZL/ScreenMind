"""
AI服务集成模块 - Web版本
基于原有的AI服务模块适配
"""
import google.generativeai as genai
import openai
import requests
import json
import os
from typing import Optional, Dict, Any
import base64
import io
from PIL import Image

class WebConfig:
    """Web版本的简化配置类"""

    @staticmethod
    def get_available_models():
        return {
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

    @staticmethod
    def get_ai_prompt():
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

class AIService:
    """AI服务类 - Web版本"""

    def __init__(self, provider: str = "qwen", model: str = "qwen-vl-plus"):
        self.current_provider = provider
        self.current_model = model
        self.client = None
        self.config = WebConfig()
        self._initialize_model()

    def _initialize_model(self):
        """根据当前配置初始化模型"""
        try:
            api_key = self._get_api_key()
            print(f"尝试初始化模型: {self.current_provider}:{self.current_model}")

            if not api_key:
                print(f"警告: 未设置 {self.current_provider} 的API密钥")
                return

            # 隐藏API密钥的敏感部分
            masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
            print(f"使用API密钥: {masked_key}")

            if self.current_provider == "gemini":
                self._initialize_gemini(api_key)
            elif self.current_provider == "qwen":
                self._initialize_qwen(api_key)
            elif self.current_provider == "openai":
                self._initialize_openai(api_key)
            else:
                print(f"不支持的AI提供商: {self.current_provider}")
                return

            print(f"{self.current_provider}:{self.current_model} 初始化成功")

        except Exception as e:
            print(f"模型初始化失败: {e}")
            self.client = None

    def _get_api_key(self) -> str:
        """获取当前模型的API密钥"""
        env_key = {
            "gemini": "GEMINI_API_KEY",
            "qwen": "QWEN_API_KEY",
            "openai": "OPENAI_API_KEY"
        }.get(self.current_provider, "")

        return os.getenv(env_key, "")

    def _initialize_gemini(self, api_key: str):
        """初始化Gemini模型"""
        genai.configure(api_key=api_key)
        self.client = genai.GenerativeModel(self.current_model)

    def _initialize_qwen(self, api_key: str):
        """初始化Qwen模型"""
        available_models = self.config.get_available_models()
        model_config = available_models["qwen"]
        self.client = openai.OpenAI(
            api_key=api_key,
            base_url=model_config.get("base_url")
        )

    def _initialize_openai(self, api_key: str):
        """初始化OpenAI模型"""
        self.client = openai.OpenAI(api_key=api_key)

    def set_model(self, provider: str, model: str, api_key: str = None):
        """设置模型并重新初始化"""
        available_models = self.config.get_available_models()

        if provider not in available_models:
            return False

        if model not in available_models[provider]["models"]:
            return False

        self.current_provider = provider
        self.current_model = model

        # 更新环境变量中的API密钥
        if api_key:
            env_key = available_models[provider]["api_key_env"]
            os.environ[env_key] = api_key

        self._initialize_model()
        return True

    def analyze_image(self, image_base64: str) -> Optional[str]:
        """
        分析图片并返回AI回答

        Args:
            image_base64: base64编码的图片数据

        Returns:
            AI分析结果文本，失败返回None
        """
        if not self.client:
            error_msg = f"错误: AI模型未初始化，请检查API密钥设置 (当前提供商: {self.current_provider})"
            print(error_msg)
            return error_msg

        try:
            prompt = self.config.get_ai_prompt()
            print(f"开始分析图片，使用模型: {self.current_provider}:{self.current_model}")

            if self.current_provider == "gemini":
                return self._analyze_with_gemini(image_base64, prompt)
            elif self.current_provider in ["qwen", "openai"]:
                return self._analyze_with_openai_compatible(image_base64, prompt)
            else:
                error_msg = f"错误: 不支持的AI提供商: {self.current_provider}"
                print(error_msg)
                return error_msg

        except Exception as e:
            error_msg = self._handle_error(e)
            print(f"AI分析异常: {error_msg}")
            return error_msg

    def _analyze_with_gemini(self, image_base64: str, prompt: str) -> str:
        """使用Gemini分析图片"""
        image_data = base64.b64decode(image_base64)
        image = Image.open(io.BytesIO(image_data))

        response = self.client.generate_content([prompt, image])

        if response and response.text:
            return response.text.strip()
        else:
            return "错误: AI未返回有效响应"

    def _analyze_with_openai_compatible(self, image_base64: str, prompt: str) -> str:
        """使用OpenAI兼容API分析图片"""
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_base64}"
                        }
                    }
                ]
            }
        ]

        response = self.client.chat.completions.create(
            model=self.current_model,
            messages=messages,
            max_tokens=1000
        )

        if response.choices and response.choices[0].message.content:
            return response.choices[0].message.content.strip()
        else:
            return "错误: AI未返回有效响应"

    def _handle_error(self, error: Exception) -> str:
        """处理错误信息"""
        error_msg = str(error)
        if "API_KEY" in error_msg or "Unauthorized" in error_msg:
            return f"错误: API密钥无效，请检查API密钥设置"
        elif "quota" in error_msg.lower() or "rate" in error_msg.lower():
            return "错误: API配额已用完或调用频率过高，请稍后再试"
        elif "timeout" in error_msg.lower():
            return "错误: 请求超时，请检查网络连接"
        else:
            return f"错误: AI分析失败 - {error_msg}"

    def test_connection(self) -> bool:
        """
        测试AI服务连接

        Returns:
            bool: 连接是否正常
        """
        if not self.client:
            return False

        try:
            # 创建一个小的测试图片
            test_image = Image.new('RGB', (100, 100), color='white')
            buffer = io.BytesIO()
            test_image.save(buffer, format='PNG')
            test_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

            # 测试API调用
            test_prompt = "请简单描述这张图片"

            if self.current_provider == "gemini":
                response = self.client.generate_content([test_prompt, test_image])
                return response and response.text is not None
            else:
                messages = [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": test_prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/png;base64,{test_base64}"}
                            }
                        ]
                    }
                ]
                response = self.client.chat.completions.create(
                    model=self.current_model,
                    messages=messages,
                    max_tokens=100
                )
                return response.choices and response.choices[0].message.content

        except Exception as e:
            print(f"AI服务连接测试失败: {e}")
            return False

    def get_current_model_info(self) -> Dict[str, str]:
        """获取当前模型信息"""
        available_models = self.config.get_available_models()
        model_config = available_models.get(self.current_provider, {})
        return {
            "provider": self.current_provider,
            "model": self.current_model,
            "name": model_config.get("name", "未知模型")
        }

class QuestionAnalyzer:
    """题目分析器 - Web版本"""

    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service

    def analyze_question_image(self, image_base64: str) -> Dict[str, Any]:
        """
        分析题目图片

        Args:
            image_base64: base64编码的图片

        Returns:
            分析结果字典，包含题目类型、内容、答案等
        """
        result = {
            'success': False,
            'question_type': '未知',
            'question_content': '',
            'answer': '',
            'explanation': '',
            'raw_response': '',
            'error': None
        }

        try:
            # 调用AI分析
            print(f"QuestionAnalyzer开始调用AI服务...")
            ai_response = self.ai_service.analyze_image(image_base64)

            if not ai_response:
                result['error'] = "AI未返回响应"
                print("AI服务未返回任何响应")
                return result

            # 检查是否是错误消息
            if ai_response.startswith("错误:"):
                result['error'] = ai_response
                print(f"AI服务返回错误: {ai_response}")
                return result

            result['raw_response'] = ai_response
            print(f"AI服务响应成功，长度: {len(ai_response)} 字符")

            # 解析AI响应
            parsed_result = self._parse_ai_response(ai_response)
            result.update(parsed_result)
            result['success'] = True

        except Exception as e:
            result['error'] = f"分析失败: {str(e)}"
            print(f"QuestionAnalyzer异常: {str(e)}")

        return result

    def _parse_ai_response(self, response: str) -> Dict[str, str]:
        """
        解析AI响应文本

        Args:
            response: AI原始响应

        Returns:
            解析后的结构化数据
        """
        parsed = {
            'question_type': '未知',
            'question_content': '',
            'answer': '',
            'explanation': ''
        }

        try:
            lines = response.split('\n')
            current_field = None

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # 识别字段标识
                if line.startswith('题目类型：') or line.startswith('题目类型:'):
                    parsed['question_type'] = line.split('：', 1)[-1].split(':', 1)[-1].strip()
                elif line.startswith('题目内容：') or line.startswith('题目内容:'):
                    parsed['question_content'] = line.split('：', 1)[-1].split(':', 1)[-1].strip()
                    current_field = 'question_content'
                elif line.startswith('正确答案：') or line.startswith('正确答案:') or line.startswith('答案：') or line.startswith('答案:'):
                    parsed['answer'] = line.split('：', 1)[-1].split(':', 1)[-1].strip()
                    current_field = 'answer'
                elif line.startswith('解析：') or line.startswith('解析:') or line.startswith('说明：') or line.startswith('说明:'):
                    parsed['explanation'] = line.split('：', 1)[-1].split(':', 1)[-1].strip()
                    current_field = 'explanation'
                else:
                    # 继续添加到当前字段
                    if current_field and line:
                        if parsed[current_field]:
                            parsed[current_field] += '\n' + line
                        else:
                            parsed[current_field] = line

            # 如果解析失败，将整个响应作为答案
            if not any(parsed.values()):
                parsed['answer'] = response
                parsed['question_type'] = '未识别'

        except Exception as e:
            print(f"解析AI响应失败: {e}")
            parsed['answer'] = response
            parsed['question_type'] = '解析失败'

        return parsed