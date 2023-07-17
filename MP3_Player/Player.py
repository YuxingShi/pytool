from tkinter import Tk, Frame, Button, Label, Scale, filedialog, Listbox
import pygame
import os


class MusicPlayer:
    def __init__(self):
        self.root = Tk()
        self.root.title("MP3 播放器")

        self.frame1 = Frame(self.root)
        self.frame1.pack(pady=20)

        self.label_file = Label(self.frame1, text="选择一个MP3文件", font=("Helvetica", 12))
        self.label_file.pack(side="left", padx=(10, 0))

        self.button_file = Button(self.frame1, text="选择文件", command=self.select_file)
        self.button_file.pack(side="left")

        self.frame2 = Frame(self.root)
        self.frame2.pack(pady=10)

        self.label_song = Label(self.frame2, text="当前歌曲:", font=("Helvetica", 12))
        self.label_song.pack()

        self.label_current_song = Label(self.frame2, text="", font=("Helvetica", 12), wraplength=350)
        self.label_current_song.pack()

        self.frame3 = Frame(self.root)
        self.frame3.pack(pady=5)

        self.play_button = Button(self.frame3, text="播放", command=self.play_music)
        self.play_button.grid(row=0, column=0, padx=10)

        self.pause_button = Button(self.frame3, text="暂停", command=self.pause_music)
        self.pause_button.grid(row=0, column=1, padx=10)

        self.stop_button = Button(self.frame3, text="停止", command=self.stop_music)
        self.stop_button.grid(row=0, column=2, padx=10)

        self.volume_label = Label(self.frame3, text="音量", font=("Helvetica", 10))
        self.volume_label.grid(row=0, column=3, padx=10)

        self.volume_scale = Scale(self.frame3, from_=0, to=1, resolution=0.1, orient="horizontal",
                                  command=self.set_volume)
        self.volume_scale.set(0.5)  # 默认音量为0.5
        self.volume_scale.grid(row=0, column=4, padx=10)

        self.frame4 = Frame(self.root)
        self.frame4.pack(pady=20)

        self.playlist_label = Label(self.frame4, text="播放列表", font=("Helvetica", 12))
        self.playlist_label.pack()

        self.playlist = Listbox(self.frame4, width=50, height=10, selectbackground="#a6a6a6")
        self.playlist.pack(pady=5)

        self.frame5 = Frame(self.root)
        self.frame5.pack(pady=10)
        # 播放进度条
        self.progress_label = Label(self.frame5, text="进度条", font=("Helvetica", 12))
        self.progress_label.pack()

        self.progress_scale = Scale(self.frame5, from_=0, to=100, orient="horizontal", length=400,
                                    showvalue=False, sliderrelief="flat", sliderlength=20)
        self.progress_scale.pack()
        # 播放时间
        self.label_current_time = Label(self.root, text="00:00", font=("Arial", 12))
        self.label_current_time.pack()

        self.music_files = []
        self.current_index = None

        pygame.mixer.init()
        pygame.mixer.music.set_endevent(pygame.USEREVENT)

        self.root.protocol("WM_DELETE_WINDOW", self.quit_player)

    def select_file(self):
        file_path = filedialog.askopenfilename(defaultextension=".mp3",
                                               filetypes=(("MP3 Files", "*.mp3"), ("All Files", "*.*")))
        if file_path:
            self.music_files.append(file_path)
            filename = os.path.basename(file_path)
            self.playlist.insert("end", filename)

    def play_music(self):
        if self.current_index is not None:
            pygame.mixer.music.unpause()
        else:
            if self.music_files:
                self.current_index = 0
                self.play_selected_music()

    def play_selected_music(self):
        file_path = self.music_files[self.current_index]
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()

        filename = os.path.basename(file_path)
        self.label_current_song.config(text=filename)

    def pause_music(self):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()

    def stop_music(self):
        pygame.mixer.music.stop()
        self.current_index = None
        self.progress_scale.set(0)
        self.label_current_song.config(text="")

    def set_volume(self, volume):
        pygame.mixer.music.set_volume(float(volume))

    def update_progress(self):
        if pygame.mixer.music.get_busy():
            progress = pygame.mixer.music.get_pos() / 1000  # 获取当前播放的时间（以秒为单位）
            song_length = pygame.mixer.music.get_length() / 1000  # 获取当前歌曲的总长度（以秒为单位）
            minutes, seconds = divmod(progress, 60)
            current_time = "{:02d}:{:02d}".format(int(minutes), int(seconds))

            self.label_current_time.config(text=current_time)

            self.progress_scale.config(to=song_length, value=progress)  # 更新进度条的范围和值

            minutes, seconds = divmod(progress, 60)
            current_time = "{:02d}:{:02d}".format(int(minutes), int(seconds))

            minutes, seconds = divmod(song_length, 60)
            total_time = "{:02d}:{:02d}".format(int(minutes), int(seconds))

            self.label_current_song.config(
                text=f"当前歌曲: {self.music_files[self.current_index]} ({current_time} / {total_time})")

        self.root.after(1000, self.update_progress)  # 每隔1秒更新一次进度条

    def quit_player(self):
        pygame.mixer.music.stop()
        self.root.destroy()


def main():
    player = MusicPlayer()
    player.root.mainloop()


if __name__ == "__main__":
    main()
