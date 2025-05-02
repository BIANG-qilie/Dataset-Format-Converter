import os
import math
import numpy as np
import shutil
import glob

def calculate_obb_parameters(points):
    """
    将四个顶点坐标转换为中心点、宽度、高度和角度
    points: 四个顶点的坐标 [(x1,y1), (x2,y2), (x3,y3), (x4,y4)]
    """
    # 将点转换为numpy数组以便计算
    points = np.array(points)
    
    # 计算中心点
    center = np.mean(points, axis=0)
    
    # 计算主方向（使用PCA）
    centered_points = points - center
    cov_matrix = np.cov(centered_points.T)
    eigenvalues, eigenvectors = np.linalg.eig(cov_matrix)
    
    # 获取主方向
    main_direction = eigenvectors[:, np.argmax(eigenvalues)]
    
    # 计算角度（弧度）
    angle = math.atan2(main_direction[1], main_direction[0])
    
    # 将点投影到主方向
    projected_points = np.dot(centered_points, main_direction)
    
    # 计算宽度和高度
    width = np.max(projected_points) - np.min(projected_points)
    height = np.max(np.dot(centered_points, eigenvectors[:, np.argmin(eigenvalues)]))
    
    # 将角度转换为度数
    angle_degrees = math.degrees(angle)
    
    return center[0], center[1], width, height, angle_degrees

def get_unique_class_ids(directory):
    """
    扫描目录中所有txt文件，获取所有唯一的类别ID
    """
    class_ids = set()
    
    # 获取目录中所有txt文件
    txt_files = glob.glob(os.path.join(directory, "*.txt"))
    
    for file_path in txt_files:
        with open(file_path, 'r') as f:
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
    
    return sorted(list(class_ids))

def create_classes_file(output_dir, class_ids):
    """
    根据类别ID和用户输入创建classes.txt文件
    """
    classes = [""] * (max(class_ids) + 1)  # 创建一个足够大的列表以容纳所有类别
    
    print("请为每个类别输入名称：")
    for class_id in class_ids:
        class_name = input(f"类别 {class_id} 的名称: ")
        classes[class_id] = class_name
    
    # 写入classes.txt文件
    classes_path = os.path.join(output_dir, "classes.txt")
    with open(classes_path, 'w') as f:
        for class_name in classes:
            f.write(f"{class_name}\n")
    
    print(f"classes.txt 文件已创建在 {classes_path}")
    return classes_path

def YOLOOBB2labelimgOBB(input_file, output_file, img_width=None, img_height=None):
    """
    将YOLOOBB格式转换为labelimgOBB格式
    YOLOOBB格式为归一化坐标（0-1之间），labelimgOBB格式为像素坐标
    """
    with open(input_file, 'r') as f:
        lines = f.readlines()
    
    converted_lines = ["YOLO_OBB\n"]  # 添加YOLO_OBB标识作为第一行
    for line in lines:
        parts = line.strip().split()
        if len(parts) < 9:  # 确保行有足够的元素
            continue
            
        class_id = parts[0]
        # 提取四个顶点的坐标
        points = []
        for i in range(4):
            x = float(parts[1 + i*2])
            y = float(parts[2 + i*2])
            
            # 如果提供了图片尺寸，且坐标是归一化的（0-1之间），则转换为像素坐标
            if img_width is not None and img_height is not None and (x <= 1.0 and y <= 1.0):
                x = x * img_width
                y = y * img_height
            
            points.append([x, y])
        
        # 计算OBB参数
        x_center, y_center, width, height, angle = calculate_obb_parameters(points)
        
        # 创建新的行
        new_line = f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f} {angle:.6f}\n"
        converted_lines.append(new_line)
    
    # 创建输出文件的目录（如果不存在）
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # 写入转换后的文件
    with open(output_file, 'w') as f:
        f.writelines(converted_lines)

