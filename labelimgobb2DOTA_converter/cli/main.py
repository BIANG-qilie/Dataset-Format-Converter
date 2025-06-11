"""
命令行界面主模块

提供命令行工具的主要功能
"""

import argparse
import os
import sys
from typing import Optional

from ..core.converter import DOTA2labelimgOBB, labelimgOBB2DOTA
from ..utils.file_utils import get_unique_class_ids, get_txt_files, create_classes_file
from ..utils.dataset_utils import generate_dataset_yaml, create_class_names_file


def get_valid_path(prompt: str, check_dir: bool = True, is_output: bool = False) -> str:
    """获取有效的路径"""
    while True:
        path = input(prompt).strip()
        if not path:
            print("路径不能为空，请重新输入。")
            continue
        
        if check_dir:
            if is_output:
                # 对于输出目录，尝试创建它
                try:
                    os.makedirs(path, exist_ok=True)
                    return path
                except Exception as e:
                    print(f"无法创建目录 {path}: {e}")
                    continue
            else:
                # 对于输入目录，检查是否存在
                if os.path.isdir(path):
                    return path
                else:
                    print(f"目录不存在: {path}")
                    continue
        else:
            return path


def get_positive_int(prompt: str) -> int:
    """获取正整数"""
    while True:
        try:
            value = int(input(prompt))
            if value > 0:
                return value
            else:
                print("请输入一个正整数。")
        except ValueError:
            print("请输入一个有效的整数。")


def get_image_dimensions() -> tuple[Optional[int], Optional[int]]:
    """获取图片尺寸"""
    use_dimensions = input("是否需要指定图片尺寸进行坐标转换？(y/n): ").lower().strip()
    
    if use_dimensions in ['y', 'yes', '是']:
        width = get_positive_int("请输入图片宽度（像素）: ")
        height = get_positive_int("请输入图片高度（像素）: ")
        return width, height
    else:
        return None, None


def yoloobb_to_labelimgobb_mode():
    """YOLOOBB到labelimgOBB转换模式"""
    print("\n==== YOLOOBB到labelimgOBB转换 ====")
    
    # 获取输入和输出目录
    input_dir = get_valid_path("请输入YOLOOBB标签目录路径: ", check_dir=True)
    output_dir = get_valid_path("请输入labelimgOBB标签输出目录路径: ", check_dir=True, is_output=True)
    
    # 获取图片尺寸
    img_width, img_height = get_image_dimensions()
    
    # 询问是否创建classes.txt
    create_classes = input("是否自动创建classes.txt文件？(y/n): ").lower().strip() in ['y', 'yes', '是']
    
    # 处理classes.txt文件
    if create_classes:
        class_ids = get_unique_class_ids(input_dir)
        if class_ids:
            print(f"\n在输入目录中发现以下类别ID: {class_ids}")
            create_classes_file(output_dir, class_ids)
        else:
            print("未发现任何类别ID")
    
    # 转换文件
    txt_files = get_txt_files(input_dir)
    print(f"\n开始转换 {len(txt_files)} 个文件...")
    
    for input_path in txt_files:
        filename = os.path.basename(input_path)
        output_path = os.path.join(output_dir, filename)
        print(f"转换 {filename}...")
        DOTA2labelimgOBB(input_path, output_path, img_width, img_height)
    
    print("\n转换完成!")


def labelimgobb_to_yoloobb_mode():
    """labelimgOBB到YOLOOBB转换模式"""
    print("\n==== labelimgOBB到YOLOOBB转换 ====")
    
    # 获取输入和输出目录
    input_dir = get_valid_path("请输入labelimgOBB标签目录路径: ", check_dir=True)
    output_dir = get_valid_path("请输入YOLOOBB标签输出目录路径: ", check_dir=True, is_output=True)
    
    # 获取图片尺寸
    img_width, img_height = get_image_dimensions()
    
    # 处理classes.txt文件
    classes_path = os.path.join(input_dir, "classes.txt")
    if os.path.exists(classes_path):
        print("发现classes.txt文件，正在处理...")
        
        # 读取类别名称
        with open(classes_path, 'r', encoding='utf-8') as f:
            class_names = [line.strip() for line in f.readlines() if line.strip()]
        
        if class_names:
            print(f"读取到类别文件，共{len(class_names)}个类别")
            
            # 复制classes.txt到输出目录
            import shutil
            shutil.copy(classes_path, os.path.join(output_dir, "classes.txt"))
            
            # 生成class_names.txt文件
            class_names_path = create_class_names_file(output_dir, class_names)
            print(f"已生成class_names.txt文件: {class_names_path}")
            
            # 生成dataset.yaml文件
            yaml_path = generate_dataset_yaml(output_dir, class_names)
            print(f"已生成dataset.yaml文件: {yaml_path}")
    
    # 转换文件
    txt_files = get_txt_files(input_dir)
    print(f"\n开始转换 {len(txt_files)} 个文件...")
    
    for input_path in txt_files:
        filename = os.path.basename(input_path)
        output_path = os.path.join(output_dir, filename)
        print(f"转换 {filename}...")
        labelimgOBB2DOTA(input_path, output_path, img_width, img_height)
    
    print("\n转换完成!")



