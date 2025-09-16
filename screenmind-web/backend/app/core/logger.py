"""
日志配置模块
"""
import logging
import logging.handlers
import os
from datetime import datetime
from pathlib import Path

def setup_logger(
    name: str = "screenmind",
    log_file: str = None,
    log_level: str = "INFO",
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
    """
    配置并返回日志记录器

    Args:
        name: 日志记录器名称
        log_file: 日志文件路径，如果为None则自动生成
        log_level: 日志级别
        max_bytes: 日志文件最大大小（字节）
        backup_count: 保留的备份文件数量

    Returns:
        配置好的日志记录器
    """

    # 创建日志目录
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # 如果没有指定日志文件，则使用默认命名
    if log_file is None:
        log_file = log_dir / f"screenmind_{datetime.now().strftime('%Y%m%d')}.log"
    else:
        log_file = log_dir / log_file

    # 创建日志记录器
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))

    # 清除已有的处理器，避免重复添加
    logger.handlers.clear()

    # 创建文件处理器（支持日志轮转）
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )

    # 创建日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    file_handler.setFormatter(formatter)

    # 添加处理器到日志记录器
    logger.addHandler(file_handler)

    # 防止日志传播到根记录器（避免重复输出）
    logger.propagate = False

    return logger

def get_logger(name: str = "screenmind") -> logging.Logger:
    """
    获取已配置的日志记录器

    Args:
        name: 日志记录器名称

    Returns:
        日志记录器
    """
    return logging.getLogger(name)

# 创建默认的应用日志记录器
app_logger = setup_logger("screenmind.app")
api_logger = setup_logger("screenmind.api")
ai_logger = setup_logger("screenmind.ai")

# 禁用uvicorn的默认日志输出到控制台
def disable_uvicorn_console_logging():
    """禁用uvicorn的控制台日志输出"""
    # 获取uvicorn相关的日志记录器
    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_access_logger = logging.getLogger("uvicorn.access")
    uvicorn_error_logger = logging.getLogger("uvicorn.error")

    # 移除所有处理器
    for logger in [uvicorn_logger, uvicorn_access_logger, uvicorn_error_logger]:
        logger.handlers.clear()
        logger.propagate = False

    # 重定向到文件
    uvicorn_file_logger = setup_logger("uvicorn", "uvicorn.log")
    uvicorn_access_file_logger = setup_logger("uvicorn.access", "uvicorn_access.log")

    # 将uvicorn日志重定向到文件
    uvicorn_logger.addHandler(uvicorn_file_logger.handlers[0])
    uvicorn_access_logger.addHandler(uvicorn_access_file_logger.handlers[0])
    uvicorn_error_logger.addHandler(uvicorn_file_logger.handlers[0])