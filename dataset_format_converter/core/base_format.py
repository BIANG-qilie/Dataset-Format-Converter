"""
基础格式抽象类 - 定义所有格式类的通用接口
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pathlib import Path
import os

from .common_format import CommonFormat


class BaseFormat(ABC):
    """
    所有格式类的基类
    
    定义了格式转换的标准接口和通用方法
    """
    
    def __init__(self):
        """初始化格式类"""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """格式名称"""
        pass
    
    @property
    @abstractmethod
    def file_extension(self) -> str:
        """文件扩展名"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """格式描述"""
        pass
    
    @abstractmethod
    def verify(self, file_path: str) -> bool:
        """
        验证文件是否符合该格式
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 是否符合格式
        """
        pass
    
    @abstractmethod
    def _format2common(self, file_path: str, image_width: int, image_height: int,
                      class_names: Optional[List[str]] = None) -> CommonFormat:
        """
        将格式文件转换为中间格式（私有方法）
        
        Args:
            file_path: 输入文件路径
            image_width: 图片宽度
            image_height: 图片高度
            class_names: 类别名称列表（可选）
            
        Returns:
            CommonFormat: 中间格式对象
        """
        pass
    
    @abstractmethod
    def _common2format(self, common_data: CommonFormat, output_path: str) -> None:
        """
        将中间格式转换为该格式文件（私有方法）
        
        Args:
            common_data: 中间格式数据
            output_path: 输出文件路径
        """
        pass
    
    def format2commonSolo(self, file_path: str, image_width: int, image_height: int,
                         class_names: Optional[List[str]] = None) -> CommonFormat:
        """
        单文件转换：格式 -> 中间格式
        
        Args:
            file_path: 输入文件路径
            image_width: 图片宽度
            image_height: 图片高度
            class_names: 类别名称列表（可选）
            
        Returns:
            CommonFormat: 中间格式对象
        """
        
        return self._format2common(file_path, image_width, image_height, class_names)
    
    def common2formatSolo(self, common_data: CommonFormat, output_path: str) -> None:
        """
        单文件转换：中间格式 -> 格式
        
        Args:
            common_data: 中间格式数据
            output_path: 输出文件路径
        """
        # 确保输出目录存在
        output_dir = os.path.dirname(output_path)
        if output_dir:  # 只有当目录不为空时才创建
            os.makedirs(output_dir, exist_ok=True)
        
        self._common2format(common_data, output_path)
    
    def format2commonMulti(self, input_dir: str, image_width: int, image_height: int,
                          class_names: Optional[List[str]] = None) -> List[CommonFormat]:
        """
        多文件转换：格式 -> 中间格式
        
        Args:
            input_dir: 输入目录
            image_width: 图片宽度
            image_height: 图片高度
            class_names: 类别名称列表（可选）
            
        Returns:
            List[CommonFormat]: 中间格式对象列表
        """
        results = []
        input_path = Path(input_dir)
        
        # 查找所有符合扩展名的文件
        pattern = f"*{self.file_extension}"
        for file_path in input_path.glob(pattern):
            try:
                common_data = self._format2common(str(file_path), image_width, image_height, class_names)
                if common_data is not None:
                    common_data.image_filename = file_path.stem  # 保存文件名（不含扩展名）
                    results.append(common_data)
            except Exception as e:
                print(f"警告：处理文件 {file_path} 时出错: {e}")
        
        return results
    
    def common2formatMulti(self, common_data_list: List[CommonFormat], output_dir: str) -> None:
        """
        多文件转换：中间格式 -> 格式
        
        Args:
            common_data_list: 中间格式数据列表
            output_dir: 输出目录
        """
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        for common_data in common_data_list:
            # 生成输出文件名
            if common_data.image_filename:
                output_filename = f"{common_data.image_filename}{self.file_extension}"
            else:
                output_filename = f"converted_{len(os.listdir(output_dir))}{self.file_extension}"
            
            output_path = os.path.join(output_dir, output_filename)
            
            try:
                self._common2format(common_data, output_path)
            except Exception as e:
                print(f"警告：生成文件 {output_path} 时出错: {e}")
    
    def _get_class_names(self, file_paths: List[str]) -> List[str]:
        """
        获取类别名称列表 - 通用实现
        
        Args:
            file_paths: 文件路径列表
            
        Returns:
            List[str]: 类别名称列表
        """
        if not file_paths:
            return []
        
        # 尝试从classes.txt文件读取（适用于YOLO系列格式）
        dir_path = os.path.dirname(file_paths[0])
        classes_file = os.path.join(dir_path, "classes.txt")
        
        if os.path.exists(classes_file) and os.path.isfile(classes_file):
            try:
                with open(classes_file, 'r', encoding='utf-8') as f:
                    class_names = [line.strip() for line in f.readlines() if line.strip()]
                    return class_names
            except Exception as e:
                print(f"警告：读取classes.txt文件失败: {e}")
        
        # 如果没有classes.txt文件，尝试从数据文件中解析
        return self._extract_class_names_from_files(file_paths)
    
    def _extract_class_names_from_files(self, file_paths: List[str]) -> List[str]:
        """
        从数据文件中提取类别名称 - 子类可重写此方法
        
        Args:
            file_paths: 文件路径列表
            
        Returns:
            List[str]: 类别名称列表
        """
        # 默认返回空列表，子类可根据需要重写
        return []
    
    def get_format_info(self) -> Dict[str, Any]:
        """
        获取格式信息
        
        Returns:
            Dict: 格式信息字典
        """
        return {
            'name': self.name,
            'file_extension': self.file_extension,
            'description': self.description
        } 