# coding:utf-8
# @Time    : 2022/7/18 19:45
# @Author  : ShiYuxing
# @Email   : shiyuxing1988@gmail.com
# @File    : SliderRecognizedServer.py.py
# 滑块验证码识别服务
# @Software: hzpython
import random
import time
import os
import re
import base64
import json
import numpy as np
import js2py
import cv2
from flask import Flask, make_response, request, jsonify, g
from loguru import logger


def _check_directory(directory: str):
    if not os.path.exists(directory):
        os.makedirs(directory)

app = Flask(__name__)
curpath = os.path.split(os.path.realpath(__file__))[0]
_check_directory(os.path.join(curpath, 'logs'))
_check_directory(os.path.join(curpath, 'failure_data'))
_check_directory(os.path.join(curpath, 'success_data'))

logfile = os.path.join(curpath, 'logs', 'checkcode.log')
logger.add(logfile, level="INFO", rotation="500MB", encoding="utf-8", enqueue=True, retention="30 days")
failure_data = os.path.join(curpath, 'failure_data')
success_data = os.path.join(curpath, 'success_data')





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
    return rows_list


def calculate_index(text_list: list):
    first_line = text_list[0]
    last_line = text_list[-1]
    sub = '01111111111111111111111111111110'  # 加个0排除干扰
    f_index_list = [substr.start() for substr in re.finditer(sub, first_line)]
    f_len = f_index_list.__len__()
    l_index_list = [substr.start() for substr in re.finditer(sub, last_line)]
    l_len = l_index_list.__len__()
    if f_len == 1 and l_len == 2:
        return f_index_list[0]
    elif f_len == 2 and l_len == 1:  # 第一行匹配到两次子串
        return l_index_list[0]
    elif f_len == 1 and l_len == 1:  # 干扰块与目标块重合起干扰块在上层
        f_index, l_index = f_index_list[0], l_index_list[0]
        if f_index > l_index:  # 左上角或右下角干扰块
            if last_line[f_index + 1] == '1':  # 右下角干扰块 +1,因为匹配串为01111111111111111111111111111110
                return f_index
            else:  # 左上角干扰块
                return l_index
        elif f_index < l_index:  # 左下角或右上角干扰块
            if first_line[l_index + 1] == '1':  # 右上角干扰块 +1,因为匹配串为01111111111111111111111111111110
                return l_index
            else:  # 左下角干扰块
                return f_index
        else:  # 干扰块与目标块重合
            return f_index_list[0]
    elif f_len == 0 and l_len == 1:  # 重合，干扰块缺口在首行，干扰块在目标块上方
        return l_index_list[0]
    elif f_len == 1 and l_len == 0:  # 重合，干扰块缺口在尾巴行，干扰块在目标块下方
        return f_index_list[0]
    else:  # 没有匹配到字符串则是未找到滑块
        raise Exception('无法识别滑块位置！')


@app.before_request
def _init_counters():
    with open('counter.json', 'r') as fp:
        g.request_counter = json.load(fp)


