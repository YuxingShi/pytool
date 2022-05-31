# coding:utf-8
'''
Created on 2017年10月24日

@author: Shiyx
'''

import time
import os
import winsound
import cv2
import threading

from datetime import datetime

tpThread = None
cap = cv2.VideoCapture(0)
cv2.namedWindow("Camera", 0)  # 0可调整窗口大小，1，默认窗口
cv2.resizeWindow("Camera", 300, 200)  # 初始化窗口大小


def _take_photo():
    save_path = 'F:\DelayPhoto'
    if not os.path.exists(save_path):
        os.mkdir(save_path)
    res = cv2.resize(frame1, (320, 240), interpolation=cv2.INTER_AREA)
    tf_name = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
    tp_name = "%s\%s.jpg" % (save_path, tf_name)
    cv2.imwrite(tp_name, res)
    winsound.PlaySound('ALARM8', winsound.SND_ASYNC)
    time.sleep(60)  # 拍照间隔时间秒


while True:  # 主程序
    ret1, frame1 = cap.read()  # get a frame
    if not ret1:
        break
    timestamp = time.strftime(
        '%Y-%m-%d %H:%M:%S', time.localtime(time.time()))  # 增加时间水印
    cv2.putText(frame1, timestamp, (10, 25), cv2.FONT_ITALIC,
                1.0, (0, 255, 0), thickness=2)
    cv2.imshow("Camera", frame1)
    current_time = datetime.now()
    if int(current_time.hour) >= 0 and int(current_time.hour) <= 23:
        if not tpThread:
            tpThread = threading.Thread(target=_take_photo)
            tpThread.start()
        else:
            if tpThread.isAlive():
                pass
            else:
                tpThread = None
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()
if __name__ == '__main__':
    pass
