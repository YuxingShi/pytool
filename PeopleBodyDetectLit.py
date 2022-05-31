# coding:utf-8
'''
Created on 2021年9月18日

@author: Shiyx
'''

import time
import os
import winsound
import cv2
import threading

_DEBUG = True
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
# hog.setSVMDetector(cv2.HOGDescriptor_getDaimlerPeopleDetector())

timer = None
cap = cv2.VideoCapture(0)
cv2.namedWindow("people detection", 0)  # 0可调整窗口大小，1，默认窗口
cv2.resizeWindow("people detection", 300, 300)  # 初始化窗口大小
cv2.startWindowThread()


if _DEBUG:
    # scale值变化
    def scale_modify(*args):
        pass
    cv2.namedWindow('people detection')
    cv2.createTrackbar('scale_value', 'people detection', 105, 500, scale_modify)


def _take_photo():
    save_path = time.strftime('F:\snapshoot\%Y-%m-%d', time.localtime(time.time()))  # 生成日期文件夹
    if not os.path.exists(save_path):
        os.mkdir(save_path)
    res = cv2.resize(frame1, (320, 240), interpolation=cv2.INTER_AREA)
    tp_name = "%s\%s.jpg" % (save_path, int(time.time() * 1000))
    cv2.imwrite(tp_name, frame1)
    winsound.PlaySound('ALARM8', winsound.SND_ASYNC)
    time.sleep(1)


def is_inside(o, i):
    ox, oy, ow, oh = o
    ix, iy, iw, ih = i
    return ox > ix and oy > iy and ox + ow < ix + iw and oy + oh < iy + ih


def draw_person(image, person):
    x, y, w, h = person
    cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 255), 2)


while True:  # 主程序
    ret1, frame1 = cap.read()  # get a frame
    if not ret1:
        break
    scale_value = cv2.getTrackbarPos('scale_value', 'people detection')
    scale_value_float = scale_value/100.0
    found, w = hog.detectMultiScale(frame1, winStride=(8, 8), scale=scale_value_float)
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))  # 增加时间水印
    cv2.putText(frame1, timestamp, (10, 25), cv2.FONT_ITALIC, 1.0, (0, 255, 0), thickness=2)
    found_filtered = []
    for ri, r in enumerate(found):
        for qi, q, in enumerate(found):
            if ri != qi and is_inside(r, q):
                break
            else:
                found_filtered.append(r)
        for person in found_filtered:
            draw_person(frame1, person)
            if not timer:
                timer = threading.Thread(target=_take_photo, daemon=True)
                timer.start()
            else:
                if timer.isAlive():
                    pass
                else:
                    timer = None
    cv2.imshow("people detection", frame1)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()


if __name__ == '__main__':
    pass
