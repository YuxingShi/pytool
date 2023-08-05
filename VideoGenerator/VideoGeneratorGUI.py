# coding: utf-8
import json
import os
import subprocess
import sys
from threading import Thread
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk

from tts_demo import text_to_speech
from playsound import playsound
# from moviepy.editor import *
from video_gen import generate_video

# os.environ['IMAGEIO_FFMPEG_EXE'] = '/opt/homebrew/bin/ffmpeg'

MAC_OS = False
MOUSE_RIGHT_BUTTON = '<Button-3>'
if sys.platform == 'darwin':
    MAC_OS = True
    MOUSE_RIGHT_BUTTON = '<Button-2>'


class App(tk.Tk):
    cur_file_name = None
    cur_directory = '/Users/shiyx/Desktop'
    thread_playsound = None

    def __init__(self):
        super().__init__()
        self.title("语音配图视频生成")
        self.protocol("WM_DELETE_WINDOW", self._on_closing_)  # 绑定窗口关闭事件
        # 菜单
        self.menu_bar = tk.Menu(self)
        self.config(menu=self.menu_bar)
        self.file_menu = tk.Menu(self.menu_bar, tearoff=False)
        self.menu_bar.add_cascade(label="文件", menu=self.file_menu)
        self.file_menu.add_command(label="选择目录", command=self.select_directory)
        self.file_menu.add_command(label="选择文件", command=self.select_file)
        self.tool_menu = tk.Menu(self.menu_bar, tearoff=False)
        self.menu_bar.add_cascade(label="工具", menu=self.tool_menu)
        frame_main = tk.Frame(self)
        frame_main.pack(side='top', fill=tk.Y)
        # 左Frame
        frame_left = tk.LabelFrame(frame_main, text='文件列表')
        frame_left.pack(side='left', fill=tk.Y)
        frame_file_type = tk.Frame(frame_left)
        frame_file_type.pack(side='top')
        tk.Label(frame_file_type, text='文件类型').pack(side='left')
        self.combobox_file_type = ttk.Combobox(frame_file_type, state='readonly')
        self.combobox_file_type.pack(side='left')
        self.combobox_file_type.bind('<<ComboboxSelected>>', self.on_combobox_selected)
        frame_treeview = tk.Frame(frame_left)
        frame_treeview.pack(side='top', fill=tk.BOTH, expand=True)
        self.treeview = ttk.Treeview(frame_treeview)
        self.treeview.pack(side='left', fill=tk.BOTH, expand=True)
        self.treeview.bind("<<TreeviewSelect>>", self.on_treeview_select)
        # 绑定右击事件，显示上下文菜单
        self.treeview.bind(MOUSE_RIGHT_BUTTON, self.treeview_context_menu_callback)
        # treeview 垂直滚动条
        self.treeview_scrollbar_y = ttk.Scrollbar(frame_treeview, orient=tk.VERTICAL, command=self.treeview.yview)
        self.treeview_scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.treeview.configure(yscrollcommand=self.treeview_scrollbar_y.set)
        # treeview水平滚动条
        self.treeview_scrollbar_x = ttk.Scrollbar(frame_left, orient=tk.HORIZONTAL, command=self.treeview.xview)
        self.treeview_scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.treeview.configure(xscrollcommand=self.treeview_scrollbar_x.set)
        # treeview 创建上下文菜单
        self.treeview_context_menu = tk.Menu(self, tearoff=0)
        # self.treeview_context_menu.add_command(label="获取歌曲信息", command=self.get_song_information)
        self.treeview_context_menu.add_command(label="打开文件所在目录", command=self.open_file_directory)
        # self.treeview_context_menu.add_command(label="FTP传送", command=self.ftp_transmit)

        # 中Frame
        frame_middle = tk.Frame(frame_main)
        frame_middle.pack(side='right', fill=tk.BOTH, expand=True)
        frame_image = tk.LabelFrame(frame_middle, text='配图')
        frame_image.pack(side='top', fill=tk.X)
        self.label_image = tk.Label(frame_image)
        self.label_image.pack(side='left')
        frame_text = tk.LabelFrame(frame_middle, text='文稿')
        frame_text.pack(side='top')
        self.text_scripts = tk.Text(frame_text)
        self.text_scripts.pack(side='top', expand=True, fill=tk.BOTH)
        self.btn_save = ttk.Button(frame_text, text="生成视频", command=self.start_generate_video)
        self.btn_save.pack(side='top', pady=5)

        frame_status = tk.Frame(self)
        frame_status.pack(side='bottom', fill=tk.X)
        # 创建状态栏
        self.label_status_bar = ttk.Label(frame_status, text="就绪", relief=tk.SUNKEN)
        self.label_status_bar.pack(side='left', fill=tk.X, expand=True)
        # 创建进度条
        self.progress = ttk.Progressbar(frame_status, mode='determinate')
        self.progress.pack(side='left', fill=tk.X, expand=True)

        # # 右边Frame
        # frame_right = tk.LabelFrame(self, text='浏览器')
        # frame_right.pack(side='right', fill=tk.BOTH, expand=True)
        self._init_data()

    def _on_closing_(self):
        self.destroy()

    def _init_data(self):
        file_type_list = ['ALL', 'mp3', 'mp4', 'txt']
        self.combobox_file_type['values'] = file_type_list
        self.combobox_file_type.set(file_type_list[0])
        self.load_directory(self.cur_directory)

    @staticmethod
    def is_image(file_path):
        try:
            Image.open(file_path)
            return True
        except IOError:
            return False

    @staticmethod
    def get_dict_from_json(filename):
        file_path = os.path.abspath(filename)
        if os.path.isfile(file_path):
            with open(file_path, 'r', encoding='utf-8') as fp:
                return json.load(fp)

    @staticmethod
    def write2file(text: str, filename:str):
        with open(filename, 'w', encoding='utf-8') as fp:
            fp.write(text)

    @staticmethod
    def readfile(filename: str):
        with open(filename, 'r', encoding='utf-8')as fp:
            return fp.read()

    @staticmethod
    def write_dict2json(filename, obj: dict):
        with open(filename, 'w')as fp:
            json.dump(obj, fp, ensure_ascii=False, indent=4)

    @staticmethod
    def remove_empty_directories(directory):
        for root, dirs, files in os.walk(directory, topdown=False):
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                if not os.listdir(dir_path):  # 检查目录是否为空
                    os.rmdir(dir_path)

    # @staticmethod
    # def generate_video(audio_file, image_file, output_file):
    #     # 加载音频文件
    #     audio_clip = AudioFileClip(audio_file)
    #
    #     # 创建配图片段
    #     image_clip = ImageClip(image_file).set_duration(audio_clip.duration)
    #
    #     # 将音频与配图合成为视频
    #     video_clip = image_clip.set_audio(audio_clip)
    #
    #     # 保存视频文件
    #     video_clip.write_videofile(output_file, fps=1, codec='libx264', audio_codec="aac")
    #
    # @staticmethod
    # def merge_video_clips(video_files, output_file):
    #     # 创建一个空的视频剪辑对象
    #     final_clip = None
    #
    #     # 逐个加载和拼接视频片段
    #     for file in video_files:
    #         clip = VideoFileClip(file)
    #         if final_clip is None:
    #             final_clip = clip
    #         else:
    #             final_clip = concatenate_videoclips([final_clip, clip])
    #
    #     # 保存最终合并的视频
    #     final_clip.write_videofile(output_file, codec='libx264')

    def select_directory(self):
        self.cur_directory = filedialog.askdirectory()
        if self.cur_directory:
            self.load_directory(self.cur_directory)

    def select_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.load_file(file_path)

    @staticmethod
    def _create_directorys(dirs: list):
        dst_dir_name = os.path.join(*dirs)
        if not os.path.exists(dst_dir_name):
            os.makedirs(dst_dir_name)
        return dst_dir_name

    def load_directory(self, path, parent="", file_type=None):
        if not parent:
            self.treeview.delete(*self.treeview.get_children())
            # 添加根节点
            root_node = self.treeview.insert("", tk.END, text=path, open=True)
            parent = root_node
        # 遍历目录下的子目录和文件
        for item in sorted(os.listdir(path)):
            item_path = os.path.join(path, item)
            is_dir = os.path.isdir(item_path)
            if is_dir:
                # 添加子目录节点
                dir_node = self.treeview.insert(parent, tk.END, text=item, open=False)
                self.load_directory(item_path, dir_node)
            else:
                # 添加文件节点
                if file_type:
                    if item.lower().endswith(file_type):
                        self.treeview.insert(parent, tk.END, text=item)
                else:
                    self.treeview.insert(parent, tk.END, text=item)

    def load_file(self, file_path):
        self.treeview.delete(*self.treeview.get_children())
        # 添加根节点
        root_node = self.treeview.insert("", tk.END, text=file_path)

    def on_combobox_selected(self, *event):
        value = self.combobox_file_type.get().strip()
        if value == 'ALL':
            ft = None
        else:
            ft = value
        self.load_directory(self.cur_directory, file_type=ft)

    def on_treeview_select(self, *event):
        selected_item = self.treeview.focus()
        self.cur_file_name = self.get_treeview_node_full_path(selected_item)
        name, ext = os.path.splitext(self.cur_file_name)
        print(ext)
        if os.path.isfile(self.cur_file_name):
            if self.is_image(self.cur_file_name):
                self.show_image(self.cur_file_name)
                txt_filename = '{}.txt'.format(name)
                mp3_filename = '{}.mp3'.format(name)
                if os.path.exists(txt_filename):
                    self.show_text(txt_filename)
                if os.path.exists(mp3_filename):
                    self.play_sound(mp3_filename)
            elif ext in ['.mp3', '.m4a']:
                self.play_sound(self.cur_file_name)
            elif ext in ['.txt']:
                self.show_text(self.cur_file_name)

    def show_text(self, filename: str):
        text = self.readfile(filename)
        self.text_scripts.delete(1.0, tk.END)
        self.text_scripts.insert(1.0, text)

    def play_sound(self, file_path):
        self.thread_playsound = Thread(target=playsound, args=(file_path,), daemon=True)
        self.thread_playsound.start()
        if self.thread_playsound.is_alive():
            return

    def get_treeview_node_full_path(self, item):
        item_text = self.treeview.item(item)["text"]
        parent_item = self.treeview.parent(item)
        if parent_item:
            item_text = self.get_treeview_node_full_path(parent_item) + '/' + item_text
            return item_text
        else:
            return item_text

    def treeview_context_menu_callback(self, event):
        # 选择鼠标右击的行
        selected_item = self.treeview.identify_row(event.y)
        if selected_item:
            # 弹出上下文菜单
            self.treeview.focus(selected_item)
            self.treeview.selection_set(selected_item)
            self.treeview_context_menu.post(event.x_root, event.y_root)

    def open_file_directory(self):
        path, _ = os.path.split(self.cur_file_name)
        if MAC_OS:
            cmds = 'open "{}"'.format(path)
        else:
            cmds = 'start {}'.format(path)
            print(cmds)
        subprocess.Popen(cmds, shell=True)

    def show_image(self, path):
        image = Image.open(path)
        image.thumbnail((300, 300))  # 调整图片大小
        photo = ImageTk.PhotoImage(image)
        self.label_image.configure(image=photo)
        self.label_image.image = photo

    def start_generate_video(self, *event):
        text_scripts = self.text_scripts.get(1.0, tk.END).strip()
        if text_scripts == '':
            messagebox.showinfo('提示', '您未输入的任何脚本文字！')
            return
        name, ext = os.path.splitext(self.cur_file_name)
        txt_filename = '{}.txt'.format(name)
        mp3_filename = '{}.mp3'.format(name)
        mp4_filename = '{}.mp4'.format(name)
        Thread(target=self._thread_generate_video, args=(text_scripts, txt_filename, mp3_filename, self.cur_file_name, mp4_filename), daemon=True).start()

    def _thread_generate_video(self, text, txt_path, mp3_path, image_path, mp4_path):
        self.progress['value'] = 0
        text_to_speech(text, mp3_path)
        self.write2file(text, txt_path)
        self.progress['value'] = 50
        generate_video(mp3_path, image_path, mp4_path)
        self.progress['value'] = 100
        self.load_directory(self.cur_directory)


if __name__ == "__main__":
    App = App()
    App.mainloop()
