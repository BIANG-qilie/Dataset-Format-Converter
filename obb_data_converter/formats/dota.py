"""
DOTA 格式处理类

格式说明：
- 每行格式：x1 y1 x2 y2 x3 y3 x4 y4 class_name [difficulty]
- 坐标为像素值
- 四个点的坐标（顺序不定）
- 最后为类别名称，可选择性地包含难度级别
"""

import os
import numpy as np
from typing import List, Optional

from ..core.base_format import BaseFormat
from ..core.common_format import CommonFormat, BoundingBox
from ..core.geometry_utils import normalize_coordinates, denormalize_coordinates


class DOTAFormat(BaseFormat):
    """DOTA 格式处理类"""
    
    @property
    def name(self) -> str:
        return "DOTA"
    
    @property
    def file_extension(self) -> str:
        return ".txt"
    
    @property
    def description(self) -> str:
        return "DOTA format: x1 y1 x2 y2 x3 y3 x4 y4 class_name [difficulty] (pixel coordinates)"
    
    def verify(self, file_path: str) -> bool:
        """
        验证文件是否符合DOTA格式
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 是否符合格式
        """
        if not os.path.exists(file_path):
            return False
        
        if not file_path.endswith('.txt'):
            return False
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 空文件也是有效的
            if not lines:
                return True
            
            for line in lines:
                line = line.strip()
                if not line:  # 跳过空行
                    continue
                
                parts = line.split()
                
                # 检查是否至少有9个部分（8个坐标 + 类别名）
                if len(parts) < 9:
                    return False
                
                # 检查前8个是否为数字（坐标）
                try:
                    [float(x) for x in parts[:8]]
                except ValueError:
                    return False
                
                # 第9个必须是类别名（字符串）
                if not parts[8]:
                    return False
                
                # 如果有第10个，检查是否为数字（难度级别）
                if len(parts) > 9:
                    try:
                        int(parts[9])
                    except ValueError:
                        return False
            
            return True
            
        except Exception:
            return False
    
    def _format2common(self, file_path: str, image_width: int, image_height: int,
                      class_names: Optional[List[str]] = None) -> CommonFormat:
        """
        将DOTA格式转换为中间格式
        
        Args:
            file_path: 输入文件路径
            image_width: 图片宽度
            image_height: 图片高度
            class_names: 类别名称列表（将被更新）
            
        Returns:
            CommonFormat: 中间格式对象
        """
        if class_names is None:
            class_names = []
        
        bounding_boxes = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            parts = line.split()
            if len(parts) < 9:
                continue
            
            # 提取四个角点坐标（像素值）
            pixel_corners = np.array([
                [float(parts[0]), float(parts[1])],  # 第一个点
                [float(parts[2]), float(parts[3])],  # 第二个点
                [float(parts[4]), float(parts[5])],  # 第三个点
                [float(parts[6]), float(parts[7])]   # 第四个点
            ])
            
            # 转换为归一化坐标
            normalized_corners = normalize_coordinates(pixel_corners, image_width, image_height)
            
            # 提取类别名称
            class_name = parts[8]
            
            # 提取难度级别（可选）
            difficulty = None
            if len(parts) > 9:
                try:
                    difficulty = int(parts[9])
                except ValueError:
                    pass
            
            # 更新类别名称列表
            if class_name not in class_names:
                class_names.append(class_name)
            
            # 创建边界框对象
            bbox = BoundingBox(
                class_name=class_name,
                corners=normalized_corners,
                class_id=class_names.index(class_name),
                difficulty=difficulty
            )
            
            bounding_boxes.append(bbox)
        
        return CommonFormat(
            image_width=image_width,
            image_height=image_height,
            bounding_boxes=bounding_boxes,
            class_names=class_names,
            image_filename=os.path.splitext(os.path.basename(file_path))[0]
        )
    
    def _common2format(self, common_data: CommonFormat, output_path: str) -> None:
        """
        将中间格式转换为DOTA格式
        
        Args:
            common_data: 中间格式数据
            output_path: 输出文件路径
        """
        lines = []
        
        for bbox in common_data.bounding_boxes:
            # 将归一化坐标转换为像素坐标
            pixel_corners = denormalize_coordinates(
                bbox.corners,
                common_data.image_width,
                common_data.image_height
            )
            
            # 构建输出行
            line_parts = []
            
            # 添加8个坐标值
            for i in range(4):
                line_parts.extend([
                    f"{pixel_corners[i, 0]:.6f}",
                    f"{pixel_corners[i, 1]:.6f}"
                ])
            
            # 添加类别名称
            line_parts.append(bbox.class_name)
            
            # 添加难度级别（如果存在）
            if bbox.difficulty is not None:
                line_parts.append(str(bbox.difficulty))
            
            lines.append(" ".join(line_parts) + "\n")
        
        # 写入文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.writelines(lines) 

    def _extract_class_names_from_files(self, file_paths: List[str]) -> List[str]:
        """
        从DOTA格式文件中提取类别名称
        
        Args:
            file_paths: 文件路径列表
            
        Returns:
            List[str]: 类别名称列表
        """
        class_names = set()
        for file_path in file_paths:
            if not self.verify(file_path):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split()
                    if len(parts) < 9:
                        continue
                    class_name = parts[8]
                    class_names.add(class_name)
            except Exception as e:
                print(f"警告：读取文件 {file_path} 时出错: {e}")
                
        return list(class_names)