def interactive_mode():
    """交互模式"""
    print("欢迎使用YOLOOBB格式转换工具！")
    print("=" * 50)
    
    while True:
        print("\n请选择操作：")
        print("1. YOLOOBB -> labelimgOBB")
        print("2. labelimgOBB -> YOLOOBB")
        print("3. 退出")
        
        choice = input("请输入选项（1-3）: ").strip()
        
        if choice == "1":
            yoloobb_to_labelimgobb_mode()
        elif choice == "2":
            labelimgobb_to_yoloobb_mode()
        elif choice == "3":
            print("感谢使用！再见！")
            break
        else:
            print("无效选项，请重新选择。")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="YOLOOBB和labelimgOBB格式转换工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
 示例用法:
   %(prog)s                                    # 交互模式
   %(prog)s --mode yolo2labelimg --input ./input --output ./output --width 1920 --height 1080
   %(prog)s --mode labelimg2yolo --input ./input --output ./output
        """
    )
    
    parser.add_argument("--mode", choices=["yolo2labelimg", "labelimg2yolo"],
                       help="转换模式")
    parser.add_argument("--input", "-i", help="输入目录路径")
    parser.add_argument("--output", "-o", help="输出目录路径")
    parser.add_argument("--width", "-w", type=int, help="图片宽度（像素）")
    parser.add_argument("--height", type=int, help="图片高度（像素）")
    parser.add_argument("--create-classes", action="store_true", 
                       help="自动创建classes.txt文件（仅对yolo2labelimg模式有效）")
    
    args = parser.parse_args()
    
    if not args.mode:
        # 如果没有指定模式，进入交互模式
        interactive_mode()
        return
    
    # 验证参数
    if not args.input or not args.output:
        print("错误: 必须指定输入和输出目录")
        sys.exit(1)
    
    if not os.path.isdir(args.input):
        print(f"错误: 输入目录不存在: {args.input}")
        sys.exit(1)
    
    # 创建输出目录
    try:
        os.makedirs(args.output, exist_ok=True)
    except Exception as e:
        print(f"错误: 无法创建输出目录: {e}")
        sys.exit(1)
    
    # 执行相应的转换
    if args.mode == "yolo2labelimg":
        print("执行YOLOOBB到labelimgOBB转换...")
        
        if args.create_classes:
            class_ids = get_unique_class_ids(args.input)
            if class_ids:
                print(f"发现类别ID: {class_ids}")
                create_classes_file(args.output, class_ids)
        
        txt_files = get_txt_files(args.input)
        for input_path in txt_files:
            filename = os.path.basename(input_path)
            output_path = os.path.join(args.output, filename)
            DOTA2labelimgOBB(input_path, output_path, args.width, args.height)
        
    elif args.mode == "labelimg2yolo":
        print("执行labelimgOBB到YOLOOBB转换...")
        
        # 处理classes.txt文件
        classes_path = os.path.join(args.input, "classes.txt")
        if os.path.exists(classes_path):
            with open(classes_path, 'r', encoding='utf-8') as f:
                class_names = [line.strip() for line in f.readlines() if line.strip()]
            
            if class_names:
                import shutil
                shutil.copy(classes_path, os.path.join(args.output, "classes.txt"))
                create_class_names_file(args.output, class_names)
                generate_dataset_yaml(args.output, class_names)
        
        txt_files = get_txt_files(args.input)
        for input_path in txt_files:
            filename = os.path.basename(input_path)
            output_path = os.path.join(args.output, filename)
            labelimgOBB2DOTA(input_path, output_path, args.width, args.height)
        

    
    print("转换完成!")


if __name__ == "__main__":
    main()