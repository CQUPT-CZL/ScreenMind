"""
ScreenMind主应用程序
"""
import sys
import os
import tkinter as tk
import threading
import time
from typing import Optional

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, os.path.dirname(current_dir))

from screenmind.modules.screenshot import capture_screenshot_async
from screenmind.modules.hotkey import register_screenshot_hotkey, stop_hotkey_listener
from screenmind.modules.ai_service import question_analyzer
from screenmind.gui.system_tray import SystemTray
from screenmind.gui.main_window import ResultWindow
from screenmind.config import config

class ScreenMindApp:
    """ScreenMind主应用程序类"""

    def __init__(self):
        self.root = None
        self.tray = None
        self.result_window = None
        self.is_running = False
        self.processing = False

    def initialize(self):
        """初始化应用程序"""
        try:
            print("正在初始化ScreenMind...")

            # 创建隐藏的主窗口
            self.root = tk.Tk()
            self.root.withdraw()  # 隐藏主窗口

            # 初始化结果窗口
            self.result_window = ResultWindow(self.root)

            # 初始化系统托盘
            self.tray = SystemTray(self)

            # 注册快捷键
            if not register_screenshot_hotkey(self.take_screenshot):
                print("警告: 快捷键注册失败")
                return False

            print("ScreenMind初始化完成")
            return True

        except Exception as e:
            print(f"初始化失败: {e}")
            return False

    def start(self):
        """启动应用程序"""
        if not self.initialize():
            print("应用程序初始化失败")
            return

        try:
            # 启动系统托盘
            self.tray.start()

            # 显示启动通知
            self.tray.show_notification(
                "ScreenMind启动成功",
                f"按 {config.hotkey} 开始截图分析"
            )

            self.is_running = True
            print(f"ScreenMind已启动，快捷键: {config.hotkey}")
            print("应用程序在后台运行，可通过系统托盘访问")

            # 主事件循环
            self.run_main_loop()

        except KeyboardInterrupt:
            print("\n接收到中断信号，正在退出...")
            self.quit()
        except Exception as e:
            print(f"应用程序运行出错: {e}")
            self.quit()

    def run_main_loop(self):
        """运行主事件循环"""
        try:
            while self.is_running:
                # 处理tkinter事件
                if self.root:
                    try:
                        self.root.update()
                    except tk.TclError:
                        # 窗口已关闭
                        break

                # 短暂休眠避免CPU占用过高
                time.sleep(0.1)

        except Exception as e:
            print(f"主循环出错: {e}")
        finally:
            self.quit()

    def take_screenshot(self):
        """执行截图并分析"""
        if self.processing:
            print("正在处理中，请稍候...")
            return

        print("开始截图...")
        self.processing = True

        try:
            # 显示处理通知
            if self.tray:
                self.tray.show_notification("正在截图", "请选择要分析的区域")

            # 异步截图
            capture_screenshot_async(self._on_screenshot_complete)

        except Exception as e:
            print(f"截图失败: {e}")
            self.processing = False
            if self.tray:
                self.tray.show_notification("截图失败", str(e))

    def _on_screenshot_complete(self, image_base64: Optional[str]):
        """截图完成回调"""
        try:
            if not image_base64:
                print("截图被取消")
                if self.tray:
                    self.tray.show_notification("截图取消", "未选择有效区域")
                return

            print("截图完成，正在分析...")
            if self.tray:
                self.tray.show_notification("正在分析", "AI正在识别题目...")

            # 在新线程中进行AI分析
            def analyze_image():
                try:
                    result = question_analyzer.analyze_question_image(image_base64)
                    # 在主线程中显示结果
                    self.root.after(0, lambda: self._show_analysis_result(result))
                except Exception as e:
                    error_result = {
                        'success': False,
                        'error': f"分析失败: {str(e)}"
                    }
                    self.root.after(0, lambda: self._show_analysis_result(error_result))

            analysis_thread = threading.Thread(target=analyze_image, daemon=True)
            analysis_thread.start()

        except Exception as e:
            print(f"处理截图失败: {e}")
            if self.tray:
                self.tray.show_notification("处理失败", str(e))
        finally:
            self.processing = False

    def _show_analysis_result(self, result_data: dict):
        """显示分析结果"""
        try:
            print("显示分析结果...")

            # 显示结果窗口
            if self.result_window:
                self.result_window.show_result(result_data)

            # 显示通知
            if self.tray:
                if result_data.get('success'):
                    answer = result_data.get('answer', '无答案')[:50]  # 限制长度
                    self.tray.show_notification("分析完成", f"答案: {answer}")
                else:
                    error_msg = result_data.get('error', '分析失败')
                    self.tray.show_notification("分析失败", error_msg)

        except Exception as e:
            print(f"显示结果失败: {e}")

    def quit(self):
        """退出应用程序"""
        print("正在退出ScreenMind...")
        self.is_running = False

        try:
            # 停止快捷键监听
            stop_hotkey_listener()

            # 停止系统托盘
            if self.tray:
                self.tray.stop()

            # 关闭主窗口
            if self.root:
                self.root.quit()
                self.root.destroy()

        except Exception as e:
            print(f"退出时出错: {e}")

        print("ScreenMind已退出")
        sys.exit(0)

def main():
    """主函数"""
    print("=" * 50)
    print("ScreenMind - 智能截图答题助手")
    print("版本: 0.1.0")
    print("=" * 50)

    # 检查环境
    if not config.gemini_api_key:
        print("警告: 未设置GEMINI_API_KEY环境变量")
        print("请通过以下方式设置API密钥:")
        print("1. 环境变量: export GEMINI_API_KEY='your-api-key'")
        print("2. 启动后通过托盘菜单 -> 设置 进行配置")
        print()

    # 创建并启动应用
    app = ScreenMindApp()

    try:
        app.start()
    except KeyboardInterrupt:
        print("\n接收到中断信号")
        app.quit()
    except Exception as e:
        print(f"应用程序异常退出: {e}")
        app.quit()

if __name__ == "__main__":
    main()