def labelimgOBB2YOLOOBB(input_file, output_file, img_width=None, img_height=None):
    """
    将labelimgOBB格式转换为YOLOOBB格式
    labelimgOBB格式为像素坐标，YOLOOBB格式为归一化坐标（0-1之间）
    """
    with open(input_file, 'r') as f:
        lines = f.readlines()
    
    converted_lines = []
    # 跳过第一行的"YOLO_OBB"标识
    start_idx = 1 if lines and "YOLO_OBB" in lines[0] else 0
    
    for line in lines[start_idx:]:
        parts = line.strip().split()
        if len(parts) < 6:  # 确保行有足够的元素
            continue
            
        class_id = parts[0]
        x_center = float(parts[1])
        y_center = float(parts[2])
        width = float(parts[3])
        height = float(parts[4])
        angle_degrees = float(parts[5])
        
        # 将角度转换为弧度
        angle_rad = math.radians(angle_degrees)
        
        # 计算旋转矩阵
        cos_angle = math.cos(angle_rad)
        sin_angle = math.sin(angle_rad)
        rotation_matrix = np.array([
            [cos_angle, -sin_angle],
            [sin_angle, cos_angle]
        ])
        
        # 计算未旋转时的四个顶点坐标（按照左上、右上、右下、左下顺序）
        half_width = width / 2
        half_height = height / 2
        corners = np.array([
            [-half_width, -half_height],  # 左上
            [half_width, -half_height],   # 右上
            [half_width, half_height],    # 右下
            [-half_width, half_height]    # 左下
        ])
        
        # 应用旋转
        rotated_corners = np.dot(corners, rotation_matrix.T)
        
        # 添加中心点坐标
        rotated_corners[:, 0] += x_center
        rotated_corners[:, 1] += y_center
        
        # 如果提供了图片尺寸，将像素坐标转换为归一化坐标
        if img_width is not None and img_height is not None and (rotated_corners[:, 0].max() > 1.0 or rotated_corners[:, 1].max() > 1.0):
            rotated_corners[:, 0] /= img_width
            rotated_corners[:, 1] /= img_height
        
        # 创建新的行
        new_line = f"{class_id}"
        for i in range(4):
            new_line += f" {rotated_corners[i, 0]:.6f} {rotated_corners[i, 1]:.6f}"
        
        new_line += f"\n"
        
        converted_lines.append(new_line)
    
    # 创建输出文件的目录（如果不存在）
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # 写入转换后的文件
    with open(output_file, 'w') as f:
        f.writelines(converted_lines)

def compare_formats(input_file, output_dir, img_width=None, img_height=None):
    """
    比较原始文件和转换后的文件
    """
    # 创建临时文件
    basename = os.path.basename(input_file)
    temp_labelimg = os.path.join(output_dir, f"temp_labelimg_{basename}")
    temp_yoloobb = os.path.join(output_dir, f"temp_yoloobb_{basename}")
    comparison_file = os.path.join(output_dir, f"comparison_{basename}")
    
    # 转换到labelimgOBB格式
    YOLOOBB2labelimgOBB(input_file, temp_labelimg, img_width, img_height)
    
    # 再转换回YOLOOBB格式
    labelimgOBB2YOLOOBB(temp_labelimg, temp_yoloobb, img_width, img_height)
    
    # 比较原始文件和重新转换后的文件
    with open(input_file, 'r') as f1:
        original_lines = f1.readlines()
    
    with open(temp_yoloobb, 'r') as f2:
        converted_lines = f2.readlines()
    
    comparison_content = []
    comparison_content.append("原始YOLOOBB文件和转换后YOLOOBB文件的比较：\n")
    comparison_content.append("=" * 50 + "\n")
    
    # 获取原始文件的内容
    comparison_content.append("原始YOLOOBB文件内容：\n")
    for line in original_lines:
        comparison_content.append(line)
    
    comparison_content.append("\n" + "=" * 50 + "\n")
    
    # 获取转换到labelimgOBB的内容
    with open(temp_labelimg, 'r') as f3:
        labelimg_lines = f3.readlines()
    
    comparison_content.append("中间labelimgOBB格式文件内容：\n")
    for line in labelimg_lines:
        comparison_content.append(line)
    
    comparison_content.append("\n" + "=" * 50 + "\n")
    
    # 获取转换回YOLOOBB的内容
    comparison_content.append("转换回YOLOOBB格式文件内容：\n")
    for line in converted_lines:
        comparison_content.append(line)
    
    # 写入比较结果文件
    with open(comparison_file, 'w') as f:
        f.writelines(comparison_content)
    
    print(f"比较结果已保存到 {comparison_file}")
    
    # 返回临时文件路径，以便清理
    return temp_labelimg, temp_yoloobb

def get_valid_path(prompt, check_dir=True, is_output=False):
    """
    获取有效的文件路径
    如果是输出路径且不存在，会询问是否创建
    """
    while True:
        path = input(prompt)
        path = path.strip('"\'')  # 去除可能的引号
        
        if check_dir:
            if os.path.isdir(path):
                return path
            elif is_output:
                create = input(f"目录 '{path}' 不存在，是否创建？(y/n): ")
                if create.lower() == 'y':
                    try:
                        os.makedirs(path, exist_ok=True)
                        print(f"已创建目录 '{path}'")
                        return path
                    except Exception as e:
                        print(f"创建目录失败: {e}")
                        continue
            else:
                print(f"目录 '{path}' 不存在，请重新输入")
        else:
            dir_path = os.path.dirname(path)
            if not dir_path:  # 如果是相对路径
                return path
            
            if os.path.isdir(dir_path) or not dir_path:
                return path
            elif is_output:
                create = input(f"目录 '{dir_path}' 不存在，是否创建？(y/n): ")
                if create.lower() == 'y':
                    try:
                        os.makedirs(dir_path, exist_ok=True)
                        print(f"已创建目录 '{dir_path}'")
                        return path
                    except Exception as e:
                        print(f"创建目录失败: {e}")
                        continue
            else:
                print(f"目录 '{dir_path}' 不存在，请重新输入")

