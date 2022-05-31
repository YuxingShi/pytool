# coding:utf-8
import numpy as np
import cv2

img = cv2.imread('wjf.jpg')


while True:
    cv2.imshow("sss", img[0:375, 240:480])
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cv2.destroyAllWindows()

