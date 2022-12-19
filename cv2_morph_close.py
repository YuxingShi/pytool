# -*- coding: utf-8 -*-
# By：Eastmount
import os

import cv2
import numpy as np
from pyzbar import pyzbar
from PIL import Image


def recognize_qrcode(img_path):
    qr_codes = pyzbar.decode(Image.open(img_path), symbols=[pyzbar.ZBarSymbol.QRCODE])
    if qr_codes:
        print('qrcodes', qr_codes)
        for qrcode in qr_codes:
            print('qrcode', qrcode)


def image_recovery(img_path):
    cv2.namedWindow("src", 0)  # 0可调整窗口大小，1，默认窗口

    cv2.namedWindow("result", 0)  # 0可调整窗口大小，1，默认窗口


    src_path, src_filename = os.path.split(img_path)
    # 读取图片
    src = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
    # 设置卷积核
    kernel = np.ones((8, 8), np.uint8)
    # 图像闭运算
    result = cv2.morphologyEx(src, cv2.MORPH_CLOSE, kernel)
    # 图像开运算
    # result = cv2.morphologyEx(src, cv2.MORPH_OPEN, kernel)
    while True:
        cv2.resizeWindow("src", 300, 700)  # 初始化窗口大小
        cv2.resizeWindow("result", 300, 700)  # 初始化窗口大小
        # 显示图像
        cv2.imshow("src", src)
        cv2.imshow("result", result)
        # 等待显示
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        elif cv2.waitKey(1) & 0xFF == ord('s'):
            save_filename = 'recovery_{}'.format(src_filename)
            save_path = os.path.join(src_path, save_filename)
            cv2.imwrite(save_path, result)
            break
    cv2.destroyAllWindows()


if __name__ == '__main__':
    # image_recovery('jkm_lkq.jpg')
    recognize_qrcode('jkm_wjf.jpg')
