# coding:utf-8
import json
import time
import os
from flask import request, Flask, make_response, jsonify
from flask_httpauth import HTTPBasicAuth

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False  # 设置是否传递异常 , 如果为True, 则flask运行中的错误会显示到网页中, 如果为False, 则会输出到文件中
auth = HTTPBasicAuth()


def get_json(filename):
    file_path = os.path.abspath(filename)
    if os.path.isfile(file_path):
        with open(file_path, 'r') as fp:
            return json.load(fp)
    else:
        return None


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
    data_dict = get_json('data.json')
    message = {}
    message['code'] = 0
    message['ip'] = data_dict.get('ip')
    message['serialNumber'] = data_dict.get('serialNumber') or '无法获取主机序列号！'
    return make_response(jsonify(message), 200)


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

