# coding:utf-8
import os
import time
import tkinter as tk
from tkinter import messagebox
from threading import Thread
from PIL import Image
import requests
from app import app
from cp_apply import Fj122gov


class App(tk.Tk):
    About = "版本号信息 V1.0 \n\n 慧舟驾培"
    current_listening_port = 8848
    proxy_server_thread = None
    quartz_time = 60 * 1000 * 5

    def __init__(self):
        # 创建主窗口,用于容纳其它组件 给主窗口设置标题内容
        super().__init__()
        self.title("慧舟驾培")
        self.protocol("WM_DELETE_WINDOW", self._on_closing_)  # 绑定窗口关闭事件
        # 创建一个菜单栏
        self.menu_bar = tk.Menu(self)
        self.menu_bar.add_command(label="关于", command=self.show_about)
        self.config(menu=self.menu_bar)
        frame_operation = tk.LabelFrame(self, text='服务配置')
        frame_operation.pack(side=tk.TOP)
        tk.Label(frame_operation, text='监听端口').pack(side=tk.LEFT)
        self.entry_listen_port = tk.Entry(frame_operation, width=5)
        self.entry_listen_port.pack(side=tk.LEFT)
        self.button_start_server = tk.Button(frame_operation, text='启动服务', command=self._start_server)
        self.button_start_server.pack(side=tk.LEFT)
        self.button_stop_server = tk.Button(frame_operation, text='停止服务', command=self._stop_server)
        self.button_stop_server.pack(side=tk.LEFT)
        tk.Button(frame_operation, text='手动登录', command=self._login).pack(side=tk.LEFT)
        frame_log = tk.LabelFrame(self, text='日志')
        frame_log.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)
        vs = tk.Scrollbar(frame_log)
        vs.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_log = tk.Text(frame_log, yscrollcommand=vs.set)
        self.text_log.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)
        vs.config(command=self.text_log.yview)
        # 创建状态栏
        frame_status_bar = tk.Frame(self)
        frame_status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_value1 = tk.StringVar()
        tk.Label(frame_status_bar, text='预报名服务状态', bd=1, relief=tk.SUNKEN).pack(side=tk.LEFT, fill=tk.X)
        status_bar1 = tk.Label(frame_status_bar, textvariable=self.status_value1, bd=1, relief=tk.SUNKEN)
        status_bar1.pack(side=tk.LEFT, fill=tk.X)
        tk.Label(frame_status_bar, text='交警服务状态', bd=1, relief=tk.SUNKEN).pack(side=tk.LEFT, fill=tk.X)
        self.status_value2 = tk.StringVar()
        status_bar2 = tk.Label(frame_status_bar, textvariable=self.status_value2, bd=1, relief=tk.SUNKEN)
        status_bar2.pack(side=tk.LEFT, fill=tk.X)
        self._init_data()
        self.start_all_listener()

    def _init_data(self):
        self.entry_listen_port.delete(0, tk.END)
        self.entry_listen_port.insert(tk.END, self.current_listening_port)
        self.my_job()

    def _show_window(self, icon, item):
        icon.stop()
        self.deiconify()

    def _quit_window(self, icon, item):
        icon.stop()
        self.destroy()

    def show_about(self):
        messagebox.showinfo('版本', self.About)

    def _on_closing_(self):
        result = messagebox.askyesno('提示', '是否关闭程序？否则最小化到系统托盘！')
        if result:
            self._stop_server()
            self.destroy()
        else:
            self.iconify()
            self.withdraw()
            image = Image.open(self.path_icon_file)
            menu = (item('显示主界面', self._show_window), item('退出', self._quit_window))
            icon = pystray.Icon("name", image, '慧舟驾培', menu)
            icon.run()

    def start_all_listener(self):
        # 剪切板监听线程
        try:
            self.current_listening_port = int(self.entry_listen_port.get())
        except ValueError as e:
            messagebox.showerror('错误', '请输入整数数字作为端口号')
            return
        self.proxy_server_thread = Thread(target=self.thread_proxy_server, daemon=True)
        self.proxy_server_thread.start()

    def thread_proxy_server(self):
        self.status_value1.set('正在运行')
        self.entry_listen_port.configure(state='disabled')
        self.button_start_server.configure(state='disabled')
        self.button_stop_server.configure(state='normal')
        # server = pywsgi.WSGIServer(('0.0.0.0', self.current_listening_port), app)
        # server.start()
        app.run(host='0.0.0.0', port=self.current_listening_port)
        self.status_value1.set('已停止')

    def _login(self):
        Thread(target=self.thread_login, daemon=True).start()

    def thread_login(self):
        fj = Fj122gov()
        ret, msg = fj.login()
        self._operation_log(msg)
        self.status_value2.set(msg)

    def _stop_server(self):
        Thread(target=self.thread_stop_server, daemon=True).start()

    def thread_stop_server(self):
        headers = {"Content-Type": "application/json",
                   "Authorization": "Basic aHp0ZWNoOnN1Y2Nlc3M="
                   }
        requests.post('http://127.0.0.1:{}/shutdown'.format(self.current_listening_port), headers=headers)
        self.status_value1.set('正在停止')
        self.entry_listen_port.configure(state='normal')
        self.button_start_server.configure(state='normal')
        self.button_stop_server.configure(state='disabled')

    def _start_server(self):
        self.start_all_listener()

    def _operation_log(self, text):
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        log_string = '{} {}\n'.format(timestamp, text)
        self.text_log.insert(tk.END, log_string)

    def my_job(self):
        Thread(target=self.thread_my_job, daemon=True).start()
        self.after(self.quartz_time, self.my_job)

    def thread_my_job(self):
        fj = Fj122gov()
        ret, msg = fj.test_login_status()
        self._operation_log(msg)
        self.status_value2.set(msg)
        if ret:
            ret, msg = fj.login()
            self._operation_log(msg)
            self.status_value2.set(msg)



hz_app = App()
hz_app.mainloop()
