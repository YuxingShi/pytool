# coding: utf-8
import os
import re
import shutil
import subprocess
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from urllib.parse import quote

import requests
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, TCON, USLT, _util
from mutagen.mp4 import MP4


MAC_OS = False
MOUSE_RIGHT_BUTTON = '<Button-3>'
if sys.platform == 'darwin':
    MAC_OS = True
    MOUSE_RIGHT_BUTTON = '<Button-2>'


headers_str = '''
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
Accept-Encoding: gzip, deflate, br
Accept-Language: zh-CN,zh;q=0.9
Connection: keep-alive
Host: baike.baidu.com
sec-ch-ua: "Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"
sec-ch-ua-mobile: ?0
sec-ch-ua-platform: "Windows"
Sec-Fetch-Dest: document
Sec-Fetch-Mode: navigate
Sec-Fetch-Site: none
Sec-Fetch-User: ?1
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36
'''


def get_dict_by_sep(raw_str: str, sep: str) -> dict:
    result = dict()
    items = re.findall('(.+){}(.+)\n'.format(sep), raw_str)
    for key, value in items:
        result[key] = value
    print(result)
    return result


class MP3InfoEditor:
    cur_directory = None
    cur_file_name = None
    headers = get_dict_by_sep(headers_str, ': ')
    # root_path = r'F:\mp3'
    root_path = '/Users/shiyx/Music/Music/Media.localized/Music'

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
        self.tool_menu = tk.Menu(self.menu_bar, tearoff=False)
        self.menu_bar.add_cascade(label="工具", menu=self.tool_menu)

        # 左Frame
        frame_left = tk.LabelFrame(self.root, text='文件列表')
        frame_left.pack(side='left', fill=tk.Y)
        frame_treeview = tk.Frame(frame_left)
        frame_treeview.pack(side='top', fill=tk.Y, expand=True)
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
        self.entry_title.pack(side='left', fill=tk.X, expand=True)
        self.btn_save = ttk.Button(frame_right_r1, text="保存标签", command=self.save_info)
        self.btn_save.pack(side='left', pady=5)
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
        self.text_lyric = tk.Text(frame_right_r6)
        self.text_lyric.pack(side='top', fill=tk.BOTH)
        frame_right_bt = tk.Frame(frame_middle)
        frame_right_bt.pack(side=tk.BOTTOM, fill=tk.X)

        # # 右边Frame
        # frame_right = tk.LabelFrame(self.root, text='浏览器')
        # frame_right.pack(side='right', fill=tk.BOTH, expand=True)
        self._init_data()

    def _init_data(self):
        self.load_directory(self.root_path)

    def select_directory(self):
        self.cur_directory = filedialog.askdirectory()
        if self.cur_directory:
            self.load_directory(self.cur_directory)
            self._init_compoent_data()

    def select_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.load_file(file_path)
            self._init_compoent_data()

    @staticmethod
    def _create_directorys(dirs: list):
        dst_dir_name = os.path.join(*dirs)
        if not os.path.exists(dst_dir_name):
            os.makedirs(dst_dir_name)
        return dst_dir_name

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
        if MAC_OS:
            cmds = 'open "{}"'.format(path)
        else:
            cmds = 'start {}'.format(path)
            print(cmds)
        subprocess.Popen(cmds, shell=True)

    @staticmethod
    def request_internet(url: str, headers=None):
        resp = requests.get(url, headers=headers, verify=False)
        if resp.status_code == 200:
            return resp.text

    @staticmethod
    def get_song_info_dict(html_text: str) -> dict:
        result = dict()
        pattern_publish_date = re.compile('''>发行日期</dt>\n<dd[^>]+>\n*(.*?)\n*</dd>''', flags=re.DOTALL)
        pattern_belong_album = re.compile('''>所属专辑</dt>\n<dd[^>]+>\n*(.*?)\n*</dd>''', flags=re.DOTALL)
        pattern_genre = re.compile('''>音乐风格</dt>\n<dd[^>]+>\n*(.*?)\n*</dd>''', flags=re.DOTALL)
        publish_date = pattern_publish_date.findall(html_text)
        belong_album = pattern_belong_album.findall(html_text)
        genre = pattern_genre.findall(html_text)
        result['year'] = publish_date
        result['album'] = belong_album
        result['genre'] = genre
        return result

    def get_song_information(self):
        title = self.entry_title.get().strip()
        artist = self.entry_artist.get().strip()
        kw = '{} {}'.format(title, artist)
        # baike_url = 'https://baike.baidu.com/item/{}'.format(quote(title))
        baike_url = 'https://www.baidu.com/s?wd={}'.format(quote(kw))
        if MAC_OS:
            cmds = 'open {}'.format(baike_url)
        else:
            cmds = 'start {}'.format(baike_url)
        subprocess.Popen(cmds, shell=True)
        # html = self.request_internet(url=baike_url, headers=self.headers)

    @staticmethod
    def get_id3_tags(file_path: str):
        tags = {
            'title': '',
            'artist': '未知',
            'album': '未知',
            'year': '未知',
            'genre': '未知',
            'lyric': '未知'
        }
        try:
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
                if 'USLT::XXX' in audio:
                    tags['lyric'] = audio['USLT::XXX'].text
                print(audio)
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
                if '\xa9gen' in audio:
                    tags['genre'] = audio['\xa9gen'][0]
                if '\xa9lyr' in audio:
                    tags['lyric'] = audio['\xa9lyr'][0]
                print(audio)
        except _util.ID3NoHeaderError as e:
            print(str(e))
        return tags
    
    def _init_compoent_data(self):
        """
        清理界面上所有信息
        :return:
        """
        self.entry_title.delete(0, tk.END)
        self.entry_artist.delete(0, tk.END)
        self.entry_album.delete(0, tk.END)
        self.entry_year.delete(0, tk.END)
        self.entry_genre.delete(0, tk.END)
        self.text_lyric.delete(1.0, tk.END)

    def load_mp3_info(self, filename: str):
        tags = self.get_id3_tags(filename)
        file_path, _ = os.path.splitext(filename)
        _, file_name = os.path.split(file_path)
        self._init_compoent_data()
        title = tags.get('title')
        if not title:
            title = file_name
        self.entry_title.insert(tk.END, title)
        self.entry_artist.insert(tk.END, tags.get('artist', ''))
        self.entry_album.insert(tk.END, tags.get('album', ''))
        self.entry_year.insert(tk.END, tags.get('year', ''))
        self.entry_genre.insert(tk.END, tags.get('genre', ''))
        self.text_lyric.insert(1.0, tags.get('lyric', ''))

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
        try:
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
                if 'lyric' in tags:
                    audio['USLT::XXX'] = USLT(encoding=3, text=tags['lyric'])
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
                if 'lyric' in tags:
                    audio['\xa9lyr'] = [tags['lyric']]
                if 'genre' in tags:
                    audio['\xa9gen'] = [tags['genre']]
                audio.save(file_path)
            return  True
        except Exception as e:
            return False

    @staticmethod
    def file_rename(src_file, dst_file):
        if not os.path.exists(dst_file):  # 如果文件存在则不重命名
            shutil.copy2(src_file, dst_file)
            os.remove(src_file)
            return True
        else:
            return False

    def save_info(self):
        if not self.cur_file_name:
            messagebox.showerror("提示", '未选择文件！')
            return
        file_path, _ = os.path.split(self.cur_file_name)
        _, ext = os.path.splitext(self.cur_file_name)
        tags = dict()
        title = self.entry_title.get().strip()
        artist = self.entry_artist.get().strip()
        album = self.entry_album.get().strip()
        tags['title'] = title
        tags['artist'] = artist
        tags['album'] = album
        tags['year'] = self.entry_year.get().strip()
        tags['genre'] = self.entry_genre.get().strip()
        tags['lyric'] = self.text_lyric.get(1.0, tk.END).strip()
        if self.write_id3_tags(self.cur_file_name, tags):
            messagebox.showinfo("提示", "IDV3标签信息保存成功！")
            dst_path = self._create_directorys([self.root_path, artist, album])
            new_filename = os.path.join(dst_path, '{}{}'.format(title, ext))
            if not os.path.exists(new_filename):
                shutil.move(self.cur_file_name, new_filename)
                self.load_directory(self.root_path)
                self._init_compoent_data()
        else:
            messagebox.showinfo("提示", "IDV3标签信息保存失败！")


if __name__ == "__main__":
    editor = MP3InfoEditor()
    editor.root.mainloop()
