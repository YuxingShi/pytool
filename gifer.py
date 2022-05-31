# coding:utf-8
'''
Created on 2017年8月8日

@author: Shiyx
'''
import os
import time
import imageio

src_dir = os.path.abspath('tmp')  # H:\DelayPhoto   F:\\pythonGIF\\gifsrc
dst_dir = './gifdst'
gif_duration = 0.04  # gif图片切换间隔时间（单位：秒）

# 以下参数不能修改
img_frame_list = []

if not os.path.exists(src_dir):
    os.makedirs(src_dir)
if not os.path.exists(dst_dir):
    os.makedirs(dst_dir)

srcList = os.listdir(src_dir)
print('处理图片集合：', srcList)
if srcList.__len__() == 0:
    print('没有要处理的图片！')
    os.system('PAUSE')
    exit()
srcList.sort()

for imgFileName in srcList:
    srcFilesPath = os.path.join(src_dir, imgFileName)
    img_frame = imageio.imread(srcFilesPath)
    img_frame_list.append(img_frame)

# print '生成的图像对象列表：'.decode('UTF-8'), imgList
gifFileName = time.strftime('%Y%m%d%H%M%S.gif', time.localtime(time.time()))
desFilePath = os.path.join(dst_dir, gifFileName)
imageio.mimsave(desFilePath, img_frame_list, duration=gif_duration)
print('gif图片生成', desFilePath)
os.system('PAUSE')
