# coding:utf-8
'''
Created on 2017年7月24日

@author: Shiyx
'''

import time
import os
import winsound
import cv2
import threading

_DEBUG = True
timer = None
cap = cv2.VideoCapture(3)
cv2.namedWindow("Camera", 0)  # 0可调整窗口大小，1，默认窗口
cv2.resizeWindow("Camera", 300, 200)  # 初始化窗口大小
cv2.startWindowThread()
if _DEBUG:
    # thresh值变化  
    def thresh_modify(*args):
        pass
    cv2.namedWindow('Camera-thresh')
    cv2.createTrackbar('ThreshValue', 'Camera-thresh', 25, 255, thresh_modify)


def _take_photo():
    save_path = time.strftime('F:\snapshoot\%Y-%m-%d', time.localtime(time.time()))  # 生成日期文件夹
    if not os.path.exists(save_path):
        os.mkdir(save_path)
    res = cv2.resize(frame2, (320, 240), interpolation=cv2.INTER_AREA)
    tp_name = "%s\%s.jpg" % (save_path, int(time.time() * 1000))
    # cv2.imwrite(tp_name, res)
    winsound.PlaySound('ALARM8', winsound.SND_ASYNC)
    time.sleep(1)
  

while True:  # 主程序
    ret1, frame1 = cap.read()  # get a frame
    if not ret1:
        break
    gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    gray1 = cv2.GaussianBlur(gray1, (21, 21), 0)
    ret2, frame2 = cap.read()
    if not ret2:
        break
    gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.GaussianBlur(gray2, (21, 21), 0)
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))  # 增加时间水印
    cv2.putText(frame2, timestamp, (10, 25), cv2.FONT_ITALIC, 1.0, (0, 255, 0), thickness=2)
    cv2.imshow("Camera", frame2)
    frameDelta = cv2.absdiff(gray2, gray1)  # 计算当前帧和第一帧的不同
    if _DEBUG:
        tresh_value = cv2.getTrackbarPos('ThreshValue','Camera-thresh')
        thresh = cv2.threshold(frameDelta, tresh_value, 255, cv2.THRESH_BINARY)[1]
        cv2.imshow("Camera-thresh", thresh)
    else:
        thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
    cnts = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[1]
    if cnts is not None:
        if not timer:
            timer = threading.Thread(target=_take_photo)
            timer.start()
        else:
            if timer.isAlive():
                pass
            else:
                timer = None
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()
if __name__ == '__main__':
    pass
