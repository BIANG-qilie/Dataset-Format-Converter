#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GUI主窗口 - 提供图形化界面进行格式转换
"""

import os
import sys
import threading
from pathlib import Path
from typing import Optional, List

try:
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox, scrolledtext
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False

from ..core.format_manager import format_manager
from ..config.settings import get_settings, update_settings, save_settings
from ..i18n.translation import get_available_languages, set_language, t


class DatasetConverterGUI:
    """数据集格式转换器图形界面"""
    
    def __init__(self):
        """初始化GUI"""
        if not GUI_AVAILABLE:
            raise ImportError("tkinter模块不可用，无法启动图形界面")
        
        # 加载设置
        self.settings = get_settings()
        set_language(self.settings.language)
        
        # 初始化变量
        self.root = tk.Tk()
        self.current_class_names = []
        self.setup_window()
        self.setup_styles()
        self.create_widgets()
        
        # 在界面完全创建后加载设置
        self.root.after(100, self.load_settings)
        
        # 绑定关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_window(self):
        """设置窗口属性"""
        self.root.title(t('app.title'))
        
        # 设置固定窗口大小
        window_width = 900
        window_height = 700
        self.root.geometry(f"{window_width}x{window_height}")
        
        # 锁定窗口大小，禁止调整
        self.root.resizable(False, False)
        
        # 居中显示窗口
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (window_width // 2)
        y = (self.root.winfo_screenheight() // 2) - (window_height // 2)
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # 设置图标（如果有的话）
        try:
            # 这里可以设置应用图标
            pass
        except:
            pass
    
    def setup_styles(self):
        """设置样式"""
        style = ttk.Style()
        
        # 配置样式
        style.configure('Title.TLabel', font=('TkDefaultFont', 14, 'bold'), foreground='#2c3e50')
        style.configure('Header.TLabel', font=('TkDefaultFont', 10, 'bold'), foreground='#34495e')
        style.configure('Info.TLabel', font=('TkDefaultFont', 9), foreground='#7f8c8d')
        style.configure('Success.TLabel', font=('TkDefaultFont', 9), foreground='#27ae60')
        style.configure('Error.TLabel', font=('TkDefaultFont', 9), foreground='#e74c3c')
        style.configure('Primary.TButton', font=('TkDefaultFont', 11, 'bold'))
        
        # 配置Notebook样式
        style.configure('TNotebook.Tab', padding=[15, 10], font=('TkDefaultFont', 10))
        style.configure('TNotebook', tabposition='n')
        
        # 配置LabelFrame样式
        style.configure('TLabelframe.Label', font=('TkDefaultFont', 10, 'bold'), foreground='#2c3e50')
        style.configure('TLabelframe', borderwidth=2, relief='groove')
    
    def create_widgets(self):
        """创建界面组件"""
        # 配置根窗口网格
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # 创建主标题
        title_frame = ttk.Frame(self.root)
        title_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=25, pady=(20, 10))
        
        title_label = ttk.Label(title_frame, text=t('app.title'), style='Title.TLabel')
        title_label.pack(pady=(0, 3))
        
        subtitle_label = ttk.Label(title_frame, text=t('app.description'), style='Info.TLabel')
        subtitle_label.pack()
        
        # 添加分隔线
        separator = ttk.Separator(self.root, orient='horizontal')
        separator.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=25, pady=(0, 15))
        
        # 创建Tab界面
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=25, pady=(0, 15))
        self.root.rowconfigure(2, weight=1)
        
        # 创建各个Tab
        self.create_converter_tab()
        self.create_settings_tab()
        
        # 状态栏
        self.create_status_bar()
    
    def create_converter_tab(self):
        """创建转换器Tab"""
        # 创建转换器框架
        converter_frame = ttk.Frame(self.notebook)
        self.notebook.add(converter_frame, text=t('gui.converter'))
        
        # 创建滚动框架
        canvas = tk.Canvas(converter_frame)
        scrollbar = ttk.Scrollbar(converter_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        converter_frame.columnconfigure(0, weight=1)
        converter_frame.rowconfigure(0, weight=1)
        
        # 内容区域
        content_frame = ttk.Frame(scrollable_frame, padding="20")
        content_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        content_frame.columnconfigure(0, weight=1)
        
        # 步骤1：选择格式
        self.create_format_selection_step(content_frame, 0)
        
        # 步骤2：选择输入
        self.create_input_selection_step(content_frame, 1)
        
        # 步骤3：选择输出
        self.create_output_selection_step(content_frame, 2)
        
        # 步骤4：图片尺寸
        self.create_dimensions_step(content_frame, 3)
        
        # 步骤5：类别确认
        self.create_classes_confirmation_step(content_frame, 4)
        
        # 转换区域
        self.create_conversion_step(content_frame, 5)
    
    def create_settings_tab(self):
        """创建设置Tab"""
        settings_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(settings_frame, text=t('gui.settings'))
        
        # 语言设置
        self.create_language_section(settings_frame)
        
        # 作者信息
        self.create_author_section(settings_frame)
        
        # 其他设置可以在这里添加
        
    def create_status_bar(self):
        """创建状态栏"""
        status_frame = ttk.Frame(self.root)
        status_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), padx=25, pady=(0, 15))
        
        self.status_var = tk.StringVar(value=t('gui.ready'))
        status_label = ttk.Label(status_frame, textvariable=self.status_var, 
                               relief=tk.SUNKEN, anchor=tk.W, padding="8")
        status_label.pack(fill=tk.X)
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(status_frame, variable=self.progress_var, 
                                          maximum=100, mode='determinate')
        self.progress_bar.pack(fill=tk.X, pady=(8, 0))
    
    def create_format_selection_step(self, parent, row):
        """步骤1：格式选择"""
        step_frame = ttk.LabelFrame(parent, text=f"{t('gui.step1_formats')}", padding="20")
        step_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        step_frame.columnconfigure(1, weight=1)
        
        # 创建两列布局
        left_frame = ttk.Frame(step_frame)
        left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 15))
        
        right_frame = ttk.Frame(step_frame)
        right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        step_frame.columnconfigure(0, weight=1)
        step_frame.columnconfigure(1, weight=1)
        
        # 左列：输入格式
        ttk.Label(left_frame, text=t('gui.input_format'), style='Header.TLabel').pack(anchor=tk.W, pady=(0, 8))
        
        self.input_format_var = tk.StringVar()
        formats_with_empty = [""] + format_manager.list_formats()
        input_format_combo = ttk.Combobox(left_frame, textvariable=self.input_format_var,
                                        values=formats_with_empty,
                                        state="readonly", width=28)
        input_format_combo.pack(anchor=tk.W, pady=(0, 10))
        input_format_combo.bind('<<ComboboxSelected>>', self.on_input_format_change)
        
        # 输入格式示例
        ttk.Label(left_frame, text="格式示例:", style='Info.TLabel').pack(anchor=tk.W, pady=(0, 5))
        self.input_format_example = scrolledtext.ScrolledText(left_frame, height=6, width=45, 
                                                             state='disabled', wrap=tk.WORD,
                                                             font=('Consolas', 9))
        self.input_format_example.pack(fill=tk.BOTH, expand=True)
        
        # 右列：输出格式
        ttk.Label(right_frame, text=t('gui.output_format'), style='Header.TLabel').pack(anchor=tk.W, pady=(0, 8))
        
        self.output_format_var = tk.StringVar()
        output_format_combo = ttk.Combobox(right_frame, textvariable=self.output_format_var,
                                         values=formats_with_empty,
                                         state="readonly", width=28)
        output_format_combo.pack(anchor=tk.W, pady=(0, 10))
        output_format_combo.bind('<<ComboboxSelected>>', self.on_output_format_change)
        
        # 输出格式示例
        ttk.Label(right_frame, text="格式示例:", style='Info.TLabel').pack(anchor=tk.W, pady=(0, 5))
        self.output_format_example = scrolledtext.ScrolledText(right_frame, height=6, width=45, 
                                                              state='disabled', wrap=tk.WORD,
                                                              font=('Consolas', 9))
        self.output_format_example.pack(fill=tk.BOTH, expand=True)
        
        # 初始化显示默认提示
        self.show_format_example("", self.input_format_example)
        self.show_format_example("", self.output_format_example)
    
    def create_input_selection_step(self, parent, row):
        """步骤2：输入选择"""
        step_frame = ttk.LabelFrame(parent, text=f"▶ {t('gui.step2_input')}", padding="20")
        step_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        step_frame.columnconfigure(0, weight=1)
        
        # 路径输入区域
        path_frame = ttk.Frame(step_frame)
        path_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        path_frame.columnconfigure(0, weight=1)
        
        self.input_var = tk.StringVar()
        input_entry = ttk.Entry(path_frame, textvariable=self.input_var, font=('TkDefaultFont', 10))
        input_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 15))
        
        # 按钮区域
        button_frame = ttk.Frame(path_frame)
        button_frame.grid(row=0, column=1)
        
        self.select_file_btn = ttk.Button(button_frame, text=t('gui.select_file'), 
                                        command=self.select_input_file, state='disabled',
                                        width=12)
        self.select_file_btn.grid(row=0, column=0, padx=(0, 8))
        
        self.select_folder_btn = ttk.Button(button_frame, text=t('gui.select_folder'), 
                                          command=self.select_input_folder, state='disabled',
                                          width=12)
        self.select_folder_btn.grid(row=0, column=1)
        
        # 提示信息
        self.input_hint = ttk.Label(step_frame, text=t('gui.select_format_first'), style='Info.TLabel')
        self.input_hint.grid(row=1, column=0, columnspan=2, sticky=tk.W)
    
    def create_output_selection_step(self, parent, row):
        """步骤3：输出选择"""
        step_frame = ttk.LabelFrame(parent, text=f"▷ {t('gui.step3_output')}", padding="20")
        step_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        step_frame.columnconfigure(0, weight=1)
        
        # 路径输入区域
        path_frame = ttk.Frame(step_frame)
        path_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        path_frame.columnconfigure(0, weight=1)
        
        self.output_var = tk.StringVar()
        output_entry = ttk.Entry(path_frame, textvariable=self.output_var, font=('TkDefaultFont', 10))
        output_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 15))
        
        self.select_output_btn = ttk.Button(path_frame, text=t('gui.select_folder'), 
                                          command=self.select_output_folder, state='disabled',
                                          width=12)
        self.select_output_btn.grid(row=0, column=1)
        
        # 提示信息
        self.output_hint = ttk.Label(step_frame, text=t('gui.select_output_format_first'), style='Info.TLabel')
        self.output_hint.grid(row=1, column=0, columnspan=2, sticky=tk.W)
    
    def create_dimensions_step(self, parent, row):
        """步骤4：图片尺寸"""
        step_frame = ttk.LabelFrame(parent, text=f"▣ {t('gui.step4_dimensions')}", padding="20")
        step_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # 尺寸输入
        dims_frame = ttk.Frame(step_frame)
        dims_frame.grid(row=0, column=0, sticky=tk.W, pady=(0, 15))
        
        ttk.Label(dims_frame, text=t('gui.width'), style='Header.TLabel').grid(
            row=0, column=0, sticky=tk.W, padx=(0, 8))
        self.width_var = tk.StringVar(value=str(self.settings.last_image_width))
        width_entry = ttk.Entry(dims_frame, textvariable=self.width_var, width=12, font=('TkDefaultFont', 10))
        width_entry.grid(row=0, column=1, padx=(0, 25))
        
        ttk.Label(dims_frame, text=t('gui.height'), style='Header.TLabel').grid(
            row=0, column=2, sticky=tk.W, padx=(0, 8))
        self.height_var = tk.StringVar(value=str(self.settings.last_image_height))
        height_entry = ttk.Entry(dims_frame, textvariable=self.height_var, width=12, font=('TkDefaultFont', 10))
        height_entry.grid(row=0, column=3)
        
        # 快捷按钮
        presets_frame = ttk.Frame(step_frame)
        presets_frame.grid(row=1, column=0, sticky=tk.W)
        
        ttk.Label(presets_frame, text=t('gui.common_sizes'), style='Info.TLabel').pack(
            side=tk.LEFT, padx=(0, 15))
        
        ttk.Button(presets_frame, text="1920×1080", 
                  command=lambda: self.set_dimensions(1920, 1080), width=10).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(presets_frame, text="1280×720", 
                  command=lambda: self.set_dimensions(1280, 720), width=10).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(presets_frame, text="640×480", 
                  command=lambda: self.set_dimensions(640, 480), width=10).pack(side=tk.LEFT)
    
    def create_classes_confirmation_step(self, parent, row):
        """步骤5：类别确认"""
        step_frame = ttk.LabelFrame(parent, text=f"● {t('gui.step5_classes')}", padding="20")
        step_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        step_frame.columnconfigure(0, weight=1)
        
        # 类别列表显示
        classes_label = ttk.Label(step_frame, text="检测到的类别列表:", style='Header.TLabel')
        classes_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 8))
        
        self.classes_text = scrolledtext.ScrolledText(step_frame, height=5, state='disabled', 
                                                     wrap=tk.WORD, font=('TkDefaultFont', 9))
        self.classes_text.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # 操作按钮
        btn_frame = ttk.Frame(step_frame)
        btn_frame.grid(row=2, column=0, sticky=tk.W, pady=(0, 10))
        
        self.load_classes_btn = ttk.Button(btn_frame, text=t('gui.load_classes_file'), 
                                         command=self.load_classes_file, width=16)
        self.load_classes_btn.pack(side=tk.LEFT, padx=(0, 12))
        
        self.refresh_classes_btn = ttk.Button(btn_frame, text=t('gui.refresh_classes'), 
                                            command=self.refresh_classes, state='disabled', width=12)
        self.refresh_classes_btn.pack(side=tk.LEFT)
        
        # 类别状态
        self.classes_status = ttk.Label(step_frame, text=t('gui.no_classes_detected'), style='Info.TLabel')
        self.classes_status.grid(row=3, column=0, sticky=tk.W)
    
    def create_conversion_step(self, parent, row):
        """转换步骤"""
        step_frame = ttk.LabelFrame(parent, text=f"→ {t('gui.step6_convert')}", padding="20")
        step_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        step_frame.columnconfigure(0, weight=1)
        
        # 转换摘要标题
        summary_label = ttk.Label(step_frame, text="转换配置摘要:", style='Header.TLabel')
        summary_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 8))
        
        # 转换摘要
        summary_frame = ttk.Frame(step_frame, relief='sunken', borderwidth=1)
        summary_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        summary_frame.columnconfigure(0, weight=1)
        
        self.conversion_summary = ttk.Label(summary_frame, text="请完成以上步骤配置", 
                                           style='Info.TLabel', wraplength=600, 
                                           padding="15", justify='left')
        self.conversion_summary.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # 转换按钮
        button_frame = ttk.Frame(step_frame)
        button_frame.grid(row=2, column=0)
        
        self.convert_button = ttk.Button(button_frame, text=t('gui.start_conversion'), 
                                       command=self.start_conversion, state='disabled',
                                       style='Primary.TButton', width=20, padding=(10, 8))
        self.convert_button.pack()
    
    def create_language_section(self, parent):
        """创建语言选择区域"""
        frame = ttk.LabelFrame(parent, text=t('gui.language'), padding="15")
        frame.pack(fill=tk.X, pady=(0, 15))
        
        self.language_var = tk.StringVar()
        languages = get_available_languages()
        
        language_combo = ttk.Combobox(frame, textvariable=self.language_var, 
                                    values=list(languages.values()), 
                                    state="readonly", width=20)
        language_combo.pack(anchor=tk.W)
        language_combo.bind('<<ComboboxSelected>>', self.on_language_change)
        
        # 设置当前语言
        current_lang = languages.get(self.settings.language, "English")
        self.language_var.set(current_lang)
        
        # 说明文字
        ttk.Label(frame, text=t('gui.language_restart_note'), style='Info.TLabel').pack(
            anchor=tk.W, pady=(5, 0))
    
    def create_author_section(self, parent):
        """创建作者信息区域"""
        frame = ttk.LabelFrame(parent, text="关于作者", padding="15")
        frame.pack(fill=tk.X, pady=(15, 0))
        
        # 作者名称
        author_frame = ttk.Frame(frame)
        author_frame.pack(fill=tk.X, pady=(0, 8))
        
        ttk.Label(author_frame, text="作者:", style='Header.TLabel').pack(side=tk.LEFT)
        ttk.Label(author_frame, text="BIANG", style='Info.TLabel', font=('TkDefaultFont', 12, 'bold')).pack(side=tk.LEFT, padx=(10, 0))
        
        # 项目信息
        project_frame = ttk.Frame(frame)
        project_frame.pack(fill=tk.X, pady=(0, 8))
        
        ttk.Label(project_frame, text="项目:", style='Header.TLabel').pack(side=tk.LEFT)
        ttk.Label(project_frame, text="OBB数据格式转换器", style='Info.TLabel').pack(side=tk.LEFT, padx=(10, 0))
        
        # 版本信息
        version_frame = ttk.Frame(frame)
        version_frame.pack(fill=tk.X, pady=(0, 8))
        
        ttk.Label(version_frame, text="版本:", style='Header.TLabel').pack(side=tk.LEFT)
        ttk.Label(version_frame, text="v1.0.0", style='Info.TLabel').pack(side=tk.LEFT, padx=(10, 0))
        
        # GitHub链接
        link_frame = ttk.Frame(frame)
        link_frame.pack(fill=tk.X)
        
        ttk.Label(link_frame, text="GitHub:", style='Header.TLabel').pack(side=tk.LEFT)
        ttk.Label(link_frame, text="github.com/BIANG-qilie/dataset-format-converter", 
                 style='Info.TLabel', foreground='#0066cc').pack(side=tk.LEFT, padx=(10, 0))
    
    def load_settings(self):
        """加载设置到界面"""
        # 加载输入格式设置
        if hasattr(self, 'input_format_var') and hasattr(self, 'input_format_example'):
            input_format = self.settings.last_input_format or ""
            self.input_format_var.set(input_format)
            # 更新示例显示
            self.show_format_example(input_format, self.input_format_example)
            # 如果有格式选择，触发格式变化事件以更新界面状态
            if input_format:
                self.on_input_format_change()
                
        # 加载输出格式设置        
        if hasattr(self, 'output_format_var') and hasattr(self, 'output_format_example'):
            output_format = self.settings.last_output_format or ""
            self.output_format_var.set(output_format)
            # 更新示例显示
            self.show_format_example(output_format, self.output_format_example)
            # 如果有格式选择，触发格式变化事件以更新界面状态
            if output_format:
                self.on_output_format_change()
        
        # 最后初始化界面状态
        if hasattr(self, 'conversion_summary'):
            self.update_conversion_summary()
    
    # 新的事件处理方法
    def on_input_format_change(self, event=None):
        """输入格式变化事件"""
        format_name = self.input_format_var.get()
        if format_name:
            # 启用输入选择按钮
            self.select_file_btn.config(state='normal')
            self.select_folder_btn.config(state='normal')
            self.input_hint.config(text=t('gui.format_selected_input_ready'))
            
            # 显示格式示例
            self.show_format_example(format_name, self.input_format_example)
            
            # 刷新类别
            if self.input_var.get():
                self.refresh_classes()
        
        self.update_conversion_summary()
    
    def on_output_format_change(self, event=None):
        """输出格式变化事件"""
        format_name = self.output_format_var.get()
        if format_name:
            # 启用输出选择按钮
            self.select_output_btn.config(state='normal')
            self.output_hint.config(text=t('gui.format_selected_output_ready'))
            
            # 显示格式示例
            self.show_format_example(format_name, self.output_format_example)
        
        self.update_conversion_summary()
    
    def show_format_example(self, format_name, text_widget):
        """显示格式示例"""
        examples = {
            '': '请选择一个格式以查看示例\n\n支持的格式包括：\n• YOLO-HBB - 水平边界框格式\n• YOLO-OBB - 旋转边界框格式\n• LabelImg-OBB - LabelImg工具格式\n• DOTA - 遥感数据格式\n• PASCAL-VOC - XML标注格式',
            'YOLO-HBB': '格式说明：\nclass_id x_center y_center width height\n(归一化坐标，范围0-1)\n\n示例内容：\n0 0.5 0.5 0.3 0.4\n1 0.2 0.3 0.1 0.2\n\n说明：\n第一行：类别0，中心点(0.5,0.5)，宽0.3，高0.4\n第二行：类别1，中心点(0.2,0.3)，宽0.1，高0.2',
            'YOLO-OBB': '格式说明：\nclass_id x1 y1 x2 y2 x3 y3 x4 y4\n(归一化坐标，四个角点)\n\n示例内容：\n0 0.1 0.1 0.9 0.1 0.9 0.9 0.1 0.9\n1 0.2 0.2 0.8 0.2 0.8 0.8 0.2 0.8\n\n说明：\n每行8个坐标值表示矩形的4个角点\n按顺序：左上→右上→右下→左下',
            'LabelImg-OBB': '格式说明：\n第一行固定为"YOLO_OBB"\n后续：class_id x_center y_center width height angle\n(像素坐标+角度)\n\n示例内容：\nYOLO_OBB\n0 960 540 800 600 45.0\n1 480 270 400 300 0.0\n\n说明：\n包含旋转角度信息的边界框格式',
            'DOTA': '格式说明：\nx1 y1 x2 y2 x3 y3 x4 y4 class_name [difficulty]\n(像素坐标+类别名+难度)\n\n示例内容：\n100 100 200 100 200 200 100 200 plane 0\n300 300 400 300 400 400 300 400 ship 1\n\n说明：\n遥感图像标注格式，支持任意四边形\n最后的数字表示标注难度（可选）',
            'PASCAL-VOC': '格式说明：\nXML文件格式，包含边界框信息\n\n示例结构：\n<?xml version="1.0"?>\n<annotation>\n  <object>\n    <name>person</name>\n    <bndbox>\n      <xmin>100</xmin>\n      <ymin>100</ymin>\n      <xmax>200</xmax>\n      <ymax>200</ymax>\n    </bndbox>\n  </object>\n</annotation>\n\n说明：标准的目标检测XML格式'
        }
        
        example_text = examples.get(format_name, f'{format_name} 格式示例')
        
        text_widget.config(state='normal')
        text_widget.delete(1.0, tk.END)
        text_widget.insert(1.0, example_text)
        text_widget.config(state='disabled')
    
    def select_input_file(self):
        """选择输入文件"""
        input_format = self.input_format_var.get()
        if not input_format:
            return
        
        # 根据格式设置文件类型过滤
        if input_format == 'PASCAL-VOC':
            filetypes = [(t('gui.xml_files'), "*.xml"), (t('gui.all_files'), "*.*")]
        else:
            filetypes = [(t('gui.text_files'), "*.txt"), (t('gui.all_files'), "*.*")]
        
        filename = filedialog.askopenfilename(
            title=t('gui.select_input_file'),
            filetypes=filetypes
        )
        if filename:
            self.input_var.set(filename)
            # 自动检测格式（可选）
            detected = format_manager.detect_format(filename)
            if detected and detected != input_format:
                result = messagebox.askyesno(
                    t('gui.format_mismatch_title'), 
                    t('gui.format_mismatch_message').format(
                        detected=detected, selected=input_format
                    )
                )
                if result:
                    self.input_format_var.set(detected)
                    self.on_input_format_change()
            
            # 刷新类别
            self.refresh_classes()
    
    def select_input_folder(self):
        """选择输入目录"""
        input_format = self.input_format_var.get()
        if not input_format:
            return
        
        dirname = filedialog.askdirectory(title=t('gui.select_input_folder'))
        if dirname:
            self.input_var.set(dirname)
            self.refresh_classes()
    
    def select_output_folder(self):
        """选择输出目录"""
        if not self.output_format_var.get():
            return
        
        dirname = filedialog.askdirectory(title=t('gui.select_output_folder'))
        if dirname:
            self.output_var.set(dirname)
            self.update_conversion_summary()
    
    def load_classes_file(self):
        """加载类别文件"""
        filename = filedialog.askopenfilename(
            title=t('gui.select_classes_file'),
            filetypes=[
                ("classes.txt", "classes.txt"),
                (t('gui.text_files'), "*.txt"),
                (t('gui.all_files'), "*.*")
            ]
        )
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    self.current_class_names = [line.strip() for line in f.readlines() if line.strip()]
                self.update_classes_display()
            except Exception as e:
                messagebox.showerror(t('gui.error'), f"{t('gui.load_classes_error')}: {e}")
    
    def refresh_classes(self):
        """刷新类别列表"""
        input_path = self.input_var.get()
        input_format = self.input_format_var.get()
        
        if not input_path or not input_format:
            self.current_class_names = []
            self.update_classes_display()
            return
        
        try:
            format_instance = format_manager.get_format(input_format)
            
            if os.path.isfile(input_path):
                self.current_class_names = format_instance._get_class_names([input_path])
            else:
                # 目录情况
                file_paths = []
                for f in os.listdir(input_path):
                    if f.endswith(format_instance.file_extension):
                        file_paths.append(os.path.join(input_path, f))
                self.current_class_names = format_instance._get_class_names(file_paths[:5])  # 只检查前5个文件
            
            self.update_classes_display()
            self.refresh_classes_btn.config(state='normal')
            
        except Exception as e:
            self.current_class_names = []
            self.update_classes_display()
            print(f"刷新类别时出错: {e}")
    
    def update_classes_display(self):
        """更新类别显示"""
        self.classes_text.config(state='normal')
        self.classes_text.delete(1.0, tk.END)
        
        if self.current_class_names:
            class_text = f"{t('gui.detected_classes')} ({len(self.current_class_names)}):\n\n"
            for i, class_name in enumerate(self.current_class_names):
                class_text += f"{i}: {class_name}\n"
            self.classes_text.insert(1.0, class_text)
            self.classes_status.config(text=f"{t('gui.classes_count')}: {len(self.current_class_names)}", 
                                     style='Success.TLabel')
        else:
            self.classes_text.insert(1.0, t('gui.no_classes_detected'))
            self.classes_status.config(text=t('gui.no_classes_detected'), style='Info.TLabel')
        
        self.classes_text.config(state='disabled')
        self.update_conversion_summary()
    
    def set_dimensions(self, width, height):
        """设置图片尺寸"""
        self.width_var.set(str(width))
        self.height_var.set(str(height))
        self.update_conversion_summary()
    
    def update_conversion_summary(self):
        """更新转换摘要"""
        if not hasattr(self, 'conversion_summary'):
            return
            
        input_format = self.input_format_var.get() if hasattr(self, 'input_format_var') else ""
        output_format = self.output_format_var.get() if hasattr(self, 'output_format_var') else ""
        input_path = self.input_var.get() if hasattr(self, 'input_var') else ""
        output_path = self.output_var.get() if hasattr(self, 'output_var') else ""
        
        if not all([input_format, output_format, input_path, output_path]):
            self.conversion_summary.config(text=t('gui.complete_all_steps'))
            if hasattr(self, 'convert_button'):
                self.convert_button.config(state='disabled')
            return
        
        try:
            width = int(self.width_var.get()) if hasattr(self, 'width_var') and self.width_var.get() else 0
            height = int(self.height_var.get()) if hasattr(self, 'height_var') and self.height_var.get() else 0
            if width <= 0 or height <= 0:
                raise ValueError
        except ValueError:
            self.conversion_summary.config(text=t('gui.invalid_dimensions'))
            if hasattr(self, 'convert_button'):
                self.convert_button.config(state='disabled')
            return
        
        # 创建摘要文本
        summary_parts = [
            f"{t('gui.input_format')}: {input_format}",
            f"{t('gui.output_format')}: {output_format}",
            f"{t('gui.input_path')}: {os.path.basename(input_path)}",
            f"{t('gui.output_path')}: {os.path.basename(output_path)}",
            f"{t('gui.dimensions')}: {width}×{height}",
        ]
        
        if hasattr(self, 'current_class_names') and self.current_class_names:
            summary_parts.append(f"{t('gui.classes_count')}: {len(self.current_class_names)}")
        
        summary_text = "\n".join(summary_parts)
        self.conversion_summary.config(text=summary_text)
        if hasattr(self, 'convert_button'):
            self.convert_button.config(state='normal')
    
    def on_language_change(self, event=None):
        """语言切换事件处理"""
        languages = get_available_languages()
        selected = self.language_var.get()
        
        for code, name in languages.items():
            if name == selected:
                set_language(code)
                update_settings(language=code)
                messagebox.showinfo(
                    "语言已更改" if code == 'zh' else "Language Changed", 
                    "请重启应用以完全应用新语言设置。" if code == 'zh' else "Please restart the application to fully apply the new language settings."
                )
                break
    
    def start_conversion(self):
        """开始转换（在新线程中执行）"""
        input_format = self.input_format_var.get()
        output_format = self.output_format_var.get()
        input_path = self.input_var.get()
        output_path = self.output_var.get()
        
        if not all([input_format, output_format, input_path, output_path]):
            messagebox.showerror(t('gui.error'), t('gui.complete_all_steps'))
            return
        
        try:
            width = int(self.width_var.get())
            height = int(self.height_var.get())
            if width <= 0 or height <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror(t('gui.error'), t('gui.invalid_dimensions'))
            return
        
        if not os.path.exists(input_path):
            messagebox.showerror(t('gui.error'), t('gui.input_not_exists'))
            return
        
        # 禁用转换按钮
        self.convert_button.config(state='disabled')
        self.progress_var.set(0)
        self.status_var.set(t('gui.converting'))
        
        # 在新线程中执行转换
        thread = threading.Thread(target=self.perform_conversion)
        thread.daemon = True
        thread.start()
    
    def perform_conversion(self):
        """执行转换操作"""
        try:
            input_path = self.input_var.get()
            output_path = self.output_var.get()
            input_format = self.input_format_var.get()
            output_format = self.output_format_var.get()
            width = int(self.width_var.get())
            height = int(self.height_var.get())
            
            # 更新进度
            self.root.after(0, lambda: self.progress_var.set(25))
            
            # 执行转换
            if os.path.isfile(input_path):
                # 单文件转换
                format_manager.convert_file(
                    input_file=input_path,
                    output_file=os.path.join(output_path, os.path.basename(input_path)),
                    input_format=input_format,
                    output_format=output_format,
                    image_width=width,
                    image_height=height,
                    class_names=self.current_class_names if self.current_class_names else None
                )
            else:
                # 目录转换
                format_manager.convert_directory(
                    input_dir=input_path,
                    output_dir=output_path,
                    input_format=input_format,
                    output_format=output_format,
                    image_width=width,
                    image_height=height,
                    class_names=self.current_class_names if self.current_class_names else None
                )
            
            # 更新进度
            self.root.after(0, lambda: self.progress_var.set(100))
            self.root.after(0, self.conversion_completed)
            
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda: self.conversion_failed(error_msg))
    
    def conversion_completed(self):
        """转换完成处理"""
        self.status_var.set(t('gui.conversion_completed'))
        self.convert_button.config(state='normal')
        self.progress_var.set(0)
        messagebox.showinfo(t('gui.success'), t('gui.conversion_completed'))
        
        # 保存设置
        update_settings(
            last_input_format=self.input_format_var.get(),
            last_output_format=self.output_format_var.get(),
            last_image_width=int(self.width_var.get()),
            last_image_height=int(self.height_var.get())
        )
    
    def conversion_failed(self, error_msg):
        """转换失败处理"""
        self.status_var.set(t('gui.conversion_failed'))
        self.convert_button.config(state='normal')
        self.progress_var.set(0)
        messagebox.showerror(t('gui.error'), f"{t('gui.conversion_failed')}: {error_msg}")
    
    def on_closing(self):
        """窗口关闭事件"""
        # 保存窗口大小
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        update_settings(window_width=width, window_height=height)
        save_settings()
        self.root.destroy()
    
    def run(self):
        """运行GUI"""
        self.root.mainloop()


def main():
    """GUI主函数"""
    if not GUI_AVAILABLE:
        print("错误：tkinter模块不可用，无法启动图形界面")
        print("请安装完整的Python环境或安装tkinter模块")
        sys.exit(1)
    
    try:
        app = DatasetConverterGUI()
        app.run()
    except Exception as e:
        print(f"启动GUI失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 