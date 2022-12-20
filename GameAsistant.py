# coding:utf-8
import time
from threading import Thread
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import win32gui
import win32con
import win32api
from PIL import ImageGrab
from pynput import keyboard, mouse


class App(tk.Tk):
    flag_mouse_click = False

    def __init__(self):
        """初始化"""
        super().__init__()
        self.title("游戏助手")
        self.protocol("WM_DELETE_WINDOW", self._on_closing_)  # 绑定窗口关闭事件
        # 取得窗口句柄
        wd_name = '咸鱼之王'
        self.hwnd = win32gui.FindWindow(0, wd_name)
        if not self.hwnd:
            print("窗口找不到，请确认窗口句柄名称：【%s】" % wd_name)
            exit()
        # 窗口显示最前面
        # win32gui.SetForegroundWindow(self.hwnd)
        # 获取窗口位置,左上角，右下角
        # left, top, right, bottom = win32gui.GetWindowRect(self.hwnd)
        self.scree_left_and_right_point = win32gui.GetWindowRect(self.hwnd)
        self.start_all_listener()
        print(self.scree_left_and_right_point)

    # 主窗口关闭事件处理
    def _on_closing_(self):
        self.destroy()

    # 开启监听剪切板线程
    def start_all_listener(self):
        # 剪切板监听线程
        Thread(target=self.thread_keyboard_listening, daemon=True).start()
        Thread(target=self.thread_mouse_click, daemon=True).start()

    def thread_mouse_click(self):
        while True:
            if self.flag_mouse_click:
                self.set_mouse_at_window_center()
                self.mouse_click()

    def thread_keyboard_listening(self):
        with keyboard.GlobalHotKeys(
                {'<ctrl>+s': self.on_start_mouse_click, '<ctrl>+t': self.on_terminal_mouse_click}) as hot_key:
            hot_key.join()

    def on_start_mouse_click(self):
        self.flag_mouse_click = True

    def on_terminal_mouse_click(self):
        self.flag_mouse_click = False

    def set_mouse_at_window_center(self):
        left, top, right, bottom = self.scree_left_and_right_point
        window_center = (left + right) // 2, (top + bottom) // 2
        win32api.SetCursorPos(window_center)

    @staticmethod
    def mouse_click():
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
        time.sleep(0.01)
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)

    def screenshot(self):
        """屏幕截图"""

        # 1、用grab函数截图，参数为左上角和右下角左标
        # image = ImageGrab.grab((417, 257, 885, 569))
        print(win32gui.IsWindowEnabled(self.hwnd))
        image = ImageGrab.grab(self.scree_left_and_right_point)
        with open('./test.jpg', 'wb') as fp:
            image.save(fp)
        # # 2、分切小图
        # # exit()
        # image_list = {}
        # offset = self.im_width  # 39
        #
        # # 8行12列
        # for x in range(8):
        #     image_list[x] = {}
        #     for y in range(12):
        #         # print("show",x, y)
        #         # exit()
        #         top = x * offset
        #         left = y * offset
        #         right = (y + 1) * offset
        #         bottom = (x + 1) * offset
        #         # 用crop函数切割成小图标，参数为图标的左上角和右下角左边
        #         im = image.crop((left, top, right, bottom))
        #         # 将切割好的图标存入对应的位置
        #         image_list[x][y] = im
        # return image_list


hz_app = App()
hz_app.mainloop()
