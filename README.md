# Dataset Format Converter

<div align="center">

[![Python Version](https://img.shields.io/badge/python-3.6+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

多格式数据集标注转换工具，支持图形界面和命令行操作。

Multi-format dataset annotation converter with GUI and CLI support.

**📖 语言版本 / Language Versions**: [中文](README.md) | [English](README_EN.md)

[功能特性](#功能特性) • [安装方法](#安装方法) • [使用指南](#使用指南) • [项目结构](#项目结构) • [开发指南](#开发指南)

</div>

## 📋 功能特性

- 🔄 **多格式转换**: 支持5种主流标注格式互转
  - YOLO-HBB (传统YOLO水平边界框)
  - YOLO-OBB (Ultralytics旋转边界框)
  - LabelImg-OBB (带角度的OBB格式)
  - DOTA (多边形格式)
  - PASCAL VOC (XML格式)

- 🖼️ **图形界面**: 直观易用的GUI界面
- ⌨️ **命令行工具**: 适合批量处理和自动化
- 📦 **统一架构**: 基于中间格式的三步转换流程
- 🌍 **多语言支持**: 支持英文和简体中文
- 💾 **设置记忆**: 自动保存用户偏好设置
- 🎯 **格式验证**: 自动检测和验证输入格式
- 📐 **坐标转换**: 智能处理归一化和像素坐标转换

## 🚀 安装方法

### 从PyPI安装

```bash
pip install dataset-format-converter
```

### 开发者安装
```bash
# 基本安装
pip install dataset-format-converter

# 开发者安装  
pip install dataset-format-converter[dev]

# 包含GUI支持
pip install dataset-format-converter[gui]
```

### 从源码安装

```bash
git clone https://github.com/BIANG-qilie/dataset-format-converter.git
cd dataset-format-converter
pip install -e .
```

## 📖 使用指南

### 支持的格式

| 格式                       | 形式                                              | 坐标   | 角度           | 是否支持 OBB |
| -------------------------- | ------------------------------------------------- | ------ | -------------- | ------------ |
| **YOLO-HBB/YOLO**          | `class_id x_center y_center width height`         | 归一化 | 无             | ❌ 水平框     |
| **YOLO-OBB (Ultralytics)** | `class_id x1 y1 x2 y2 x3 y3 x4 y4`                | 归一化 | 无             | ✅ 多边形框   |
| **LabelImg-OBB**           | `class_id x_center y_center width height angle`   | 像素值 | ✅ 有角度       | ✅ RBox       |
| **DOTA**                   | `x1 y1 x2 y2 x3 y3 x4 y4 class_name [difficulty]` | 像素值 | 无（隐式方向） | ✅ 多边形框   |
| **PASCAL VOC**             | `<xmin>, <ymin>, <xmax>, <ymax>` in XML tags      | 像素值 | 无             | ❌ 水平框     |

### 命令行工具

#### 交互模式
```bash
dataset-format-converter
```

#### 直接转换
```bash
# 单文件转换
dataset-format-converter --input input.txt --output output.txt \
  --input-format YOLO-OBB --output-format LabelImg-OBB \
  --width 1920 --height 1080

# 目录批量转换
dataset-format-converter --input ./labels --output ./converted \
  --input-format DOTA --output-format YOLO-OBB \
  --width 1920 --height 1080

# 指定类别名称文件
dataset-format-converter --input input.txt --output output.txt \
  --input-format YOLO-OBB --output-format PASCAL-VOC \
  --width 1920 --height 1080 --classes classes.txt

# 列出所有支持的格式
dataset-format-converter --list-formats

# 设置语言
dataset-format-converter --language zh
```

### 图形界面

启动GUI界面：

```bash
dataset-converter-gui
```

### Python API

```python
from dataset_format_converter import format_manager

# 单文件转换
format_manager.convert_file(
    input_file='input.txt',
    output_file='output.txt', 
    input_format='YOLO-OBB',
    output_format='LabelImg-OBB',
    image_width=1920,
    image_height=1080
)

# 批量转换
format_manager.convert_directory(
    input_dir='./labels',
    output_dir='./converted',
    input_format='DOTA', 
    output_format='YOLO-OBB',
    image_width=1920,
    image_height=1080
)

# 列出支持的格式
formats = format_manager.list_formats()
print(formats)  # ['YOLO-HBB', 'YOLO-OBB', 'LabelImg-OBB', 'DOTA', 'PASCAL-VOC']

# 自动检测格式
detected_format = format_manager.detect_format('input.txt')
print(f"检测到格式: {detected_format}")
```

## 📁 项目结构

```
dataset_format_converter/
├── __init__.py                    # 包初始化
├── core/                          # 核心功能
│   ├── __init__.py
│   ├── common_format.py           # 中间格式定义
│   ├── base_format.py             # 格式基类
│   ├── format_manager.py          # 格式管理器
│   └── geometry_utils.py          # 几何变换工具
├── formats/                       # 格式实现
│   ├── __init__.py
│   ├── yolo_hbb.py               # YOLO-HBB格式
│   ├── yolo_obb.py               # YOLO-OBB格式  
│   ├── labelimg_obb.py           # LabelImg-OBB格式
│   ├── dota.py                   # DOTA格式
│   └── pascal_voc.py             # PASCAL VOC格式
├── i18n/                          # 国际化
│   ├── __init__.py
│   ├── translation.py            # 翻译管理器
│   └── locales/                  # 语言文件
│       ├── en.json               # 英文翻译
│       └── zh.json               # 中文翻译
├── config/                        # 配置管理
│   ├── __init__.py
│   └── settings.py               # 设置管理器
├── cli/                          # 命令行界面
│   ├── __init__.py
│   └── main.py                   # CLI主程序
└── gui/                          # 图形界面
    ├── __init__.py
    └── main_window.py            # GUI主窗口
```

## 🛠️ 架构设计

### 三步转换流程

本工具采用基于中间格式的三步转换架构：

1. **格式验证**: 验证输入文件是否符合指定格式
2. **输入格式 → 中间格式**: 将输入格式转换为统一的中间格式
3. **中间格式 → 输出格式**: 将中间格式转换为目标输出格式

### 中间格式

中间格式包含：
- 图片宽度和高度（像素）
- 四个角点坐标（归一化，0-1范围）
- 类别名称列表（有序）
- 其他元数据（置信度、难度等）

### 格式类结构

每个格式类都继承自`BaseFormat`并实现以下方法：

- `verify()`: 验证文件格式
- `_format2common()`: 格式转中间格式（私有）
- `_common2format()`: 中间格式转格式（私有）
- `format2commonSolo()`: 单文件转换
- `common2formatSolo()`: 单文件转换
- `format2commonMulti()`: 多文件转换
- `common2formatMulti()`: 多文件转换

## 🌍 国际化支持

支持英文和简体中文界面：

```python
from dataset_format_converter.i18n import set_language, t

# 设置语言
set_language('zh')  # 中文
set_language('en')  # 英文

# 使用翻译
print(t('app.title'))  # 获取应用标题
print(t('messages.conversion_complete'))  # 获取完成消息
```

## 🧪 开发指南

### 设置开发环境

```bash
git clone https://github.com/BIANG-qilie/dataset-format-converter.git
cd dataset-format-converter

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装开发依赖
pip install -e .[dev]
```

### 添加新格式支持

1. 在`obb_data_converter/formats/`目录创建新的格式类
2. 继承`BaseFormat`类并实现必需方法
3. 在`obb_data_converter/formats/__init__.py`中导入
4. 格式管理器会自动注册新格式

### 运行测试

```bash
# 运行所有测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=obb_data_converter --cov-report=html
```

### 代码格式化

```bash
# 格式化代码
black obb_data_converter/

# 检查代码风格
flake8 obb_data_converter/
```

## 📄 示例

### 类别名称文件格式

```text
# classes.txt
person
car
bicycle
motorcycle
truck
```

### 配置文件

用户设置自动保存在`~/.dataset_format_converter/settings.json`：

```json
{
  "language": "zh",
  "last_input_format": "YOLO-OBB", 
  "last_output_format": "LabelImg-OBB",
  "last_image_width": 1920,
  "last_image_height": 1080,
  "window_width": 800,
  "window_height": 600
}
```

## 🤝 贡献指南

1. Fork本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

## 📝 更新日志

### v1.0.0 (当前版本)
- ✨ 全新架构设计，支持多格式转换
- 🌍 添加国际化支持（英文/中文）
- 💾 用户设置持久化
- 🔧 统一的CLI和API接口
- 📦 模块化格式支持
- 🧪 完整的测试覆盖

## 📄 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 👨‍💻 作者

**Blake Zhu** - [GitHub](https://github.com/BIANG-qilie)

## 🙏 致谢

- 感谢所有为本项目贡献代码的开发者
- 感谢YOLO、LabelImg、DOTA等项目的启发

---

<div align="center">

**如果这个项目对您有帮助，请给它一个⭐️**

**If this project helps you, please give it a ⭐️**

</div> 