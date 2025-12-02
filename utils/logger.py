"""
日志配置工具
"""
import sys
from loguru import logger
from pathlib import Path
from config.settings import TestConfig

def setup_logger():
    """
    配置loguru日志器

    Returns:
        logger: 配置好的logger实例
    """
    # 移除默认handler
    logger.remove()

    # 控制台handler - INFO级别
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level="INFO",
        colorize=True,
    )

    # 文件handler - DEBUG级别
    log_file = TestConfig.LOGS_DIR / "test_{time:YYYY-MM-DD}.log"
    logger.add(
        log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
        rotation="00:00",  # 每天轮转
        retention="7 days",  # 保留7天
        compression="zip",  # 压缩旧日志
    )

    # 错误日志单独记录
    error_log_file = TestConfig.LOGS_DIR / "error_{time:YYYY-MM-DD}.log"
    logger.add(
        error_log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="ERROR",
        rotation="00:00",
        retention="30 days",
        compression="zip",
    )

    return logger

# 创建全局logger实例
test_logger = setup_logger()
