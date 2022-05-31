# coding:utf-8
import re
import cv2
import pytesseract
import numpy as np


def get_verify_code(image_stream):
    image = np.asarray(bytearray(image_stream), dtype="uint8")
    im = cv2.imdecode(image, cv2.IMREAD_COLOR)
    im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    h, w = im.shape
    color = 30
    for y in range(0, w):
        for x in range(0, h):
            if im[x, y] > color:
                im[x, y] = 255  # 根据灰度转化成白色
            else:
                im[x, y] = 0
            # 去边框
            span = 2
            if x < span or x > h - span:
                im[x, y] = 255
            if y < span or y > w - span:
                im[x, y] = 255
    # 查找除号的位置
    length = 0
    line_start = -1
    for m in range(0, w - 1):
        if im[16, m] < color:
            if line_start == -1:
                line_start = m
            length = length + 1
        else:
            if length > 10:
                # 判断是否为除号上面的点,如果是去掉减号，让其变成:
                is_divide = im[10, int(line_start + length / 2) - 1]
                is_add = im[13, int(line_start + length / 2) - 1]
                # 去除加号与后面字符的连接数
                cv2.rectangle(im, (line_start + 13, 16), (line_start + 14, 17), 255, -1)
                if is_divide == 0 and is_add == 255:
                    # 去掉除号换成A来识别
                    cv2.rectangle(im, (line_start, 0), (line_start + length - 4, 32), 255, -1)
                    cv2.putText(im, "A", (int(line_start), 22), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1,
                                cv2.LINE_AA)
                break
            line_start = -1
            length = 0
    # 处理完图片，开始识别图形中的算式
    config = r'-c tessedit_char_whitelist=0123456789+-xXA÷: --psm 7'
    text = pytesseract.image_to_string(im, config=config)
    print('raw_text', text)
    text = text.replace('A', '/')
    text = text.replace('÷', '/')
    text = text.replace('x', '*')
    text = text.replace('X', '*')
    text = text.replace('**', '*')
    try:
        text = re.findall('(\d*[\*\+-/]\d*)', text)[0]
        print('text', text)
        result = str(int(eval(text)))
        print('result', result)
        return result
    except IndexError as e:
        return None
    except SyntaxError as e:
        return None

