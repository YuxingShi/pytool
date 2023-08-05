# coding:utf-8
from gtts import gTTS

def text_to_speech(text, output_file):
    tts = gTTS(text=text, lang='zh')  # 将文本转换为英文语音，如果需要其他语言，请更改lang参数 zh zh-TW en
    tts.save(output_file)


if __name__ == '__main__':
    # 调用函数进行文本转语音
    text = "你好，这里是中国公安"
    output_file = "output.mp3"
    text_to_speech(text, output_file)
