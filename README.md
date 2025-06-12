# labelimgobb2DOTA Converter

<div align="center">

[![Python Version](https://img.shields.io/badge/python-3.6+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

一个用于转换DOTA格式和labelimgOBB格式的工具，支持图形界面和命令行操作。

[功能特性](#功能特性) • [安装方法](#安装方法) • [使用指南](#使用指南) • [项目结构](#项目结构) • [开发指南](#开发指南)

</div>

## 📋 功能特性

- 🔄 **双向转换**: 支持YOLOOBB ↔ labelimgOBB格式互转
- 🖼️ **图形界面**: 直观易用的GUI界面
- ⌨️ **命令行工具**: 适合批量处理和自动化
- 📦 **数据集生成**: 自动生成dataset.yaml和class_names.txt
- 🐍 **Python API**: 可直接在代码中调用
- ✅ **格式验证**: 确保转换结果的准确性
- 📊 **格式比较**: 转换精度验证和差异报告
- 🏷️ **类别管理**: 自动生成类别文件和数据集配置
- 📐 **坐标转换**: 支持归一化坐标和像素坐标转换
- 🎯 **预设支持**: 内置DOTA、COCO等常用数据集类别

## 🚀 安装方法

### 从PyPI安装

```bash
pip install labelimgobb2DOTA-converter
```

### 开发者安装
```bash
# 基本安装
pip install labelimgobb2DOTA-converter

# 开发者安装  
pip install labelimgobb2DOTA-converter[dev]
```

### 从源码安装

```bash
git clone https://github.com/BIANG-qilie/labelimgobb2DOTA.git
cd labelimgobb2DOTA
pip install -e .
```

## 📖 使用指南

### 图形界面

启动GUI界面：

```bash
labelimgobb2DOTA-gui
```

或者：

```python
from labelimgobb2DOTA_converter.gui import ConvertLabelsGUI
app = ConvertLabelsGUI()
app.mainloop()
```

### 命令行工具

#### 交互模式

```bash
labelimgobb2DOTA-cli
```

#### 直接转换

```bash
# YOLOOBB → labelimgOBB
labelimgobb2DOTA-cli --mode yolo2labelimg --input ./yolo_labels --output ./labelimg_labels --width 1920 --height 1080

# labelimgOBB → YOLOOBB  
labelimgobb2DOTA-cli --mode labelimg2yolo --input ./labelimg_labels --output ./yolo_labels --width 1920 --height 1080
```

### Python API

```python
from labelimgobb2DOTA_converter import (
    DOTA2labelimgOBB,
    labelimgOBB2DOTA
)

# 单文件转换
DOTA2labelimgOBB('input.txt', 'output.txt', img_width=1920, img_height=1080)

# 批量转换
import glob
for file in glob.glob('*.txt'):
    labelimgOBB2DOTA(file, f'converted_{file}', 1920, 1080)
```

## 📁 项目结构

```
labelimgobb2DOTA-converter/
├── labelimgobb2DOTA_converter/          # 主包
│   ├── __init__.py            # 包初始化
│   │   ├── __init__.py
│   │   ├── core/                  # 核心功能
│   │   │   ├── __init__.py
│   │   │   ├── converter.py       # 格式转换器
│   │   │   └── obb_utils.py       # OBB数学工具
│   │   ├── utils/                 # 工具函数
│   │   │   ├── __init__.py
│   │   │   ├── file_utils.py      # 文件处理
│   │   │   └── dataset_utils.py   # 数据集工具
│   │   ├── gui/                   # 图形界面
│   │   │   ├── __init__.py
│   │   │   ├── main_window.py     # 主窗口
│   │   │   └── dialogs.py         # 对话框
│   │   └── cli/                   # 命令行接口
│   │       ├── __init__.py
│   │       └── main.py            # CLI主程序
│   ├── tests/                     # 测试文件
│   ├── examples/                  # 示例文件
│   ├── docs/                      # 文档
│   ├── pyproject.toml            # 项目配置
│   └── README.md                 # 项目说明
```

## 🛠️ 开发指南

### 设置开发环境

```bash
git clone https://github.com/BIANG-qilie/labelimgobb2DOTA.git
cd labelimgobb2DOTA

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装开发依赖
pip install -e .[dev]

# 安装pre-commit钩子
pre-commit install
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=labelimgobb2DOTA_converter --cov-report=html

# 运行特定测试
pytest tests/test_converter.py
```

### 代码格式化

```bash
# 格式化代码
black labelimgobb2DOTA_converter/

# 检查代码风格
flake8 labelimgobb2DOTA_converter/

# 类型检查
mypy labelimgobb2DOTA_converter/
```

## 📄 文件格式说明

### DOTA格式 ( [Ultralytics 的 YOLO obb的数据格式](https://docs.ultralytics.com/tasks/obb/) )
```
class_id x1 y1 x2 y2 x3 y3 x4 y4
```
- 坐标为归一化值（0-1之间）
- (x1,y1), (x2,y2), (x3,y3), (x4,y4)为四个顶点坐标

### labelimgOBB格式
```
YOLO_OBB
class_id x_center y_center width height angle
```
- 第一行为固定标识符
- 坐标为像素值
- angle为角度（度数）

## 🤝 贡献指南

1. Fork本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

## 📝 更新日志

### v0.1.0 (当前版本)
- ✨ 重构项目架构，采用模块化设计
- 🔧 添加命令行工具支持
- 📦 支持pip安装
- 🧪 添加单元测试
- 📚 完善文档和示例
- 🎯 支持数据集配置文件生成

## 📄 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 👨‍💻 作者

**Blake Zhu** - [GitHub](https://github.com/BIANG-qilie)

## �� 致谢

- 感谢所有为本项目贡献代码的开发者
- 感谢YOLO和labelimg项目的启发

---

<div align="center">

**如果这个项目对您有帮助，请给它一个⭐️**

</div> 