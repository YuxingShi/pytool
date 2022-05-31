# -*- coding: utf-8 -*-

import pyaudio
from threading import Thread


class Recorder(object):
    def __init__(self, chunk=1024, channels=1, rate=64000):
        self.CHUNK = chunk
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = channels
        self.RATE = rate
        self._running = True
        self._frames = []

    def start(self):
        Thread(target=self.__recording, daemon=True).start()

    def __recording(self):
        self._running = True
        self._frames = []
        p = pyaudio.PyAudio()
        stream = p.open(format=self.FORMAT, channels=self.CHANNELS, rate=self.RATE, input=True,
                        frames_per_buffer=self.CHUNK)
        stream_output = p.open(format=self.FORMAT, channels=self.CHANNELS, rate=self.RATE, output=True,
                               frames_per_buffer=self.CHUNK)
        while self._running:
            data = stream.read(self.CHUNK)
            self._frames.append(data)
            stream_output.write(data)
        stream.stop_stream()
        stream.close()
        stream_output.stop_stream()
        stream_output.close()
        p.terminate()

    def stop(self):
        self._running = False


if __name__ == "__main__":
    rec = Recorder()
    rec.start()
    input('输入任意按键退出')
