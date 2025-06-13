"""
核心模块 - 包含中间格式定义和基础功能
"""

from .common_format import CommonFormat, BoundingBox
from .format_manager import FormatManager
from .base_format import BaseFormat

__all__ = ['CommonFormat', 'BoundingBox', 'FormatManager', 'BaseFormat'] 