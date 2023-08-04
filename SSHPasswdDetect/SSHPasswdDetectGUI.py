# coding:utf-8
import os
import json
from threading import Thread
from concurrent.futures import ThreadPoolExecutor, as_completed
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import paramiko


class App(tk.Tk):
    path_ssh = os.path.abspath('./OpenSSH-Win64')
    path_hosts = os.path.abspath('hosts.json')
    path_passwd = os.path.abspath('passwd.txt')
    dict_hosts = None
    list_passwd = None
    all_tasks = None
    tpe = ThreadPoolExecutor(max_workers=8)

    def __init__(self):
        super().__init__()
        self.title("测试工作任务面板")
        self.protocol("WM_DELETE_WINDOW", self._on_closing_)  # 绑定窗口关闭事件
        self.attributes('-topmost', False, '-fullscreen', False)
        # 禁止用户调整窗口大小
        self.resizable(False, False)
        frame_row1 = tk.Frame(self)
        frame_row1.pack(side='top')
        tk.Label(frame_row1, text='主机IP').pack(side='left')
        self.entry_ip = ttk.Entry(frame_row1)
        self.entry_ip.pack(side='left')
        tk.Label(frame_row1, text='端口(默认：22)').pack(side='left')
        self.entry_port = ttk.Entry(frame_row1, width=5)
        self.entry_port.pack(side='left')
        self.button_detect = ttk.Button(frame_row1, text='开始探测', command=self.detect_start)
        self.button_detect.pack(side='left')
        frame_row2 = tk.Frame(self)
        frame_row2.pack(side='top', fill=tk.X)
        tk.Label(frame_row2, text='用户名：').pack(side='left')
        self.entry_username = ttk.Entry(frame_row2)
        self.entry_username.pack(side='left')
        tk.Label(frame_row2, text='密码：').pack(side='left')
        self.entry_password = ttk.Entry(frame_row2)
        self.entry_password.pack(side='left')
        frame_row3 = tk.Frame(self)
        frame_row3.pack(side='bottom', fill=tk.X)
        # 创建状态栏
        self.label_status_bar = ttk.Label(frame_row3, text="就绪", relief=tk.SUNKEN)
        self.label_status_bar.pack(side='left', fill=tk.X, expand=True)
        # 创建进度条
        self.progress = ttk.Progressbar(frame_row3, mode='determinate')
        self.progress.pack(side='left', fill=tk.X, expand=True)
        self._init_data()

    def _init_data(self):
        self.entry_port.insert(0, '22')
        self.entry_username.insert(0, 'root')
        self.dict_hosts = self.read_json(self.path_hosts)
        self.list_passwd = self.get_line_from_file(self.path_passwd)
        # self.update_progress()

    def _on_closing_(self):
        self.destroy()

    def update_progress(self):
        self.progress['value'] += 10
        if self.progress['value'] >= 100:
            self.progress['value'] = 0
        self.after(1000, self.update_progress)

    @staticmethod
    def read_json(file_name):
        with open(file_name, 'r')as fp:
            try:
                dict_obj = json.load(fp)
                return dict_obj
            except json.decoder.JSONDecodeError as e:
                dict_obj = {}
                return dict_obj

    @staticmethod
    def write_dict2json(obj: dict, file_name: str):
        with open(file_name, 'w')as fp:
            json.dump(obj, fp)

    @staticmethod
    def get_line_from_file(file_name: str):
        with open(file_name, 'r') as fp:
            return [line.strip('\n') for line in fp.readlines()]

    @staticmethod
    def connect_host_test(ip='10.168.1.173', port=22, user='root', password='root'):
        try:
            # 创建ssh客户端
            client = paramiko.SSHClient()
            # 第一次ssh远程时会提示输入yes或者no
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            # 密码方式远程连接
            client.connect(ip, port, username=user, password=password, timeout=60)
            client.close()
            return 0, (ip, port, user, password)
        except paramiko.AuthenticationException as e:
            return 1, '{} {} {} 密码错误'.format(ip, port, user, password)
        except Exception as e:
            return 2, '{} {} {} 主机连接失败！'.format(ip, port, user, password)

    def detect_start(self, *event):
        ip = self.entry_ip.get().strip()
        if ip == '':
            messagebox.showinfo('提示', '请输入主机IP')
            return
        self.all_tasks = [self.tpe.submit(self.connect_host_test, ip=ip, password=passwd) for passwd in self.list_passwd]
        Thread(target=self._thread_detect_start, daemon=True).start()

    def _thread_detect_start(self):
        passwd = '未知'
        for task in as_completed(self.all_tasks):
            ret, result = task.result()
            if ret:
                self.progress['value'] += 1
                continue
            else:
                print(result)
                passwd = result[3]
                self.entry_password.delete(0, tk.END)
                self.entry_password.insert(0, passwd)
                self.dict_hosts[result[0]] = {'port': result[1], 'user': result[2], 'passwd': passwd}
                self.write_dict2json(self.dict_hosts, self.path_hosts)
                self.progress['value'] = 100
                break
        messagebox.showinfo('提示', '密码为：【{}】'.format(passwd))
        self.progress['value'] = 0


if __name__ == "__main__":
    hz_app = App()
    hz_app.mainloop()
