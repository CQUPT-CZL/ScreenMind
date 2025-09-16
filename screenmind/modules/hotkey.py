"""
全局快捷键监听模块
"""
import threading
from typing import Callable, Optional
from pynput import keyboard
import sys
import os

class HotkeyListener:
    """全局快捷键监听器"""

    def __init__(self):
        self.listener = None
        self.callback = None
        self.hotkey_combination = None
        self.pressed_keys = set()
        self.is_running = False

    def register_hotkey(self, hotkey: str, callback: Callable[[], None]) -> bool:
        """
        注册全局快捷键

        Args:
            hotkey: 快捷键组合，格式如 "cmd+shift+q" 或 "ctrl+shift+q"
            callback: 快捷键触发时的回调函数

        Returns:
            bool: 注册是否成功
        """
        try:
            self.callback = callback
            self.hotkey_combination = self._parse_hotkey(hotkey)

            if not self.hotkey_combination:
                print(f"无法解析快捷键: {hotkey}")
                return False

            # 停止之前的监听器
            self.stop()

            # 启动新的监听器
            self.listener = keyboard.Listener(
                on_press=self._on_key_press,
                on_release=self._on_key_release
            )

            self.listener.start()
            self.is_running = True
            print(f"快捷键 {hotkey} 注册成功")
            return True

        except Exception as e:
            print(f"注册快捷键失败: {e}")
            return False

    def _parse_hotkey(self, hotkey: str) -> Optional[set]:
        """
        解析快捷键字符串

        Args:
            hotkey: 快捷键字符串，如 "cmd+shift+q"

        Returns:
            解析后的按键集合
        """
        try:
            keys = hotkey.lower().split('+')
            parsed_keys = set()

            for key in keys:
                key = key.strip()
                if key == 'cmd' and sys.platform == 'darwin':
                    parsed_keys.add(keyboard.Key.cmd)
                elif key == 'ctrl':
                    parsed_keys.add(keyboard.Key.ctrl_l)
                elif key == 'shift':
                    parsed_keys.add(keyboard.Key.shift)
                elif key == 'alt':
                    parsed_keys.add(keyboard.Key.alt_l)
                elif len(key) == 1:
                    parsed_keys.add(keyboard.KeyCode.from_char(key))
                else:
                    # 处理特殊键
                    special_keys = {
                        'space': keyboard.Key.space,
                        'enter': keyboard.Key.enter,
                        'tab': keyboard.Key.tab,
                        'esc': keyboard.Key.esc,
                        'escape': keyboard.Key.esc,
                    }
                    if key in special_keys:
                        parsed_keys.add(special_keys[key])
                    else:
                        print(f"未知的键: {key}")
                        return None

            return parsed_keys

        except Exception as e:
            print(f"解析快捷键失败: {e}")
            return None

    def _on_key_press(self, key):
        """按键按下事件"""
        try:
            # 标准化按键
            normalized_key = self._normalize_key(key)
            if normalized_key:
                self.pressed_keys.add(normalized_key)

            # 检查是否匹配快捷键组合
            if self.hotkey_combination and self.pressed_keys >= self.hotkey_combination:
                self._trigger_callback()

        except Exception as e:
            print(f"处理按键事件失败: {e}")

    def _on_key_release(self, key):
        """按键释放事件"""
        try:
            normalized_key = self._normalize_key(key)
            if normalized_key and normalized_key in self.pressed_keys:
                self.pressed_keys.remove(normalized_key)
        except Exception as e:
            print(f"处理按键释放事件失败: {e}")

    def _normalize_key(self, key):
        """标准化按键"""
        try:
            # 处理修饰键
            if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                return keyboard.Key.ctrl_l
            elif key == keyboard.Key.shift_l or key == keyboard.Key.shift_r:
                return keyboard.Key.shift
            elif key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
                return keyboard.Key.alt_l
            elif key == keyboard.Key.cmd_l or key == keyboard.Key.cmd_r:
                return keyboard.Key.cmd
            else:
                return key
        except:
            return key

    def _trigger_callback(self):
        """触发回调函数"""
        if self.callback:
            try:
                # 在新线程中执行回调，避免阻塞监听器
                thread = threading.Thread(target=self.callback, daemon=True)
                thread.start()
            except Exception as e:
                print(f"执行回调函数失败: {e}")

    def stop(self):
        """停止监听器"""
        if self.listener and self.is_running:
            self.listener.stop()
            self.is_running = False
            self.pressed_keys.clear()

    def is_listening(self) -> bool:
        """检查是否正在监听"""
        return self.is_running and self.listener and self.listener.running

# 全局快捷键监听器实例
hotkey_listener = HotkeyListener()

def register_screenshot_hotkey(callback: Callable[[], None]) -> bool:
    """
    注册截图快捷键

    Args:
        callback: 截图回调函数

    Returns:
        bool: 注册是否成功
    """
    # 根据系统选择快捷键
    if sys.platform == 'darwin':  # macOS
        hotkey = "cmd+shift+q"
    else:  # Windows/Linux
        hotkey = "ctrl+shift+q"

    return hotkey_listener.register_hotkey(hotkey, callback)

def stop_hotkey_listener():
    """停止快捷键监听"""
    hotkey_listener.stop()