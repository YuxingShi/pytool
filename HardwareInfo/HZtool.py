# coding:utf-8
import os
import re
import subprocess
import sys
import time
import tkinter as tk
from tkinter import messagebox
from threading import Thread
import socket
import json
from app import app

PLATFORM = sys.platform


class App(tk.Tk):
    About = "版本号信息 V1.0 \n\n 慧舟科技"
    current_listening_port = 8848
    proxy_server_thread = None
    data_dict = None
    data_json = 'data.json'
    serial_number_file = 'serial_number'
    ip_file = 'ip'

    def __init__(self):
        # 创建主窗口,用于容纳其它组件 给主窗口设置标题内容
        super().__init__()
        self.title("慧舟科技")
        self.protocol("WM_DELETE_WINDOW", self._on_closing_)  # 绑定窗口关闭事件
        self.resizable(width=False, height=False)  # 设置窗口不可调节大小
        # 创建一个菜单栏
        self.menu_bar = tk.Menu(self)
        self.menu_bar.add_command(label="关于", command=self.show_about)
        self.config(menu=self.menu_bar)
        frame_ip = tk.LabelFrame(self, text='本机信息')
        frame_ip.pack(side=tk.TOP, fill=tk.BOTH)
        self.value_ip = tk.StringVar()  # '本机IP：'
        self.value_serial_number = tk.StringVar()  # '本机序列号：'
        tk.Label(frame_ip, textvariable=self.value_ip).pack(side=tk.TOP)
        tk.Label(frame_ip, textvariable=self.value_serial_number).pack(side=tk.TOP)
        # 创建状态栏
        self.status_value = tk.StringVar()
        self.status_value.set('剪切板关键字转换（开启）：')
        status_bar = tk.Label(self, textvariable=self.status_value, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.start_all_listener()

    def _on_closing_(self):
        self.destroy()

    def show_about(self):
        messagebox.showinfo('版本', self.About)

    def _init_data(self):
        self.value_ip.set('本机IP：{}'.format(self.data_dict.get('ip')))
        self.value_serial_number.set('本机序列号：{}'.format(self.data_dict.get('serialNumber')))
        with open(self.data_json, 'w') as fp:
            json.dump(self.data_dict, fp)

    @staticmethod
    def get_localhost_ip():
        soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            soc.connect(('8.8.8.8', 80))
            ip = soc.getsockname()[0]
        except Exception as e:
            ip = None
        finally:
            soc.close()
        return ip

    @staticmethod
    def get_serial_number():
        if PLATFORM == 'win32':
            cmd = 'wmic bios get serialnumber'
            sys_code = 'GBK'
            pattern = '\r\r\n(.*?)\r\r'
        elif PLATFORM == 'darwin':
            cmd = "/usr/sbin/system_profiler SPHardwareDataType |fgrep 'Serial'|awk '{print $NF}'"
            sys_code = 'UTF-8'
            pattern = '(.*?)\n'
        elif PLATFORM.count('linux'):
            cmd = "sudo dmidecode -t system|grep 'Serial Number'|awk -F ':' '{print $NF}'"
            sys_code = 'UTF-8'
        else:
            return '无法识别的系统类型！'
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = p.stdout.read().decode(sys_code)
        output_list = re.findall(pattern, output, flags=re.DOTALL)
        return output_list[0]

    @staticmethod
    def write2file(filename, content):
        with open(filename, 'w') as fp:
            fp.write(content)

    def start_all_listener(self):
        # 监听线程
        self.proxy_server_thread = Thread(target=self.thread_proxy_server, daemon=True)
        self.proxy_server_thread.start()

    def thread_proxy_server(self):
        self.status_value.set('正在运行')
        self.data_dict = {'ip': self.get_localhost_ip(), 'serialNumber': self.get_serial_number()}
        self._init_data()
        app.run(host='0.0.0.0', port=self.current_listening_port)
        self.status_value.set('已停止')


hz_app = App()
hz_app.mainloop()
