# coding:utf-8
import json
import sys
import re
import time
import os
import socket
from flask import request, Flask, make_response, jsonify, g
from flask_httpauth import HTTPBasicAuth

PLATFORM = sys.platform

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False  # 设置是否传递异常 , 如果为True, 则flask运行中的错误会显示到网页中, 如果为False, 则会输出到文件中
auth = HTTPBasicAuth()


def get_localhost_ip():
    ip = None
    try:
        soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        soc.connect(('8.8.8.8', 80))
        ip = soc.getsockname()[0]
    finally:
        soc.close()
    return ip


def get_serial_number():
    if PLATFORM == 'win32':
        cmd = 'wmic bios get serialnumber'
    elif PLATFORM == 'darwin':
        cmd = "/usr/sbin/system_profiler SPHardwareDataType |fgrep 'Serial'|awk '{print $NF}'"
    elif PLATFORM == 'linux2':
        cmd = ''
    os.system()


@auth.get_password
def get_password(username):
    if username == "hztech":
        return "success"
    return None


@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized'}), 401)


@app.route('/information', methods=['GET'])
@auth.login_required
def information():
    # 获取本机ip及序列号
    message = {}

    if result[0] == 0:
        return_dict = {'code': result[0], 'message': result[1], 'wwlsh': result[2]}
    else:
        return_dict = {'code': result[0], 'message': result[1]}
    return make_response(jsonify(return_dict), 200)


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


@app.route('/shutdown', methods=['POST'])
def shutdown():
    shutdown_server()
    return 'Server shutting down...'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)

