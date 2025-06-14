"""
设置管理器 - 处理用户配置的保存和加载
"""

import os
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class Settings:
    """用户设置数据类"""
    language: str = 'en'
    last_input_format: str = 'YOLO-OBB'
    last_output_format: str = 'LabelImg-OBB'
    last_input_path: str = ''
    last_output_path: str = ''
    last_image_width: int = 1920
    last_image_height: int = 1080
    last_class_names_file: str = ''
    window_width: int = 800
    window_height: int = 600
    window_x: int = 100
    window_y: int = 100
    theme: str = 'default'
    auto_detect_format: bool = True
    remember_last_paths: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Settings':
        """从字典创建设置对象"""
        # 过滤掉不存在的字段
        valid_fields = {field.name for field in cls.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered_data)


class SettingsManager:
    """设置管理器"""
    
    def __init__(self):
        """初始化设置管理器"""
        self.settings_file = self._get_settings_file_path()
        self._settings = self._load_settings()
    
    def _get_settings_file_path(self) -> str:
        """获取设置文件路径"""
        # 获取用户主目录
        home_dir = os.path.expanduser('~')
        
        # 创建应用配置目录
        config_dir = os.path.join(home_dir, '.dataset_format_converter')
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        
        return os.path.join(config_dir, 'settings.json')
    
    def _load_settings(self) -> Settings:
        """加载设置"""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return Settings.from_dict(data)
            except Exception as e:
                print(f"警告：无法加载设置文件 {self.settings_file}: {e}")
                print("使用默认设置")
        
        # 返回默认设置
        return Settings()
    
    def save_settings(self) -> None:
        """保存设置到文件"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self._settings.to_dict(), f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"警告：无法保存设置文件 {self.settings_file}: {e}")
    
    def get_settings(self) -> Settings:
        """获取当前设置"""
        return self._settings
    
    def update_settings(self, **kwargs) -> None:
        """更新设置"""
        for key, value in kwargs.items():
            if hasattr(self._settings, key):
                setattr(self._settings, key, value)
            else:
                print(f"警告：未知的设置项 '{key}'")
    
    def reset_settings(self) -> None:
        """重置为默认设置"""
        self._settings = Settings()


# 全局设置管理器实例
_settings_manager = SettingsManager()


def get_settings() -> Settings:
    """获取当前设置"""
    return _settings_manager.get_settings()


def save_settings() -> None:
    """保存设置"""
    _settings_manager.save_settings()


def update_settings(**kwargs) -> None:
    """更新设置"""
    _settings_manager.update_settings(**kwargs)


def reset_settings() -> None:
    """重置设置"""
    _settings_manager.reset_settings() 