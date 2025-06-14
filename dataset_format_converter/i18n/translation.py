"""
翻译管理器 - 处理多语言支持
"""

import os
import json
from typing import Dict, Any


class Translation:
    """翻译管理器"""
    
    def __init__(self):
        """初始化翻译管理器"""
        self.current_lang = 'en'
        self.translations: Dict[str, Dict[str, Any]] = {}
        self._load_translations()
    
    def _load_translations(self) -> None:
        """加载翻译文件"""
        # 获取当前文件所在目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        locales_dir = os.path.join(current_dir, 'locales')
        
        if not os.path.exists(locales_dir):
            os.makedirs(locales_dir)
            self._create_default_translations(locales_dir)
        
        # 加载所有语言文件
        for filename in os.listdir(locales_dir):
            if filename.endswith('.json'):
                lang_code = filename[:-5]  # 去掉.json扩展名
                file_path = os.path.join(locales_dir, filename)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        self.translations[lang_code] = json.load(f)
                except Exception as e:
                    print(f"警告：无法加载语言文件 {filename}: {e}")
    
    def _create_default_translations(self, locales_dir: str) -> None:
        """创建默认的翻译文件"""
        # 英文翻译
        en_translations = {
            "app": {
                        "title": "Dataset Format Converter",
        "description": "Multi-format dataset annotation converter"
            },
            "formats": {
                "yolo_hbb": "YOLO-HBB",
                "yolo_obb": "YOLO-OBB",
                "labelimg_obb": "LabelImg-OBB",
                "dota": "DOTA",
                "pascal_voc": "PASCAL VOC"
            },
            "gui": {
                "input_format": "Input Format:",
                "output_format": "Output Format:",
                "input_path": "Input Path:",
                "output_path": "Output Path:",
                "image_width": "Image Width:",
                "image_height": "Image Height:",
                "class_names": "Class Names:",
                "browse": "Browse",
                "convert": "Convert",
                "cancel": "Cancel",
                "success": "Success",
                "error": "Error",
                "warning": "Warning",
                "info": "Info",
                "file": "File",
                "directory": "Directory",
                "language": "Language",
                "settings": "Settings"
            },
            "cli": {
                "usage": "Usage",
                "options": "Options",
                "input": "Input file or directory",
                "output": "Output file or directory",
                "input_format": "Input format",
                "output_format": "Output format",
                "width": "Image width",
                "height": "Image height",
                "classes": "Class names file",
                "help": "Show this help message",
                "version": "Show version information"
            },
            "messages": {
                "conversion_complete": "Conversion completed successfully!",
                "conversion_failed": "Conversion failed: {error}",
                "file_not_found": "File not found: {file}",
                "invalid_format": "Invalid format: {format}",
                "invalid_dimensions": "Invalid image dimensions",
                "no_files_found": "No files found in directory",
                "creating_output_dir": "Creating output directory: {dir}",
                "processing_file": "Processing file: {file}",
                "skipping_file": "Skipping file: {file}"
            }
        }
        
        # 中文翻译
        zh_translations = {
            "app": {
                "title": "OBB数据格式转换器",
                "description": "多格式OBB标注转换工具"
            },
            "formats": {
                "yolo_hbb": "YOLO-HBB",
                "yolo_obb": "YOLO-OBB",
                "labelimg_obb": "LabelImg-OBB",
                "dota": "DOTA",
                "pascal_voc": "PASCAL VOC"
            },
            "gui": {
                "input_format": "输入格式：",
                "output_format": "输出格式：",
                "input_path": "输入路径：",
                "output_path": "输出路径：",
                "image_width": "图片宽度：",
                "image_height": "图片高度：",
                "class_names": "类别名称：",
                "browse": "浏览",
                "convert": "转换",
                "cancel": "取消",
                "success": "成功",
                "error": "错误",
                "warning": "警告",
                "info": "信息",
                "file": "文件",
                "directory": "目录",
                "language": "语言",
                "settings": "设置"
            },
            "cli": {
                "usage": "用法",
                "options": "选项",
                "input": "输入文件或目录",
                "output": "输出文件或目录",
                "input_format": "输入格式",
                "output_format": "输出格式",
                "width": "图片宽度",
                "height": "图片高度",
                "classes": "类别名称文件",
                "help": "显示帮助信息",
                "version": "显示版本信息"
            },
            "messages": {
                "conversion_complete": "转换成功完成！",
                "conversion_failed": "转换失败：{error}",
                "file_not_found": "文件未找到：{file}",
                "invalid_format": "无效格式：{format}",
                "invalid_dimensions": "无效的图片尺寸",
                "no_files_found": "目录中未找到文件",
                "creating_output_dir": "创建输出目录：{dir}",
                "processing_file": "处理文件：{file}",
                "skipping_file": "跳过文件：{file}"
            }
        }
        
        # 保存翻译文件
        with open(os.path.join(locales_dir, 'en.json'), 'w', encoding='utf-8') as f:
            json.dump(en_translations, f, indent=2, ensure_ascii=False)
        
        with open(os.path.join(locales_dir, 'zh.json'), 'w', encoding='utf-8') as f:
            json.dump(zh_translations, f, indent=2, ensure_ascii=False)
    
    def set_language(self, lang_code: str) -> None:
        """设置当前语言"""
        if lang_code in self.translations:
            self.current_lang = lang_code
        else:
            print(f"警告：不支持的语言代码 '{lang_code}'，使用默认语言 'en'")
            self.current_lang = 'en'
    
    def translate(self, key: str, **kwargs) -> str:
        """
        翻译文本
        
        Args:
            key: 翻译键，使用点号分隔嵌套结构，如 'gui.input_format'
            **kwargs: 格式化参数
            
        Returns:
            str: 翻译后的文本
        """
        # 获取当前语言的翻译
        current_translations = self.translations.get(self.current_lang, {})
        
        # 按点号分割键
        keys = key.split('.')
        value = current_translations
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                # 如果在当前语言中找不到，尝试使用英文
                if self.current_lang != 'en':
                    en_translations = self.translations.get('en', {})
                    value = en_translations
                    for k in keys:
                        if isinstance(value, dict) and k in value:
                            value = value[k]
                        else:
                            # 如果英文中也找不到，返回键本身
                            return key
                else:
                    return key
                break
        
        # 如果最终值不是字符串，返回键本身
        if not isinstance(value, str):
            return key
        
        # 格式化字符串
        try:
            return value.format(**kwargs)
        except (KeyError, ValueError):
            return value
    
    def get_available_languages(self) -> Dict[str, str]:
        """获取可用的语言列表"""
        return {
            'en': 'English',
            'zh': '简体中文'
        }


# 全局翻译实例
_translation = Translation()


def t(key: str, **kwargs) -> str:
    """
    翻译函数的简化接口
    
    Args:
        key: 翻译键
        **kwargs: 格式化参数
        
    Returns:
        str: 翻译后的文本
    """
    return _translation.translate(key, **kwargs)


def set_language(lang_code: str) -> None:
    """设置语言"""
    _translation.set_language(lang_code)


def get_current_language() -> str:
    """获取当前语言"""
    return _translation.current_lang


def get_available_languages() -> Dict[str, str]:
    """获取可用语言列表"""
    return _translation.get_available_languages() 