@app.route('/check/slider/', methods=['POST'], strict_slashes=False)
def slider_check():
    """
    请求body格式
    ｛"seed": 1234,
    "data": {
    "slider": "iVBORw0KGgoAAAANSUhEUgAAADIAAAAyCAYAAAAeP4ixAAAB8UlEQVR42u2ZvUoDQRSF8zY+hU9gpQStbAQtBX8IWIio8QcMURuDVkEEO4kWlpLKKtZqJ6niU4ycgSPjZTfZmLnrJt4Lh9md7Ozeb87dnU1SKllYjHe4hJgIiLGDYcKvb++u99nzeul03F2rNT4wTHRrYcYnH4I0Lq/c/cNj8WGY4PXumtdHt/sDZL96kC+MGzGe2m03O1f2oisoK4AQZlAUAgTJzk9PucWlZXd6cuxFCG7nCtK8uf2eWVy8ft7wZSGF2cZnOOawduaTxT6TRst+tiwxjud2eec5HgxPhItJEF5UthCSJIxUCIEJkmOpar0ZHwRJEQRJJIHIWZVJhyXF/iR3OR6Q0UFQ41lAJFRYZnAV4j7bNJCoTzSeiBAAGuSILDfMLEsIbegUwHBM2mSogxzVL/o6kSYmneX4qKt/EgggQkeGBRlmjBrI+samh+jnSNbZzvKZGgjLCsriwKhSAVlZrXg3uB7wKaSp6CBIXNqPxyfuGU1FB4ETmCG2eBlEeQGwsr2nJhUQ3h9cwHiv8OZHS4X9ocK+pG3ZRgeRyfAVhK7IhGMpFxCt5KMCpIEAAm+lmiAqP07k7Yja1968HckNxBwxR+yp9XtHklbyf72OTNTKrg5ijpgj5siEO/KXUag/fAoBYWFhYWFhkRJfOqu1esi4SCQAAAAASUVORK5CYII=",
    "background": "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",
    "y": "36,24,22,29,14,var host = window.location.host;var seed = callThePageFunction(224566235);seed = host.indexOf('.')>2?parseInt(seed/(host.charCodeAt(0)+host.charCodeAt(1)+host.charCodeAt(2))):parseInt(seed/(host.charCodeAt(0)+host.charCodeAt(1)));seed=parseInt(seed/41);seed=parseInt(seed/999);seed=seed%902;seed=Math.abs(seed+1)%5;seed=Math.abs(seed+1)%5;seed=Math.abs(seed+1)%5;seed=Math.abs(seed+1)%5;y_index=seed;"
  }｝
    :return:{"code": 0, "x_index": 193, "y_index": 17, "message": "操作成功"}
    """
    remote_ip = request.remote_addr
    message = {}
    g.request_counter['total'] = g.request_counter.get('total') + 1
    req_data = request.get_data(parse_form_data=True, as_text=True)
    logger.info('远程主机【{}】请求数据【{}】'.format(remote_ip, req_data))
    if len(req_data) != 0:
        try:
            context = js2py.EvalJs()
            req_json = json.loads(req_data)
            background = base64_to_image(req_json.get('data').get('background'))
            slider = base64_to_image(req_json.get('data').get('slider'))
            y = req_json.get('data').get('y')
            seed = req_json.get('seed')
            # js统一执行
            # js_content = """
            #         var window={location:{host: "%s"}}
            #         function callThePageFunction(seed) {
            #             htmlSeed = %s
            #             return seed = seed > 0 ? seed - htmlSeed : seed + htmlSeed;
            #                         }
            #         sy="%s"
            #         var arr = sy.split(',')
            #         var bds = arr[arr.length - 1]
            #         eval(bds)
            #         var y = arr[y_index]
            #         """ % ('fj.122.gov.cn', seed, y)
            # context.execute(js_content)
            # y_index = int(context.y)
            # js分段执行
            js_content = """
                                var window={location:{host: "%s"}}
                                function callThePageFunction(seed) {
                                    htmlSeed = %s
                                    return seed = seed > 0 ? seed - htmlSeed : seed + htmlSeed;
                                                }
                                """ % ('fj.122.gov.cn', seed)
            context.execute(js_content)
            y_list = y.split(',')
            y_js = y_list[-1]
            [context.execute(y_js_split) for y_js_split in y_js.split(';')]  # 分段执行js
            y_index = int(y_list[int(context.y_index)])
            # 获取图片参数
            _, width, _ = background.shape
            s_height, _, _ = slider.shape
            cut_background = background[y_index + 10:y_index + s_height - 10, 0:width]
            cut_thresh = to_thresh(cut_background)
            x_index = calculate_index(thresh2str(cut_thresh))
            message['code'] = 0
            message['x_index'] = x_index - 10 + round(random.random(), 1)  # -10，偏移量，增加小数点一位
            message['y_index'] = y_index
            message['message'] = '操作成功！'
            g.request_counter['success'] = g.request_counter.get('success') + 1
            dict2json(req_json, os.path.join(success_data, time_file_name('json')))
        except Exception as e:
            message['code'] = -1
            message['message'] = str(e)
            g.request_counter['failure'] = g.request_counter.get('failure') + 1
            dict2json(req_json, os.path.join(failure_data, time_file_name('json')))
        success_ratio = round((g.request_counter.get('success') / g.request_counter.get('total')) * 100, 2)
        logger.info('远程主机【{}】返回数据【{}】 识别成功率【{}%】'.format(remote_ip, message, success_ratio))
        dict2json(g.request_counter, 'counter.json')
        response = make_response(jsonify(message), 200)
        return response


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
