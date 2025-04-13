import os
import math
import numpy as np
import shutil
import glob
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import sys
from functools import partial

# 导入原有的函数
from convert_labels import (
    calculate_obb_parameters, 
    get_unique_class_ids, 
    YOLOOBB2labelimgOBB, 
    labelimgOBB2YOLOOBB, 
    compare_formats
)

class RedirectText:
    """用于重定向输出到文本控件"""
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.buffer = ""

    def write(self, string):
        self.buffer += string
        # 每次有换行时更新UI
        if "\n" in self.buffer:
            lines = self.buffer.split("\n")
            self.buffer = lines[-1]  # 保留最后一个不完整的行
            for line in lines[:-1]:
                self.update_ui(line + "\n")

    def update_ui(self, text):
        # 在主线程中更新UI
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.insert(tk.END, text)
        self.text_widget.see(tk.END)
        self.text_widget.config(state=tk.DISABLED)

    def flush(self):
        if self.buffer:
            self.update_ui(self.buffer)
            self.buffer = ""

class ClassesInputDialog(tk.Toplevel):
    """类别输入对话框"""
    def __init__(self, parent, class_ids, output_dir):
        super().__init__(parent)
        self.title("类别设置")
        self.class_ids = class_ids
        self.output_dir = output_dir
        self.result = None
        self.current_preset = None  # 当前使用的预设
        self.confirmed = False  # 添加确认标志，默认为False
        
        # 预设类别
        self.dota_classes = [
            "plane", "ship", "storage-tank", "baseball-diamond", 
            "tennis-court", "basketball-court", "ground-track-field", 
            "harbor", "bridge", "large-vehicle", "small-vehicle", 
            "helicopter", "roundabout", "soccer-ball-field", "swimming-pool"
        ]
        
        self.coco_classes = [
            "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train", 
            "truck", "boat", "traffic light", "fire hydrant", "stop sign", 
            "parking meter", "bench", "bird", "cat", "dog", "horse", "sheep", 
            "cow", "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella", 
            "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", 
            "sports ball", "kite", "baseball bat", "baseball glove", "skateboard", 
            "surfboard", "tennis racket", "bottle", "wine glass", "cup", "fork", 
            "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange", 
            "broccoli", "carrot", "hot dog", "pizza", "donut", "cake", "chair", 
            "couch", "potted plant", "bed", "dining table", "toilet", "tv", 
            "laptop", "mouse", "remote", "keyboard", "cell phone", "microwave", 
            "oven", "toaster", "sink", "refrigerator", "book", "clock", "vase", 
            "scissors", "teddy bear", "hair drier", "toothbrush"
        ]
        
        self.imported_classes = []  # 从文件导入的类别
        
        # 设置窗口大小和位置
        window_width = 750  # 增加窗口宽度以适应新按钮和预览区域
        window_height = 600 # 增加高度以显示更多类别
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # 设置背景色
        self.configure(background="#f0f0f0")
        
        # 主框架
        main_frame = ttk.Frame(self, padding=(15, 10))
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建顶部标题
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = ttk.Label(
            header_frame, 
            text="类别设置", 
            font=("微软雅黑", 12, "bold"),
            foreground="#333333"
        )
        title_label.pack(side=tk.LEFT)
        
        # 分割线
        separator = ttk.Separator(main_frame, orient="horizontal")
        separator.pack(fill=tk.X, pady=(0, 15))
        
        # 创建说明标签
        ttk.Label(
            main_frame, 
            text="请为每个类别设置名称，可以选择预设或从文件导入",
            font=("微软雅黑", 9)
        ).pack(anchor=tk.W, pady=(0, 10))
        
        # 添加预设选择框架
        preset_frame = ttk.LabelFrame(main_frame, text="预设选择", padding=(10, 5))
        preset_frame.pack(fill=tk.X, pady=(0, 10))
        
        preset_buttons_frame = ttk.Frame(preset_frame)
        preset_buttons_frame.pack(fill=tk.X, pady=8)
        
        # 添加DOTA v1预设按钮
        dota_btn = ttk.Button(
            preset_buttons_frame, 
            text="DOTA v1", 
            width=15,
            command=lambda: self.show_all_preset_classes("dota")
        )
        dota_btn.pack(side=tk.LEFT, padx=5)
        
        # 添加COCO预设按钮
        coco_btn = ttk.Button(
            preset_buttons_frame, 
            text="COCO", 
            width=15,
            command=lambda: self.show_all_preset_classes("coco")
        )
        coco_btn.pack(side=tk.LEFT, padx=5)
        
        # 添加从文件导入按钮
        import_btn = ttk.Button(
            preset_buttons_frame, 
            text="从文件导入",
            width=15,
            command=self.import_from_file
        )
        import_btn.pack(side=tk.LEFT, padx=5)
        
        # 创建Notebook控件
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 创建"编辑类别"选项卡 - 用于编辑类别ID对应的名称
        edit_tab = ttk.Frame(notebook, padding=10)
        notebook.add(edit_tab, text="编辑类别")
        
        # 创建"所有类别"选项卡 - 用于显示预设中的所有类别
        all_classes_tab = ttk.Frame(notebook, padding=10)
        notebook.add(all_classes_tab, text="所有类别")
        
        # 在编辑选项卡中创建一个框架来容纳类别名称输入
        edit_frame = ttk.Frame(edit_tab)
        edit_frame.pack(fill=tk.BOTH, expand=True)
        
        # 添加标题
        ttk.Label(
            edit_frame, 
            text="为检测到的类别ID设置名称:",
            font=("微软雅黑", 9, "bold")
        ).pack(anchor=tk.W, pady=(0, 5))
        
        # 创建一个滚动区域
        entries_frame = ttk.Frame(edit_frame, borderwidth=1, relief="solid")
        entries_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        canvas = tk.Canvas(entries_frame, background="#ffffff", highlightthickness=0)
        scrollbar = ttk.Scrollbar(entries_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, padding=5)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 创建类别名称输入框
        self.class_entries = {}
        self.scrollable_frame = scrollable_frame
        self.create_class_entries()
        
        # 在"所有类别"选项卡中创建文本区域显示所有类别
        all_classes_frame = ttk.Frame(all_classes_tab)
        all_classes_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(
            all_classes_frame, 
            text="预设或导入的所有类别列表:",
            font=("微软雅黑", 9, "bold")
        ).pack(anchor=tk.W, pady=(0, 5))
        
        text_frame = ttk.Frame(all_classes_frame, borderwidth=1, relief="solid")
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.all_classes_text = scrolledtext.ScrolledText(
            text_frame, 
            wrap=tk.WORD,
            font=("Consolas", 9),
            background="#ffffff"
        )
        self.all_classes_text.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        self.all_classes_text.config(state=tk.DISABLED)
        
        # 创建底部按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(15, 0))
        
        # 分割线
        separator2 = ttk.Separator(main_frame, orient="horizontal")
        separator2.pack(fill=tk.X, pady=(0, 10), before=button_frame)
        
        # 取消按钮
        cancel_btn = ttk.Button(
            button_frame, 
            text="取消", 
            command=self.cancel,
            width=15
        )
        cancel_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # 确认按钮
        confirm_btn = ttk.Button(
            button_frame, 
            text="确认类别并开始转换", 
            command=self.save_classes,
            width=20,
            style="Accent.TButton"  # 使用强调样式
        )
        confirm_btn.pack(side=tk.RIGHT)
        
        # 添加一个自定义按钮样式
        style = ttk.Style()
        try:
            style.configure("Accent.TButton", 
                          foreground="#ffffff", 
                          background="#007bff", 
                          font=("微软雅黑", 9, "bold"))
            style.map("Accent.TButton",
                    foreground=[('pressed', '#ffffff'), ('active', '#ffffff')],
                    background=[('pressed', '#0069d9'), ('active', '#3395ff')])
        except:
            pass  # 如果样式设置失败，使用默认样式
        
        # 处理窗口关闭事件（点击X按钮）
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        
        # 使对话框模态
        self.transient(parent)
        self.grab_set()
        parent.wait_window(self)
    
    def create_class_entries(self):
        """创建类别输入框"""
        # 清空之前的输入框
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # 创建新的输入框
        self.class_entries = {}
        
        # 添加标题行
        header_frame = ttk.Frame(self.scrollable_frame)
        header_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(header_frame, text="类别ID", width=10, 
                font=("微软雅黑", 9, "bold")).pack(side=tk.LEFT, padx=(5, 10))
        ttk.Label(header_frame, text="类别名称", 
                font=("微软雅黑", 9, "bold")).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 创建分隔线
        separator = ttk.Separator(self.scrollable_frame, orient="horizontal")
        separator.pack(fill=tk.X, pady=5)
        
        # 为每个类别ID创建一行
        for class_id in sorted(self.class_ids):
            frame_row = ttk.Frame(self.scrollable_frame)
            frame_row.pack(fill=tk.X, padx=5, pady=3)
            
            # 类别ID标签
            id_label = ttk.Label(frame_row, text=f"ID {class_id}:", width=10)
            id_label.pack(side=tk.LEFT, padx=(5, 10))
            
            # 类别名称输入框
            entry = ttk.Entry(frame_row)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            # 默认类别名称为"class{class_id}"
            entry.insert(0, f"class{class_id}")
            self.class_entries[class_id] = entry
            
            # 为奇数行添加不同的背景色
            if class_id % 2 == 1:
                frame_row.configure(style="Alt.TFrame")
    
    def show_all_preset_classes(self, preset_type):
        """显示预设中的所有类别"""
        self.current_preset = preset_type
        preset_classes = self.dota_classes if preset_type == "dota" else self.coco_classes
        
        # 更新所有类别文本区域
        self.all_classes_text.config(state=tk.NORMAL)
        self.all_classes_text.delete(1.0, tk.END)
        
        preset_name = "DOTA v1" if preset_type == "dota" else "COCO"
        
        # 添加标题，使用tag设置样式
        self.all_classes_text.tag_configure("title", font=("微软雅黑", 10, "bold"), foreground="#007bff")
        self.all_classes_text.tag_configure("header", font=("微软雅黑", 9, "bold"), foreground="#555555")
        self.all_classes_text.tag_configure("even_row", background="#f8f9fa")
        self.all_classes_text.tag_configure("id", foreground="#0066cc", font=("Consolas", 9))
        
        self.all_classes_text.insert(tk.END, f"{preset_name}预设中的所有类别\n", "title")
        self.all_classes_text.insert(tk.END, f"总共 {len(preset_classes)} 个类别\n\n")
        
        # 添加表头
        self.all_classes_text.insert(tk.END, "ID\t类别名称\n", "header")
        self.all_classes_text.insert(tk.END, "──────────────────────────────\n")
        
        # 插入所有类别
        for i, class_name in enumerate(preset_classes):
            # 为偶数行添加背景色
            tag = "even_row" if i % 2 == 0 else ""
            id_tag = "id"
            
            # 添加ID和类别名称
            self.all_classes_text.insert(tk.END, f"{i}\t", (tag, id_tag))
            self.all_classes_text.insert(tk.END, f"{class_name}\n", tag)
        
        self.all_classes_text.config(state=tk.DISABLED)
        
        # 同时应用预设到当前类别ID
        self.apply_preset(preset_type)
    
    def apply_preset(self, preset_type):
        """应用预设类别到当前类别ID"""
        preset_classes = self.dota_classes if preset_type == "dota" else self.coco_classes
        
        # 获取已排序的类别ID
        sorted_class_ids = sorted(self.class_ids)
        
        # 更新输入框中的类别名称
        for i, class_id in enumerate(sorted_class_ids):
            if i < len(preset_classes):
                # 清除当前内容
                self.class_entries[class_id].delete(0, tk.END)
                # 插入预设类别名称
                self.class_entries[class_id].insert(0, preset_classes[i])

        # 显示应用成功的消息
        preset_name = "DOTA v1" if preset_type == "dota" else "COCO"
        
        # 使用自定义消息框
        self.show_notification(f"{preset_name}预设已应用到当前类别", "success")
    
    def show_notification(self, message, message_type="info"):
        """显示漂亮的通知消息"""
        # 创建通知窗口
        notification = tk.Toplevel(self)
        notification.overrideredirect(True)  # 无边框窗口
        notification.attributes("-topmost", True)  # 置顶显示
        
        # 设置窗口位置（居中显示）
        x = self.winfo_rootx() + self.winfo_width() // 2 - 150
        y = self.winfo_rooty() + 50
        notification.geometry(f"300x50+{x}+{y}")
        
        # 根据消息类型设置样式
        bg_color = "#d4edda" if message_type == "success" else "#cce5ff"
        fg_color = "#155724" if message_type == "success" else "#004085"
        
        # 创建消息框架
        msg_frame = tk.Frame(notification, bg=bg_color, padx=10, pady=10)
        msg_frame.pack(fill=tk.BOTH, expand=True)
        
        # 添加图标和消息
        icon_label = ttk.Label(msg_frame, text="✓" if message_type == "success" else "ℹ", 
                             font=("微软雅黑", 12, "bold"), foreground=fg_color, background=bg_color)
        icon_label.pack(side=tk.LEFT, padx=(5, 10))
        
        msg_label = ttk.Label(msg_frame, text=message, 
                            font=("微软雅黑", 9), foreground=fg_color, background=bg_color)
        msg_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 添加圆角边框效果
        notification.update_idletasks()
        notification.lift()
        
        # 3秒后自动关闭
        notification.after(3000, notification.destroy)
    
    def import_from_file(self):
        """从文件导入类别名称"""
        try:
            file_path = filedialog.askopenfilename(
                title="选择类别文件",
                filetypes=[
                    ("文本文件", "*.txt"),
                    ("所有文件", "*.*")
                ]
            )
            
            if not file_path:
                return
            
            # 读取类别文件
            with open(file_path, 'r', encoding='utf-8') as f:
                class_names = [line.strip() for line in f.readlines()]
            
            # 过滤掉空行
            class_names = [name for name in class_names if name]
            
            if not class_names:
                messagebox.showwarning("警告", "导入的类别文件为空")
                return
            
            # 确认是否导入
            message = f"已从文件读取{len(class_names)}个类别名称:\n"
            preview = class_names[:5]  # 最多显示前5个
            if len(class_names) > 5:
                preview.append("...")
            message += "\n".join(preview)
            
            if len(self.class_ids) > len(class_names):
                message += f"\n\n注意: 类别数量不足，有{len(self.class_ids)-len(class_names)}个类别将使用默认名称"
            
            confirm = messagebox.askyesno("确认导入", message)
            if not confirm:
                return
            
            # 保存导入的类别名称
            self.imported_classes = class_names
            
            # 显示所有导入的类别
            self.all_classes_text.config(state=tk.NORMAL)
            self.all_classes_text.delete(1.0, tk.END)
            
            self.all_classes_text.insert(tk.END, "从文件导入的所有类别:\n\n")
            
            for i, class_name in enumerate(class_names):
                self.all_classes_text.insert(tk.END, f"{i}: {class_name}\n")
            
            self.all_classes_text.config(state=tk.DISABLED)
            
            # 应用类别名称到当前类别ID
            for i, class_id in enumerate(sorted(self.class_ids)):
                if i < len(class_names):
                    class_name = class_names[i]
                else:
                    class_name = f"class{class_id}"
                
                # 设置输入框值
                if class_id in self.class_entries:
                    entry = self.class_entries[class_id]
                    entry.delete(0, tk.END)
                    entry.insert(0, class_name)
            
            messagebox.showinfo("导入成功", f"成功导入{len(class_names)}个类别名称")
            
        except Exception as e:
            messagebox.showerror("导入错误", f"无法从文件导入类别: {str(e)}")
    
    def save_classes(self):
        """保存类别信息并确认开始转换"""
        max_class_id = max(self.class_ids)
        classes = [""] * (max_class_id + 1)
        
        for class_id, entry in self.class_entries.items():
            class_name = entry.get().strip()
            if not class_name:
                class_name = f"class{class_id}"
            classes[class_id] = class_name
        
        # 写入classes.txt文件
        classes_path = os.path.join(self.output_dir, "classes.txt")
        try:
            with open(classes_path, 'w') as f:
                for class_name in classes:
                    f.write(f"{class_name}\n")
            
            self.result = classes_path
            # 设置确认标志，表示用户确认转换
            self.confirmed = True
            messagebox.showinfo("保存成功", f"类别信息已保存到 {classes_path}")
            self.destroy()
        except Exception as e:
            messagebox.showerror("错误", f"保存类别文件失败: {e}")
    
    def cancel(self):
        """取消操作"""
        self.result = None
        # 设置确认标志为False，表示用户取消转换
        self.confirmed = False
        self.destroy()

