# coding:utf-8
import base64
from urllib.parse import urlencode, quote
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder

student_info_data = {"SFZMHM": "350121196004243523",
                     "SFZMMC": "A",
                     "SFZYXQZ": "2122-12-31",
                     "SFZYXQS": "2007-07-13",
                     "XM": "欧梅碧",
                     "CSRQ": "1960-04-24",
                     "GJ": "156",
                     "XB": "0",
                     "DJZSXZQH": "350121",
                     "DJZSXXDZ": "福建省福州市闽侯县红峰村宪窗15号1",
                     "DZYX": "555555140742@qq.com",
                     "LXZSXZQH": "350121",
                     "LY": "B",
                     "LXZSXXDZ": "福建省福州市闽侯县红峰村宪窗19号2",
                     "SJHM": "15606915242",
                     "BS": "1",
                     "YJDZ": "福建省福州市闽侯县红峰村宪窗19号3",
                     "YZBM": "350100",
                     "XZQH": "350121",
                     "LXDH": "77777777",
                     "ZZZM": "",
                     "ZKCX": "C1",
                     "MODAL": "2"
                     }

headers = {"Content-Type": "application/json",
           "Authorization": "Basic aHp0ZWNoOnN1Y2Nlc3M="
           }


def get_image_stream(file_name):
    with open(file_name, 'rb') as fp:
        return fp.read()


resp = requests.post('http://127.0.0.1:5000/submit_student_info', json=student_info_data, headers=headers)
if resp.status_code == 200:
    resp_json = resp.json()
    print('resp_json', resp_json)
    if resp_json.get('code') == 0:
        # 上传图片
        wwlsh = resp_json.get('wwlsh')
        image_content = str(base64.encodebytes(get_image_stream(r'F:\test\test1\9AE33987A61752E3644A258BAA045ADB.jpg')),
                            encoding='utf-8')
        image_data = {'wwlsh': wwlsh,
                      'imageName': 4,
                      'imageContent': image_content}
        resp = requests.post('http://127.0.0.1:5000/image_upload', json=image_data, headers=headers)
        print('resp_json', resp.json())
        image_content = str(base64.encodebytes(get_image_stream(r'F:\test\test1\1111.jpg')),
                            encoding='utf-8')
        image_data = {'wwlsh': wwlsh,
                      'imageName': 6,
                      'imageContent': image_content}
        resp = requests.post('http://127.0.0.1:5000/image_upload', json=image_data, headers=headers)
        print('resp_json', resp.json())
        image_content = str(base64.encodebytes(get_image_stream(r'F:\test\test1\8df80a561d42d67035f2f784779e0f1a.jpg')),
                            encoding='utf-8')
        image_data = {'wwlsh': wwlsh,
                      'imageName': 2,
                      'imageContent': image_content}
        resp = requests.post('http://127.0.0.1:5000/image_upload', json=image_data, headers=headers)
        print('resp_json', resp.json())
        # 确认提交修改信息
        image_data = {'wwlsh': wwlsh}
        resp = requests.post('http://127.0.0.1:5000/commit', json=image_data, headers=headers)
        print('resp_json', resp.json())
# resp = requests.post('http://127.0.0.1:5001/get_code', data=get_image_stream(r'E:\PyCharmProj\pytool\auto_apply\check_code\1649819891909.jpg'))
# print('resp', resp.status_code)
# if resp.status_code == 200:
#     print(resp.json())
