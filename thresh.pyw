# coding:utf-8
'''
Created on 2017年8月8日

@author: Shiyx
'''
import os
import time
import tkinter.messagebox as message_box
from tkinter import *
import cv2

src_dir = './dest'
dst_dir = os.path.abspath('tmp')

if not os.path.exists(src_dir):
    os.makedirs(src_dir)
if not os.path.exists(dst_dir):
    os.makedirs(dst_dir)


def showPicture():
    try:
        imgFileName = fileList.get(fileList.curselection())
    except TclError:
        message_box.showwarning('警告', '请选择图片')
        return
    srcFilesPath = os.path.join(src_dir, imgFileName)
    cv2.namedWindow("Picture", 0)
    cv2.resizeWindow("Picture", 300, 400)
    frame = cv2.imread(srcFilesPath, cv2.IMREAD_UNCHANGED)
    while True:
        cv2.imshow('Picture', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()


def showThreshPicture():
    try:
        imgFileName = fileList.get(fileList.curselection())
    except TclError:
        message_box.showwarning('警告', '请选择图片')
        return
    srcFilesPath = os.path.join(src_dir, imgFileName)
    cv2.namedWindow("ThreshPicture", 0)
    cv2.resizeWindow("ThreshPicture", 300, 400)
    frame = cv2.imread(srcFilesPath, cv2.IMREAD_UNCHANGED)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 135, 255, cv2.THRESH_BINARY)[1]
    while True:
        cv2.imshow('ThreshPicture', thresh)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()


def transferCurrent():
    try:
        imgFileName = fileList.get(fileList.curselection())
    except TclError:
        message_box.showwarning('警告', '请选择图片')
        return
    srcFilesPath = os.path.join(src_dir, imgFileName)
    frame = cv2.imread(srcFilesPath, cv2.IMREAD_UNCHANGED)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 135, 255, cv2.THRESH_BINARY)[1]
    dstFileName = "%s\%s.jpg" % (dst_dir, int(time.time() * 1000))
    desFilePath = os.path.join(dst_dir, dstFileName)
    cv2.imwrite(desFilePath, thresh)
    message_box.showinfo('信息', '转换成功！')


def transferAll():
    for imgFileName in srcList:
        srcFilesPath = os.path.join(src_dir, imgFileName)
        frame = cv2.imread(srcFilesPath)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 135, 255, cv2.THRESH_BINARY)[1]
        gifFileName = "%s\%s.jpg" % (dst_dir, int(time.time() * 1000))
        desFilePath = os.path.join(dst_dir, gifFileName)
        cv2.imwrite(desFilePath, thresh)
    message_box.showinfo('信息', '转换成功！')


root = Tk()  # 创建窗口对象的背景色
root.title('图片二值化处理')  # 设置标题
root.geometry('400x200')  # 设置窗口大小
root.resizable(width=False, height=False)

frame_list = Frame(root, width=150, height=150, borderwidth=2)
frame_button = Frame(root, width=150, height=150, borderwidth=2)

fileListLabel = Label(frame_list, text="待处理文件列表", font=("Arial", 9), width=15, height=2)
fileList = Listbox(frame_list)  # 创建文件列表组件
sl = Scrollbar(root, orient=VERTICAL)

srcList = os.listdir(src_dir)
if srcList.__len__() == 0:
    fileList.insert(0, 'Nothing')
srcList.sort()

#  初始化fileList内容
for imgFileName in srcList:
    fileList.insert(END, imgFileName)

frame_list.grid(row=0, column=0)
frame_button.grid(row=0, column=1)

fileListLabel.grid(row=0, column=0)
fileList.grid(row=1, column=0)
Button(frame_button, text="查看图片", command=showPicture).grid(row=0, column=0)
Button(frame_button, text="二值图片", command=showThreshPicture).grid(row=1, column=0)
Button(frame_button, text="转换当前图片", command=transferCurrent).grid(row=2, column=0)
Button(frame_button, text="转换全部图片", command=transferAll).grid(row=3, column=0)
root.mainloop()
