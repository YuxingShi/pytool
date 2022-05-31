#coding:utf-8
'''
Created on 2017年8月8日

@author: Shiyx
'''
import os
import time
import cv2
import numpy as np
#src_dir = 'F:\\pythonVideo\\srcImage'
src_dir = 'H:\\snapshoot\\2017-10-26'
dst_dir = 'F:\\pythonVideo\\dstVideo'
#以下参数不能修改
imgList = []
size = (320, 240)
fps = 5

videoName =  time.strftime('%Y%m%d%H%M%S.avi', time.localtime(time.time()))
desFilePath = os.path.join(dst_dir, videoName)
#===============================================================================
# #指定写视频的格式, I420-avi, MJPG-mp4
# 视频格式包括: 
# I420(适合处理大文件) -> .avi;
# PIMI -> .avi;
# MJPG -> .avi & .mp4
# THEO -> .ogv;
# FLV1(flash video, 流媒体视频) -> .flv
#===============================================================================
#fourcc 设置视频解码器 -1则运行时提示选择
fourcc = cv2.VideoWriter_fourcc(*'DIVX')
fourcc = -1
video = cv2.VideoWriter(desFilePath, fourcc, fps, size)
if not os.path.exists(src_dir):
        os.makedirs(src_dir)    
if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)
              
srcList = os.listdir(src_dir)
print '处理图片集合：'.decode('UTF-8'), srcList
if srcList.__len__() == 0:
    print '没有要处理的图片！'.decode('UTF-8')
    #os.system('PAUSE')
    exit()
srcList.sort()

for imgFileName in srcList:
    srcFilesPath = os.path.join(src_dir, imgFileName)
    frame = cv2.imread(srcFilesPath, cv2.IMREAD_UNCHANGED)
    cv2.imshow('Display', frame)
    video.write(frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

print '视频生成成功'.decode('UTF-8'), desFilePath
#os.system('PAUSE')