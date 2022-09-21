# coding:utf-8
import os
import asyncio
import socket
import json
import re
import subprocess
import sys
import tkinter as tk
from threading import Thread
from tkinter import messagebox

import wmi
import websockets
from app import app

PLATFORM = sys.platform


class WebSocketServer(Thread):
    def __init__(self, loop):
        Thread.__init__(self)
        self.main_loop = loop
        self.data_dict = self.get_json('data.json')

    def run(self):
        asyncio.set_event_loop(self.main_loop)
        asyncio.get_event_loop().run_until_complete(websockets.serve(self.echo, 'localhost', 8765))
        asyncio.get_event_loop().run_forever()

    async def echo(self, websocket, path):
        async for rec_message in websocket:
            if rec_message == 'information':
                message = json.dumps(self.data_dict.get('LocalMachine'))
            else:
                message = ''
            await websocket.send(message)

    @staticmethod
    def get_json(filename):
        file_path = os.path.abspath(filename)
        if os.path.isfile(file_path):
            with open(file_path, 'r') as fp:
                return json.load(fp)
        else:
            return None


class App(tk.Tk):
    About = "版本号信息 V1.0 \n\n 慧舟科技"
    current_listening_port = 8848
    proxy_server_thread = None
    data_dict = {}
    data_json = os.path.abspath('data.json')

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
        frame_info = tk.LabelFrame(self, text='本机信息')
        frame_info.pack(side=tk.TOP, fill=tk.BOTH)
        self.text_info = tk.Text(frame_info, width=36, height=5)
        self.text_info.pack(side=tk.TOP)
        # 创建状态栏
        self.status_value = tk.StringVar()
        self.status_value.set('剪切板关键字转换（开启）：')
        status_bar = tk.Label(self, textvariable=self.status_value, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self._init_data()
        self.start_all_listener()

    def _on_closing_(self):
        self.destroy()

    def show_about(self):
        messagebox.showinfo('版本', self.About)

    def _init_data(self):
        self.data_dict = self.get_json(self.data_json)
        ip = self.get_localhost_ip()
        bios, baseboard, cpu = self.get_serial_number()
        self.data_dict['LocalMachine'] = {'ip': ip, 'biosSn': bios, 'baseboardSn': baseboard, 'cpuSn': cpu}
        text = '本机IP：{}\nBIOS序列号：{}\n主板序列号：{}\nCPU序列号：{}' \
            .format(self.data_dict.get('LocalMachine').get('ip'),
                    self.data_dict.get('LocalMachine').get('biosSn'),
                    self.data_dict.get('LocalMachine').get('baseboardSn'),
                    self.data_dict.get('LocalMachine').get('cpuSn'))
        self.text_info.insert(1.0, text)
        self.text_info.configure(state='disabled')
        with open(self.data_json, 'w') as fp:
            json.dump(self.data_dict, fp)

    @staticmethod
    def write2file(filename, content):
        with open(filename, 'w') as fp:
            fp.write(content)

    @staticmethod
    def get_json(filename):
        file_path = os.path.abspath(filename)
        if os.path.isfile(file_path):
            with open(file_path, 'r') as fp:
                return json.load(fp)
        else:
            return None

    @staticmethod
    def cmd_executor(cmd: str):
        if PLATFORM == 'darwin' or PLATFORM.count('linux'):
            sys_code = 'UTF-8'
        else:
            sys_code = 'GBK'
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return p.communicate()[0].decode(sys_code)  # 不用调用标准输出

    # def get_localhost_ip(self):
    #     output = self.cmd_executor('ipconfig /all')
    #     ip = re.findall('IPv4.*: (.*?)\(', output, flags=re.DOTALL)[0]
    #     return ip

    def get_localhost_ip(self):
        soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            ip = self.data_dict.get('service').get('ip')
            port = self.data_dict.get('service').get('port')
            soc.connect((ip, port))
            ip = soc.getsockname()[0]
        except Exception as e:
            ip = None
        finally:
            soc.close()
        return ip

    def get_serial_number(self):
        return_list = []
        if PLATFORM == 'win32':

            c = wmi.WMI()
            def cpuid():
                # CPU序列号
                cc = ""
                for cpu in c.Win32_Processor():
                    # print(cpu.ProcessorId.strip())
                    cc += cpu.ProcessorId.strip()
                return cc
            def zhubanid():
                # 主板序列号
                cc = ""
                for board_id in c.Win32_BaseBoard():
                    # print(board_id.SerialNumber)
                    cc += board_id.SerialNumber
                return cc
            def biosid():
                # bios序列号
                cc = ""
                for bios_id in c.Win32_BIOS():
                    # print(bios_id.SerialNumber.strip())
                    cc += bios_id.SerialNumber.strip()
                return cc
            return biosid(), zhubanid(), cpuid()
        elif PLATFORM == 'darwin':
            cmd_bios = "/usr/sbin/system_profiler SPHardwareDataType |fgrep 'Serial'|awk '{print $NF}'"
            pattern = '(.*?)\n'
            cmd_list = [cmd_bios]
        elif PLATFORM.count('linux'):
            cmd_bios = "sudo dmidecode -t system|grep 'Serial Number'|awk -F ':' '{print $NF}'"
            cmd_list = [cmd_bios]
            pattern = '(.*?)\n'
        else:
            return '无法识别的系统类型！'

        for cmd in cmd_list:
            output = self.cmd_executor(cmd)
            serial_number = re.findall(pattern, output, flags=re.DOTALL)[0]
            return_list.append(serial_number)
        return return_list

    def start_all_listener(self):
        self.start_http_server()
        self.start_websocket_server()

    @staticmethod
    def start_websocket_server():
        new_loop = asyncio.new_event_loop()
        web_soc = WebSocketServer(new_loop)
        web_soc.setDaemon(True)
        web_soc.start()

    def start_http_server(self):
        # 监听线程
        self.proxy_server_thread = Thread(target=self.thread_http_server, daemon=True)
        self.proxy_server_thread.start()

    def thread_http_server(self):
        self.status_value.set('正在运行')
        app.run(host='0.0.0.0', port=8848)
        self.status_value.set('已停止')


hz_app = App()
hz_app.mainloop()
