"""
数据集生成工具函数

包含dataset.yaml和class_names.txt文件生成功能
"""

import os
from typing import List


def generate_dataset_yaml(output_dir: str, class_names: List[str], 
                         dataset_path: str = "./your_dataset") -> str:
    """
    生成YOLO格式的dataset.yaml文件
    
    Args:
        output_dir: 输出目录
        class_names: 类别名称列表
        dataset_path: 数据集根目录路径
        
    Returns:
        str: 生成的dataset.yaml文件路径
    """
    yaml_path = os.path.join(output_dir, "dataset.yaml")
    
    with open(yaml_path, 'w', encoding='utf-8') as f:
        f.write(f"path: {dataset_path}  # 数据集根目录\n")
        f.write("train: images/train   # 训练集路径（相对path）\n")
        f.write("val: images/val       # 验证集路径\n")
        f.write("test: images/test     # 测试集路径（可选）\n\n")
        f.write(f"nc: {len(class_names)}  # 类别数量\n")
        f.write("names: [")
        for i, name in enumerate(class_names):
            if i > 0:
                f.write(", ")
            f.write(f"'{name}'")
        f.write("]  # 类别名称\n")
    
    return yaml_path


def create_class_names_file(output_dir: str, class_names: List[str]) -> str:
    """
    创建class_names.txt文件
    
    Args:
        output_dir: 输出目录
        class_names: 类别名称列表
        
    Returns:
        str: 生成的class_names.txt文件路径
    """
    class_names_path = os.path.join(output_dir, "class_names.txt")
    
    with open(class_names_path, 'w', encoding='utf-8') as f:
        for name in class_names:
            f.write(f"{name}\n")
    
    return class_names_path


def create_training_structure(base_dir: str) -> None:
    """
    创建标准的YOLO训练目录结构
    
    Args:
        base_dir: 基础目录路径
    """
    directories = [
        "images/train",
        "images/val", 
        "images/test",
        "labels/train",
        "labels/val",
        "labels/test"
    ]
    
    for dir_path in directories:
        full_path = os.path.join(base_dir, dir_path)
        os.makedirs(full_path, exist_ok=True)
        
        # 创建.gitkeep文件以保持空目录
        gitkeep_path = os.path.join(full_path, ".gitkeep")
        if not os.path.exists(gitkeep_path):
            with open(gitkeep_path, 'w') as f:
                f.write("")


def validate_class_names(class_names: List[str]) -> bool:
    """
    验证类别名称的有效性
    
    Args:
        class_names: 类别名称列表
        
    Returns:
        bool: 是否有效
    """
    if not class_names:
        return False
    
    # 检查是否有空名称
    for name in class_names:
        if not name or not name.strip():
            return False
    
    # 检查是否有重复名称
    if len(class_names) != len(set(class_names)):
        return False
    
    return True 