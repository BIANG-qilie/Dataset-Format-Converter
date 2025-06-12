"""
labelimgOBB2DOTA Converter - 一个用于转换DOTA和labelimgOBB格式的工具

这个包提供了用于转换不同OBB标注格式的工具，包括：
- DOTA格式（归一化坐标）
- labelimgOBB格式（像素坐标）

主要功能：
- 格式转换
- 批量处理
- 图形界面
- 命令行界面
"""

__version__ = "0.1.3"
__author__ = "Blake Zhu"
__email__ = "2112304124@mail2.gdut.edu.cn"

from .core.converter import (
    DOTA2labelimgOBB,
    labelimgOBB2DOTA
)
from .core.obb_utils import calculate_obb_parameters
from .utils.file_utils import get_unique_class_ids

__all__ = [
    'calculate_obb_parameters',
    'DOTA2labelimgOBB', 
    'labelimgOBB2DOTA',
    'get_unique_class_ids'
] 