#coding: utf-8
import tkinter as tk
import sounddevice as sd
import soundfile as sf
from threading import Thread


class AudioRecorderApp:
    def __init__(self, window):
        self.window = window
        self.window.title("Audio Recorder")

        # 创建开始录音按钮
        self.btn_record = tk.Button(window, text="Record", command=self.start_recording)
        self.btn_record.pack(pady=10)

        # 创建停止录音按钮
        self.btn_stop = tk.Button(window, text="Stop", state=tk.DISABLED, command=self.stop_recording)
        self.btn_stop.pack(pady=5)

        # 创建播放录音按钮
        self.btn_play = tk.Button(window, text="Play", state=tk.DISABLED, command=self.play_recording)
        self.btn_play.pack(pady=5)

        # 创建暂停录音按钮
        self.btn_pause = tk.Button(window, text="Pause", state=tk.DISABLED, command=self.pause_recording)
        self.btn_pause.pack(pady=5)

        self.is_recording = False
        self.recording_thread = None
        self.recording_data = None

    def start_recording(self):
        self.is_recording = True
        self.btn_record.configure(state=tk.DISABLED)
        self.btn_stop.configure(state=tk.NORMAL)

        # 开启录音线程
        self.recording_thread = Thread(target=self.record_audio)
        self.recording_thread.start()

    def stop_recording(self):
        self.is_recording = False
        self.btn_record.configure(state=tk.NORMAL)
        self.btn_stop.configure(state=tk.DISABLED)
        self.btn_play.configure(state=tk.NORMAL)

    def record_audio(self):
        samplerate = 44100  # 采样率
        duration = 5  # 录音时长（秒）
        self.recording_data = sd.rec(int(samplerate * duration), samplerate=samplerate, channels=1)
        sd.wait()

    def play_recording(self):
        if self.recording_data is not None:
            sf.write("recording.wav", self.recording_data, samplerate=44100)

            # 使用播放器播放录音
            playback_thread = Thread(target=self.play_audio)
            playback_thread.start()

    def play_audio(self):
        data, samplerate = sf.read("recording.wav")
        sd.play(data, samplerate)
        sd.wait()

    def pause_recording(self):
        pass


window = tk.Tk()
app = AudioRecorderApp(window)
window.mainloop()
