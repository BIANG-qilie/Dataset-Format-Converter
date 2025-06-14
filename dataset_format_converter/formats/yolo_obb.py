"""
YOLO-OBB (Ultralytics) 格式处理类

格式说明：
- 每行格式：class_id x1 y1 x2 y2 x3 y3 x4 y4
- 坐标为归一化值（0-1之间）
- (x1,y1), (x2,y2), (x3,y3), (x4,y4)为四个顶点坐标
"""

import os
import numpy as np
from typing import List, Optional

from ..core.base_format import BaseFormat
from ..core.common_format import CommonFormat, BoundingBox
from ..core.geometry_utils import normalize_coordinates, denormalize_coordinates


class YoloOBBFormat(BaseFormat):
    """YOLO-OBB (Ultralytics) 格式处理类"""
    
    @property
    def name(self) -> str:
        return "YOLO-OBB"
    
    @property
    def file_extension(self) -> str:
        return ".txt"
    
    @property
    def description(self) -> str:
        return "YOLO-OBB (Ultralytics) format: class_id x1 y1 x2 y2 x3 y3 x4 y4 (normalized coordinates)"
    
    def verify(self, file_path: str) -> bool:
        """
        验证文件是否符合YOLO-OBB格式
        
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
                
                # 检查是否有9个部分（class_id + 8个坐标）
                if len(parts) != 9:
                    return False
                
                # 检查class_id是否为整数
                try:
                    int(parts[0])
                except ValueError:
                    return False
                
                # 检查8个坐标是否为浮点数且在0-1范围内
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
        将YOLO-OBB格式转换为中间格式
        
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

        # 跳过 class_names.txt
        if os.path.basename(file_path) == "class_names.txt":
            return None
        
        # 跳过 dataset.yaml
        if os.path.basename(file_path) == "dataset.yaml":
            return None
        
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            parts = line.split()
            if len(parts) != 9:
                continue
            
            class_id = int(parts[0])
            
            # 提取四个角点坐标（已经是归一化的）
            corners = np.array([
                [float(parts[1]), float(parts[2])],  # 第一个点
                [float(parts[3]), float(parts[4])],  # 第二个点
                [float(parts[5]), float(parts[6])],  # 第三个点
                [float(parts[7]), float(parts[8])]   # 第四个点
            ])
            
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
        将中间格式转换为YOLO-OBB格式
        
        Args:
            common_data: 中间格式数据
            output_path: 输出文件路径
        """
        lines = []
        
        for bbox in common_data.bounding_boxes:
            # 获取类别ID
            class_id = common_data.get_class_id(bbox.class_name)
            
            # 角点坐标已经是归一化的
            corners = bbox.corners
            
            # 构建输出行
            line_parts = [str(class_id)]
            for i in range(4):
                line_parts.extend([
                    f"{corners[i, 0]:.6f}",
                    f"{corners[i, 1]:.6f}"
                ])
            
            lines.append(" ".join(line_parts) + "\n")
        
        # 写入文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.writelines(lines) 

    def _generate_class_names_txt(self, class_names: List[str], output_path: str) -> bool:
        """
        生成类别名称列表文件   class_names.txt
        """
        try:
            if os.path.exists(output_path) and os.path.isdir(output_path):
                dir_path = output_path
            else:
                dir_path = os.path.dirname(output_path)

            with open(os.path.join(dir_path, "class_names.txt"), 'w', encoding='utf-8') as f:
                for class_name in class_names:
                    f.write(class_name + "\n")
            return True
        except Exception as e:
            print(f"Error generating class names file: {e}")
            return False
        
    def _generate_dataset_yaml(self, class_names: List[str],  output_path: str) -> bool:
        """
        生成数据集配置文件 dataset.yaml
        """
        try:
            if os.path.exists(output_path) and os.path.isdir(output_path):
                dir_path = output_path
            else:
                dir_path = os.path.dirname(output_path)
            with open(os.path.join(dir_path, "dataset.yaml"), 'w', encoding='utf-8') as f:
                f.write(f"path: {dir_path}\n")
                f.write(f"train: train/images\n")
                f.write(f"val: val/images\n")
                f.write(f"test: test/images\n")
                f.write(f"nc: {len(class_names)}\n")
                f.write(f"""names: [{', '.join([f"'{name}'" for name in class_names])}]\n""")
            return True
        except Exception as e:
            print(f"Error generating dataset yaml file: {e}")
            return False
    
    def common2formatSolo(self, common_data: CommonFormat, output_path: str) -> None:
        """
        将中间格式转换为YOLO-OBB格式
        
        Args:
            common_data: 中间格式数据
            output_path: 输出文件路径
        """
        self._generate_class_names_txt(common_data.class_names, output_path)
        self._generate_dataset_yaml(common_data.class_names, output_path)
        super().common2formatSolo(common_data, output_path)

    def common2formatMulti(self, common_data_list: List[CommonFormat], output_path: str) -> None:
        """
        将中间格式转换为YOLO-OBB格式

        Args:
            common_data_list: 中间格式数据列表
            output_path: 输出文件路径
        """
        if len(common_data_list) == 0:
            raise ValueError("common_data_list is empty")
        self._generate_class_names_txt(common_data_list[0].class_names, output_path)
        self._generate_dataset_yaml(common_data_list[0].class_names, output_path)
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        for common_data in common_data_list:
            self._common2format(common_data, os.path.join(output_path, f"{common_data.image_filename}.txt"))
        super().common2formatMulti(common_data_list, output_path)