"""
健康检查API
"""
from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "ScreenMind API",
        "version": "1.0.0"
    }

@router.get("/status")
async def service_status():
    """服务状态检查"""
    return {
        "api": "running",
        "ai_service": "available",  # 可以添加AI服务连接检查
        "uptime": "unknown"  # 可以添加启动时间计算
    }