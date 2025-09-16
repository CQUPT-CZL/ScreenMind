"""
主GUI界面
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
from typing import Optional
import sys
import os

class ResultWindow:
    """结果显示窗口"""

    def __init__(self, parent=None):
        self.window = None
        self.parent = parent

    def show_result(self, result_data: dict):
        """
        显示分析结果

        Args:
            result_data: 分析结果数据
        """
        if self.window:
            self.window.destroy()

        self.window = tk.Toplevel(self.parent) if self.parent else tk.Tk()
        self.window.title("ScreenMind - 分析结果")
        self.window.geometry("500x400")
        self.window.attributes('-topmost', True)

        # 创建主框架
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        row = 0

        # 显示结果
        if result_data.get('success'):
            # 题目类型
            ttk.Label(main_frame, text="题目类型:", font=("Arial", 10, "bold")).grid(
                row=row, column=0, sticky=tk.W, pady=(0, 5)
            )
            ttk.Label(main_frame, text=result_data.get('question_type', '未知')).grid(
                row=row, column=1, sticky=tk.W, pady=(0, 5)
            )
            row += 1

            # 题目内容
            if result_data.get('question_content'):
                ttk.Label(main_frame, text="题目内容:", font=("Arial", 10, "bold")).grid(
                    row=row, column=0, sticky=(tk.W, tk.N), pady=(0, 5)
                )
                content_text = tk.Text(main_frame, height=3, wrap=tk.WORD)
                content_text.insert(tk.END, result_data['question_content'])
                content_text.config(state=tk.DISABLED)
                content_text.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
                row += 1

            # 答案
            ttk.Label(main_frame, text="答案:", font=("Arial", 12, "bold"), foreground="red").grid(
                row=row, column=0, sticky=(tk.W, tk.N), pady=(0, 5)
            )
            answer_text = tk.Text(main_frame, height=2, wrap=tk.WORD, font=("Arial", 11, "bold"))
            answer_text.insert(tk.END, result_data.get('answer', '无答案'))
            answer_text.config(state=tk.DISABLED, bg="#ffffcc")
            answer_text.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
            row += 1

            # 解析
            if result_data.get('explanation'):
                ttk.Label(main_frame, text="解析:", font=("Arial", 10, "bold")).grid(
                    row=row, column=0, sticky=(tk.W, tk.N), pady=(0, 5)
                )
                explanation_text = scrolledtext.ScrolledText(main_frame, height=6, wrap=tk.WORD)
                explanation_text.insert(tk.END, result_data['explanation'])
                explanation_text.config(state=tk.DISABLED)
                explanation_text.grid(row=row, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
                main_frame.rowconfigure(row, weight=1)
                row += 1

        else:
            # 显示错误信息
            ttk.Label(main_frame, text="错误:", font=("Arial", 12, "bold"), foreground="red").grid(
                row=row, column=0, sticky=tk.W, pady=(0, 5)
            )
            error_text = scrolledtext.ScrolledText(main_frame, height=10, wrap=tk.WORD)
            error_msg = result_data.get('error', '未知错误')
            if result_data.get('raw_response'):
                error_msg += f"\n\nAI原始响应:\n{result_data['raw_response']}"
            error_text.insert(tk.END, error_msg)
            error_text.config(state=tk.DISABLED)
            error_text.grid(row=row, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
            main_frame.rowconfigure(row, weight=1)
            row += 1

        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row, column=0, columnspan=2, pady=(10, 0))

        # 复制答案按钮
        if result_data.get('success') and result_data.get('answer'):
            copy_btn = ttk.Button(
                button_frame,
                text="复制答案",
                command=lambda: self._copy_to_clipboard(result_data['answer'])
            )
            copy_btn.pack(side=tk.LEFT, padx=(0, 10))

        # 关闭按钮
        close_btn = ttk.Button(button_frame, text="关闭", command=self.window.destroy)
        close_btn.pack(side=tk.LEFT)

        # 窗口居中
        self._center_window()

        # 设置焦点
        self.window.focus_set()

    def _copy_to_clipboard(self, text: str):
        """复制文本到剪贴板"""
        try:
            self.window.clipboard_clear()
            self.window.clipboard_append(text)
            messagebox.showinfo("提示", "答案已复制到剪贴板")
        except Exception as e:
            messagebox.showerror("错误", f"复制失败: {e}")

    def _center_window(self):
        """窗口居中显示"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')

