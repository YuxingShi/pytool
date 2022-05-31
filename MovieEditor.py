# coding:utf-8
import os
from moviepy.editor import *
# # 把图片列表变成视频
# src_path = 'H:/DelayPhoto/dropletevaporation'
# files_list = [os.path.join(src_path, new_path) for new_path in os.listdir(src_path)]
# print('files_list', files_list)
# clip = ImageSequenceClip(files_list, fps=15)
# # 保存视频 其中，verbose为打印详细信息与否，audio为是否写入声音。
# clip.write_videofile('./droplet_evaporation3.mp4', codec='mpeg4', verbose=True, audio=False)

# 读取视频到内存
src_path = 'I:/record/20190320/19'
files_list = [os.path.join(src_path, new_path) for new_path in os.listdir(src_path)]
vfc_list = [VideoFileClip(path).resize(newsize=(640, 360)) for path in files_list]  # path为输入视频路径
# 对多个视频在时长上进行拼接 注意：method=‘compose’是必要的，它使得各种编码方式不同的视频也可以进行拼接，否则，如果输入编码方式不同的视频会报错。
result_clip = concatenate_videoclips(vfc_list, method='compose')  # vfc_list为VideoFileClip的对象组成的list
result_clip.write_videofile('./2019032019_640X360.mp4', codec='mpeg4', verbose=True, audio=True, threads=8)
result_clip.close()

