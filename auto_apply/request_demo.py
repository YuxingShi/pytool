# coding:utf-8
import base64
import os
import json
from urllib.parse import urlencode, quote
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder


def get_file_list(dir_path: str):
    return [os.path.join(dir_path, file_name) for file_name in os.listdir(dir_path)]


def load_json(file_name: str) -> dict:
    with open(file_name, 'r') as f:
        return json.load(f)


def post(file_name: str):
    body = load_json(file_name)
    check_resp = requests.post('http://localhost:5000/check/slider', json=body)
    if check_resp.status_code == 200:
        check_resp_json = check_resp.json()
        if check_resp_json.get('code') == 0:
            x = check_resp_json.get('x_index')
            y = check_resp_json.get('y_index')
            return x, y


if __name__ == "__main__":
    # for file_name in get_file_list(r'E:\PyCharmProj\pytool\auto_apply\failure_data'):
    # for file_name in get_file_list(r'E:\PyCharmProj\pytool\auto_apply\success_data'):
    #     print(post(file_name))
    # for _ in range(100):
    #     print(post('failure_data/f1.json'))
    print(post(r'E:\PyCharmProj\pytool\auto_apply\success_data\1658281701060.json'))

