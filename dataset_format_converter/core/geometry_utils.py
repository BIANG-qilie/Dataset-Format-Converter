"""
几何变换工具 - 处理OBB和坐标转换的数学运算
"""

import numpy as np
import math
from typing import Tuple, List


def normalize_coordinates(corners: np.ndarray, image_width: int, image_height: int) -> np.ndarray:
    """
    将像素坐标归一化到 [0, 1] 范围
    
    Args:
        corners: 角点坐标 (4, 2)
        image_width: 图片宽度
        image_height: 图片高度
        
    Returns:
        np.ndarray: 归一化后的坐标 (4, 2)
    """
    normalized = corners.copy()
    normalized[:, 0] = normalized[:, 0] / image_width  # x坐标
    normalized[:, 1] = normalized[:, 1] / image_height  # y坐标
    
    # 确保坐标在 [0, 1] 范围内
    normalized = np.clip(normalized, 0.0, 1.0)
    
    return normalized


def denormalize_coordinates(corners: np.ndarray, image_width: int, image_height: int) -> np.ndarray:
    """
    将归一化坐标转换为像素坐标
    
    Args:
        corners: 归一化坐标 (4, 2)
        image_width: 图片宽度
        image_height: 图片高度
        
    Returns:
        np.ndarray: 像素坐标 (4, 2)
    """
    pixels = corners.copy()
    pixels[:, 0] = pixels[:, 0] * image_width  # x坐标
    pixels[:, 1] = pixels[:, 1] * image_height  # y坐标
    
    return pixels


def calculate_obb_parameters(corners: np.ndarray) -> Tuple[float, float, float, float, float]:
    """
    从四个角点计算OBB参数（中心点、宽高、角度）
    
    Args:
        corners: 四个角点坐标 (4, 2)，顺序：左上，右上，右下，左下
        
    Returns:
        Tuple: (x_center, y_center, width, height, angle_degrees)
    """
    # 计算中心点
    center_x = np.mean(corners[:, 0])
    center_y = np.mean(corners[:, 1])
    
    # 计算宽度和高度
    # 宽度：左上到右上的距离
    width = np.linalg.norm(corners[1] - corners[0])
    # 高度：左上到左下的距离  
    height = np.linalg.norm(corners[3] - corners[0])
    
    # 计算角度（从左上到右上的向量与x轴的夹角）
    edge_vector = corners[1] - corners[0]
    angle_radians = np.arctan2(edge_vector[1], edge_vector[0])
    angle_degrees = np.degrees(angle_radians)
    
    # 确保角度在 [-90, 90] 范围内
    if angle_degrees > 90:
        angle_degrees -= 180
    elif angle_degrees < -90:
        angle_degrees += 180
    
    return center_x, center_y, width, height, angle_degrees


def obb_to_corners(center_x: float, center_y: float, width: float, height: float, 
                   angle_degrees: float) -> np.ndarray:
    """
    从OBB参数计算四个角点坐标
    
    Args:
        center_x: 中心点x坐标
        center_y: 中心点y坐标
        width: 宽度
        height: 高度
        angle_degrees: 角度（度）
        
    Returns:
        np.ndarray: 四个角点坐标 (4, 2)，顺序：左上，右上，右下，左下
    """
    # 转换为弧度
    angle_radians = np.radians(angle_degrees)
    cos_angle = np.cos(angle_radians)
    sin_angle = np.sin(angle_radians)
    
    # 在局部坐标系中的四个角点（相对于中心点）
    half_width = width / 2
    half_height = height / 2
    
    local_corners = np.array([
        [-half_width, -half_height],  # 左上
        [half_width, -half_height],   # 右上
        [half_width, half_height],    # 右下
        [-half_width, half_height]    # 左下
    ])
    
    # 旋转变换矩阵
    rotation_matrix = np.array([
        [cos_angle, -sin_angle],
        [sin_angle, cos_angle]
    ])
    
    # 应用旋转变换
    rotated_corners = local_corners @ rotation_matrix.T
    
    # 平移到实际位置
    global_corners = rotated_corners + np.array([center_x, center_y])
    
    return global_corners


def rect_to_corners(x_min: float, y_min: float, x_max: float, y_max: float) -> np.ndarray:
    """
    将矩形坐标转换为四个角点
    
    Args:
        x_min: 左上角x坐标
        y_min: 左上角y坐标
        x_max: 右下角x坐标
        y_max: 右下角y坐标
        
    Returns:
        np.ndarray: 四个角点坐标 (4, 2)
    """
    return np.array([
        [x_min, y_min],  # 左上
        [x_max, y_min],  # 右上
        [x_max, y_max],  # 右下
        [x_min, y_max]   # 左下
    ])


def corners_to_rect(corners: np.ndarray) -> Tuple[float, float, float, float]:
    """
    将角点坐标转换为轴对齐的矩形边界框
    
    Args:
        corners: 角点坐标 (4, 2)
        
    Returns:
        Tuple: (x_min, y_min, x_max, y_max)
    """
    x_min = np.min(corners[:, 0])
    y_min = np.min(corners[:, 1])
    x_max = np.max(corners[:, 0])
    y_max = np.max(corners[:, 1])
    
    return x_min, y_min, x_max, y_max


def yolo_to_corners(x_center: float, y_center: float, width: float, height: float) -> np.ndarray:
    """
    将YOLO格式（中心点+宽高）转换为四个角点
    
    Args:
        x_center: 中心点x坐标（归一化）
        y_center: 中心点y坐标（归一化）
        width: 宽度（归一化）
        height: 高度（归一化）
        
    Returns:
        np.ndarray: 四个角点坐标 (4, 2)
    """
    half_width = width / 2
    half_height = height / 2
    
    return np.array([
        [x_center - half_width, y_center - half_height],  # 左上
        [x_center + half_width, y_center - half_height],  # 右上
        [x_center + half_width, y_center + half_height],  # 右下
        [x_center - half_width, y_center + half_height]   # 左下
    ])


def corners_to_yolo(corners: np.ndarray) -> Tuple[float, float, float, float]:
    """
    将角点坐标转换为YOLO格式（中心点+宽高）
    
    Args:
        corners: 角点坐标 (4, 2)
        
    Returns:
        Tuple: (x_center, y_center, width, height)
    """
    x_min, y_min, x_max, y_max = corners_to_rect(corners)
    
    x_center = (x_min + x_max) / 2
    y_center = (y_min + y_max) / 2
    width = x_max - x_min
    height = y_max - y_min
    
    return x_center, y_center, width, height 