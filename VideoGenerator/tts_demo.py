# coding:utf-8
from gtts import gTTS
import playsound

def text_to_speech(text, output_file):
    tts = gTTS(text=text, lang='en')  # 将文本转换为英文语音，如果需要其他语言，请更改lang参数
    tts.save(output_file)
    playsound.playsound(output_file)  # 播放语音

# 调用函数进行文本转语音
text = "Hello, how are you today?"
output_file = "output.mp3"
text_to_speech(text, output_file)
