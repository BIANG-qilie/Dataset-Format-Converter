"""
命令行界面主程序
"""

import argparse
import os
import sys
from typing import List, Optional

from ..core.format_manager import format_manager
from ..i18n.translation import t, set_language, get_available_languages
from ..config.settings import get_settings, update_settings, save_settings
from .. import __version__


def load_class_names(file_path: str) -> List[str]:
    """
    从文件加载类别名称
    
    Args:
        file_path: 类别名称文件路径
        
    Returns:
        List[str]: 类别名称列表
    """
    if not os.path.exists(file_path):
        return []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 过滤空行和注释
        class_names = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                class_names.append(line)
        
        return class_names
    
    except Exception as e:
        print(f"{t('messages.error')}: {t('messages.file_not_found', file=file_path)}")
        return []


def interactive_mode():
    """交互模式"""
    print(f"\n=== {t('app.title')} ===")
    print(f"{t('app.description')}\n")
    
    # 显示支持的格式
    formats = format_manager.list_formats()
    print(f"{t('cli.input_format')}:")
    for i, fmt in enumerate(formats, 1):
        info = format_manager.get_format_info(fmt)
        print(f"  {i}. {fmt} - {info['description']}")
    
    # 选择输入格式
    while True:
        try:
            choice = input(f"\n{t('cli.input_format')} (1-{len(formats)}): ")
            if choice.lower() in ['q', 'quit', 'exit']:
                return
            
            index = int(choice) - 1
            if 0 <= index < len(formats):
                input_format = formats[index]
                break
            else:
                print(f"{t('messages.error')}: {t('messages.invalid_format', format=choice)}")
        except (ValueError, KeyboardInterrupt):
            print(f"\n{t('messages.error')}: {t('messages.invalid_format', format=choice)}")
            continue
    
    # 选择输出格式
    print(f"\n{t('cli.output_format')}:")
    for i, fmt in enumerate(formats, 1):
        info = format_manager.get_format_info(fmt)
        print(f"  {i}. {fmt} - {info['description']}")
    
    while True:
        try:
            choice = input(f"\n{t('cli.output_format')} (1-{len(formats)}): ")
            if choice.lower() in ['q', 'quit', 'exit']:
                return
            
            index = int(choice) - 1
            if 0 <= index < len(formats):
                output_format = formats[index]
                break
            else:
                print(f"{t('messages.error')}: {t('messages.invalid_format', format=choice)}")
        except (ValueError, KeyboardInterrupt):
            print(f"\n{t('messages.error')}: {t('messages.invalid_format', format=choice)}")
            continue
    
    # 输入文件/目录路径
    input_path = input(f"\n{t('cli.input')}: ").strip()
    if not input_path or not os.path.exists(input_path):
        print(f"{t('messages.error')}: {t('messages.file_not_found', file=input_path)}")
        return
    
    # 输出文件/目录路径
    output_path = input(f"{t('cli.output')}: ").strip()
    if not output_path:
        print(f"{t('messages.error')}: {t('cli.output')}")
        return
    
    # 图片尺寸
    try:
        width = int(input(f"{t('cli.width')} (1920): ") or "1920")
        height = int(input(f"{t('cli.height')} (1080): ") or "1080")
    except ValueError:
        print(f"{t('messages.error')}: {t('messages.invalid_dimensions')}")
        return
    
    # 类别名称文件（可选）
    class_names_file = input(f"{t('cli.classes')} ({t('cli.help')}): ").strip()
    class_names = None
    if class_names_file and os.path.exists(class_names_file):
        class_names = load_class_names(class_names_file)
    
    # 执行转换
    try:
        if os.path.isfile(input_path):
            print(f"\n{t('messages.processing_file', file=input_path)}")
            format_manager.convert_file(
                input_path, output_path, input_format, output_format,
                width, height, class_names
            )
        else:
            print(f"\n{t('messages.creating_output_dir', dir=output_path)}")
            format_manager.convert_directory(
                input_path, output_path, input_format, output_format,
                width, height, class_names
            )
        
        print(f"\n{t('messages.conversion_complete')}")
        
    except Exception as e:
        print(f"\n{t('messages.conversion_failed', error=str(e))}")


