"""
核心转换模块

提供格式转换的核心功能
"""

from .converter import DOTA2labelimgOBB, labelimgOBB2DOTA
from .obb_utils import calculate_obb_parameters

__all__ = [
    'DOTA2labelimgOBB',
    'labelimgOBB2DOTA',
    'calculate_obb_parameters'
] 