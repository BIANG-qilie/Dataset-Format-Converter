"""
格式管理器 - 管理所有支持的格式并执行转换
"""

from typing import List, Dict, Type, Optional
from .base_format import BaseFormat
from .common_format import CommonFormat
import os


class FormatManager:
    """
    格式管理器 - 集中管理所有支持的格式
    """
    
    def __init__(self):
        """初始化格式管理器"""
        self._formats: Dict[str, BaseFormat] = {}
        self._register_default_formats()
    
    def _register_default_formats(self) -> None:
        """注册默认支持的格式"""
        # 这里会在后续实现具体格式时导入并注册
        try:
            from ..formats.yolo_hbb import YoloHBBFormat
            self.register_format(YoloHBBFormat())
        except ImportError:
            pass
        
        try:
            from ..formats.yolo_obb import YoloOBBFormat
            self.register_format(YoloOBBFormat())
        except ImportError:
            pass
        
        try:
            from ..formats.labelimg_obb import LabelImgOBBFormat
            self.register_format(LabelImgOBBFormat())
        except ImportError:
            pass
        
        try:
            from ..formats.dota import DOTAFormat
            self.register_format(DOTAFormat())
        except ImportError:
            pass
        
        try:
            from ..formats.pascal_voc import PascalVOCFormat
            self.register_format(PascalVOCFormat())
        except ImportError:
            pass
    
    def register_format(self, format_instance: BaseFormat) -> None:
        """
        注册格式
        
        Args:
            format_instance: 格式实例
        """
        self._formats[format_instance.name] = format_instance
    
    def unregister_format(self, format_name: str) -> None:
        """
        注销格式
        
        Args:
            format_name: 格式名称
        """
        if format_name in self._formats:
            del self._formats[format_name]
    
    def get_format(self, format_name: str) -> BaseFormat:
        """
        获取格式实例
        
        Args:
            format_name: 格式名称
            
        Returns:
            BaseFormat: 格式实例
            
        Raises:
            ValueError: 如果格式不存在
        """
        if format_name not in self._formats:
            raise ValueError(f"Format '{format_name}' is not supported. "
                           f"Available formats: {list(self._formats.keys())}")
        return self._formats[format_name]
    
    def list_formats(self) -> List[str]:
        """
        列出所有支持的格式
        
        Returns:
            List[str]: 格式名称列表
        """
        return list(self._formats.keys())
    
    def get_format_info(self, format_name: str) -> Dict:
        """
        获取格式信息
        
        Args:
            format_name: 格式名称
            
        Returns:
            Dict: 格式信息
        """
        format_instance = self.get_format(format_name)
        return format_instance.get_format_info()
    
    def get_all_formats_info(self) -> Dict[str, Dict]:
        """
        获取所有格式的信息
        
        Returns:
            Dict: 所有格式信息
        """
        return {name: self.get_format_info(name) for name in self.list_formats()}
    
    def detect_format(self, file_path: str) -> Optional[str]:
        """
        自动检测文件格式
        
        Args:
            file_path: 文件路径
            
        Returns:
            Optional[str]: 检测到的格式名称，如果无法检测则返回None
        """
        for format_name, format_instance in self._formats.items():
            if format_instance.verify(file_path):
                return format_name
        return None
    
    def output_verbose(self, input_format: str, output_format: str, image_width: int, image_height: int, class_names: Optional[List[str]] = None) -> None:
        print(f"Input format: {input_format}")
        print(f"Output format: {output_format}")
        print(f"Image width: {image_width}")
        print(f"Image height: {image_height}")
        print(f"Class names: {class_names}")

    def convert_file(self, input_file: str, output_file: str, 
                    input_format: str, output_format: str,
                    image_width: int, image_height: int,
                    class_names: Optional[List[str]] = None, 
                    verbose: bool = False) -> None:
        """
        转换单个文件
        
        Args:
            input_file: 输入文件路径
            output_file: 输出文件路径
            input_format: 输入格式名称
            output_format: 输出格式名称
            image_width: 图片宽度
            image_height: 图片高度
            class_names: 类别名称列表（可选）
        """
        # 获取格式实例
        input_fmt = self.get_format(input_format)
        output_fmt = self.get_format(output_format)
        
        # 步骤1：输入格式 -> 中间格式
        if class_names is None:
            class_names = input_fmt._get_class_names([input_file])
        
        if verbose:
            self.output_verbose(input_format, output_format, image_width, image_height, class_names)
       
        
        common_data = input_fmt.format2commonSolo(input_file, image_width, image_height, class_names)
        
        # 步骤2：中间格式 -> 输出格式
        output_fmt.common2formatSolo(common_data, output_file)
    
    def convert_directory(self, input_dir: str, output_dir: str,
                         input_format: str, output_format: str,
                         image_width: int, image_height: int,
                         class_names: Optional[List[str]] = None,
                         verbose: bool = False) -> None:
        """
        转换整个目录
        
        Args:
            input_dir: 输入目录
            output_dir: 输出目录
            input_format: 输入格式名称
            output_format: 输出格式名称
            image_width: 图片宽度
            image_height: 图片高度
            class_names: 类别名称列表（可选）
        """
        # 获取格式实例
        input_fmt = self.get_format(input_format)
        output_fmt = self.get_format(output_format)
        # 步骤1：输入格式 -> 中间格式（批量）
        if class_names is None:
            if os.path.exists(input_dir) and os.path.isdir(input_dir):
                class_names = input_fmt._get_class_names([os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith(input_fmt.file_extension)])
            else:
                raise ValueError(f"Input directory {input_dir} is not a valid directory")
         
        if verbose:
            self.output_verbose(input_format, output_format, image_width, image_height, class_names)    
        
        common_data_list = input_fmt.format2commonMulti(input_dir, image_width, image_height, class_names)
        
        # 步骤2：中间格式 -> 输出格式（批量）
        output_fmt.common2formatMulti(common_data_list, output_dir)
    
    def is_format_supported(self, format_name: str) -> bool:
        """
        检查格式是否被支持
        
        Args:
            format_name: 格式名称
            
        Returns:
            bool: 是否支持
        """
        return format_name in self._formats


# 全局格式管理器实例
format_manager = FormatManager() 