def get_positive_int(prompt):
    """
    获取正整数输入
    """
    while True:
        try:
            value = input(prompt)
            if not value:  # 允许为空
                return None
            
            int_value = int(value)
            if int_value <= 0:
                print("请输入正整数")
                continue
            
            return int_value
        except ValueError:
            print("请输入有效的整数")

def get_image_dimensions():
    """
    获取图片尺寸
    返回: (宽度, 高度)
    """
    print("\n请输入图片尺寸信息:")
    img_width = get_positive_int("图片宽度（像素）: ")
    img_height = get_positive_int("图片高度（像素）: ")
    
    if not img_width or not img_height:
        print("警告: 未提供完整的图片尺寸，将无法进行坐标转换")
        return None, None
    
    print(f"图片尺寸: {img_width}x{img_height} 像素")
    return img_width, img_height

def main():
    print("=== YOLOOBB 和 labelimgOBB 格式转换工具 ===")
    
    # 选择要执行的操作
    mode = input("选择模式: 1=YOLOOBB到labelimgOBB, 2=labelimgOBB到YOLOOBB, 3=比较转换: ")

    # 获取输入和输出路径
    if mode == "1":
        # YOLOOBB到labelimgOBB转换
        print("\n==== YOLOOBB到labelimgOBB转换 ====")
        print("说明: 此模式将YOLOOBB格式（归一化坐标）转换为labelimgOBB格式（像素坐标）")
        
        input_dir = get_valid_path("输入YOLOOBB标签目录: ", is_output=False)
        output_dir = get_valid_path("输出labelimgOBB标签目录: ", is_output=True)
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 获取图片尺寸
        print("\nYOLOOBB格式使用归一化坐标，需要转换为像素坐标")
        img_width, img_height = get_image_dimensions()
        
        # 获取所有唯一的类别ID
        class_ids = get_unique_class_ids(input_dir)
        print(f"\n在输入目录中发现以下类别ID: {class_ids}")
        
        # 创建classes.txt文件
        create_classes_file(output_dir, class_ids)
        
        # 处理所有txt文件
        print("\n开始转换文件...")
        txt_files = glob.glob(os.path.join(input_dir, "*.txt"))
        for input_path in txt_files:
            filename = os.path.basename(input_path)
            output_path = os.path.join(output_dir, filename)
            print(f"转换 {filename}...")
            YOLOOBB2labelimgOBB(input_path, output_path, img_width, img_height)
        
    elif mode == "2":
        # labelimgOBB到YOLOOBB转换
        print("\n==== labelimgOBB到YOLOOBB转换 ====")
        print("说明: 此模式将labelimgOBB格式（像素坐标）转换为YOLOOBB格式（归一化坐标）")
        
        input_dir = get_valid_path("输入labelimgOBB标签目录: ", is_output=False)
        output_dir = get_valid_path("输出YOLOOBB标签目录: ", is_output=True)
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 获取图片尺寸
        print("\nlabelimgOBB格式使用像素坐标，需要转换为归一化坐标")
        img_width, img_height = get_image_dimensions()
        
        # 处理所有txt文件
        print("\n开始转换文件...")
        txt_files = glob.glob(os.path.join(input_dir, "*.txt"))
        for input_path in txt_files:
            filename = os.path.basename(input_path)
            if filename=="classes.txt":
                continue
            output_path = os.path.join(output_dir, filename)
            
            print(f"转换 {filename}...")
            labelimgOBB2YOLOOBB(input_path, output_path, img_width, img_height)
        
    elif mode == "3":
        # 比较转换
        print("\n==== 格式转换比较 ====")
        print("说明: 此模式将YOLOOBB格式转换为labelimgOBB格式，再转回YOLOOBB格式，并比较结果")
        
        input_dir = get_valid_path("输入YOLOOBB标签目录: ", is_output=False)
        output_dir = get_valid_path("输出比较结果目录: ", is_output=True)
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 获取图片尺寸
        print("\n请输入图片尺寸以进行坐标转换")
        img_width, img_height = get_image_dimensions()
        
        # 比较转换
        print("\n开始比较转换...")
        txt_files = glob.glob(os.path.join(input_dir, "*.txt"))
        for input_path in txt_files:
            filename = os.path.basename(input_path)
            print(f"比较 {filename}...")
            compare_formats(input_path, output_dir, img_width, img_height)
    else:
        print("无效的模式选择")
        return
    
    print("\n转换完成!")
    print("=" * 50)

if __name__ == "__main__":
    main() 