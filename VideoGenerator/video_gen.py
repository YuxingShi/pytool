# coding:utf-8

from moviepy.editor import *


def generate_video(audio_file, image_file, output_file):
    # 加载音频文件
    audio_clip = AudioFileClip(audio_file)

    # 创建配图片段
    image_clip = ImageClip(image_file).set_duration(audio_clip.duration)

    # 将音频与配图合成为视频
    video_clip = image_clip.set_audio(audio_clip)

    # 保存视频文件
    video_clip.write_videofile(output_file, codec='libx264', audio_codec="aac")

# 调用函数生成视频
audio_file = "audio.mp3"
image_file = "image.jpg"
output_file = "output_video.mp4"
generate_video(audio_file, image_file, output_file)

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

# 调用函数合并视频
video_files = ["video1.mp4", "video2.mp4", "video3.mp4"]
output_file = "merged_video.mp4"
merge_video_clips(video_files, output_file)
