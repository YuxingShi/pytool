# coding:utf-8
# @Time    : 2022/9/29 19:45
# @Author  : ShiYuxing
# @Email   : shiyuxing1988@gmail.com
# @File    : test_server.py
# 测试试用服务
# @Software: hzpython
import hashlib
from flask import Flask, make_response, request, jsonify
from loguru import logger

from tool_func import *


app = Flask(__name__)
curpath = os.path.split(os.path.realpath(__file__))[0]
check_directory(os.path.join(curpath, 'logs'))
check_directory(os.path.join(curpath, 'failure_data'))
check_directory(os.path.join(curpath, 'success_data'))

logfile = os.path.join(curpath, 'logs', 'checkcode.log')
logger.add(logfile, level="INFO", rotation="500MB", encoding="utf-8", enqueue=True, retention="30 days")
failure_data = os.path.join(curpath, 'failure_data')
success_data = os.path.join(curpath, 'success_data')


@app.route('/tool/sm2Encrypt/', methods=['POST'], strict_slashes=False)
def sm2Encrypt():
    remote_ip = request.remote_addr
    message = {}
    req_data = request.get_data(parse_form_data=True, as_text=True)
    logger.info('远程主机【{}】请求数据【{}】'.format(remote_ip, req_data))
    if len(req_data) != 0:
        try:
            req_json = json.loads(req_data)
            text = req_json.get('text')
            public_key = req_json.get('public_key')
            message['code'] = 0
            message['sm2password'] = sm2_password(text, public_key)
            message['message'] = '操作成功！'
        except Exception as e:
            message['code'] = -1
            message['message'] = str(e)
        response = make_response(jsonify(message), 200)
        logger.info('远程主机【{}】返回数据【{}】'.format(remote_ip, message))
        return response


@app.route('/tool/hncb_pre_login/', methods=['POST'], strict_slashes=False)
def hncb_pre_login():
    remote_ip = request.remote_addr
    message = {}
    key = request.args.get('key')
    req_data = request.get_data(parse_form_data=True, as_text=True)
    # text = json.dumps(json.loads(req_data), ensure_ascii=False)
    logger.info('远程主机【{}】请求数据【{}】'.format(remote_ip, req_data))
    if len(req_data) != 0:
        try:
            bytes_encrypt_key = bytes(key, encoding='utf-8')
            sm4_utils = SMUtils(bytes_encrypt_key)
            bytes_raw_string = bytes(req_data, encoding='utf-8')
            encrypt_string = sm4_utils.SM4encryptData_ECB(bytes_raw_string)
            message['code'] = 0
            message['sm4Encrypt'] = encrypt_string
            message['CRC'] = SMUtils.getSM3(req_data)
            message['message'] = '操作成功！'
        except Exception as e:
            message['code'] = -1
            message['message'] = str(e)
        response = make_response(jsonify(message), 200)
        logger.info('远程主机【{}】返回数据【{}】'.format(remote_ip, message))
        return response


@app.route('/tool/hncb_files/', methods=['POST'], strict_slashes=False)
def hncb_files():
    """
    生成补贴文件
    请求数据格式：对象姓名|身份证号|发放账号|补贴标准|补贴数量|应发金额|实发金额|补贴类型代码|备注|操作类型|是否代领|代领明细信息(无代领信息为空)；
    :return:
    """
    remote_ip = request.remote_addr
    message = {}
    key = request.args.get('key')
    req_data = request.get_data(parse_form_data=True, as_text=True)
    logger.info('远程主机【{}】请求数据【{}】'.format(remote_ip, req_data))
    if len(req_data) != 0:
        try:
            bytes_encrypt_key = bytes(key, encoding='utf-8')
            sm4_utils = SMUtils(bytes_encrypt_key)
            # 对上传的数据进行处理
            rows = req_data.split('\r\n')
            new_rows = []
            raw_string = ''
            for row in rows:
                cols = row.split('|')
                new_cols = []
                for col in cols[:3]:  # 前三列进行sm4加密 对象姓名|身份证号|发放账号
                    if col == '':
                        new_col = ''
                    else:
                        new_col = sm4_utils.SM4encryptData_ECB(bytes(col, encoding='utf-8'))
                    new_cols.append(new_col)
                new_cols.extend(cols[3:])
                new_rows.append('|'.join(new_cols))
                raw_string += new_cols[2] + new_cols[0] + new_cols[1] + new_cols[6]  # MD5值：加密后的卡号、补贴对象姓名、身份证号、金额(实发金额) 32位小写
            new_rows.append(hashlib.md5(bytes(raw_string, encoding='utf-8')).hexdigest())
            return_text = '\n'.join(new_rows)
            save2file('./test.txt', return_text)
            message['code'] = 0
            message['text'] = return_text
            message['message'] = '操作成功！'
        except Exception as e:
            message['code'] = -1
            message['message'] = str(e)
        response = make_response(jsonify(message), 200)
        logger.info('远程主机【{}】返回数据【{}】'.format(remote_ip, message))
        return response


@app.route('/tool/sm4Decrypt/', methods=['POST'], strict_slashes=False)
def sm4Decrypt():
    remote_ip = request.remote_addr
    message = {}
    req_data = request.get_data(parse_form_data=True, as_text=True)
    logger.info('远程主机【{}】请求数据【{}】'.format(remote_ip, req_data))
    if len(req_data) != 0:
        try:
            req_json = json.loads(req_data)
            text = req_json.get('text')
            key = req_json.get('key')
            bytes_encrypt_key = bytes(key, encoding='utf-8')
            sm4_utils = SMUtils(bytes_encrypt_key)
            # message['code'] = 0
            # message['sm4Decrypt'] = sm4_utils.SM4decryptData_ECB(text)
            # message['message'] = '操作成功！'
            message = sm4_utils.SM4decryptData_ECB(text)
        except Exception as e:
            message['code'] = -1
            message['message'] = str(e)
        response = make_response(message, 200)
        logger.info('远程主机【{}】返回数据【{}】'.format(remote_ip, message))
        return response


@app.route('/tool/RSAEncrypt/', methods=['POST'], strict_slashes=False)
def RSAEncrypt():
    remote_ip = request.remote_addr
    message = {}
    req_data = request.get_data(parse_form_data=True, as_text=True)
    logger.info('远程主机【{}】请求数据【{}】'.format(remote_ip, req_data))
    if len(req_data) != 0:
        try:
            req_json = json.loads(req_data)
            text = req_json.get('text')
            key = req_json.get('key')
            bytes_encrypt_key = bytes(key, encoding='utf-8')
            sm4_utils = SMUtils(bytes_encrypt_key)
            # message['code'] = 0
            # message['sm4Decrypt'] = sm4_utils.SM4decryptData_ECB(text)
            # message['message'] = '操作成功！'
            message = sm4_utils.SM4decryptData_ECB(text)
        except Exception as e:
            message['code'] = -1
            message['message'] = str(e)
        response = make_response(message, 200)
        logger.info('远程主机【{}】返回数据【{}】'.format(remote_ip, message))
        return response


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
