"""
格式转换核心模块

提供YOLOOBB和labelimgOBB格式之间的转换功能
"""

import os
import shutil
from typing import Optional, Tuple

from .obb_utils import (
    calculate_obb_parameters, 
    obb_to_corners,
    normalize_coordinates,
    denormalize_coordinates
)


def DOTA2labelimgOBB(input_file: str, output_file: str, 
                       img_width: Optional[int] = None, 
                       img_height: Optional[int] = None) -> None:
    """
    将DOTA格式转换为labelimgOBB格式
    
    Args:
        input_file: 输入文件路径（DOTA格式）
        output_file: 输出文件路径（labelimgOBB格式）
        img_width: 图片宽度（用于坐标转换）
        img_height: 图片高度（用于坐标转换）
    """
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    converted_lines = ["YOLO_OBB\n"]  # 添加YOLO_OBB标识作为第一行
    
    for line in lines:
        parts = line.strip().split()
        if len(parts) < 9:  # 确保行有足够的元素
            continue
            
        class_id = parts[0]
        # 提取四个顶点的坐标
        points = []
        for i in range(4):
            x = float(parts[1 + i*2])
            y = float(parts[2 + i*2])
            
            # 如果提供了图片尺寸，且坐标是归一化的（0-1之间），则转换为像素坐标
            if (img_width is not None and img_height is not None and 
                x <= 1.0 and y <= 1.0):
                x = x * img_width
                y = y * img_height
            
            points.append([x, y])
        
        # 计算OBB参数
        x_center, y_center, width, height, angle = calculate_obb_parameters(points)
        
        # 创建新的行
        new_line = f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f} {angle:.6f}\n"
        converted_lines.append(new_line)
    
    # 创建输出文件的目录（如果不存在）
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # 写入转换后的文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(converted_lines)


def labelimgOBB2DOTA(input_file: str, output_file: str,
                       img_width: Optional[int] = None,
                       img_height: Optional[int] = None) -> None:
    """
    将labelimgOBB格式转换为DOTA格式
    
    Args:
        input_file: 输入文件路径（labelimgOBB格式）
        output_file: 输出文件路径（DOTA格式）
        img_width: 图片宽度（用于坐标转换）
        img_height: 图片高度（用于坐标转换）
    """
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    converted_lines = []
    # 跳过第一行的"YOLO_OBB"标识
    start_idx = 1 if lines and "YOLO_OBB" in lines[0] else 0
    
    for line in lines[start_idx:]:
        parts = line.strip().split()
        if len(parts) < 6:  # 确保行有足够的元素
            continue
            
        class_id = parts[0]
        x_center = float(parts[1])
        y_center = float(parts[2])
        width = float(parts[3])
        height = float(parts[4])
        angle_degrees = float(parts[5])
        
        # 将OBB参数转换为四个角点
        rotated_corners = obb_to_corners(x_center, y_center, width, height, angle_degrees)
        
        # 如果提供了图片尺寸，将像素坐标转换为归一化坐标
        if (img_width is not None and img_height is not None and 
            (rotated_corners[:, 0].max() > 1.0 or rotated_corners[:, 1].max() > 1.0)):
            rotated_corners = normalize_coordinates(rotated_corners, img_width, img_height)
        
        # 创建新的行
        new_line = f"{class_id}"
        for i in range(4):
            new_line += f" {rotated_corners[i, 0]:.6f} {rotated_corners[i, 1]:.6f}"
        new_line += "\n"
        
        converted_lines.append(new_line)
    
    # 创建输出文件的目录（如果不存在）
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # 写入转换后的文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(converted_lines)


 