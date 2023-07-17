# coding: utf-8
import os
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import requests
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, TCON, TEXT
from mutagen.mp4 import MP4


class MP3InfoEditor:
    cur_directory = None
    cur_file_name = None

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("MP3文件信息编辑")
        # 菜单
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)
        self.file_menu = tk.Menu(self.menu_bar, tearoff=False)
        self.menu_bar.add_cascade(label="文件", menu=self.file_menu)
        self.file_menu.add_command(label="选择目录", command=self.select_directory)
        self.file_menu.add_command(label="选择文件", command=self.select_file)

        # 左Frame
        frame_left = tk.LabelFrame(self.root, text='文件列表')
        frame_left.pack(side='left', fill=tk.Y)
        frame_treeview = tk.Frame(frame_left)
        frame_treeview.pack(side='top', fill=tk.Y, expand=True)
        self.treeview = ttk.Treeview(frame_treeview)
        self.treeview.pack(side='left', fill=tk.BOTH, expand=True)
        self.treeview.bind("<<TreeviewSelect>>", self.on_treeview_select)
        # 绑定右击事件，显示上下文菜单
        self.treeview.bind("<Button-3>", self.treeview_context_menu_callback)
        # treeview 垂直滚动条
        self.treeview_scrollbar_y = ttk.Scrollbar(frame_treeview, orient=tk.VERTICAL, command=self.treeview.yview)
        self.treeview_scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.treeview.configure(yscrollcommand=self.treeview_scrollbar_y.set)
        # treeview水平滚动条
        self.treeview_scrollbar_x = ttk.Scrollbar(frame_left, orient=tk.HORIZONTAL, command=self.treeview.xview)
        self.treeview_scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.treeview.configure(xscrollcommand=self.treeview_scrollbar_x.set)
        # treeview 创建上下文菜单
        self.treeview_context_menu = tk.Menu(self.root, tearoff=0)
        self.treeview_context_menu.add_command(label="获取歌曲信息", command=self.get_song_information)
        self.treeview_context_menu.add_command(label="打开文件所在目录", command=self.open_file_directory)
        # 中Frame
        frame_middle = tk.LabelFrame(self.root, text='文件信息')
        frame_middle.pack(side='right', fill=tk.BOTH, expand=True)
        frame_right_r1 = tk.Frame(frame_middle)
        frame_right_r1.pack(side='top', fill=tk.X)
        self.label_title = tk.Label(frame_right_r1, text="标题:")
        self.label_title.pack(side='left', pady=5)
        self.entry_title = tk.Entry(frame_right_r1)
        self.entry_title.pack(side='left')
        frame_right_r2 = tk.Frame(frame_middle)
        frame_right_r2.pack(side='top', fill=tk.X)
        self.label_artist = tk.Label(frame_right_r2, text="歌手:")
        self.label_artist.pack(side='left', pady=5)
        self.entry_artist = tk.Entry(frame_right_r2)
        self.entry_artist.pack(side='left')
        frame_right_r3 = tk.Frame(frame_middle)
        frame_right_r3.pack(side='top', fill=tk.X)
        self.label_album = tk.Label(frame_right_r3, text="专辑:")
        self.label_album.pack(side='left', pady=5)
        self.entry_album = tk.Entry(frame_right_r3)
        self.entry_album.pack(side='left')
        frame_right_r4 = tk.Frame(frame_middle)
        frame_right_r4.pack(side='top', fill=tk.X)
        self.label_year = tk.Label(frame_right_r4, text="年份:")
        self.label_year.pack(side='left', pady=5)
        self.entry_year = tk.Entry(frame_right_r4)
        self.entry_year.pack(side='left')
        frame_right_r5 = tk.Frame(frame_middle)
        frame_right_r5.pack(side='top', fill=tk.X)
        self.label_genre = tk.Label(frame_right_r5, text="风格:")
        self.label_genre.pack(side='left', pady=5)
        self.entry_genre = tk.Entry(frame_right_r5)
        self.entry_genre.pack(side='left')
        frame_right_r6 = tk.Frame(frame_middle)
        frame_right_r6.pack(side='top', fill=tk.X)
        self.label_lyric = tk.Label(frame_right_r6, text="歌词")
        self.label_lyric.pack(side='top', pady=5)
        self.entry_lyric = tk.Text(frame_right_r6)
        self.entry_lyric.pack(side='top', fill=tk.BOTH)
        frame_right_bt = tk.Frame(frame_middle)
        frame_right_bt.pack(side=tk.BOTTOM, fill=tk.X)
        self.btn_save = tk.Button(frame_right_bt, text="保存", command=self.save_info)
        self.btn_save.pack(side='right', pady=10)
        # # 右边Frame
        # frame_right = tk.LabelFrame(self.root, text='浏览器')
        # frame_right.pack(side='right', fill=tk.BOTH, expand=True)
        self._init_data()

    def _init_data(self):
        self.load_directory('F:\mp3')

    def select_directory(self):
        self.cur_directory = filedialog.askdirectory()
        if self.cur_directory:
            self.load_directory(self.cur_directory)

    def select_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.load_file(file_path)

    def load_directory(self, path, parent=""):
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
                self.treeview.insert(parent, tk.END, text=item)

    def load_file(self, file_path):
        self.treeview.delete(*self.treeview.get_children())
        # 添加根节点
        root_node = self.treeview.insert("", tk.END, text=file_path)

    def on_treeview_select(self, event):
        selected_item = self.treeview.focus()
        self.cur_file_name = self.get_treeview_node_full_path(selected_item)
        if os.path.isfile(self.cur_file_name):
            # messagebox.showinfo("选中项", f"您选择了：{full_path_item_text}")
            self.load_mp3_info(self.cur_file_name)

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
        cmds = 'start {}'.format(path)
        subprocess.Popen(cmds, shell=True)

    def get_song_information(self):
        _, filename = os.path.split(self.cur_file_name)
        baike_url = 'https://baike.baidu.com/item/{}'.format(filename.split('.m')[0].replace(' ', ''))
        # requests.get()

        subprocess.Popen('start {}'.format(baike_url.replace(' ', '')), shell=True)

    @staticmethod
    def get_id3_tags(file_path: str):
        tags = {}
        audio = None
        if file_path.lower().endswith('.mp3'):
            audio = ID3(file_path)
            if 'TIT2' in audio:
                tags['title'] = audio['TIT2'].text[0]
            if 'TPE1' in audio:
                tags['artist'] = audio['TPE1'].text[0]
            if 'TALB' in audio:
                tags['album'] = audio['TALB'].text[0]
            if 'TDRC' in audio:
                tags['year'] = audio['TDRC'].text[0]
            if 'TCON' in audio:
                tags['genre'] = audio['TCON'].text[0]
            if 'TEXT' in audio:
                tags['lyric'] = audio['TEXT'].text[0]
        elif file_path.lower().endswith('.m4a'):
            audio = MP4(file_path)
            if '\xa9nam' in audio:
                tags['title'] = audio['\xa9nam'][0]
            if '\xa9ART' in audio:
                tags['artist'] = audio['\xa9ART'][0]
            if '\xa9alb' in audio:
                tags['album'] = audio['\xa9alb'][0]
            if '\xa9day' in audio:
                tags['year'] = audio['\xa9day'][0]
            if 'gnre' in audio:
                tags['genre'] = audio['gnre'][0]
        print('audio', audio)
        return tags

    def get_audio_tags(self, file_path: str):
        """
        获取音频文件的标签信息
        :param file_path:
        :return:
        """
        tags = {}
        if file_path.lower().endswith('.mp3'):
            audio = MP3(file_path)
            if 'title' in audio.tags:  # 标题
                tags['title'] = audio.tags['title'][0]
            if 'artist' in audio.tags:  # 艺术家
                tags['artist'] = audio.tags['artist'][0]
            if 'album' in audio.tags:  # 专辑
                tags['album'] = audio.tags['album'][0]
            if 'year' in audio.tags:  # 年份
                tags['year'] = audio.tags['year'][0]
            if 'genre' in audio.tags:  # 流派
                tags['genre'] = audio.tags['genre'][0]
        elif file_path.lower().endswith('.m4a'):
            audio = MP4(file_path)
            if '\xa9nam' in audio.tags:
                tags['title'] = audio.tags['\xa9nam'][0]
            if '\xa9ART' in audio.tags:
                tags['artist'] = audio.tags['\xa9ART'][0]
            if '\xa9alb' in audio.tags:
                tags['album'] = audio.tags['\xa9alb'][0]
            if '\xa9day' in audio.tags:
                tags['year'] = audio.tags['\xa9day'][0]
            if 'gnre' in audio.tags:
                tags['genre'] = audio.tags['gnre'][0]
        return tags

    def load_mp3_info(self, filename: str):
        try:
            tags = self.get_id3_tags(filename)
            file_path, _ = os.path.splitext(filename)
            _, file_name = os.path.split(file_path)
            if file_name.count('-') == 1:
                f_title, f_artist = file_name.split('-')
            else:
                f_title, f_artist = file_name, ''
            print(tags)
            self.entry_title.delete(0, tk.END)
            self.entry_artist.delete(0, tk.END)
            self.entry_album.delete(0, tk.END)
            self.entry_year.delete(0, tk.END)
            self.entry_genre.delete(0, tk.END)
            self.entry_lyric.delete(1.0, tk.END)
            title = tags.get('title')
            if not title:
                title = f_title
            artist = tags.get('artist')
            if not artist:
                artist = f_artist
            self.entry_title.insert(tk.END, title)
            self.entry_artist.insert(tk.END, artist)
            self.entry_album.insert(tk.END, tags.get('album', ''))
            self.entry_year.insert(tk.END, tags.get('year', ''))
            self.entry_genre.insert(tk.END, tags.get('genre', ''))
            self.entry_lyric.insert(1.0, tags.get('lyric', ''))
        except Exception as e:
            messagebox.showerror("错误", str(e))

    @staticmethod
    def write_tags(file_path: str, tags: dict):
        if file_path.lower().endswith('.mp3'):
            audio = MP3(file_path)
            audio.delete()
            for key, value in tags.items():
                audio[key] = value
            audio.save()

        elif file_path.lower().endswith('.m4a'):
            audio = MP4(file_path)
            audio.delete()
            for key, value in tags.items():
                audio[key] = [value]
            audio.save()

    @staticmethod
    def write_id3_tags(file_path: str, tags: dict):
        if file_path.lower().endswith('.mp3'):
            audio = ID3()
            if 'title' in tags:
                audio['TIT2'] = TIT2(encoding=3, text=tags['title'])
            if 'artist' in tags:
                audio['TPE1'] = TPE1(encoding=3, text=tags['artist'])
            if 'album' in tags:
                audio['TALB'] = TALB(encoding=3, text=tags['album'])
            if 'year' in tags:
                audio['TDRC'] = TDRC(encoding=3, text=tags['year'])
            if 'genre' in tags:
                audio['TCON'] = TCON(encoding=3, text=tags['genre'])
            audio.save(file_path)
        elif file_path.lower().endswith('.m4a'):
            audio = MP4()
            if 'title' in tags:
                audio['\xa9nam'] = [tags['title']]
            if 'artist' in tags:
                audio['\xa9ART'] = [tags['artist']]
            if 'album' in tags:
                audio['\xa9alb'] = [tags['album']]
            if 'year' in tags:
                audio['\xa9day'] = [tags['year']]
            if 'genre' in tags:
                audio['gnre'] = [tags['genre']]
            audio.save(file_path)

    def save_info(self):
        try:
            if not self.cur_file_name:
                messagebox.showerror("提示", '未选择文件！')
                return
            tags = dict()
            tags['title'] = self.entry_title.get().strip()
            tags['artist'] = self.entry_artist.get().strip()
            tags['album'] = self.entry_album.get().strip()
            tags['year'] = self.entry_year.get().strip()
            tags['genre'] = self.entry_genre.get().strip()
            self.write_id3_tags(self.cur_file_name, tags)
            messagebox.showinfo("成功", "信息保存成功！")
        except Exception as e:
            messagebox.showerror("错误", str(e))


if __name__ == "__main__":
    editor = MP3InfoEditor()
    editor.root.mainloop()
