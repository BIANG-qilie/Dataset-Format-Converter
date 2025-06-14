"""
LabelImg-OBB 格式处理类

格式说明：
- 第一行：YOLO_OBB
- 每行格式：class_id x_center y_center width height angle
- 坐标为像素值
- angle为角度（度数）
"""

import os
import numpy as np
from typing import List, Optional

from ..core.base_format import BaseFormat
from ..core.common_format import CommonFormat, BoundingBox
from ..core.geometry_utils import (
    normalize_coordinates, denormalize_coordinates,
    obb_to_corners, calculate_obb_parameters
)


class LabelImgOBBFormat(BaseFormat):
    """LabelImg-OBB 格式处理类"""
    
    @property
    def name(self) -> str:
        return "LabelImg-OBB"
    
    @property
    def file_extension(self) -> str:
        return ".txt"
    
    @property
    def description(self) -> str:
        return "LabelImg-OBB format: First line 'YOLO_OBB', then class_id x_center y_center width height angle (pixel coordinates)"
    
    def verify(self, file_path: str) -> bool:
        """
        验证文件是否符合LabelImg-OBB格式
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
            
            # 空文件不是有效的LabelImg-OBB格式
            if not lines:
                return False
            
            # 检查第一行是否为"YOLO_OBB"
            first_line = lines[0].strip()
            if first_line != "YOLO_OBB":
                return False
            
            # 检查其余行
            for line in lines[1:]:
                line = line.strip()
                if not line:  # 跳过空行
                    continue
                
                parts = line.split()
                
                # 检查是否有6个部分
                if len(parts) != 6:
                    return False
                
                # 检查class_id是否为整数
                try:
                    int(parts[0])
                except ValueError:
                    return False
                
                # 检查5个参数是否为浮点数
                try:
                    [float(x) for x in parts[1:]]
                except ValueError:
                    return False
            
            return True
            
        except Exception:
            return False
    
    def _format2common(self, file_path: str, image_width: int, image_height: int,
                      class_names: Optional[List[str]] = None) -> CommonFormat:
        """
        将LabelImg-OBB格式转换为中间格式
        
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
        
        # 跳过第一行的"YOLO_OBB"标识
        for line in lines[1:]:
            line = line.strip()
            if not line:
                continue
            
            parts = line.split()
            if len(parts) != 6:
                continue
            
            class_id = int(parts[0])
            x_center = float(parts[1])
            y_center = float(parts[2])
            width = float(parts[3])
            height = float(parts[4])
            angle_degrees = float(parts[5])
            
            # 将OBB参数转换为四个角点（像素坐标）
            pixel_corners = obb_to_corners(x_center, y_center, width, height, angle_degrees)
            
            # 转换为归一化坐标
            normalized_corners = normalize_coordinates(pixel_corners, image_width, image_height)
            
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
                corners=normalized_corners,
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
        将中间格式转换为LabelImg-OBB格式
        
        Args:
            common_data: 中间格式数据
            output_path: 输出文件路径
        """
        lines = ["YOLO_OBB\n"]  # 第一行标识符
        
        for bbox in common_data.bounding_boxes:
            # 获取类别ID
            class_id = common_data.get_class_id(bbox.class_name)
            
            # 将归一化坐标转换为像素坐标
            pixel_corners = denormalize_coordinates(
                bbox.corners, 
                common_data.image_width, 
                common_data.image_height
            )
            
            # 计算OBB参数
            x_center, y_center, width, height, angle_degrees = calculate_obb_parameters(pixel_corners)
            
            # 构建输出行
            line = f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f} {angle_degrees:.6f}\n"
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
        将中间格式转换为LabelImg-OBB格式
        """
        self._generate_classes_txt(common_data.class_names, output_path)
        super().common2formatSolo(common_data, output_path)
    
    def common2formatMulti(self, common_data_list: List[CommonFormat], output_path: str) -> None:
        """
        将中间格式转换为LabelImg-OBB格式
        """
        if len(common_data_list) == 0:
            raise ValueError("common_data_list is empty")
        self._generate_classes_txt(common_data_list[0].class_names, output_path)
        super().common2formatMulti(common_data_list, output_path)