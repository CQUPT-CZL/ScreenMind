"""
配置管理API
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os

router = APIRouter()

class APIKeyRequest(BaseModel):
    provider: str
    api_key: str

class ModelConfigRequest(BaseModel):
    provider: str
    model: str

# 模拟配置存储 (实际应用中应该使用数据库或加密存储)
_config_store = {
    "current_provider": "qwen",
    "current_model": "qwen-vl-plus",
    "api_keys": {}  # 实际应用中应该加密存储
}

@router.get("/models")
async def get_available_models():
    """获取可用的AI模型配置"""
    return {
        "success": True,
        "data": {
            "available_models": {
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
            },
            "current_config": {
                "provider": _config_store["current_provider"],
                "model": _config_store["current_model"]
            }
        }
    }

@router.post("/api-key")
async def set_api_key(request: APIKeyRequest):
    """设置API密钥"""
    try:
        # 验证提供商是否有效
        valid_providers = ["gemini", "qwen", "openai"]
        if request.provider not in valid_providers:
            raise HTTPException(status_code=400, detail="无效的AI提供商")

        # 存储API密钥 (实际应用中应该加密)
        _config_store["api_keys"][request.provider] = request.api_key

        # 设置环境变量 (临时方案)
        env_key = {
            "gemini": "GEMINI_API_KEY",
            "qwen": "QWEN_API_KEY",
            "openai": "OPENAI_API_KEY"
        }[request.provider]

        os.environ[env_key] = request.api_key

        return {
            "success": True,
            "message": f"{request.provider} API密钥设置成功"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"设置API密钥失败: {str(e)}")

@router.post("/model")
async def set_model(request: ModelConfigRequest):
    """设置当前使用的AI模型"""
    try:
        # 获取可用模型配置
        available_models = {
            "gemini": ["gemini-1.5-flash", "gemini-1.5-pro"],
            "qwen": ["qwen-vl-plus", "qwen-vl-max"],
            "openai": ["gpt-4o", "gpt-4o-mini"]
        }

        # 验证提供商和模型
        if request.provider not in available_models:
            raise HTTPException(status_code=400, detail="无效的AI提供商")

        if request.model not in available_models[request.provider]:
            raise HTTPException(status_code=400, detail="该提供商不支持指定的模型")

        # 更新配置
        _config_store["current_provider"] = request.provider
        _config_store["current_model"] = request.model

        return {
            "success": True,
            "message": f"模型已切换到 {request.provider}:{request.model}",
            "data": {
                "provider": request.provider,
                "model": request.model
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"设置模型失败: {str(e)}")

@router.get("/settings")
async def get_settings():
    """获取当前设置"""
    return {
        "success": True,
        "data": {
            "current_provider": _config_store["current_provider"],
            "current_model": _config_store["current_model"],
            "api_keys_configured": {
                provider: bool(api_key)
                for provider, api_key in _config_store["api_keys"].items()
            },
            "app_info": {
                "name": "ScreenMind",
                "version": "1.0.0",
                "description": "智能截图答题助手 - 网页版"
            }
        }
    }

@router.delete("/api-key/{provider}")
async def remove_api_key(provider: str):
    """删除指定提供商的API密钥"""
    try:
        if provider not in ["gemini", "qwen", "openai"]:
            raise HTTPException(status_code=400, detail="无效的AI提供商")

        # 删除存储的API密钥
        if provider in _config_store["api_keys"]:
            del _config_store["api_keys"][provider]

        # 清除环境变量
        env_key = {
            "gemini": "GEMINI_API_KEY",
            "qwen": "QWEN_API_KEY",
            "openai": "OPENAI_API_KEY"
        }[provider]

        if env_key in os.environ:
            del os.environ[env_key]

        return {
            "success": True,
            "message": f"{provider} API密钥已删除"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除API密钥失败: {str(e)}")