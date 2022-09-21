# coding:utf-8
import json
import os
from loguru import logger
from flask import request, Flask, make_response, jsonify

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False  # 设置是否传递异常 , 如果为True, 则flask运行中的错误会显示到网页中, 如果为False, 则会输出到文件中


def get_json(filename):
    file_path = os.path.abspath(filename)
    if os.path.isfile(file_path):
        with open(file_path, 'r') as fp:
            return json.load(fp)
    else:
        return None


@app.route('/information', methods=['GET'])
def information():
    # 获取本机ip及序列号
    data_dict = get_json('data.json')
    message = {}
    message['code'] = 0
    message['ip'] = data_dict.get('LocalMachine').get('ip')
    message['biosSn'] = data_dict.get('LocalMachine').get('biosSn') or '无法获取BIOS序列号！'
    message['baseboardSn'] = data_dict.get('LocalMachine').get('baseboardSn') or '无法获取主版序列号！'
    message['cpuSn'] = data_dict.get('LocalMachine').get('cpuSn') or '无法获取CPU序列号！'
    logger.info('返回信息【{}】'.format(message))
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

