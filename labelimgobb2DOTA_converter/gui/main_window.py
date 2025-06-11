"""
GUI主窗口模块

YOLOOBB和labelimgOBB格式转换工具的图形界面
"""

import os
import glob
import shutil
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from functools import partial

# 导入核心功能模块
from ..core.converter import DOTA2labelimgOBB, labelimgOBB2DOTA
from ..utils.file_utils import get_unique_class_ids
from ..utils.dataset_utils import generate_dataset_yaml, create_class_names_file
from .dialogs import ClassesInputDialog, RedirectText


class ConvertLabelsGUI(tk.Tk):
    """YOLOOBB和labelimgOBB格式转换工具图形界面"""
    
    def __init__(self):
        super().__init__()
        self.title("YOLOOBB和labelimgOBB格式转换工具")
        
        # 设置应用图标（如果有）
        try:
            self.iconbitmap("icon.ico")
        except:
            pass
        
        # 设置应用主题和样式
        self.style = ttk.Style()
        try:
            self.style.theme_use("clam")
        except:
            pass
        
        # 自定义样式
        self._configure_styles()
        
        # 主背景色
        self.configure(background="#f0f0f0")
        
        self.create_widgets()
        self._configure_window()
        
        # 初始化变量
        self.conversion_thread = None
    
    def _configure_styles(self):
        """配置样式"""
        self.style.configure("TButton", padding=6, relief="flat", font=("微软雅黑", 9))
        self.style.configure("TLabel", font=("微软雅黑", 9))
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TLabelframe", background="#f0f0f0", font=("微软雅黑", 9, "bold"))
        self.style.configure("TLabelframe.Label", font=("微软雅黑", 9, "bold"))
        self.style.configure("TNotebook", background="#f0f0f0")
        self.style.configure("TNotebook.Tab", padding=[12, 4], font=("微软雅黑", 9))
    
    def _configure_window(self):
        """配置窗口大小和位置"""
        window_width = 850
        window_height = 650
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # 最小窗口尺寸
        self.minsize(750, 550)
    
    def create_widgets(self):
        """创建界面组件"""
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建一个Notebook（选项卡控件）
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 创建两个选项卡（分别对应两种转换模式）
        tab1 = ttk.Frame(notebook, padding=10)
        tab2 = ttk.Frame(notebook, padding=10)
        
        notebook.add(tab1, text="YOLOOBB到labelimgOBB")
        notebook.add(tab2, text="labelimgOBB到YOLOOBB")
        
        # 选项卡1: YOLOOBB到labelimgOBB转换
        self.create_tab_content(tab1, mode=1)
        
        # 选项卡2: labelimgOBB到YOLOOBB转换
        self.create_tab_content(tab2, mode=2)
        
        # 创建日志输出区域
        self._create_log_area(main_frame)
        
        # 状态栏
        self._create_status_bar(main_frame)
    
    def _create_log_area(self, parent):
        """创建日志输出区域"""
        log_frame = ttk.LabelFrame(parent, text="日志输出", padding=5)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=10)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.config(state=tk.DISABLED)
        
        # 重定向标准输出到日志区域
        self.stdout_redirect = RedirectText(self.log_text)
        sys.stdout = self.stdout_redirect
    
    def _create_status_bar(self, parent):
        """创建状态栏"""
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        status_bar = ttk.Label(parent, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM, pady=2)
    
    def create_tab_content(self, tab, mode):
        """创建选项卡内容"""
        # 顶部说明
        descriptions = {
            1: "将YOLOOBB格式（归一化坐标）转换为labelimgOBB格式（像素坐标）",
            2: "将labelimgOBB格式（像素坐标）转换为YOLOOBB格式（归一化坐标）"
        }
        
        ttk.Label(tab, text=descriptions[mode]).pack(anchor=tk.W, pady=5)
        
        # 目录选择框架
        self._create_directory_section(tab, mode)
        
        # 图片尺寸框架
        self._create_image_size_section(tab, mode)
        
        # 额外选项框架（仅模式1需要）
        if mode == 1:
            self._create_options_section(tab, mode)
        
        # 操作按钮
        self._create_action_buttons(tab, mode)
    
    def _create_directory_section(self, tab, mode):
        """创建目录选择区域"""
        dirs_frame = ttk.LabelFrame(tab, text="目录设置", padding=5)
        dirs_frame.pack(fill=tk.X, pady=5)
        
        # 输入目录
        input_frame = ttk.Frame(dirs_frame)
        input_frame.pack(fill=tk.X, pady=2)
        
        input_labels = {
            1: "YOLOOBB标签目录:",
            2: "labelimgOBB标签目录:"
        }
        
        ttk.Label(input_frame, text=input_labels[mode], width=20).pack(side=tk.LEFT)
        
        input_var = tk.StringVar()
        input_entry = ttk.Entry(input_frame, textvariable=input_var)
        input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        browse_in_btn = ttk.Button(input_frame, text="浏览...", 
                                 command=lambda: self.browse_directory(input_var))
        browse_in_btn.pack(side=tk.LEFT)
        
        # 输出目录
        output_frame = ttk.Frame(dirs_frame)
        output_frame.pack(fill=tk.X, pady=2)
        
        output_labels = {
            1: "labelimgOBB标签目录:",
            2: "YOLOOBB标签目录:"
        }
        
        ttk.Label(output_frame, text=output_labels[mode], width=20).pack(side=tk.LEFT)
        
        output_var = tk.StringVar()
        output_entry = ttk.Entry(output_frame, textvariable=output_var)
        output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        browse_out_btn = ttk.Button(output_frame, text="浏览...", 
                                  command=lambda: self.browse_directory(output_var))
        browse_out_btn.pack(side=tk.LEFT)
        
        # 存储变量
        if not hasattr(self, f'tab{mode}_vars'):
            setattr(self, f'tab{mode}_vars', {})
        
        vars_dict = getattr(self, f'tab{mode}_vars')
        vars_dict['input_var'] = input_var
        vars_dict['output_var'] = output_var
    
    def _create_image_size_section(self, tab, mode):
        """创建图片尺寸设置区域"""
        img_frame = ttk.LabelFrame(tab, text="图片尺寸设置", padding=5)
        img_frame.pack(fill=tk.X, pady=5)
        
        # 预设选择框架
        presets_frame = ttk.Frame(img_frame)
        presets_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(presets_frame, text="预设尺寸:").pack(side=tk.LEFT, padx=5)
        
        # 常用分辨率预设
        presets = [
            ("720p", 1280, 720), 
            ("1080p", 1920, 1080), 
            ("4K", 3840, 2160),
            ("VGA", 640, 480),
            ("QVGA", 320, 240)
        ]
        
        # 创建宽度和高度变量
        width_var = tk.StringVar()
        height_var = tk.StringVar()
        
        # 添加预设按钮
        for name, w, h in presets:
            preset_btn = ttk.Button(
                presets_frame, 
                text=name, 
                command=lambda w=w, h=h: self.apply_size_preset(width_var, height_var, w, h)
            )
            preset_btn.pack(side=tk.LEFT, padx=2)
        
        # 添加从图片导入尺寸按钮
        import_btn = ttk.Button(
            presets_frame,
            text="从图片导入",
            command=lambda: self.import_size_from_image(width_var, height_var)
        )
        import_btn.pack(side=tk.LEFT, padx=5)
        
        # 宽度输入
        width_frame = ttk.Frame(img_frame)
        width_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(width_frame, text="图片宽度（像素）:", width=15).pack(side=tk.LEFT)
        width_entry = ttk.Entry(width_frame, textvariable=width_var)
        width_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 高度输入
        height_frame = ttk.Frame(img_frame)
        height_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(height_frame, text="图片高度（像素）:", width=15).pack(side=tk.LEFT)
        height_entry = ttk.Entry(height_frame, textvariable=height_var)
        height_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 存储变量
        vars_dict = getattr(self, f'tab{mode}_vars')
        vars_dict['width_var'] = width_var
        vars_dict['height_var'] = height_var
    
    def _create_options_section(self, tab, mode):
        """创建额外选项区域（仅模式1）"""
        options_frame = ttk.LabelFrame(tab, text="类别设置", padding=5)
        options_frame.pack(fill=tk.X, pady=5)
        
        create_classes_var = tk.BooleanVar(value=True)
        create_classes_check = ttk.Checkbutton(
            options_frame, 
            text="自动创建classes.txt文件", 
            variable=create_classes_var
        )
        create_classes_check.pack(anchor=tk.W)
        
        # 存储变量
        vars_dict = getattr(self, f'tab{mode}_vars')
        vars_dict['create_classes_var'] = create_classes_var
    
    def _create_action_buttons(self, tab, mode):
        """创建操作按钮"""
        buttons_frame = ttk.Frame(tab)
        buttons_frame.pack(fill=tk.X, pady=10)
        
        button_texts = {
            1: "开始转换",
            2: "开始转换"
        }
        
        vars_dict = getattr(self, f'tab{mode}_vars')
        
        convert_btn = ttk.Button(
            buttons_frame, 
            text=button_texts[mode], 
            command=lambda: self.start_conversion(mode, vars_dict)
        )
        convert_btn.pack(side=tk.RIGHT)
    
    def browse_directory(self, var):
        """浏览并选择目录"""
        directory = filedialog.askdirectory(title="选择目录")
        if directory:
            var.set(directory)
    
    def start_conversion(self, mode, vars_dict):
        """开始转换过程"""
        # 检查是否有正在进行的线程
        if self.conversion_thread and self.conversion_thread.is_alive():
            messagebox.showinfo("提示", "当前有转换任务正在进行，请等待完成。")
            return
        
        # 验证输入参数
        if not self._validate_inputs(vars_dict):
            return
        
        # 更新状态
        self.status_var.set("正在处理...")
        
        # 在新线程中执行转换
        conversion_methods = {
            1: self.run_yoloobb_to_labelimgobb,
            2: self.run_labelimgobb_to_yoloobb
        }
        
        method = conversion_methods[mode]
        args = self._get_conversion_args(mode, vars_dict)
        
        self.conversion_thread = threading.Thread(target=method, args=args)
        self.conversion_thread.daemon = True
        self.conversion_thread.start()
        
        # 启动检查线程状态的定时器
        self.after(100, self.check_thread_status)
    
    def _validate_inputs(self, vars_dict):
        """验证输入参数"""
        input_dir = vars_dict['input_var'].get().strip()
        output_dir = vars_dict['output_var'].get().strip()
        width_str = vars_dict['width_var'].get().strip()
        height_str = vars_dict['height_var'].get().strip()
        
        if not input_dir:
            messagebox.showerror("错误", "请选择输入目录")
            return False
        
        if not output_dir:
            messagebox.showerror("错误", "请选择输出目录")
            return False
        
        if not os.path.isdir(input_dir):
            messagebox.showerror("错误", f"输入目录不存在: {input_dir}")
            return False
        
        # 尝试创建输出目录
        try:
            os.makedirs(output_dir, exist_ok=True)
        except Exception as e:
            messagebox.showerror("错误", f"创建输出目录失败: {e}")
            return False
        
        # 验证图片尺寸
        if width_str and height_str:
            try:
                img_width = int(width_str)
                img_height = int(height_str)
                if img_width <= 0 or img_height <= 0:
                    messagebox.showerror("错误", "图片尺寸必须为正整数")
                    return False
            except ValueError:
                messagebox.showerror("错误", "图片尺寸必须为整数")
                return False
        elif width_str or height_str:
            messagebox.showerror("错误", "请同时提供图片宽度和高度")
            return False
        
        return True
    
    def _get_conversion_args(self, mode, vars_dict):
        """获取转换参数"""
        input_dir = vars_dict['input_var'].get().strip()
        output_dir = vars_dict['output_var'].get().strip()
        width_str = vars_dict['width_var'].get().strip()
        height_str = vars_dict['height_var'].get().strip()
        
        img_width = int(width_str) if width_str else None
        img_height = int(height_str) if height_str else None
        
        if mode == 1:
            create_classes = vars_dict.get('create_classes_var', tk.BooleanVar(value=False)).get()
            return (input_dir, output_dir, img_width, img_height, create_classes)
        else:
            return (input_dir, output_dir, img_width, img_height)
    
    def check_thread_status(self):
        """检查转换线程状态"""
        if self.conversion_thread and not self.conversion_thread.is_alive():
            self.status_var.set("处理完成")
            self.conversion_thread = None
        else:
            # 继续检查
            self.after(100, self.check_thread_status)
    
    def run_yoloobb_to_labelimgobb(self, input_dir, output_dir, img_width, img_height, create_classes):
        """执行YOLOOBB到labelimgOBB的转换"""
        try:
            print(f"\n==== YOLOOBB到labelimgOBB转换 ====")
            print(f"输入目录: {input_dir}")
            print(f"输出目录: {output_dir}")
            
            if img_width and img_height:
                print(f"图片尺寸: {img_width}x{img_height} 像素")
            else:
                print("警告: 未提供图片尺寸，将无法进行坐标转换")
            
            # 处理classes.txt文件
            if create_classes:
                class_ids = get_unique_class_ids(input_dir)
                print(f"\n在输入目录中发现以下类别ID: {class_ids}")
                
                # 在主线程中打开类别设置对话框
                self.after(0, lambda: self.open_classes_dialog(class_ids, output_dir))
                
                # 等待对话框关闭
                while not hasattr(self, 'classes_dialog_result'):
                    import time
                    time.sleep(0.1)
                
                if hasattr(self, 'classes_dialog_confirmed') and not self.classes_dialog_confirmed:
                    print("用户取消了类别设置，转换已中止")
                    return
                
                if self.classes_dialog_result:
                    print(f"classes.txt 文件已创建在 {self.classes_dialog_result}")
                else:
                    print("未创建classes.txt文件")
                
                # 清理临时属性
                delattr(self, 'classes_dialog_result')
                if hasattr(self, 'classes_dialog_confirmed'):
                    delattr(self, 'classes_dialog_confirmed')
            
            # 处理所有txt文件
            print("\n开始转换文件...")
            txt_files = glob.glob(os.path.join(input_dir, "*.txt"))
            
            for input_path in txt_files:
                filename = os.path.basename(input_path)
                output_path = os.path.join(output_dir, filename)
                print(f"转换 {filename}...")
                DOTA2labelimgOBB(input_path, output_path, img_width, img_height)
            
            print("\n转换完成!")
            print("=" * 50)
        except Exception as e:
            print(f"转换过程中发生错误: {str(e)}")
            import traceback
            print(traceback.format_exc())
    
    def run_labelimgobb_to_yoloobb(self, input_dir, output_dir, img_width, img_height):
        """执行labelimgOBB到YOLOOBB的转换"""
        try:
            print(f"\n==== labelimgOBB到YOLOOBB转换 ====")
            print(f"输入目录: {input_dir}")
            print(f"输出目录: {output_dir}")
            
            if img_width and img_height:
                print(f"图片尺寸: {img_width}x{img_height} 像素")
            else:
                print("警告: 未提供图片尺寸，将无法进行坐标转换")
            
            # 处理classes.txt文件
            classes_path = os.path.join(input_dir, "classes.txt")
            if os.path.exists(classes_path):
                print("发现classes.txt文件，正在处理...")
                
                # 读取类别名称
                with open(classes_path, 'r', encoding='utf-8') as f:
                    class_names = [line.strip() for line in f.readlines() if line.strip()]
                
                if class_names:
                    print(f"读取到类别文件，共{len(class_names)}个类别")
                    
                    # 生成class_names.txt文件
                    class_names_path = create_class_names_file(output_dir, class_names)
                    print(f"已生成class_names.txt文件: {class_names_path}")
                    
                    # 生成dataset.yaml文件
                    yaml_path = generate_dataset_yaml(output_dir, class_names)
                    print(f"已生成dataset.yaml文件: {yaml_path}")
            
            # 转换文件
            txt_files = glob.glob(os.path.join(input_dir, "*.txt"))
            txt_files = [f for f in txt_files if os.path.basename(f).lower() != "classes.txt"]
            
            print(f"\n开始转换 {len(txt_files)} 个文件...")
            
            for input_path in txt_files:
                filename = os.path.basename(input_path)
                output_path = os.path.join(output_dir, filename)
                print(f"转换 {filename}...")
                labelimgOBB2DOTA(input_path, output_path, img_width, img_height)
            
            print("\n转换完成!")
            print("=" * 50)
        except Exception as e:
            print(f"转换过程中发生错误: {str(e)}")
            import traceback
            print(traceback.format_exc())
    
    def open_classes_dialog(self, class_ids, output_dir):
        """打开类别设置对话框"""
        dialog = ClassesInputDialog(self, class_ids, output_dir)
        self.classes_dialog_result = dialog.result
        self.classes_dialog_confirmed = dialog.confirmed
    
    def apply_size_preset(self, width_var, height_var, width, height):
        """应用图片尺寸预设"""
        width_var.set(str(width))
        height_var.set(str(height))
    
    def import_size_from_image(self, width_var, height_var):
        """从图片导入尺寸"""
        try:
            from PIL import Image
            file_path = filedialog.askopenfilename(
                title="选择图片文件",
                filetypes=[
                    ("图片文件", "*.jpg;*.jpeg;*.png;*.bmp;*.tif;*.tiff")
                ]
            )
            
            if file_path:
                # 打开图片并获取尺寸
                with Image.open(file_path) as img:
                    width, height = img.size
                    width_var.set(str(width))
                    height_var.set(str(height))
                    messagebox.showinfo("图片尺寸", f"成功导入图片尺寸: {width}x{height}")
        except ImportError:
            messagebox.showerror("错误", "无法导入PIL库，请安装Pillow: pip install Pillow")
        except Exception as e:
            messagebox.showerror("错误", f"无法获取图片尺寸: {str(e)}")


def main():
    """主函数"""
    app = ConvertLabelsGUI()
    app.mainloop()
    
    # 恢复stdout
    sys.stdout = sys.__stdout__


if __name__ == "__main__":
    main()