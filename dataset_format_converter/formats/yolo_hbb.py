"""
YOLO-HBB 格式处理类

格式说明：
- 每行格式：class_id x_center y_center width height
- 坐标为归一化值（0-1之间）
- 这是传统的YOLO水平边界框格式
"""

import os
import numpy as np
from typing import List, Optional

from ..core.base_format import BaseFormat
from ..core.common_format import CommonFormat, BoundingBox
from ..core.geometry_utils import yolo_to_corners, corners_to_yolo


class YoloHBBFormat(BaseFormat):
    """YOLO-HBB 格式处理类"""
    
    @property
    def name(self) -> str:
        return "YOLO-HBB"
    
    @property
    def file_extension(self) -> str:
        return ".txt"
    
    @property
    def description(self) -> str:
        return "YOLO-HBB format: class_id x_center y_center width height (normalized coordinates)"
    
    def verify(self, file_path: str) -> bool:
        """
        验证文件是否符合YOLO-HBB格式
        
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
                
                # 检查是否有5个部分（class_id + 4个参数）
                if len(parts) != 5:
                    return False
                
                # 检查class_id是否为整数
                try:
                    int(parts[0])
                except ValueError:
                    return False
                
                # 检查4个坐标参数是否为浮点数且在0-1范围内
                try:
                    coords = [float(x) for x in parts[1:]]
                    if not all(0 <= coord <= 1 for coord in coords):
                        return False
                except ValueError:
                    return False
            
            return True
            
        except Exception:
            return False
    
    def _format2common(self, file_path: str, image_width: int, image_height: int,
                      class_names: Optional[List[str]] = None) -> CommonFormat:
        """
        将YOLO-HBB格式转换为中间格式
        
        Args:
            file_path: 输入文件路径
            image_width: 图片宽度
            image_height: 图片高度
            class_names: 类别名称列表
            
        Returns:
            CommonFormat: 中间格式对象
        """
        if class_names is None:
            class_names = []
        
        bounding_boxes = []

        # 跳过 classes.txt
        if os.path.basename(file_path) == "classes.txt":
            return None
        
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            parts = line.split()
            if len(parts) != 5:
                continue
            
            class_id = int(parts[0])
            x_center = float(parts[1])
            y_center = float(parts[2])
            width = float(parts[3])
            height = float(parts[4])
            
            # 将YOLO格式转换为四个角点（归一化坐标）
            corners = yolo_to_corners(x_center, y_center, width, height)
            
            # 获取类别名称
            if class_id < len(class_names):
                class_name = class_names[class_id]
            else:
                class_name = f"class_{class_id}"
                # 扩展类别名称列表
                while len(class_names) <= class_id:
                    class_names.append(f"class_{len(class_names)}")
            
            # 创建边界框对象
            bbox = BoundingBox(
                class_name=class_name,
                corners=corners,
                class_id=class_id
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
        将中间格式转换为YOLO-HBB格式
        
        Args:
            common_data: 中间格式数据
            output_path: 输出文件路径
        """
        lines = []
        
        for bbox in common_data.bounding_boxes:
            # 获取类别ID
            class_id = common_data.get_class_id(bbox.class_name)
            
            # 将角点转换为YOLO格式
            x_center, y_center, width, height = corners_to_yolo(bbox.corners)
            
            # 构建输出行
            line = f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n"
            lines.append(line)
        
        # 写入文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.writelines(lines) 

    def _generate_classes_txt(self, class_names: List[str], output_path: str) -> bool:
        """
        生成classes.txt文件
        """
        try:
            if os.path.exists(output_path) and os.path.isdir(output_path):
                dir_path = output_path
            else:
                dir_path = os.path.dirname(output_path)
            with open(os.path.join(dir_path, "classes.txt"), 'w', encoding='utf-8') as f:
                for class_name in class_names:
                    f.write(class_name + "\n")
            return True
        except Exception as e:
            print(f"Error generating classes.txt file: {e}")
            return False
        
    def common2formatSolo(self, common_data: CommonFormat, output_path: str) -> None:
        """
        将中间格式转换为YOLO-HBB格式
        """
        self._generate_classes_txt(common_data.class_names, output_path)
        super().common2formatSolo(common_data, output_path)
    
    def common2formatMulti(self, common_data_list: List[CommonFormat], output_path: str) -> None:
        """
        将中间格式转换为YOLO-HBB格式
        """
        if len(common_data_list) == 0:
            raise ValueError("common_data_list is empty")
        self._generate_classes_txt(common_data_list[0].class_names, output_path)
        super().common2formatMulti(common_data_list, output_path)