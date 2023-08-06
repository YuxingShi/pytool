# coding:utf-8
# import os
import numpy as np
from moviepy.editor import *
from moviepy.video import fx


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
    width = 1170  # 视频宽度
    height = 2530  # 视频高度
    # 创建一个空白图像数组
    # blank_image = np.zeros((height, width, 3), dtype=np.uint8)
    # 创建一个空的视频剪辑对象
    # final_clip = ImageClip(blank_image, ismask=False)
    final_clip = None

    # 逐个加载和拼接视频片段
    for file in video_files:
        clip = VideoFileClip(file)
        # 调整较小视频的尺寸和位置
        if clip.size[0] < width:  # 如果clip1的宽度小于clip2的宽度
            clip = clip.resize(width=width)  # 将clip1的宽度调整为和clip2相同
            # clip = clip.fx(fx.resize, width=width, height=480)  # 将clip1的宽度调整为和clip2相同
            # clip = clip.set_position(("center", height / 2))  # 将clip1水平居中与clip2对齐
        # else:
        #     clip2 = clip2.resize(width=clip.size[0])  # 将clip2的宽度调整为和clip1相同
        #     clip2 = clip2.set_position(("center", clip1.size[1] / 2))  # 将clip2水平居中与clip1对齐
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
