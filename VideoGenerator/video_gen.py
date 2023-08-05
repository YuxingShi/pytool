# coding:utf-8
# import os
# os.environ["IMAGEIO_FFMPEG_EXE"] = "/opt/homebrew/bin/ffmpeg"
from moviepy.editor import *


def generate_video(audio_file, image_file, output_file):
    # 加载音频文件
    audio_clip = AudioFileClip(audio_file)

    # 创建配图片段
    image_clip = ImageClip(image_file).set_duration(audio_clip.duration)

    # 将音频与配图合成为视频
    video_clip = image_clip.set_audio(audio_clip)

    # 保存视频文件
    video_clip.write_videofile(output_file, fps=1, codec='libx264', audio_codec="aac")


def merge_video_clips(video_files, output_file):
    # 创建一个空的视频剪辑对象
    final_clip = None

    # 逐个加载和拼接视频片段
    for file in video_files:
        clip = VideoFileClip(file)
        if final_clip is None:
            final_clip = clip
        else:
            final_clip = concatenate_videoclips([final_clip, clip])

    # 保存最终合并的视频
    final_clip.write_videofile(output_file, codec='libx264')


if __name__ == '__main__':
    # 调用函数生成视频
    # audio_file = "/Users/shiyx/Desktop/WechatIMG1407.mp3"
    # image_file = "/Users/shiyx/Desktop/WechatIMG1407.jpeg"
    # output_file = "/Users/shiyx/Desktop/WechatIMG1407.mp4"
    # generate_video(audio_file, image_file, output_file)
    # 调用函数合并视频
    dst_path = "/Users/shiyx/Desktop/"
    video_files = ["WechatIMG1407.mp4"]
    output_file = os.path.join(dst_path, "merged_video.mp4")
    merge_video_clips(video_files, output_file)
