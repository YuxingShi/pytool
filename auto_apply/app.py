# coding:utf-8
import json
from flask import request, Response, Flask, make_response, jsonify, abort
from flask_httpauth import HTTPBasicAuth
from flask_cors import CORS  # 服务端支持跨域获取数据
from functools import wraps

from cp_apply import Fj122gov

app = Flask(__name__)
CORS(app, supports_credentials=True)  # 服务端支持跨域获取数据
auth = HTTPBasicAuth()


@auth.get_password
def get_password(username):
    if username == "hztech":
        return "success"
    return None


@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized'}), 401)


@app.route('/submit_student_info', methods=['POST'])
@auth.login_required
def submit_student_info():
    if request.method == 'POST':
        req_data = request.get_data(parse_form_data=True, as_text=True)
        if len(req_data) != 0:
            json_data = json.loads(req_data)
            # 提交数据内容校验
            check_list = ["SFZMHM", "SFZMMC", "SFZYXQZ", "SFZYXQS", "XM", "CSRQ", "GJ", "XB", "DJZSXZQH", "DJZSXXDZ",
                          "DZYX", "LXZSXZQH", "LY", "LXZSXXDZ", "SJHM", "BS", "YJDZ", "YZBM", "XZQH", "ZZZM",
                          "ZKCX", "MODAL"]
            for key in check_list:
                if json_data.get(key) is None:  # 请求的数据中缺少列表中的字段则返回失败
                    return_dict = {'code': 2, 'message': '提交的内容缺少关键字:{}'.format(key)}
                    return make_response(jsonify(return_dict), 200)
            # 进入预报名程序
            fj = Fj122gov('35011801016507', 'Za123456', '24680!#%&(tmri')
            if fj.test_login_status():
                print('session未过期，直接报名！')
                result = fj.pre_apply(json_data)
                if result:  # 成功返回操作学员流水号
                    return_dict = {'code': 0, 'wwlsh': result, 'message': '学员信息保存成功！'}
                    return make_response(jsonify(return_dict), 200)
            else:
                print('session过期，重新登录后再预报名！')
                fj.login()
                result = fj.pre_apply(json_data)
                if result:  # 成功返回操作学员流水号
                    return_dict = {'code': 0, 'wwlsh': result, 'message': '学员信息保存成功！'}
                    return make_response(jsonify(return_dict), 200)
        else:
            return_dict = {'code': 1, 'message': '请求的body为空！'}
            return make_response(jsonify(return_dict), 200)


@app.route('/image_upload', methods=['POST'])
@auth.login_required
def image_upload():
    if request.method == 'POST':
        req_data = request.get_data(parse_form_data=True, as_text=True)
        if len(req_data) != 0:
            json_data = json.loads(req_data)
            fj = Fj122gov('35011801016507', 'Za123456', '24680!#%&(tmri')
            if fj.test_login_status():
                print('session未过期，上传图片！')
                desc = fj.upload_image(json_data)
            else:
                print('session过期，重新登录后再上传图片！')
                fj.login()
                desc = fj.upload_image(json_data)
            return_dict = {'result': 0, 'desc': desc}
            return make_response(jsonify(return_dict), 200)
        else:
            return_dict = {'result': 0, 'desc': '请求的body为空！'}
            return make_response(jsonify(return_dict), 200)


@app.route('/commit', methods=['POST'])
@auth.login_required
def commit():
    if request.method == 'POST':
        req_data = request.get_data(parse_form_data=True, as_text=True)
        if len(req_data) != 0:
            json_data = json.loads(req_data)
            fj = Fj122gov('35011801016507', 'Za123456', '24680!#%&(tmri')
            if fj.test_login_status():
                print('session未过期，确认提交！')
                desc = fj.commit(json_data)
            else:
                print('session过期，重新登录后再确认提交！')
                fj.login()
                desc = fj.commit(json_data)
            return_dict = {'result': 0, 'desc': desc}
            return make_response(jsonify(return_dict), 200)
        else:
            return_dict = {'result': 0, 'desc': '请求的body为空！'}
            return make_response(jsonify(return_dict), 200)


if __name__ == '__main__':
    app.run(debug=True)
