# coding:utf-8
import time
import os
import re
import base64
import json
import numpy as np
import js2py
import cv2
import requests

context = js2py.EvalJs()
slider_path = os.path.abspath('slider_json')


def time_file_name(ext: str):
    return '{}.{}'.format(int(time.time() * 1000), ext)


def dict2json(obj: dict, file_name: str):
    with open(file_name, 'w') as fp:
        json.dump(obj, fp)  # 将字典数据存储到本地json格式


def base64_to_image(base64_code):
    """把BASE64字符串转为图片"""
    img_data = base64.b64decode(base64_code)
    img_array = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(img_array, 1)
    return img


def to_thresh(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)[1]


def thresh2str(thresh_img):
    height, width = thresh_img.shape
    rows_list = []
    for h in range(height):
        row = ''
        for w in range(width):
            value = thresh_img[h, w]
            if value > 0:
                flag = '1'
            else:
                flag = '0'
            row += flag
        rows_list.append(row)
    print('\n'.join(rows_list))
    return rows_list


def calculate_index(text_list: list):
    first_line = text_list[0]
    last_line = text_list[-1]
    sub = '111111111111111111111111111111'
    f_index_list = [substr.start() for substr in re.finditer(sub, first_line)]
    f_len = f_index_list.__len__()
    l_index_list = [substr.start() for substr in re.finditer(sub, last_line)]
    l_len = l_index_list.__len__()
    if f_len == 1:
        return f_index_list[0]
    elif f_len == 2:  # 第一行匹配到两次子串
        if l_len == 1:
            return l_index_list[0]  # 如果最后一行只找到一次子串则就是该index
        else:
            return l_index_list[0]  # 如果最后一行匹配到多个默认返回第一个
    else:  # 没有匹配到字符串则是未找到滑块
        raise Exception('未找到匹配的index')


seed_js = """
function getRandomNumberByRange(start, end) {
            return Math.floor(Math.random() * (end - start) + start)
        }
var newSeed = function () {
           var num = getRandomNumberByRange(3,6)
           var seed = ''
           for(var i = 0;i<num; i++){
               seed+= getRandomNumberByRange(1,9)
           }
           return parseInt(seed)
       }"""
context.execute(seed_js)
seed = context.newSeed()
print('seed', seed)
data = {'seed': seed}
# resp = requests.post('https://fj.122.gov.cn/m/tmri/captcha/sliderImg', data=data, verify=False)
# if resp.status_code == 200:
    # resp = resp.json()
resp = {"message": "\u64cd\u4f5c\u6210\u529f\uff01", "data": {"slider": "iVBORw0KGgoAAAANSUhEUgAAADIAAAAyCAYAAAAeP4ixAAABLUlEQVR42u3ZMQ6CMBQGYO/g7OQNdFIT42qIF2BxcTHewkQXE6/g5OTECVxcGAwH8DDoa4RAKaWQthT9X/KnDAx8eY8S0l4PhUKhUCiDFTtQgIggg+s0zTDw2Ordl+lKWT/GLNuXHx+jeSHn5ywX0T18tGFEENXwwH04yaGqro1A+pcVezh+rQujVQQr655+SOCXhkatCSwLTHDGR0sGEeYDawLMjiN1rH2IpHPZVMGchBRQ387JQFq3YNH3RCcmt3Iw4xATXRKNoXaIrZHjAwgggFiG2N61rEFsILRCbD84IIAAAggggAACCCD6/stHt023IQSg7KJTvAgPLFYgsqozIq0dK6iATEKsnmY58e8NiAKGXmZ6iZ1HlGESAO1InUGobAY/cZSNA/5/rTfIk69caWVTngAAAABJRU5ErkJggg==", "background": "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", "y": "36,26,23,28,var host = window.location.host;var seed = callThePageFunction(661761471);seed = host.indexOf('.')>2?parseInt(seed/(host.charCodeAt(0)+host.charCodeAt(1)+host.charCodeAt(2))):parseInt(seed/(host.charCodeAt(0)+host.charCodeAt(1)));seed=seed%290;seed=parseInt(seed/122);seed-=644;seed-=102;seed=Math.abs(seed+1)%4;y_index=seed;"}, "code": 200, "seed": 13187}
resp['seed'] = seed
file_name = os.path.join(slider_path, time_file_name('json'))
dict2json(resp, file_name)
background = base64_to_image(resp.get('data').get('background'))
slider = base64_to_image(resp.get('data').get('slider'))
y = resp.get('data').get('y')
js_content = """
        var window={location:{host: "%s"}}
        function callThePageFunction(seed) {
            htmlSeed = %s
            return seed = seed > 0 ? seed - htmlSeed : seed + htmlSeed;
                        }
        sy="%s"
        var arr = sy.split(',')
        var bds = arr[arr.length - 1]
        eval(bds)
        var y = arr[seed]       
        """ % ('fj.122.gov.cn', seed, y)
# context = js2py.EvalJs()
context.execute(js_content)
y = int(context.y)
# background = cv2.imread('background.jpg', cv2.IMREAD_UNCHANGED)
thresh = to_thresh(background)
# slider = cv2.imread('slider.jpg', cv2.IMREAD_UNCHANGED)
height, width, _ = background.shape
s_height, s_width, _ = slider.shape
cut = background[y + 10:y + s_height - 10, 0:width]
cut_thresh = to_thresh(cut)
print(cut_thresh.shape)
print('index:', calculate_index(thresh2str(cut_thresh)))
cv2.namedWindow("Picture", 0)
cv2.namedWindow("slider", 0)
cv2.namedWindow("cut", 0)
cv2.resizeWindow("Picture", width, height)
cv2.resizeWindow("slider", s_width, s_height)
cv2.resizeWindow("cut", width, 50)
while True:
    cv2.imshow('Picture', background)
    cv2.imshow('slider', slider)
    cv2.imshow('cut', cut_thresh)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cv2.destroyAllWindows()
