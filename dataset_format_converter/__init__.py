"""
Dataset Format Converter - 多格式数据集标注转换工具

支持多种目标检测标注格式之间的相互转换：
- YOLO-HBB/YOLO
- YOLO-OBB (Ultralytics)
- LabelImg-OBB
- DOTA
- PASCAL VOC

主要功能：
- 多格式相互转换
- 统一的中间格式
- 批量处理
- 图形界面
- 命令行界面
- 多语言支持
"""

__version__ = "1.0.1"
__author__ = "Blake Zhu"
__email__ = "2112304124@mail2.gdut.edu.cn"

from .core.common_format import CommonFormat, BoundingBox
from .core.format_manager import FormatManager
from .formats.yolo_hbb import YoloHBBFormat
from .formats.yolo_obb import YoloOBBFormat
from .formats.labelimg_obb import LabelImgOBBFormat
from .formats.dota import DOTAFormat
from .formats.pascal_voc import PascalVOCFormat

__all__ = [
    'CommonFormat',
    'BoundingBox', 
    'FormatManager',
    'YoloHBBFormat',
    'YoloOBBFormat',
    'LabelImgOBBFormat',
    'DOTAFormat',
    'PascalVOCFormat'
] 