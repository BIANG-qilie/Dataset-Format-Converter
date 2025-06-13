"""
PASCAL VOC 格式处理类

格式说明：
- XML格式文件
- 使用 <xmin>, <ymin>, <xmax>, <ymax> 标签
- 坐标为像素值
- 这是水平边界框格式（不支持旋转）
"""

import os
import xml.etree.ElementTree as ET
import numpy as np
from typing import List, Optional

from ..core.base_format import BaseFormat
from ..core.common_format import CommonFormat, BoundingBox
from ..core.geometry_utils import rect_to_corners, corners_to_rect, normalize_coordinates, denormalize_coordinates


class PascalVOCFormat(BaseFormat):
    """PASCAL VOC 格式处理类"""
    
    @property
    def name(self) -> str:
        return "PASCAL-VOC"
    
    @property
    def file_extension(self) -> str:
        return ".xml"
    
    @property
    def description(self) -> str:
        return "PASCAL VOC format: XML with <xmin>, <ymin>, <xmax>, <ymax> tags (pixel coordinates)"
    
    def verify(self, file_path: str) -> bool:
        """
        验证文件是否符合PASCAL VOC格式
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 是否符合格式
        """
        if not os.path.exists(file_path):
            return False
        
        if not file_path.endswith('.xml'):
            return False
        
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # 检查根节点是否为annotation
            if root.tag != 'annotation':
                return False
            
            # 检查是否有object节点
            objects = root.findall('object')
            
            for obj in objects:
                # 检查必需的子节点
                name = obj.find('name')
                bndbox = obj.find('bndbox')
                
                if name is None or bndbox is None:
                    return False
                
                # 检查边界框坐标
                xmin = bndbox.find('xmin')
                ymin = bndbox.find('ymin')
                xmax = bndbox.find('xmax')
                ymax = bndbox.find('ymax')
                
                if any(coord is None for coord in [xmin, ymin, xmax, ymax]):
                    return False
                
                # 检查坐标是否为数字
                try:
                    float(xmin.text)
                    float(ymin.text)
                    float(xmax.text)
                    float(ymax.text)
                except (ValueError, TypeError):
                    return False
            
            return True
            
        except ET.ParseError:
            return False
        except Exception:
            return False
    
    def _format2common(self, file_path: str, image_width: int, image_height: int,
                      class_names: Optional[List[str]] = None) -> CommonFormat:
        """
        将PASCAL VOC格式转换为中间格式
        
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
        
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        # 提取图片信息（如果XML中有的话）
        size_node = root.find('size')
        if size_node is not None:
            width_node = size_node.find('width')
            height_node = size_node.find('height')
            if width_node is not None and height_node is not None:
                try:
                    xml_width = int(width_node.text)
                    xml_height = int(height_node.text)
                    # 如果XML中的尺寸与提供的尺寸不同，使用XML中的
                    if xml_width != image_width or xml_height != image_height:
                        print(f"警告：XML中的图片尺寸 ({xml_width}x{xml_height}) 与提供的尺寸 ({image_width}x{image_height}) 不一致，使用XML中的尺寸")
                        image_width = xml_width
                        image_height = xml_height
                except ValueError:
                    pass
        
        # 处理对象
        objects = root.findall('object')
        
        for obj in objects:
            name_node = obj.find('name')
            bndbox = obj.find('bndbox')
            
            if name_node is None or bndbox is None:
                continue
            
            class_name = name_node.text
            
            # 提取边界框坐标
            xmin = float(bndbox.find('xmin').text)
            ymin = float(bndbox.find('ymin').text)
            xmax = float(bndbox.find('xmax').text)
            ymax = float(bndbox.find('ymax').text)
            
            # 转换为四个角点（像素坐标）
            pixel_corners = rect_to_corners(xmin, ymin, xmax, ymax)
            
            # 转换为归一化坐标
            normalized_corners = normalize_coordinates(pixel_corners, image_width, image_height)
            
            # 更新类别名称列表
            if class_name not in class_names:
                class_names.append(class_name)
            
            # 创建边界框对象
            bbox = BoundingBox(
                class_name=class_name,
                corners=normalized_corners,
                class_id=class_names.index(class_name)
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
        将中间格式转换为PASCAL VOC格式
        
        Args:
            common_data: 中间格式数据
            output_path: 输出文件路径
        """
        # 创建根节点
        root = ET.Element('annotation')
        
        # 添加文件名（如果有的话）
        if common_data.image_filename:
            filename = ET.SubElement(root, 'filename')
            filename.text = f"{common_data.image_filename}.jpg"  # 假设是jpg格式
        
        # 添加图片尺寸信息
        size = ET.SubElement(root, 'size')
        width = ET.SubElement(size, 'width')
        height = ET.SubElement(size, 'height')
        depth = ET.SubElement(size, 'depth')
        
        width.text = str(common_data.image_width)
        height.text = str(common_data.image_height)
        depth.text = '3'  # 假设是RGB图像
        
        # 添加分割信息
        segmented = ET.SubElement(root, 'segmented')
        segmented.text = '0'
        
        # 处理每个边界框
        for bbox in common_data.bounding_boxes:
            # 将归一化坐标转换为像素坐标
            pixel_corners = denormalize_coordinates(
                bbox.corners,
                common_data.image_width,
                common_data.image_height
            )
            
            # 转换为矩形边界框（PASCAL VOC只支持水平边界框）
            xmin, ymin, xmax, ymax = corners_to_rect(pixel_corners)
            
            # 创建object节点
            obj = ET.SubElement(root, 'object')
            
            # 添加类别名称
            name = ET.SubElement(obj, 'name')
            name.text = bbox.class_name
            
            # 添加姿态信息
            pose = ET.SubElement(obj, 'pose')
            pose.text = 'Unspecified'
            
            # 添加截断信息
            truncated = ET.SubElement(obj, 'truncated')
            truncated.text = '0'
            
            # 添加遮挡信息
            occluded = ET.SubElement(obj, 'occluded')
            occluded.text = '0'
            
            # 添加边界框
            bndbox = ET.SubElement(obj, 'bndbox')
            xmin_elem = ET.SubElement(bndbox, 'xmin')
            ymin_elem = ET.SubElement(bndbox, 'ymin')
            xmax_elem = ET.SubElement(bndbox, 'xmax')
            ymax_elem = ET.SubElement(bndbox, 'ymax')
            
            xmin_elem.text = f"{xmin:.0f}"
            ymin_elem.text = f"{ymin:.0f}"
            xmax_elem.text = f"{xmax:.0f}"
            ymax_elem.text = f"{ymax:.0f}"
            
            # 添加难度信息（如果有的话）
            difficult = ET.SubElement(obj, 'difficult')
            if bbox.difficulty is not None:
                difficult.text = str(bbox.difficulty)
            else:
                difficult.text = '0'
        
        # 写入文件
        tree = ET.ElementTree(root)
        ET.indent(tree, space="  ", level=0)  # 格式化XML
        tree.write(output_path, encoding='utf-8', xml_declaration=True) 

    def _extract_class_names_from_files(self, file_paths: List[str]) -> List[str]:
        """
        从PASCAL VOC格式文件中提取类别名称
        
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
                tree = ET.parse(file_path)
                root = tree.getroot()
                objects = root.findall('object')
                
                for obj in objects:
                    name = obj.find('name')
                    if name is not None and name.text:
                        class_names.add(name.text)
            except Exception as e:
                print(f"警告：读取文件 {file_path} 时出错: {e}")
                
        return list(class_names)
    