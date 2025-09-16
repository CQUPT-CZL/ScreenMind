"""
系统托盘界面
"""
import threading
import sys
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem, Menu
import tkinter as tk
from .main_window import SettingsWindow, ResultWindow

class SystemTray:
    """系统托盘管理器"""

    def __init__(self, app_instance):
        self.app = app_instance
        self.icon = None
        self.settings_window = None
        self.is_running = False

    def create_tray_icon(self):
        """创建托盘图标"""
        # 创建一个简单的图标
        image = Image.new('RGB', (64, 64), color='blue')
        draw = ImageDraw.Draw(image)

        # 绘制一个简单的相机图标
        # 外框
        draw.rectangle([8, 16, 56, 48], outline='white', width=2)
        # 镜头
        draw.ellipse([20, 24, 44, 40], outline='white', width=2)
        # 顶部小矩形
        draw.rectangle([24, 8, 40, 16], outline='white', width=2)

        return image

    def create_menu(self):
        """创建右键菜单"""
        return Menu(
            MenuItem("ScreenMind", lambda: None, enabled=False),
            MenuItem("─" * 20, lambda: None, enabled=False),
            MenuItem("手动截图", self._manual_screenshot),
            MenuItem("设置", self._show_settings),
            MenuItem("─" * 20, lambda: None, enabled=False),
            MenuItem("退出", self._quit_application)
        )

    def start(self):
        """启动系统托盘"""
        if self.is_running:
            return

        try:
            image = self.create_tray_icon()
            menu = self.create_menu()

            self.icon = pystray.Icon(
                "ScreenMind",
                image,
                "ScreenMind - 智能截图答题助手",
                menu
            )

            self.is_running = True

            # 在新线程中运行托盘图标
            def run_tray():
                try:
                    self.icon.run()
                except Exception as e:
                    print(f"托盘图标运行失败: {e}")
                finally:
                    self.is_running = False

            tray_thread = threading.Thread(target=run_tray, daemon=True)
            tray_thread.start()

            print("系统托盘启动成功")

        except Exception as e:
            print(f"启动系统托盘失败: {e}")

    def stop(self):
        """停止系统托盘"""
        if self.icon and self.is_running:
            self.icon.stop()
            self.is_running = False

    def _manual_screenshot(self, icon=None, item=None):
        """手动触发截图"""
        try:
            if self.app:
                # 在主线程中执行截图
                threading.Thread(target=self.app.take_screenshot, daemon=True).start()
        except Exception as e:
            print(f"手动截图失败: {e}")

    def _show_settings(self, icon=None, item=None):
        """显示设置窗口"""
        try:
            def show_settings_window():
                # 创建临时root窗口（隐藏）
                root = tk.Tk()
                root.withdraw()

                settings = SettingsWindow(root)
                settings.show_settings()

                # 等待设置窗口关闭
                root.wait_window(settings.window)
                root.destroy()

            # 在新线程中显示设置窗口
            threading.Thread(target=show_settings_window, daemon=True).start()

        except Exception as e:
            print(f"显示设置窗口失败: {e}")

    def _quit_application(self, icon=None, item=None):
        """退出应用程序"""
        try:
            if self.app:
                self.app.quit()
        except Exception as e:
            print(f"退出应用程序失败: {e}")

    def show_notification(self, title: str, message: str):
        """显示系统通知"""
        try:
            if self.icon:
                self.icon.notify(message, title)
        except Exception as e:
            print(f"显示通知失败: {e}")

    def update_tooltip(self, text: str):
        """更新托盘图标提示文字"""
        try:
            if self.icon:
                self.icon.title = text
        except Exception as e:
            print(f"更新提示文字失败: {e}")