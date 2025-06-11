"""
OBB（Oriented Bounding Box）相关的数学计算工具

包含：
- 几何计算
- 坐标转换
- 角度计算
"""

import math
import numpy as np


def calculate_obb_parameters(points):
    """
    将四个顶点坐标转换为中心点、宽度、高度和角度
    
    Args:
        points: 四个顶点的坐标 [(x1,y1), (x2,y2), (x3,y3), (x4,y4)]
    
    Returns:
        tuple: (x_center, y_center, width, height, angle_degrees)
    """
    # 将点转换为numpy数组以便计算
    points = np.array(points)
    
    # 计算中心点
    center = np.mean(points, axis=0)
    
    # 计算主方向（使用PCA）
    centered_points = points - center
    cov_matrix = np.cov(centered_points.T)
    eigenvalues, eigenvectors = np.linalg.eig(cov_matrix)
    
    # 获取主方向
    main_direction = eigenvectors[:, np.argmax(eigenvalues)]
    
    # 计算角度（弧度）
    angle = math.atan2(main_direction[1], main_direction[0])
    
    # 将点投影到主方向
    projected_points = np.dot(centered_points, main_direction)
    
    # 计算宽度和高度
    width = np.max(projected_points) - np.min(projected_points)
    height = np.max(np.dot(centered_points, eigenvectors[:, np.argmin(eigenvalues)]))
    
    # 将角度转换为度数
    angle_degrees = math.degrees(angle)
    
    return center[0], center[1], width, height, angle_degrees


def obb_to_corners(x_center, y_center, width, height, angle_degrees):
    """
    将OBB参数转换为四个角点坐标
    
    Args:
        x_center: 中心点x坐标
        y_center: 中心点y坐标  
        width: 宽度
        height: 高度
        angle_degrees: 角度（度）
    
    Returns:
        np.ndarray: 四个角点坐标数组，形状为(4, 2)
    """
    # 将角度转换为弧度
    angle_rad = math.radians(angle_degrees)
    
    # 计算旋转矩阵
    cos_angle = math.cos(angle_rad)
    sin_angle = math.sin(angle_rad)
    rotation_matrix = np.array([
        [cos_angle, -sin_angle],
        [sin_angle, cos_angle]
    ])
    
    # 计算未旋转时的四个顶点坐标（按照左上、右上、右下、左下顺序）
    half_width = width / 2
    half_height = height / 2
    corners = np.array([
        [-half_width, -half_height],  # 左上
        [half_width, -half_height],   # 右上
        [half_width, half_height],    # 右下
        [-half_width, half_height]    # 左下
    ])
    
    # 应用旋转
    rotated_corners = np.dot(corners, rotation_matrix.T)
    
    # 添加中心点坐标
    rotated_corners[:, 0] += x_center
    rotated_corners[:, 1] += y_center
    
    return rotated_corners


def normalize_coordinates(points, img_width, img_height):
    """
    将像素坐标归一化到[0,1]范围
    
    Args:
        points: 坐标点数组
        img_width: 图片宽度
        img_height: 图片高度
    
    Returns:
        np.ndarray: 归一化后的坐标
    """
    normalized_points = points.copy()
    normalized_points[:, 0] /= img_width
    normalized_points[:, 1] /= img_height
    return normalized_points


def denormalize_coordinates(points, img_width, img_height):
    """
    将归一化坐标转换为像素坐标
    
    Args:
        points: 归一化坐标点数组
        img_width: 图片宽度
        img_height: 图片高度
    
    Returns:
        np.ndarray: 像素坐标
    """
    pixel_points = points.copy()
    pixel_points[:, 0] *= img_width
    pixel_points[:, 1] *= img_height
    return pixel_points 