def main():
    """CLI主函数"""
    # 加载设置
    settings = get_settings()
    set_language(settings.language)
    
    parser = argparse.ArgumentParser(
        prog='dataset-format-converter',
        description=t('app.description'),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # 添加参数
    parser.add_argument(
        '--input', '-i',
        help=t('cli.input'),
        metavar='PATH'
    )
    
    parser.add_argument(
        '--output', '-o',
        help=t('cli.output'),
        metavar='PATH'
    )
    
    parser.add_argument(
        '--input-format', '-if',
        choices=format_manager.list_formats(),
        help=t('cli.input_format')
    )
    
    parser.add_argument(
        '--output-format', '-of',
        choices=format_manager.list_formats(),
        help=t('cli.output_format')
    )
    
    parser.add_argument(
        '--width', '-w',
        type=int,
        default=settings.last_image_width,
        help=f"{t('cli.width')} (默认: {settings.last_image_width})"
    )
    
    parser.add_argument(
        '--height',
        type=int,
        default=settings.last_image_height,
        help=f"{t('cli.height')} (默认: {settings.last_image_height})"
    )
    
    parser.add_argument(
        '--classes', '-c',
        help=t('cli.classes'),
        metavar='FILE'
    )
    
    parser.add_argument(
        '--language', '-l',
        choices=list(get_available_languages().keys()),
        help=t('gui.language')
    )
    
    parser.add_argument(
        '--version', '-v',
        action='version',
        version=f'%(prog)s {__version__}'
    )
    
    parser.add_argument(
        '--list-formats',
        action='store_true',
        help="列出所有支持的格式"
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help="显示详细信息"
    )

    # 解析参数
    args = parser.parse_args()
    
    # 设置语言
    if args.language:
        set_language(args.language)
        update_settings(language=args.language)
        save_settings()
    
    # 列出格式
    if args.list_formats:
        print(f"\n{t('cli.options')}:")
        for fmt in format_manager.list_formats():
            info = format_manager.get_format_info(fmt)
            print(f"  {fmt:<15} - {info['description']}")
        return
    
    # 如果没有提供足够的参数，进入交互模式
    if not all([args.input, args.output, args.input_format, args.output_format]):
        interactive_mode()
        return
    
    # 验证输入
    if not os.path.exists(args.input):
        print(f"{t('messages.error')}: {t('messages.file_not_found', file=args.input)}")
        sys.exit(1)
    
    if args.width <= 0 or args.height <= 0:
        print(f"{t('messages.error')}: {t('messages.invalid_dimensions')}")
        sys.exit(1)
    
    # 加载类别名称
    class_names = None
    if args.classes:
        if os.path.exists(args.classes):
            class_names = load_class_names(args.classes)
        else:
            print(f"{t('messages.warning')}: {t('messages.file_not_found', file=args.classes)}")
    
    # 执行转换
    try:
        if os.path.isfile(args.input):
            print(f"{t('messages.processing_file', file=args.input)}")
            format_manager.convert_file(
                args.input, args.output, args.input_format, args.output_format,
                args.width, args.height, class_names, args.verbose
            )
        else:
            print(f"{t('messages.creating_output_dir', dir=args.output)}")
            format_manager.convert_directory(
                args.input, args.output, args.input_format, args.output_format,
                args.width, args.height, class_names, args.verbose
            )
        
        print(f"{t('messages.conversion_complete')}")
        
        # 更新设置
        update_settings(
            last_input_format=args.input_format,
            last_output_format=args.output_format,
            last_input_path=args.input,
            last_output_path=args.output,
            last_image_width=args.width,
            last_image_height=args.height,
            last_class_names_file=args.classes or ''
        )
        save_settings()
        
    except Exception as e:
        print(f"{t('messages.conversion_failed', error=str(e))}")
        sys.exit(1)


if __name__ == '__main__':
    main() 