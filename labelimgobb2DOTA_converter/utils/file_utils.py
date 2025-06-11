"""
文件处理工具函数

包含文件读取、扫描、类别ID提取等功能
"""

import os
import glob
from typing import List, Set


def get_unique_class_ids(directory: str) -> List[int]:
    """
    扫描目录中所有txt文件，获取所有唯一的类别ID
    
    Args:
        directory: 要扫描的目录路径
        
    Returns:
        List[int]: 排序后的唯一类别ID列表
    """
    class_ids: Set[int] = set()
    
    # 获取目录中所有txt文件
    txt_files = glob.glob(os.path.join(directory, "*.txt"))
    
    for file_path in txt_files:
        # 跳过classes.txt文件
        if os.path.basename(file_path).lower() == "classes.txt":
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
                for line in lines:
                    parts = line.strip().split()
                    if not parts:
                        continue
                    
                    # 第一个值是类别ID
                    class_id = parts[0]
                    try:
                        class_id_int = int(class_id)
                        class_ids.add(class_id_int)
                    except ValueError:
                        # 如果不是整数，跳过
                        continue
        except (IOError, UnicodeDecodeError) as e:
            print(f"警告: 无法读取文件 {file_path}: {e}")
            continue
    
    return sorted(list(class_ids))


def read_classes_file(classes_file: str) -> List[str]:
    """
    读取classes.txt文件
    
    Args:
        classes_file: classes.txt文件路径
        
    Returns:
        List[str]: 类别名称列表
    """
    try:
        with open(classes_file, 'r', encoding='utf-8') as f:
            class_names = [line.strip() for line in f.readlines() if line.strip()]
        return class_names
    except (IOError, UnicodeDecodeError) as e:
        print(f"错误: 无法读取类别文件 {classes_file}: {e}")
        return []


def create_classes_file(output_dir: str, class_ids: List[int]) -> str:
    """
    根据类别ID和用户输入创建classes.txt文件
    
    Args:
        output_dir: 输出目录
        class_ids: 类别ID列表
        
    Returns:
        str: 创建的classes.txt文件路径
    """
    classes = [""] * (max(class_ids) + 1)  # 创建一个足够大的列表以容纳所有类别
    
    print("请为每个类别输入名称：")
    for class_id in class_ids:
        class_name = input(f"类别 {class_id} 的名称: ")
        classes[class_id] = class_name if class_name else f"class{class_id}"
    
    # 写入classes.txt文件
    classes_path = os.path.join(output_dir, "classes.txt")
    os.makedirs(output_dir, exist_ok=True)
    
    with open(classes_path, 'w', encoding='utf-8') as f:
        for class_name in classes:
            f.write(f"{class_name}\n")
    
    print(f"classes.txt 文件已创建在 {classes_path}")
    return classes_path


def get_txt_files(directory: str, exclude_classes: bool = True) -> List[str]:
    """
    获取目录中的所有txt文件
    
    Args:
        directory: 目录路径
        exclude_classes: 是否排除classes.txt文件
        
    Returns:
        List[str]: txt文件路径列表
    """
    txt_files = glob.glob(os.path.join(directory, "*.txt"))
    
    if exclude_classes:
        txt_files = [f for f in txt_files 
                    if os.path.basename(f).lower() != "classes.txt"]
    
    return txt_files


def ensure_directory_exists(directory: str) -> None:
    """
    确保目录存在，如果不存在则创建
    
    Args:
        directory: 目录路径
    """
    os.makedirs(directory, exist_ok=True) 