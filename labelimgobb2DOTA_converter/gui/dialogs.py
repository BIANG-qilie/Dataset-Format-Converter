"""
GUI对话框模块

包含类别设置对话框和其他辅助对话框
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext


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
        
        self._create_ui()
        
        # 处理窗口关闭事件（点击X按钮）
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        
        # 使对话框模态
        self.transient(parent)
        self.grab_set()
        parent.wait_window(self)
    
    def _create_ui(self):
        """创建用户界面"""
        # 设置窗口大小和位置
        window_width = 800
        window_height = 700
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # 设置最小窗口大小
        self.minsize(800, 700)
        
        # 设置背景色
        self.configure(background="#f0f0f0")
        
        # 主框架
        main_frame = ttk.Frame(self, padding=(15, 10))
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        self._create_header(main_frame)
        self._create_preset_section(main_frame)
        self._create_notebook(main_frame)
        self._create_buttons(main_frame)
    
    def _create_header(self, parent):
        """创建标题区域"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = ttk.Label(
            header_frame, 
            text="类别设置", 
            font=("微软雅黑", 12, "bold"),
            foreground="#333333"
        )
        title_label.pack(side=tk.LEFT)
        
        # 分割线
        separator = ttk.Separator(parent, orient="horizontal")
        separator.pack(fill=tk.X, pady=(0, 15))
        
        # 创建说明标签
        ttk.Label(
            parent, 
            text="请为每个类别设置名称，可以选择预设或从文件导入",
            font=("微软雅黑", 9)
        ).pack(anchor=tk.W, pady=(0, 10))
    
    def _create_preset_section(self, parent):
        """创建预设选择区域"""
        preset_frame = ttk.LabelFrame(parent, text="预设选择", padding=(10, 5))
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
    
    def _create_notebook(self, parent):
        """创建选项卡控件"""
        # 创建Notebook控件
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 创建"编辑类别"选项卡
        edit_tab = ttk.Frame(notebook, padding=10)
        notebook.add(edit_tab, text="编辑类别")
        
        # 创建"所有类别"选项卡
        all_classes_tab = ttk.Frame(notebook, padding=10)
        notebook.add(all_classes_tab, text="所有类别")
        
        self._create_edit_tab(edit_tab)
        self._create_all_classes_tab(all_classes_tab)
    
    def _create_edit_tab(self, tab):
        """创建编辑类别选项卡"""
        edit_frame = ttk.Frame(tab)
        edit_frame.pack(fill=tk.BOTH, expand=True)
        
        # 添加标题
        ttk.Label(
            edit_frame, 
            text="为检测到的类别ID设置名称:",
            font=("微软雅黑", 9, "bold")
        ).pack(anchor=tk.W, pady=(0, 5))
        
        # 创建滚动区域
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
    
    def _create_all_classes_tab(self, tab):
        """创建所有类别选项卡"""
        all_classes_frame = ttk.Frame(tab)
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
    
    def _create_buttons(self, parent):
        """创建按钮区域"""
        # 创建底部按钮区域
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=(15, 0))
        
        # 分割线
        separator2 = ttk.Separator(parent, orient="horizontal")
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
            style="Accent.TButton"
        )
        confirm_btn.pack(side=tk.RIGHT)
        
        # 添加按钮样式
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
            pass
    
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
            if class_id < len(preset_classes):
                # 清除当前内容
                self.class_entries[class_id].delete(0, tk.END)
                # 插入预设类别名称
                self.class_entries[class_id].insert(0, preset_classes[class_id])

        # 显示应用成功的消息
        preset_name = "DOTA v1" if preset_type == "dota" else "COCO"
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
            with open(classes_path, 'w', encoding='utf-8') as f:
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