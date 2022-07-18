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
resp = requests.post('https://fj.122.gov.cn/m/tmri/captcha/sliderImg', data=data, verify=False)
if resp.status_code == 200:
    resp = resp.json()
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