class SettingsWindow:
    """设置窗口"""

    def __init__(self, parent=None):
        self.window = None
        self.parent = parent
        self.provider_var = tk.StringVar()
        self.model_var = tk.StringVar()
        self.api_key_var = tk.StringVar()
        self.provider_models = {}

    def show_settings(self):
        """显示设置窗口"""
        if self.window:
            self.window.lift()
            return

        self.window = tk.Toplevel(self.parent) if self.parent else tk.Tk()
        self.window.title("ScreenMind - 设置")
        self.window.geometry("500x400")
        self.window.resizable(False, False)

        # 创建主框架
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # AI模型选择
        ttk.Label(main_frame, text="AI模型设置", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(0, 10))

        # 模型提供商选择
        provider_frame = ttk.Frame(main_frame)
        provider_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(provider_frame, text="模型提供商:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)

        from ..config import config
        providers = list(config.available_models.keys())
        self.provider_combo = ttk.Combobox(
            provider_frame,
            textvariable=self.provider_var,
            values=[config.available_models[p]["name"] for p in providers],
            state="readonly",
            width=30
        )
        self.provider_combo.pack(side=tk.RIGHT)
        self.provider_combo.bind('<<ComboboxSelected>>', self._on_provider_changed)

        # 具体模型选择
        model_frame = ttk.Frame(main_frame)
        model_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(model_frame, text="具体模型:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)

        self.model_combo = ttk.Combobox(
            model_frame,
            textvariable=self.model_var,
            state="readonly",
            width=30
        )
        self.model_combo.pack(side=tk.RIGHT)

        # API密钥设置
        ttk.Separator(main_frame, orient='horizontal').pack(fill=tk.X, pady=(10, 10))

        self.api_key_label = ttk.Label(main_frame, text="API密钥:", font=("Arial", 10, "bold"))
        self.api_key_label.pack(anchor=tk.W, pady=(0, 5))

        # API密钥输入框
        api_key_frame = ttk.Frame(main_frame)
        api_key_frame.pack(fill=tk.X, pady=(0, 10))

        self.api_key_entry = ttk.Entry(api_key_frame, textvariable=self.api_key_var, show="*", width=50)
        self.api_key_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        show_btn = ttk.Button(api_key_frame, text="显示", command=self._toggle_api_key_visibility)
        show_btn.pack(side=tk.RIGHT, padx=(5, 0))

        # 帮助链接
        self.help_label = ttk.Label(main_frame, text="", foreground="blue", cursor="hand2")
        self.help_label.pack(anchor=tk.W, pady=(0, 10))

        # 当前模型信息
        ttk.Separator(main_frame, orient='horizontal').pack(fill=tk.X, pady=(10, 10))
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(info_frame, text="当前使用模型:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        self.current_model_label = ttk.Label(info_frame, text="", foreground="green")
        self.current_model_label.pack(side=tk.LEFT, padx=(10, 0))

        # 快捷键说明
        if sys.platform == 'darwin':
            hotkey_text = "快捷键: Cmd + Shift + Q"
        else:
            hotkey_text = "快捷键: Ctrl + Shift + Q"
        ttk.Label(main_frame, text=hotkey_text, font=("Arial", 10)).pack(anchor=tk.W, pady=(0, 20))

        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)

        ttk.Button(button_frame, text="测试连接", command=self._test_connection).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="保存", command=self._save_settings).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="取消", command=self._close_window).pack(side=tk.RIGHT)

        # 加载当前设置
        self._load_settings()

        # 窗口关闭事件
        self.window.protocol("WM_DELETE_WINDOW", self._close_window)

        # 窗口居中
        self._center_window()

    def _on_provider_changed(self, event=None):
        """提供商改变时更新模型列表"""
        from ..config import config

        provider_names = [config.available_models[p]["name"] for p in config.available_models.keys()]
        selected_name = self.provider_var.get()

        if selected_name in provider_names:
            # 找到对应的provider key
            provider_key = None
            for key, info in config.available_models.items():
                if info["name"] == selected_name:
                    provider_key = key
                    break

            if provider_key:
                models = config.available_models[provider_key]["models"]
                self.model_combo.config(values=models)
                if models:
                    self.model_var.set(models[0])

                # 更新API密钥标签和帮助文本
                api_key_env = config.available_models[provider_key]["api_key_env"]
                self.api_key_label.config(text=f"{api_key_env}:")

                # 更新帮助链接
                help_links = {
                    "gemini": "获取API密钥: https://makersuite.google.com/app/apikey",
                    "qwen": "获取API密钥: https://dashscope.console.aliyun.com/apiKey",
                    "openai": "获取API密钥: https://platform.openai.com/api-keys"
                }
                self.help_label.config(text=help_links.get(provider_key, ""))

                # 加载对应的API密钥
                if provider_key == "gemini":
                    self.api_key_var.set(config.gemini_api_key)
                elif provider_key == "qwen":
                    self.api_key_var.set(config.qwen_api_key)
                elif provider_key == "openai":
                    self.api_key_var.set(config.openai_api_key)

    def _toggle_api_key_visibility(self):
        """切换API密钥可见性"""
        if self.api_key_entry.cget("show") == "*":
            self.api_key_entry.config(show="")
        else:
            self.api_key_entry.config(show="*")

    def _load_settings(self):
        """加载当前设置"""
        from ..config import config
        from ..modules.ai_service import ai_service

        # 设置当前提供商
        current_provider_name = config.available_models[config.current_provider]["name"]
        self.provider_var.set(current_provider_name)

        # 触发提供商改变事件来更新模型列表
        self._on_provider_changed()

        # 设置当前模型
        self.model_var.set(config.current_model)

        # 显示当前模型信息
        model_info = ai_service.get_current_model_info()
        self.current_model_label.config(text=f"{model_info['name']} - {model_info['model']}")

    def _test_connection(self):
        """测试AI连接"""
        try:
            from ..modules.ai_service import ai_service

            # 临时更新设置进行测试
            provider_name = self.provider_var.get()
            model = self.model_var.get()
            api_key = self.api_key_var.get().strip()

            if not api_key:
                messagebox.showwarning("警告", "请先输入API密钥")
                return

            # 找到provider key
            from ..config import config
            provider_key = None
            for key, info in config.available_models.items():
                if info["name"] == provider_name:
                    provider_key = key
                    break

            if not provider_key:
                messagebox.showerror("错误", "无效的模型提供商")
                return

            # 临时设置模型
            old_provider = ai_service.current_provider
            old_model = ai_service.current_model

            ai_service.set_model(provider_key, model, api_key)

            # 测试连接
            if ai_service.test_connection():
                messagebox.showinfo("成功", "连接测试成功！")
            else:
                messagebox.showerror("失败", "连接测试失败，请检查API密钥和网络连接")
                # 恢复原设置
                ai_service.set_model(old_provider, old_model)

        except Exception as e:
            messagebox.showerror("错误", f"测试连接失败: {e}")

    def _save_settings(self):
        """保存设置"""
        try:
            from ..modules.ai_service import ai_service
            from ..config import config

            provider_name = self.provider_var.get()
            model = self.model_var.get()
            api_key = self.api_key_var.get().strip()

            if not api_key:
                messagebox.showwarning("警告", "请输入有效的API密钥")
                return

            # 找到provider key
            provider_key = None
            for key, info in config.available_models.items():
                if info["name"] == provider_name:
                    provider_key = key
                    break

            if not provider_key:
                messagebox.showerror("错误", "无效的模型提供商")
                return

            # 保存设置
            if ai_service.set_model(provider_key, model, api_key):
                messagebox.showinfo("成功", "设置已保存")
                self._close_window()
            else:
                messagebox.showerror("错误", "保存设置失败")

        except Exception as e:
            messagebox.showerror("错误", f"保存设置失败: {e}")

    def _close_window(self):
        """关闭窗口"""
        if self.window:
            self.window.destroy()
            self.window = None

    def _center_window(self):
        """窗口居中显示"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')