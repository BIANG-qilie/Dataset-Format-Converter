# Dataset Format Converter

<div align="center">

[![Python Version](https://img.shields.io/badge/python-3.6+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Multi-format dataset annotation converter with GUI and CLI support.

**📖 Language Versions / 语言版本**: [中文](README.md) | [English](README_EN.md)

[Features](#features) • [Installation](#installation) • [Usage Guide](#usage-guide) • [Project Structure](#project-structure) • [Development](#development)

</div>

## 📋 Features

- 🔄 **Multi-format Conversion**: Supports conversion between 5 mainstream annotation formats
  - YOLO-HBB (Traditional YOLO horizontal bounding boxes)
  - YOLO-OBB (Ultralytics oriented bounding boxes)
  - LabelImg-OBB (OBB format with angle information)
  - DOTA (Polygon format)
  - PASCAL VOC (XML format)

- 🖼️ **Graphical Interface**: Intuitive and user-friendly GUI
- ⌨️ **Command Line Tool**: Perfect for batch processing and automation
- 📦 **Unified Architecture**: Three-step conversion process based on intermediate format
- 🌍 **Multi-language Support**: Supports English and Simplified Chinese
- 💾 **Settings Persistence**: Automatically saves user preferences
- 🎯 **Format Validation**: Automatic detection and validation of input formats
- 📐 **Coordinate Transformation**: Smart handling of normalized and pixel coordinate conversion

## 🚀 Installation

### Install from PyPI

```bash
pip install dataset-format-converter
```

### Developer Installation
```bash
# Basic installation
pip install dataset-format-converter

# Developer installation  
pip install dataset-format-converter[dev]

# With GUI support
pip install dataset-format-converter[gui]
```

### Install from Source

```bash
git clone https://github.com/BIANG-qilie/dataset-format-converter.git
cd dataset-format-converter
pip install -e .
```

## 📖 Usage Guide

### Supported Formats

| Format                     | Structure                                         | Coordinates | Angle          | OBB Support |
| -------------------------- | ------------------------------------------------- | ----------- | -------------- | ----------- |
| **YOLO-HBB/YOLO**          | `class_id x_center y_center width height`        | Normalized  | None           | ❌ Horizontal |
| **YOLO-OBB (Ultralytics)** | `class_id x1 y1 x2 y2 x3 y3 x4 y4`               | Normalized  | None           | ✅ Polygon    |
| **LabelImg-OBB**           | `class_id x_center y_center width height angle`  | Pixel       | ✅ With angle  | ✅ RBox       |
| **DOTA**                   | `x1 y1 x2 y2 x3 y3 x4 y4 class_name [difficulty]`| Pixel       | None (implicit)| ✅ Polygon    |
| **PASCAL VOC**             | `<xmin>, <ymin>, <xmax>, <ymax>` in XML tags     | Pixel       | None           | ❌ Horizontal |

### Command Line Tool

#### Interactive Mode
```bash
dataset-format-converter
```

#### Direct Conversion
```bash
# Single file conversion
dataset-format-converter --input input.txt --output output.txt \
  --input-format YOLO-OBB --output-format LabelImg-OBB \
  --width 1920 --height 1080

# Directory batch conversion
dataset-format-converter --input ./labels --output ./converted \
  --input-format DOTA --output-format YOLO-OBB \
  --width 1920 --height 1080

# Specify class names file
dataset-format-converter --input input.txt --output output.txt \
  --input-format YOLO-OBB --output-format PASCAL-VOC \
  --width 1920 --height 1080 --classes classes.txt

# List all supported formats
dataset-format-converter --list-formats

# Set language
dataset-format-converter --language en
```

### Graphical Interface

Launch GUI:

```bash
dataset-converter-gui
```

### Python API

```python
from dataset_format_converter import format_manager

# Single file conversion
format_manager.convert_file(
    input_file='input.txt',
    output_file='output.txt', 
    input_format='YOLO-OBB',
    output_format='LabelImg-OBB',
    image_width=1920,
    image_height=1080
)

# Batch conversion
format_manager.convert_directory(
    input_dir='./labels',
    output_dir='./converted',
    input_format='DOTA', 
    output_format='YOLO-OBB',
    image_width=1920,
    image_height=1080
)

# List supported formats
formats = format_manager.list_formats()
print(formats)  # ['YOLO-HBB', 'YOLO-OBB', 'LabelImg-OBB', 'DOTA', 'PASCAL-VOC']

# Auto-detect format
detected_format = format_manager.detect_format('input.txt')
print(f"Detected format: {detected_format}")
```

## 📁 Project Structure

```
dataset_format_converter/
├── __init__.py                    # Package initialization
├── core/                          # Core functionality
│   ├── __init__.py
│   ├── common_format.py           # Intermediate format definition
│   ├── base_format.py             # Format base class
│   ├── format_manager.py          # Format manager
│   └── geometry_utils.py          # Geometry transformation tools
├── formats/                       # Format implementations
│   ├── __init__.py
│   ├── yolo_hbb.py               # YOLO-HBB format
│   ├── yolo_obb.py               # YOLO-OBB format  
│   ├── labelimg_obb.py           # LabelImg-OBB format
│   ├── dota.py                   # DOTA format
│   └── pascal_voc.py             # PASCAL VOC format
├── i18n/                          # Internationalization
│   ├── __init__.py
│   ├── translation.py            # Translation manager
│   └── locales/                  # Language files
│       ├── en.json               # English translation
│       └── zh.json               # Chinese translation
├── config/                        # Configuration management
│   ├── __init__.py
│   └── settings.py               # Settings manager
├── cli/                          # Command line interface
│   ├── __init__.py
│   └── main.py                   # CLI main program
└── gui/                          # Graphical interface
    ├── __init__.py
    └── main_window.py            # GUI main window
```

## 🛠️ Architecture Design

### Three-step Conversion Process

This tool uses a three-step conversion architecture based on intermediate format:

1. **Format Validation**: Verify if input file conforms to specified format
2. **Input Format → Intermediate Format**: Convert input format to unified intermediate format
3. **Intermediate Format → Output Format**: Convert intermediate format to target output format

### Intermediate Format

The intermediate format contains:
- Image width and height (pixels)
- Four corner coordinates (normalized, 0-1 range)
- Ordered class name list
- Other metadata (confidence, difficulty, etc.)

### Format Class Structure

Each format class inherits from `BaseFormat` and implements the following methods:

- `verify()`: Validate file format
- `_format2common()`: Format to intermediate format (private)
- `_common2format()`: Intermediate format to format (private)
- `format2commonSolo()`: Single file conversion
- `common2formatSolo()`: Single file conversion
- `format2commonMulti()`: Multi-file conversion
- `common2formatMulti()`: Multi-file conversion

## 🌍 Internationalization Support

Supports English and Simplified Chinese interfaces:

```python
from dataset_format_converter.i18n import set_language, t

# Set language
set_language('zh')  # Chinese
set_language('en')  # English

# Use translation
print(t('app.title'))  # Get app title
print(t('messages.conversion_complete'))  # Get completion message
```

## 🧪 Development Guide

### Setup Development Environment

```bash
git clone https://github.com/BIANG-qilie/dataset-format-converter.git
cd dataset-format-converter

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install development dependencies
pip install -e .[dev]
```

### Adding New Format Support

1. Create new format class in `dataset_format_converter/formats/` directory
2. Inherit from `BaseFormat` class and implement required methods
3. Import in `dataset_format_converter/formats/__init__.py`
4. Format manager will automatically register the new format

### Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage report
pytest --cov=obb_data_converter --cov-report=html
```

### Code Formatting

```bash
# Format code
black dataset_format_converter/

# Check code style
flake8 dataset_format_converter/
```

## 📄 Examples

### Class Names File Format

```text
# classes.txt
person
car
bicycle
motorcycle
truck
```

### Configuration File

User settings are automatically saved in `~/.dataset_format_converter/settings.json`:

```json
{
  "language": "en",
  "last_input_format": "YOLO-OBB", 
  "last_output_format": "LabelImg-OBB",
  "last_image_width": 1920,
  "last_image_height": 1080,
  "window_width": 800,
  "window_height": 600
}
```

## 🤝 Contributing

1. Fork this project
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Create Pull Request

## 📝 Changelog

### v1.0.0 (Current Version)
- ✨ Brand new architecture design with multi-format conversion support
- 🌍 Added internationalization support (English/Chinese)
- 💾 User settings persistence
- 🔧 Unified CLI and API interface
- 📦 Modular format support
- 🧪 Complete test coverage

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## 👨‍💻 Author

**Blake Zhu** - [GitHub](https://github.com/BIANG-qilie)

## 🙏 Acknowledgments

- Thanks to all developers who contributed code to this project
- Thanks to YOLO, LabelImg, DOTA and other projects for inspiration

---

<div align="center">

**If this project helps you, please give it a ⭐️**

</div> 