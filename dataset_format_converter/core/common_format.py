"""
中间格式定义 - 统一的数据结构

所有格式都将转换为这个中间格式，然后再转换为目标格式
"""

from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass
import numpy as np


@dataclass
class BoundingBox:
    """
    边界框数据结构
    
    Attributes:
        class_name: 类别名称
        class_id: 类别ID（可选）
        corners: 四个角点坐标（归一化，顺序：左上，右上，右下，左下）
        confidence: 置信度（可选）
        difficulty: 难度级别（可选，DOTA格式使用）
    """
    class_name: str
    corners: np.ndarray  # shape: (4, 2) - 四个角点的 (x, y) 坐标
    class_id: Optional[int] = None
    confidence: Optional[float] = None
    difficulty: Optional[int] = None
    
    def __post_init__(self):
        """验证数据格式"""
        if self.corners.shape != (4, 2):
            raise ValueError("corners must be a (4, 2) numpy array")
        
        # 确保坐标是归一化的 (0-1之间)，允许微小的数值误差
        tolerance = 1e-6  # 允许微小的数值误差
        if np.any(self.corners < -tolerance) or np.any(self.corners > 1 + tolerance):
            raise ValueError("All coordinates must be normalized (0-1)")
        
        # 将坐标限制在[0, 1]范围内以消除数值误差
        self.corners = np.clip(self.corners, 0.0, 1.0)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'class_name': self.class_name,
            'class_id': self.class_id,
            'corners': self.corners.tolist(),
            'confidence': self.confidence,
            'difficulty': self.difficulty
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BoundingBox':
        """从字典创建对象"""
        return cls(
            class_name=data['class_name'],
            corners=np.array(data['corners']),
            class_id=data.get('class_id'),
            confidence=data.get('confidence'),
            difficulty=data.get('difficulty')
        )


@dataclass
class CommonFormat:
    """
    中间格式数据结构
    
    Attributes:
        image_width: 图片宽度（像素）
        image_height: 图片高度（像素）
        bounding_boxes: 边界框列表
        class_names: 类别名称列表（有序）
        image_filename: 图片文件名（可选）
    """
    image_width: int
    image_height: int
    bounding_boxes: List[BoundingBox]
    class_names: List[str]
    image_filename: Optional[str] = None
    
    def __post_init__(self):
        """验证数据"""
        if self.image_width <= 0 or self.image_height <= 0:
            raise ValueError("Image dimensions must be positive")
        
        # 验证边界框中的类别名称是否在类别列表中
        for bbox in self.bounding_boxes:
            if bbox.class_name not in self.class_names:
                raise ValueError(f"Class '{bbox.class_name}' not found in class_names")
    
    def add_bounding_box(self, bbox: BoundingBox) -> None:
        """添加边界框"""
        if bbox.class_name not in self.class_names:
            self.class_names.append(bbox.class_name)
        self.bounding_boxes.append(bbox)
    
    def get_class_id(self, class_name: str) -> int:
        """获取类别ID"""
        try:
            return self.class_names.index(class_name)
        except ValueError:
            raise ValueError(f"Class '{class_name}' not found")
    
    def get_class_name(self, class_id: int) -> str:
        """获取类别名称"""
        if 0 <= class_id < len(self.class_names):
            return self.class_names[class_id]
        raise ValueError(f"Class ID {class_id} out of range")
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'image_width': self.image_width,
            'image_height': self.image_height,
            'image_filename': self.image_filename,
            'class_names': self.class_names,
            'bounding_boxes': [bbox.to_dict() for bbox in self.bounding_boxes]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CommonFormat':
        """从字典创建对象"""
        return cls(
            image_width=data['image_width'],
            image_height=data['image_height'],
            class_names=data['class_names'],
            bounding_boxes=[BoundingBox.from_dict(bbox_data) for bbox_data in data['bounding_boxes']],
            image_filename=data.get('image_filename')
        ) 