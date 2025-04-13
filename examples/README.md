# 示例文件

本目录包含YOLOOBB转换工具的示例文件。

## 文件说明

- `sample.txt` - YOLOOBB格式的样本标签文件
- `sample_obb.txt` - labelimgOBB格式的样本标签文件

## 使用示例

1. YOLOOBB格式转labelimgOBB格式:
   ```
   python convert_labels.py
   ```
   按提示选择模式1，然后指定examples目录为输入目录，指定您想要的输出目录。

2. labelimgOBB格式转YOLOOBB格式:
   ```
   python convert_labels.py
   ```
   按提示选择模式2，然后指定examples目录为输入目录，指定您想要的输出目录。

## 示例文件说明

### YOLOOBB格式 (sample.txt)
这个文件包含两个目标检测框：
- 类别ID为0的目标，四个顶点坐标和置信度
- 类别ID为1的目标，四个顶点坐标和置信度

### labelimgOBB格式 (sample_obb.txt)
这个文件包含两个目标检测框：
- 类别ID为0的目标，中心点坐标、宽度、高度和角度
- 类别ID为1的目标，中心点坐标、宽度、高度和角度 