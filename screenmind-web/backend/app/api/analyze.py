"""
图片分析API
"""
from fastapi import APIRouter, File, UploadFile, HTTPException
from typing import Optional
import base64
import io
import time
from PIL import Image
from ..core.logger import api_logger

router = APIRouter()

# 全局变量，将从main.py中设置
question_analyzer = None

@router.post("/analyze")
async def analyze_image(
    image: UploadFile = File(...),
    model_provider: Optional[str] = None,
    model_name: Optional[str] = None
):
    """
    分析上传的图片

    Args:
        image: 上传的图片文件
        model_provider: AI模型提供商 (optional)
        model_name: 模型名称 (optional)

    Returns:
        分析结果JSON
    """
    start_time = time.time()
    api_logger.info(f"开始分析图片: {image.filename}, 大小: {image.size if hasattr(image, 'size') else 'unknown'} bytes")

    try:
        # 验证文件类型
        if not image.content_type.startswith('image/'):
            api_logger.warning(f"无效文件类型: {image.content_type}")
            raise HTTPException(status_code=400, detail="文件必须是图片格式")

        # 读取图片数据
        image_data = await image.read()
        api_logger.info(f"成功读取图片数据: {len(image_data)} bytes")

        # 验证图片大小 (限制10MB)
        if len(image_data) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="图片文件过大，请上传小于10MB的图片")

        # 验证是否为有效图片
        try:
            pil_image = Image.open(io.BytesIO(image_data))
            pil_image.verify()
        except Exception:
            raise HTTPException(status_code=400, detail="无效的图片文件")

        # 转换为base64用于AI分析
        image_base64 = base64.b64encode(image_data).decode('utf-8')

        # 使用真实的AI分析服务
        if not question_analyzer:
            api_logger.error("AI分析服务未初始化")
            raise HTTPException(status_code=500, detail="AI分析服务未初始化")

        api_logger.info("开始调用AI分析服务...")
        analysis_result = question_analyzer.analyze_question_image(image_base64)
        if not analysis_result['success']:
            # 直接返回错误，不使用模拟数据
            error_msg = analysis_result.get('error', '分析失败')
            api_logger.error(f"AI分析失败: {error_msg}")
            raise HTTPException(status_code=500, detail=error_msg)

        # 成功获得AI分析结果
        analysis_data = {
            'question_type': analysis_result['question_type'],
            'question_content': analysis_result['question_content'],
            'answer': analysis_result['answer'],
            'explanation': analysis_result['explanation']
        }

        analysis_time = round(time.time() - start_time, 2)
        api_logger.info(f"图片分析完成，耗时: {analysis_time}秒")

        return {
            "success": True,
            "data": {
                **analysis_data,
                "analysis_time": analysis_time,
                "model_used": model_name or "qwen-vl-plus",
                "image_size": len(image_data),
                "image_format": image.content_type
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(f"图片分析出现异常: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")


@router.get("/models")
async def get_available_models():
    """获取可用的AI模型列表"""
    api_logger.info("获取可用AI模型列表")
    return {
        "success": True,
        "data": {
            "gemini": {
                "name": "Google Gemini",
                "models": ["gemini-1.5-flash", "gemini-1.5-pro"],
                "requires_api_key": True
            },
            "qwen": {
                "name": "Qwen (通义千问)",
                "models": ["qwen-vl-plus", "qwen-vl-max"],
                "requires_api_key": True
            },
            "openai": {
                "name": "OpenAI GPT",
                "models": ["gpt-4o", "gpt-4o-mini"],
                "requires_api_key": True
            }
        }
    }