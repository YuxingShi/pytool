# coding:utf-8
'''
Created on 2017年7月24日

@author: Shiyx
'''

import time
import os
# import winsound
import cv2
import threading

_DEBUG = True
global frame1
timer = None
cap = cv2.VideoCapture(0)
cv2.namedWindow("Camera", 0)  # 0可调整窗口大小，1，默认窗口
cv2.resizeWindow("Camera", 300, 200)  # 初始化窗口大小
cv2.startWindowThread()
if _DEBUG:
    # thresh值变化  
    def thresh_modify():
        pass
    cv2.namedWindow('Camera-thresh')
    cv2.createTrackbar('ThreshValue', 'Camera-thresh', 0, 255, thresh_modify)

def take_photo(event,x , y, flags, param):
    if event==cv2.EVENT_LBUTTONDOWN:
        print(x , y, flags, param)
        save_path = time.strftime('H:\snapshoot\%Y-%m-%d', time.localtime(time.time()))  # 生成日期文件夹
        if not os.path.exists(save_path):
            os.mkdir(save_path)
        res = cv2.resize(frame1, (320, 240), interpolation=cv2.INTER_AREA)
        tp_name = "%s\%s.jpg" % (save_path, time.strftime('%Y%m%d%H%M%S', time.localtime()))
        cv2.imwrite(tp_name, res)
        # winsound.PlaySound('ALARM8', winsound.SND_ASYNC)
cv2.setMouseCallback('Camera', take_photo) 


while True:  # 主程序
    ret1, frame1 = cap.read()  # get a frame
    if not ret1:
        break
    gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    gray1 = cv2.GaussianBlur(gray1, (21, 21), 0)
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))  # 增加时间水印
    show_frame = frame1.copy()
    cv2.putText(show_frame, timestamp, (10, 25), cv2.FONT_ITALIC, 1.0, (0, 255, 0), thickness=2)
    cv2.imshow("Camera", show_frame)
    if _DEBUG:
        tresh_value = cv2.getTrackbarPos('ThreshValue','Camera-thresh')
        thresh = cv2.threshold(gray1, tresh_value, 255, cv2.THRESH_BINARY)[1]
        cv2.imshow("Camera-thresh", thresh)
    else:
        thresh = cv2.threshold(gray1, 25, 255, cv2.THRESH_BINARY)[1]
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()
if __name__ == '__main__':
    pass
