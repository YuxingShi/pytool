# coding:utf-8

import os
import time
import cv2
import numpy as np
from pydub import AudioSegment
from moviepy.editor import *

# SRC_IMAGES_DIR = 'F:\\学习\连环画\\2商朝的故事 向日葵连环画'
SRC_IMAGES_DIR = 'F:\\Myself\\连环画\\2021-01-25\\商朝的故事 向日葵连环画'
# SRC_MP3_DIR = 'F:\\学习\连环画\\2商朝的故事mp3'
SRC_MP3_DIR = 'F:\\Myself\\连环画\\商朝的故事mp3'
TEMP_MP4_DIR = os.path.abspath('TEMP_MP4')
TEMP_MP3_DIR = os.path.abspath('TEMP_MP3')
DST_MP4_DIR = os.path.abspath('mp4')


def __directory_exist_check(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


def __clear_path(dir_path):
    for file_name in os.listdir(dir_path):
        file_path = os.path.join(dir_path, file_name)
        os.remove(file_path)


# 将图片生成指定秒数的MP4视频
def image2mp4(image_path, dst_file_name, seconds=5):
    print('正在处理', image_path)
    fps = round(1 / seconds, 2)
    img = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), cv2.IMREAD_COLOR)  # 解决无法使用中文路径的问题
    img_width, img_height = img.shape[:2]
    video_writer = cv2.VideoWriter(
        dst_file_name, cv2.VideoWriter_fourcc('m', 'p', '4', 'v'), fps, (img_height, img_width)
    )
    video_writer.write(img)


# 在给定的mp3前后各加入1s静音
def concat_mp3_with_silent(mp3_path, output_name):
    print('正在处理', mp3_path)
    seg = AudioSegment.from_mp3(mp3_path)
    # silent_2s = AudioSegment.silent(2000)
    silent_1s = AudioSegment.silent()
    result = silent_1s + seg + silent_1s
    result.export(output_name, format="mp3")


# 合并目录下的mp3
def mp3_merge(src_dir_path, output_name):
    print('开始合并所有分段Mp3')
    seg_empty = AudioSegment.empty()
    for file_name in os.listdir(src_dir_path):
        src_mp3_file_name = os.path.join(src_dir_path, file_name)
        seg_empty += AudioSegment.from_mp3(src_mp3_file_name)
    seg_empty.export(output_name, format="mp3")
    print('Mp3合并完成！')


# 合并目录下的mp4
def mp4_merge(src_dir_path, outputName):
    print('开始合并所有分段视频')
    clips_list = []
    for file_name in os.listdir(src_dir_path):
        src_mp4_file_name = os.path.join(src_dir_path, file_name)
        clips_list.append(VideoFileClip(src_mp4_file_name))
    final_clip = concatenate_videoclips(clips_list)  # 视频合并
    final_clip.write_videofile(outputName)
    print('视频合并完成！')


# 合并音频与视频
def merge_video_audio(video_path, audio_path, dst_path):
    video_clip = VideoFileClip(video_path)
    audio = AudioFileClip(audio_path)
    result_video = video_clip.set_audio(audio)
    result_video.write_videofile(dst_path)


if __name__ == "__main__":
    # __directory_exist_check(TEMP_MP4_DIR)
    # __directory_exist_check(TEMP_MP3_DIR)
    # __directory_exist_check(DST_MP4_DIR)
    # print('开始处理原始Mp3文件')
    # __clear_path(TEMP_MP3_DIR)
    # for file_name in os.listdir(SRC_MP3_DIR):
    #     src_file_name = os.path.join(SRC_MP3_DIR, file_name)
    #     dst_file_name = os.path.join(TEMP_MP3_DIR, file_name)
    #     concat_mp3_with_silent(src_file_name, dst_file_name)
    # print('原始Mp3文件处理完成！')
    # mp3_merge(TEMP_MP3_DIR, './temp_mp3.mp3')
    # # mp4处理
    # print('开始处理原始Mp4文件')
    # __clear_path(TEMP_MP4_DIR)
    # for file_name in os.listdir(TEMP_MP3_DIR):
    #     name, ext = file_name.split('.')
    #     src_mp3_file_name = os.path.join(TEMP_MP3_DIR, file_name)
    #     src_jpg_file_name = os.path.join(SRC_IMAGES_DIR,  '{}.jpg'.format(name))
    #     dst_file_name = os.path.join(TEMP_MP4_DIR, '{}.mp4'.format(name))
    #     duration = int(AudioFileClip(src_mp3_file_name).duration)
    #     image2mp4(src_jpg_file_name, dst_file_name, duration-1)
    # print('原始Mp4文件处理完成！')
    # mp4_merge(TEMP_MP4_DIR, './temp_mp4.mp4')
    # # 开始合并视频与音频
    # print('开始合并视频与音频')
    __clear_path(DST_MP4_DIR)
    for file_name in os.listdir(TEMP_MP4_DIR):
        name, ext = file_name.split('.')
        src_mp4_file_name = os.path.join(TEMP_MP4_DIR, file_name)
        src_mp3_file_name = os.path.join(TEMP_MP3_DIR, '{}.mp3'.format(name))
        dst_mp4_file_name = os.path.join(DST_MP4_DIR, file_name)
        merge_video_audio(src_mp4_file_name, src_mp3_file_name, dst_mp4_file_name)
    print('视频与音频合并结束')


