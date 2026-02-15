"""
Memory Saver - 简化版（使用内存检查点）
适用于Render部署环境
"""

import logging
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.base import BaseCheckpointSaver
from typing import Optional

logger = logging.getLogger(__name__)

_memory_saver: Optional[MemorySaver] = None


def get_memory_saver() -> BaseCheckpointSaver:
    """获取内存检查点"""
    global _memory_saver
    if _memory_saver is None:
        _memory_saver = MemorySaver()
        logger.info("MemorySaver initialized (data will not persist across restarts)")
    return _memory_saver
