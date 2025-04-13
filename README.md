# YOLOOBB标签转换工具

这个工具用于在不同的目标检测标签格式之间进行转换，主要支持YOLOOBB格式和labelimgOBB格式之间的互相转换。

## 功能特点

- 支持YOLOOBB格式转换为labelimgOBB格式
- 支持labelimgOBB格式转换为YOLOOBB格式
- 提供命令行界面和图形用户界面两种使用方式
- 支持批量转换整个目录中的标签文件
- 支持自定义类别名称，提供COCO和DOTA等预设类别
- 可以比较转换前后的结果，验证转换的准确性

## 安装要求

```
Python 3.6+
numpy
tkinter (Python自带，无需单独安装)
```

## 安装步骤

1. 克隆仓库：
   ```
   git clone https://github.com/yourusername/yoloobb-converter.git
   cd yoloobb-converter
   ```

2. 安装依赖：
   ```
   pip install -r requirements.txt
   ```

## 使用方法

### 图形界面模式

运行以下命令启动图形界面：

```
python convert_labels_gui.py
```

在图形界面中：
1. 选择转换模式（YOLOOBB到labelimgOBB或反向转换）
2. 设置输入目录和输出目录
3. 设置图像尺寸（如果标签是归一化坐标）
4. 点击"开始转换"按钮

### 命令行模式

运行以下命令使用命令行界面：

```
python convert_labels.py
```

按照提示输入必要的信息：
1. 选择转换模式
2. 输入源目录路径
3. 输入目标目录路径
4. 输入图像宽度和高度（如果需要）

## 转换格式说明

### YOLOOBB格式
每行格式：`class_id x1 y1 x2 y2 x3 y3 x4 y4 confidence [track_id]`
- `class_id`：类别ID
- `x1 y1, x2 y2, x3 y3, x4 y4`：四个顶点的坐标（通常是归一化坐标）
- `confidence`：置信度（可选）
- `track_id`：跟踪ID（可选）

### labelimgOBB格式
每行格式：`class_id x_center y_center width height angle`
- `class_id`：类别ID
- `x_center, y_center`：中心点坐标
- `width, height`：宽度和高度
- `angle`：旋转角度（度数）

第一行一般是 `YOLO_OBB` 标识

## 许可证

MIT

## 联系方式

如有问题或建议，请提交Issue或Pull Request。 