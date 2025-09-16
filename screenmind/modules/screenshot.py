"""
截图功能模块
"""
import io
import base64
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageGrab
from typing import Optional, Tuple, Callable
import threading

class ScreenshotCapture:
    """屏幕截图捕获器"""

    def __init__(self):
        self.root = None
        self.canvas = None
        self.start_x = 0
        self.start_y = 0
        self.current_x = 0
        self.current_y = 0
        self.rect_id = None
        self.screenshot_image = None
        self.result_callback = None
        self.is_selecting = False

    def capture_screen(self, callback: Callable[[Optional[Image.Image]], None]):
        """
        捕获屏幕截图

        Args:
            callback: 截图完成后的回调函数，参数为PIL Image对象或None
        """
        self.result_callback = callback

        try:
            # 全屏截图
            screenshot = ImageGrab.grab()

            # 创建选择界面
            self._create_selection_window(screenshot)

        except Exception as e:
            messagebox.showerror("错误", f"截图失败: {str(e)}")
            if callback:
                callback(None)

    def _create_selection_window(self, screenshot: Image.Image):
        """创建截图选择窗口"""
        self.root = tk.Toplevel()
        self.root.title("选择截图区域")
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-topmost', True)
        self.root.configure(cursor="crosshair")

        # 创建画布
        self.canvas = tk.Canvas(
            self.root,
            highlightthickness=0,
            cursor="crosshair"
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # 显示截图
        self.screenshot_image = screenshot
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # 调整图片大小以适应屏幕
        if screenshot.size != (screen_width, screen_height):
            screenshot = screenshot.resize((screen_width, screen_height), Image.Resampling.LANCZOS)

        self.photo = ImageTk.PhotoImage(screenshot)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)

        # 绑定事件
        self.canvas.bind("<Button-1>", self._on_mouse_down)
        self.canvas.bind("<B1-Motion>", self._on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_mouse_up)
        self.root.bind("<Escape>", self._on_escape)
        self.root.bind("<Return>", self._on_confirm)

        # 添加提示文字
        self.canvas.create_text(
            screen_width // 2, 50,
            text="拖拽选择区域，按Enter确认，按Esc取消",
            fill="red",
            font=("Arial", 16),
            tags="instruction"
        )

        self.root.focus_set()

    def _on_mouse_down(self, event):
        """鼠标按下事件"""
        self.start_x = event.x
        self.start_y = event.y
        self.current_x = event.x
        self.current_y = event.y
        self.is_selecting = True

        # 删除之前的选择框
        if self.rect_id:
            self.canvas.delete(self.rect_id)

    def _on_mouse_drag(self, event):
        """鼠标拖拽事件"""
        if not self.is_selecting:
            return

        self.current_x = event.x
        self.current_y = event.y

        # 删除之前的选择框
        if self.rect_id:
            self.canvas.delete(self.rect_id)

        # 绘制新的选择框
        self.rect_id = self.canvas.create_rectangle(
            self.start_x, self.start_y,
            self.current_x, self.current_y,
            outline="red", width=2
        )

    def _on_mouse_up(self, event):
        """鼠标松开事件"""
        self.current_x = event.x
        self.current_y = event.y
        self.is_selecting = False

    def _on_confirm(self, event=None):
        """确认选择"""
        if not self.rect_id:
            messagebox.showwarning("提示", "请先选择一个区域")
            return

        try:
            # 计算选择区域
            x1 = min(self.start_x, self.current_x)
            y1 = min(self.start_y, self.current_y)
            x2 = max(self.start_x, self.current_x)
            y2 = max(self.start_y, self.current_y)

            # 确保选择区域有效
            if abs(x2 - x1) < 10 or abs(y2 - y1) < 10:
                messagebox.showwarning("提示", "选择区域太小，请重新选择")
                return

            # 从原始截图中裁剪选择区域
            cropped_image = self.screenshot_image.crop((x1, y1, x2, y2))

            # 关闭选择窗口
            self.root.destroy()

            # 回调结果
            if self.result_callback:
                self.result_callback(cropped_image)

        except Exception as e:
            messagebox.showerror("错误", f"处理截图失败: {str(e)}")
            self._on_escape()

    def _on_escape(self, event=None):
        """取消选择"""
        if self.root:
            self.root.destroy()
        if self.result_callback:
            self.result_callback(None)

def image_to_base64(image: Image.Image) -> str:
    """
    将PIL Image转换为base64字符串

    Args:
        image: PIL Image对象

    Returns:
        base64编码的图片字符串
    """
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    img_data = buffer.getvalue()
    return base64.b64encode(img_data).decode('utf-8')

def capture_screenshot_async(callback: Callable[[Optional[str]], None]):
    """
    异步截图函数

    Args:
        callback: 完成回调，参数为base64编码的图片字符串或None
    """
    def on_capture_complete(image: Optional[Image.Image]):
        if image:
            try:
                base64_str = image_to_base64(image)
                callback(base64_str)
            except Exception as e:
                print(f"图片编码失败: {e}")
                callback(None)
        else:
            callback(None)

    # 在主线程中运行截图
    capture = ScreenshotCapture()
    capture.capture_screen(on_capture_complete)