class ConvertLabelsGUI(tk.Tk):
    """YOLOOBB和labelimgOBB格式转换工具图形界面"""
    def __init__(self):
        super().__init__()
        self.title("YOLOOBB和labelimgOBB格式转换工具")
        
        # 设置应用图标（如果有）
        try:
            self.iconbitmap("icon.ico")  # 如果有图标文件，取消注释
        except:
            pass  # 没有图标文件也不影响程序运行
        
        # 设置应用主题和样式
        self.style = ttk.Style()
        # 尝试使用不同的主题，如果支持的话
        try:
            # 尝试使用现代风格的主题
            self.style.theme_use("clam")  # 可选: clam, alt, default, classic, vista, xpnative
        except:
            pass  # 如果不支持，使用默认主题
        
        # 自定义样式
        self.style.configure("TButton", padding=6, relief="flat", font=("微软雅黑", 9))
        self.style.configure("TLabel", font=("微软雅黑", 9))
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TLabelframe", background="#f0f0f0", font=("微软雅黑", 9, "bold"))
        self.style.configure("TLabelframe.Label", font=("微软雅黑", 9, "bold"))
        self.style.configure("TNotebook", background="#f0f0f0")
        self.style.configure("TNotebook.Tab", padding=[12, 4], font=("微软雅黑", 9))
        
        # 主背景色
        self.configure(background="#f0f0f0")
        
        self.create_widgets()
        
        # 设置窗口大小和位置
        window_width = 850
        window_height = 650
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # 最小窗口尺寸
        self.minsize(750, 550)
        
        # 初始化变量
        self.conversion_thread = None
    
    def create_widgets(self):
        """创建界面组件"""
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建一个Notebook（选项卡控件）
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 创建三个选项卡（分别对应三种转换模式）
        tab1 = ttk.Frame(notebook, padding=10)
        tab2 = ttk.Frame(notebook, padding=10)
        tab3 = ttk.Frame(notebook, padding=10)
        
        notebook.add(tab1, text="YOLOOBB到labelimgOBB")
        notebook.add(tab2, text="labelimgOBB到YOLOOBB")
        notebook.add(tab3, text="格式转换比较")
        
        # 选项卡1: YOLOOBB到labelimgOBB转换
        self.create_tab_content(tab1, mode=1)
        
        # 选项卡2: labelimgOBB到YOLOOBB转换
        self.create_tab_content(tab2, mode=2)
        
        # 选项卡3: 比较转换
        self.create_tab_content(tab3, mode=3)
        
        # 创建日志输出区域
        log_frame = ttk.LabelFrame(main_frame, text="日志输出", padding=5)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=10)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.config(state=tk.DISABLED)
        
        # 重定向标准输出到日志区域
        self.stdout_redirect = RedirectText(self.log_text)
        sys.stdout = self.stdout_redirect
        
        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM, pady=2)
    
    def create_tab_content(self, tab, mode):
        """创建选项卡内容"""
        # 顶部说明
        if mode == 1:
            desc = "将YOLOOBB格式（归一化坐标）转换为labelimgOBB格式（像素坐标）"
        elif mode == 2:
            desc = "将labelimgOBB格式（像素坐标）转换为YOLOOBB格式（归一化坐标）"
        else:
            desc = "将YOLOOBB格式转换为labelimgOBB格式，再转回YOLOOBB格式，并比较结果"
        
        ttk.Label(tab, text=desc).pack(anchor=tk.W, pady=5)
        
        # 目录选择框架
        dirs_frame = ttk.LabelFrame(tab, text="目录设置", padding=5)
        dirs_frame.pack(fill=tk.X, pady=5)
        
        # 输入目录
        input_frame = ttk.Frame(dirs_frame)
        input_frame.pack(fill=tk.X, pady=2)
        
        in_label_text = "YOLOOBB标签目录:" if mode in (1, 3) else "labelimgOBB标签目录:"
        ttk.Label(input_frame, text=in_label_text, width=20).pack(side=tk.LEFT)
        
        input_var = tk.StringVar()
        input_entry = ttk.Entry(input_frame, textvariable=input_var)
        input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        browse_in_btn = ttk.Button(input_frame, text="浏览...", 
                                 command=lambda: self.browse_directory(input_var))
        browse_in_btn.pack(side=tk.LEFT)
        
        # 输出目录
        output_frame = ttk.Frame(dirs_frame)
        output_frame.pack(fill=tk.X, pady=2)
        
        out_label_text = "labelimgOBB标签目录:" if mode == 1 else "YOLOOBB标签目录:" if mode == 2 else "比较结果目录:"
        ttk.Label(output_frame, text=out_label_text, width=20).pack(side=tk.LEFT)
        
        output_var = tk.StringVar()
        output_entry = ttk.Entry(output_frame, textvariable=output_var)
        output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        browse_out_btn = ttk.Button(output_frame, text="浏览...", 
                                  command=lambda: self.browse_directory(output_var))
        browse_out_btn.pack(side=tk.LEFT)
        
        # 图片尺寸框架
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
        
        # 创建宽度和高度变量，供后续使用
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
        
        # 宽度
        width_frame = ttk.Frame(img_frame)
        width_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(width_frame, text="图片宽度（像素）:", width=15).pack(side=tk.LEFT)
        
        width_entry = ttk.Entry(width_frame, textvariable=width_var)
        width_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 高度
        height_frame = ttk.Frame(img_frame)
        height_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(height_frame, text="图片高度（像素）:", width=15).pack(side=tk.LEFT)
        
        height_entry = ttk.Entry(height_frame, textvariable=height_var)
        height_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 额外选项框架（仅模式1需要）
        if mode == 1:
            options_frame = ttk.LabelFrame(tab, text="类别设置", padding=5)
            options_frame.pack(fill=tk.X, pady=5)
            
            create_classes_var = tk.BooleanVar(value=True)
            create_classes_check = ttk.Checkbutton(options_frame, text="自动创建classes.txt文件", 
                                                 variable=create_classes_var)
            create_classes_check.pack(anchor=tk.W)
        
        # 操作按钮
        buttons_frame = ttk.Frame(tab)
        buttons_frame.pack(fill=tk.X, pady=10)
        
        if mode == 1:
            # 存储变量以便后续访问
            self.tab1_vars = {
                'input_var': input_var,
                'output_var': output_var,
                'width_var': width_var,
                'height_var': height_var,
                'create_classes_var': create_classes_var
            }
            
            convert_btn = ttk.Button(buttons_frame, text="开始转换", 
                                   command=lambda: self.start_conversion(mode, self.tab1_vars))
        elif mode == 2:
            # 存储变量以便后续访问
            self.tab2_vars = {
                'input_var': input_var,
                'output_var': output_var,
                'width_var': width_var,
                'height_var': height_var
            }
            
            convert_btn = ttk.Button(buttons_frame, text="开始转换", 
                                   command=lambda: self.start_conversion(mode, self.tab2_vars))
        else:
            # 存储变量以便后续访问
            self.tab3_vars = {
                'input_var': input_var,
                'output_var': output_var,
                'width_var': width_var,
                'height_var': height_var
            }
            
            convert_btn = ttk.Button(buttons_frame, text="开始比较", 
                                   command=lambda: self.start_conversion(mode, self.tab3_vars))
        
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
        
        # 获取输入参数
        input_dir = vars_dict['input_var'].get().strip()
        output_dir = vars_dict['output_var'].get().strip()
        width_str = vars_dict['width_var'].get().strip()
        height_str = vars_dict['height_var'].get().strip()
        
        # 验证输入
        if not input_dir:
            messagebox.showerror("错误", "请选择输入目录")
            return
        
        if not output_dir:
            messagebox.showerror("错误", "请选择输出目录")
            return
        
        if not os.path.isdir(input_dir):
            messagebox.showerror("错误", f"输入目录不存在: {input_dir}")
            return
        
        # 尝试创建输出目录
        try:
            os.makedirs(output_dir, exist_ok=True)
        except Exception as e:
            messagebox.showerror("错误", f"创建输出目录失败: {e}")
            return
        
        # 解析图片尺寸
        img_width = None
        img_height = None
        
        if width_str and height_str:
            try:
                img_width = int(width_str)
                img_height = int(height_str)
                
                if img_width <= 0 or img_height <= 0:
                    messagebox.showerror("错误", "图片尺寸必须为正整数")
                    return
            except ValueError:
                messagebox.showerror("错误", "图片尺寸必须为整数")
                return
        elif width_str or height_str:
            messagebox.showerror("错误", "请同时提供图片宽度和高度")
            return
        
        # 更新状态
        self.status_var.set("正在处理...")
        
        # 在新线程中执行转换
        if mode == 1:
            create_classes = vars_dict.get('create_classes_var', tk.BooleanVar(value=False)).get()
            self.conversion_thread = threading.Thread(
                target=self.run_yoloobb_to_labelimgobb,
                args=(input_dir, output_dir, img_width, img_height, create_classes)
            )
        elif mode == 2:
            self.conversion_thread = threading.Thread(
                target=self.run_labelimgobb_to_yoloobb,
                args=(input_dir, output_dir, img_width, img_height)
            )
        else:
            self.conversion_thread = threading.Thread(
                target=self.run_compare_formats,
                args=(input_dir, output_dir, img_width, img_height)
            )
        
        self.conversion_thread.daemon = True
        self.conversion_thread.start()
        
        # 启动检查线程状态的定时器
        self.after(100, self.check_thread_status)
    
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
                YOLOOBB2labelimgOBB(input_path, output_path, img_width, img_height)
            
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
            
            # 处理所有txt文件
            print("\n开始转换文件...")
            txt_files = glob.glob(os.path.join(input_dir, "*.txt"))
            
            for input_path in txt_files:
                filename = os.path.basename(input_path)
                output_path = os.path.join(output_dir, filename)
                print(f"转换 {filename}...")
                labelimgOBB2YOLOOBB(input_path, output_path, img_width, img_height)
            
            print("\n转换完成!")
            print("=" * 50)
        except Exception as e:
            print(f"转换过程中发生错误: {str(e)}")
            import traceback
            print(traceback.format_exc())
    
    def run_compare_formats(self, input_dir, output_dir, img_width, img_height):
        """执行格式比较"""
        try:
            print(f"\n==== 格式转换比较 ====")
            print(f"输入目录: {input_dir}")
            print(f"输出目录: {output_dir}")
            
            if img_width and img_height:
                print(f"图片尺寸: {img_width}x{img_height} 像素")
            else:
                print("警告: 未提供图片尺寸，将无法进行坐标转换")
            
            # 比较转换
            print("\n开始比较转换...")
            txt_files = glob.glob(os.path.join(input_dir, "*.txt"))
            
            for input_path in txt_files:
                filename = os.path.basename(input_path)
                print(f"比较 {filename}...")
                compare_formats(input_path, output_dir, img_width, img_height)
            
            print("\n比较完成!")
            print("=" * 50)
        except Exception as e:
            print(f"比较过程中发生错误: {str(e)}")
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
    app = ConvertLabelsGUI()
    app.mainloop()

if __name__ == "__main__":
    main()
    
    # 恢复stdout
    sys.stdout = sys.__stdout__ 