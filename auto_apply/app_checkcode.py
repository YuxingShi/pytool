# coding:utf-8
from flask import request, Flask, make_response, jsonify
from flask_cors import CORS  # 服务端支持跨域获取数据
from recognize_checkcode import get_verify_code


app = Flask(__name__)
CORS(app, supports_credentials=True)  # 服务端支持跨域获取数据


@app.route('/get_code', methods=['POST'])
def get_code():
    resp = make_response()
    resp.headers["Content-Type"] = "application/json"  # at JSON.parse (<anonymous>)
    resp.headers["Transfer-Encoding"] = 'zh-CN,zh;q=0.9'
    if request.method == 'POST':
        req_data = request.get_data()
        if len(req_data) != 0:
            result = get_verify_code(req_data)
            if result:
                return_result = {'code': 0, 'result': result}
            else:
                return_result = {'code': 1, 'result': None}
        else:
            return_result = {'code': 2, 'result': None}
        resp_data = jsonify(return_result)
        resp.response = resp_data
        return resp_data


if __name__ == '__main__':
    app.run(debug=True, port=5001)
