# coding:utf-8
import base64
import json
import os
import time
from urllib.parse import quote, urlencode
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from requests_toolbelt.multipart.encoder import MultipartEncoder

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class SecureKey(object):
    url = 'https://127.0.0.1:53015/ia300'
    session = requests.session()
    headers = {"Host": "127.0.0.1:53015",
               "Connection": "keep-alive",
               "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
               "sec-ch-ua-mobile": "?0",
               "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
               "Content-type": "application/x-www-form-urlencoded",
               "Accept": "*/*",
               "Origin": "https://fj.122.gov.cn",
               "Sec-Fetch-Site": "cross-site",
               "Sec-Fetch-Mode": "cors",
               "Sec-Fetch-Dest": "empty",
               "Referer": "https://fj.122.gov.cn/",
               "Accept-Encoding": "gzip, deflate, br",
               "Accept-Language": "zh-CN,zh;q=0.9"}

    def __init__(self, passwd):
        self.passwd = passwd

    def _post(self, data):
        resp = self.session.request('POST', url=self.url, headers=self.headers, data=data, verify=False)
        if resp.status_code == 200:
            return resp.json()

    def _IA300CheckExist(self):
        data = 'json={"function":"IA300CheckExist"}'
        resp_json = self._post(data)
        if resp_json.get('devCount') == 1:
            return True
        else:
            return False

    def _IA300Open(self):
        data = 'json={"function":"IA300Open", "passWd":"%s"}' % self.passwd
        self._post(data)

    def _IA300GetUID(self):
        data = 'json={"function":"IA300GetUID"}'
        resp_json = self._post(data)
        return resp_json.get('HardwareID')

    def IA300SHA1WithSeed(self, seed=None):
        if seed:
            data = 'json={"function":"IA300SHA1WithSeed", "Seed":"%s"}' % seed
            resp_json = self._post(data)
            return resp_json.get('digest')

    def get_uid(self):
        if self._IA300CheckExist():
            self._IA300Open()
            return self._IA300GetUID()
        else:
            return None

    def get_ticket_with_seed(self, seed=None):
        if self._IA300CheckExist():
            self._IA300Open()
            return self.IA300SHA1WithSeed(seed=seed)
        else:
            return None


class Fj122gov(object):
    url = 'https://fj.122.gov.cn'
    cookies_path = os.path.abspath('cookies.json')
    session = requests.session()
    headers_raw = {"Host": "fj.122.gov.cn",
                   "Connection": "keep-alive",
                   "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
                   "Accept-Encoding": "gzip, deflate, br",
                   "Accept-Language": "zh-CN,zh;q=0.9"}
    usb_key = None
    csessionid = None  # 验证码
    szzsid = None  # 设备id
    ticket = None  # 通过usbkey算的hash值
    wwlsh = None  # 学员流水号，用与数据修改

    def __init__(self, username, passwd, usb_key_passwd):
        self.usb_key = SecureKey(usb_key_passwd)
        self.szzsid = self.usb_key.get_uid()
        self.username = username
        self.passwd = quote(str(base64.encodebytes(bytes(passwd, encoding='utf-8')), encoding='utf-8').strip('\n'))
        self._load_local_cookies()

    def _init_config_dict(self):
        with open(self.cookies_path, 'r') as fp:
            self.config_dict = json.load(fp)

    def _get_url(self, path):
        return '{}{}'.format(self.url, path)

    def _get(self, url, headers, params=None):
        resp = self.session.request('GET', url=url, headers=headers, params=params, verify=False)
        if resp.status_code == 200:
            return resp

    def _post(self, url, headers, params=None, data=None):
        resp = self.session.request('POST', url=url, headers=headers, params=params, data=data, verify=False)
        if resp.status_code == 200:
            return resp

    def _load_local_cookies(self):
        with open(self.cookies_path, 'r') as fp:
            json_cookies = json.load(fp)
            for item in json_cookies.items():
                self.session.cookies[item[0]] = item[1]

    def _save_cookies(self):
        with open(self.cookies_path, 'w') as fp:
            json.dump(self.session.cookies.get_dict(), fp)  # 将cookies存储到本地

    def _clear_cookies(self):
        self.session.cookies.clear()

    @staticmethod
    def _save_image(content):
        save_image_path = 'check_code/{}.jpg'.format(int(time.time() * 1000))
        with open(save_image_path, 'wb') as fp:
            fp.write(content)

    def login_t2(self):
        headers = {"Host": "fj.122.gov.cn",
                   "Connection": "keep-alive",
                   "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
                   "sec-ch-ua-mobile": "?0",
                   "Upgrade-Insecure-Requests": "1",
                   "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
                   "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                   "Sec-Fetch-Site": "none",
                   "Sec-Fetch-Mode": "navigate",
                   "Sec-Fetch-User": "?1",
                   "Sec-Fetch-Dest": "document",
                   "Accept-Encoding": "gzip, deflate, br",
                   "Accept-Language": "zh-CN,zh;q=0.9"}
        url = self._get_url('/m/login?t=2')
        try:
            self._get(url, headers=headers)
        except requests.exceptions.ProxyError as e:
            self.login_t2()

    def user_m_index(self):
        headers = {"Host": "fj.122.gov.cn",
                   "Connection": "keep-alive",
                   "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
                   "Accept": "application/json, text/javascript, */*; q=0.01",
                   "Origin": "https://fj.122.gov.cn",
                   "X-Requested-With": "XMLHttpRequest",
                   "Referer": "https://fj.122.gov.cn/m/login?t=2",
                   "Accept-Encoding": "gzip, deflate, br",
                   "Accept-Language": "zh-CN,zh;q=0.9"}
        url = self._get_url('/user/m/index')
        self._post(url, headers=headers)

    def m_tmri_captcha_mchecktype(self):
        headers = {"Host": "fj.122.gov.cn",
                   "Connection": "keep-alive",
                   "sec-ch-ua-mobile": "?0",
                   "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
                   "Sec-Fetch-Site": "same-origin",
                   "Sec-Fetch-Mode": "cors",
                   "Sec-Fetch-Dest": "empty",
                   "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
                   "Accept": "application/json, text/javascript, */*; q=0.01",
                   "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                   "Origin": "https://fj.122.gov.cn",
                   "X-Requested-With": "XMLHttpRequest",
                   "Referer": "https://fj.122.gov.cn/m/login?t=2",
                   "Accept-Encoding": "gzip, deflate, br",
                   "Accept-Language": "zh-CN,zh;q=0.9"
                   }
        params = {'checktype': 'sgcFtVUtwJZtzwTT'}
        data_str = urlencode(params)
        # time_create = int(time.time() * 1000)
        # time_expire = time_create + 1010
        url = self._get_url('/m/tmri/captcha/mcheckType')
        # self.session.cookies['_uab_collina'] = '164687783976146996222157'
        # self.session.cookies['_dd_s'] = 'logs=1&id=d53664ff-ab45-4642-9015-fd40c376b331&created={}&expire={}'.format(
        #     time_create, time_expire)
        self._post(url, headers=headers, data=data_str)

    def m_syscode_getFeedBackConfig(self):
        headers = {"Host": "fj.122.gov.cn",
                   "Connection": "keep-alive",
                   "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
                   "Accept": "application/json, text/javascript, */*; q=0.01",
                   "Origin": "https://fj.122.gov.cn",
                   "X-Requested-With": "XMLHttpRequest",
                   "Referer": "https://fj.122.gov.cn/m/login?t=2",
                   "Accept-Encoding": "gzip, deflate, br",
                   "Accept-Language": "zh-CN,zh;q=0.9"
                   }
        time_create = int(time.time() * 1000)
        time_expire = time_create + 1010
        url = self._get_url('/m/syscode/getFeedBackConfig')
        self.session.cookies['_uab_collina'] = '164687783976146996222157'
        self.session.cookies['_dd_s'] = 'logs=1&id=d53664ff-ab45-4642-9015-fd40c376b331&created={}&expire={}'.format(
            time_create, time_expire)
        self._post(url, headers=headers)

    def m_tmri_captcha_math(self):
        """
        获取验证码
        """
        headers = {"Host": "fj.122.gov.cn",
                   "Connection": "keep-alive",
                   "sec-ch-ua-mobile": "?0",
                   "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
                   "Sec-Fetch-Site": "same-origin",
                   "Sec-Fetch-Mode": "no-cors",
                   "Sec-Fetch-Dest": "image",
                   "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
                   "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
                   "X-Requested-With": "XMLHttpRequest",
                   "Referer": "https://fj.122.gov.cn/m/login?t=2",
                   "Accept-Encoding": "gzip, deflate, br",
                   "Accept-Language": "zh-CN,zh;q=0.9"
                   }
        time_create = int(time.time() * 1000)
        url = self._get_url('/m/tmri/captcha/math?nocache={}'.format(time_create))
        resp = self._get(url, headers=headers)
        content = resp.content
        self._save_image(content)
        resp_get_code = requests.post('http://127.0.0.1:5001/get_code', data=content)  # 调用验证码服务地址获取验证码
        json_resp_get_code = resp_get_code.json()
        if json_resp_get_code.get('code') == 0:
            self.csessionid = json_resp_get_code.get('result')
        else:  # 重新获取验证码并计算
            self.m_tmri_captcha_math()

    def user_m_login_checkkey(self):
        """
        @szzsid: usbKey id;
        @csessionid: 验证码值
        """
        headers = {"Host": "fj.122.gov.cn",
                   "Connection": "keep-alive",
                   "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
                   "sec-ch-ua-mobile": "?0",
                   "Upgrade-Insecure-Requests": "1",
                   "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
                   "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                   "Sec-Fetch-Site": "none",
                   "Sec-Fetch-Mode": "navigate",
                   "Sec-Fetch-User": "?1",
                   "Sec-Fetch-Dest": "document",
                   "Accept-Encoding": "gzip, deflate, br",
                   "Accept-Language": "zh-CN,zh;q=0.9",
                   "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}
        url = self._get_url('/user/m/login/checkkey')
        params = {'usertype': '2',
                  'systemid': 'main',
                  'ticket': '',
                  'szzsid': self.szzsid,
                  'username': self.username,
                  'password': self.passwd,
                  'csessionid': self.csessionid}
        data_str = urlencode(params)
        resp = self._post(url, headers=headers, data=data_str)
        json_resp = resp.json()
        code_out = json_resp.get('code')
        if code_out == 412:
            if json_resp.get('data').get('code') == -5:  # 验证码错误
                self.m_tmri_captcha_math()
                self.user_m_login_checkkey()
            else:
                self.user_logout()  # 进行登出操作
                self.login()  # 重新登录
                return
        elif code_out == 200:
            self.ticket = self.usb_key.get_ticket_with_seed(json_resp.get('message'))
            print('self.ticket', self.ticket)

    def user_m_loginkey(self):
        """
        @szzsid: usbKey id;
        @csessionid: 验证码值
        """
        headers = {"Host": "fj.122.gov.cn",
                   "Connection": "keep-alive",
                   "Cache-Control": "max-age=0",
                   "Upgrade-Insecure-Requests": "1",
                   "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
                   "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                   "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                   "Referer": "https://fj.122.gov.cn/m/login?t=2",
                   "Accept-Encoding": "gzip, deflate, br",
                   "Accept-Language": "zh-CN,zh;q=0.9"}
        url = self._get_url('/user/m/loginkey')
        params = {'usertype': '2',
                  'systemid': 'main',
                  'ticket': self.ticket,
                  'szzsid': self.szzsid,
                  'username': self.username,
                  'password': self.passwd,
                  'csessionid': self.csessionid,
                  '5C54E6455325A3AB723CAA5EF1820BF6': '1ae1ce03ae02927c7c1b339f5fe4ff37'}
        data_str = urlencode(params)
        resp = self._post(url, headers=headers, data=data_str)
        if resp.status_code != 200:
            self.user_m_loginkey()

    def user_logout(self):
        """
        用户登出
        """
        headers = {"Host": "fj.122.gov.cn",
                   "Upgrade-Insecure-Requests": "1",
                   "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
                   "Accept": "application/x-ms-application, image/jpeg, application/xaml+xml, image/gif, image/pjpeg, application/x-ms-xbap, */*",
                   "Referer": "https://fj.122.gov.cn",
                   "Accept-Encoding": "gzip, deflate, br",
                   "Accept-Language": "zh-CN",
                   "DNT": "1",
                   "Connection": "keep-alive"}
        url = self._get_url('/user/logout')
        self._get(url, headers=headers)

    def m_loginsuccess(self):
        """
        @szzsid: usbKey id;
        @csessionid: 验证码值
        """
        headers = {"Host": "fj.122.gov.cn",
                   "Connection": "keep-alive",
                   "Cache-Control": "max-age=0",
                   "Upgrade-Insecure-Requests": "1",
                   "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
                   "Content-Type": "application/x-www-form-urlencoded",
                   "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                   "Referer": "https://fj.122.gov.cn/m/login?t=2",
                   "Accept-Encoding": "gzip, deflate, br",
                   "Accept-Language": "zh-CN,zh;q=0.9"}
        url = self._get_url('/m/loginsuccess')
        self._get(url, headers=headers)
        self._save_cookies()

    def test_login_status(self):
        """
        判断当前登录状态
        读取本地保存的cookie，进行验证，返回重定向到登录页面时候
        """
        headers = {"Host": "fj.122.gov.cn",
                   "Connection": "keep-alive",
                   "Upgrade-Insecure-Requests": "1",
                   "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
                   "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                   "Accept-Encoding": "gzip, deflate, br",
                   "Accept-Language": "zh-CN,zh;q=0.9"}
        url = self._get_url('/drv/sl/isTest')
        try:
            resp = self._post(url, headers=headers)
        except requests.exceptions.ProxyError as e:
            return False
        if resp:
            request_url = resp.url
            if request_url.count('m/login;'):  # url被重定向到登录页面
                return False
            else:
                return True
        else:
            return False

    def drv_sl_isTest(self):
        """
        读取本地保存的cookie，进行验证，返回重定向到登录页面时候
        """
        headers = {"Host": "fj.122.gov.cn",
                   "Connection": "keep-alive",
                   "Upgrade-Insecure-Requests": "1",
                   "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
                   "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                   "Accept-Encoding": "gzip, deflate, br",
                   "Accept-Language": "zh-CN,zh;q=0.9"}
        url = self._get_url('/drv/sl/isTest')
        self._post(url, headers=headers)

    def drv_sl_check_sfzmhm(self, sfzmhm='350121196004243523'):
        """
        确认再次提交修改， 并获取学员流水号
        """
        headers = {"Host": "fj.122.gov.cn",
                   "Connection": "keep-alive",
                   "Upgrade-Insecure-Requests": "1",
                   "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
                   "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                   "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                   "Accept-Encoding": "gzip, deflate, br",
                   "Accept-Language": "zh-CN,zh;q=0.9"}
        data = {'sfzmmc': 'A', 'sfzmhm': sfzmhm, 'ignoreNetDrvFlow': '1'}
        data_str = urlencode(data)
        url = self._get_url('/drv/sl/check/sfzmhm')
        resp = self._post(url, headers=headers, data=data_str)
        json_resp = json.loads(resp.text)
        code = json_resp.get('code')
        if code == 200:
            self.wwlsh = json_resp.get('data').get('wwlsh')

    def drv_sl_geneUsbKey(self):
        """
        获取 seed值并计算ticket2
        """
        headers = {"Host": "fj.122.gov.cn",
                   "Connection": "keep-alive",
                   "Upgrade-Insecure-Requests": "1",
                   "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
                   "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                   "Accept-Encoding": "gzip, deflate, br",
                   "Accept-Language": "zh-CN,zh;q=0.9"}
        url = self._get_url('/drv/sl/geneUsbKey')
        params = {'sid': self.szzsid}
        data = 'sid={}'.format(self.szzsid)
        resp = self._post(url, headers=headers, params=params, data=data)
        if resp:
            resp_json = resp.json()
            if resp_json.get('code') == 200:
                ticket = self.usb_key.get_ticket_with_seed(resp.json().get('message'))
                return ticket
        self.drv_sl_geneUsbKey()

    def drv_sl_saveYyslxx(self, data=None):
        """
        更新报名信息
        """
        headers = {"Host": "fj.122.gov.cn",
                   "Connection": "keep-alive",
                   "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
                   "Accept": "application/json, text/javascript, */*; q=0.01",
                   "Origin": "https://fj.122.gov.cn",
                   "X-Requested-With": "XMLHttpRequest",
                   "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                   "Referer": "https://fj.122.gov.cn/drv/sl/edit/235002203187549414",
                   "Accept-Encoding": "gzip, deflate, br",
                   "Accept-Language": "zh-CN,zh;q=0.9"}
        url = self._get_url('/drv/sl/saveYyslxx')
        ticket = self.drv_sl_geneUsbKey()
        data['TICKET'] = ticket
        data_str = urlencode(data)
        resp = self._post(url, headers=headers, data=data_str)
        json_resp = resp.json()
        if json_resp.get('code') == 200:  # 返回操作成功
            return json_resp.get('data').get('wwlsh')  # 返回操作学员的流水号
        else:
            return None

    def drv_sl_image_save(self, wwlsh, bz, image_stream):
        """
        高拍仪图片保存
        @wwlsh XX流水号
        @params bz 4:身份证明正反面照片；6：驾驶证申请表照片；2：现场照片；8.驾驶证证件照
        @params image_stream:图片文件流
        """
        headers = {"Host": "fj.122.gov.cn",
                   "Connection": "keep-alive",
                   "User-Agent": "DoccameraOcx",
                   "DNT": "1",
                   "Pragma": "no-cache"
                   }
        url = self._get_url('/drv/sl/image/save')
        ticket = self.drv_sl_geneUsbKey()
        params = {'bz': bz,
                  'wwlsh': wwlsh,
                  'ticket': ticket}
        trackdata = ('D://{}.JPG'.format(bz), image_stream, 'image/pjpeg')
        fields = {
            'para1': bytes('福建捷宇电脑科技有限公司', encoding='utf-8'),
            'para2': 'SGH',
            'trackdata': trackdata,
            'submitted': 'hello'
        }
        multipart_encoder = MultipartEncoder(fields=fields, boundary='---------------------------7b4a6d158c9')
        headers['Content-Type'] = multipart_encoder.content_type
        resp = self._post(url, headers=headers, params=params, data=multipart_encoder)
        return resp.text

    def drv_sl_commit(self, wwlsh):
        """
        提交确认
        """
        headers = {"Host": "fj.122.gov.cn",
                   "Connection": "keep-alive",
                   "Cache-Control": "no-cache",
                   "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                   "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
                   "Accept-Encoding": "gzip, deflate",
                   "Referer": "https://fj.122.gov.cn/drv/sl/image/235002204088030157/2",
                   "Accept-Language": "zh-CN",
                   "DNT": "1",
                   }
        url = self._get_url('/drv/sl/commit')
        params = {'ly': 'B',
                  'wwlsh': wwlsh,
                  'zpwwlsh': ''}
        data_str = urlencode(params)
        resp = self._post(url, headers=headers, data=data_str)
        return resp.text

    def drv_sl_image_get_image(self, wwlsh, bz):
        """
        图片获取
        @params bz 4:身份证明正反面照片；6：驾驶证申请表照片；2：现场照片
        """
        headers = {"Host": "fj.122.gov.cn",
                   "Connection": "keep-alive",
                   "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
                   "Accept-Encoding": "gzip, deflate",
                   "Referer": "https://fj.122.gov.cn/drv/sl/image/235002204088030157/2",
                   "Accept-Language": "zh-CN",
                   "DNT": "1",
                   "Pragma": "no-cache"
                   }
        url = self._get_url('/drv/sl/image/getImage')
        params = {'bz': bz,
                  'wwlsh': wwlsh}
        resp = self._get(url, headers=headers, params=params)
        self._save_image(resp.content)

    def login(self):
        self._clear_cookies()
        self.login_t2()
        self.user_m_index()
        self.m_tmri_captcha_mchecktype()
        self.m_syscode_getFeedBackConfig()
        self.m_tmri_captcha_math()
        self.user_m_login_checkkey()
        self.user_m_loginkey()
        self.m_loginsuccess()

    def pre_apply(self, data=None):
        if data:
            sfzmhm = data.get('SFZMHM')  # 获取data中的身份证号码
            self.drv_sl_check_sfzmhm(sfzmhm)
            self.drv_sl_isTest()
            return self.drv_sl_saveYyslxx(data)

    def upload_image(self, data=None):
        if data:
            wwlsh = data.get('wwlsh')
            bz = data.get('imageName')
            image_base64 = data.get('imageContent')
            image_stream = base64.decodebytes(bytes(image_base64, encoding='utf-8'))
            self.drv_sl_image_save(wwlsh, bz, image_stream)

    def commit(self, data=None):
        if data:
            wwlsh = data.get('wwlsh')
            self.drv_sl_commit(wwlsh=wwlsh)


if __name__ == '__main__':
    key = SecureKey('24680!#%&(tmri')
    print(key._IA300CheckExist())
    # print(key.get_ticket_with_seed('SSHLGDMVHKYBRMOZOVDWOLTSGAAITIPS'))
    # fj = Fj122gov('35011801016507', 'Za123456', '24680!#%&(tmri')
    # if fj.test_login_status():
    #     fj.pre_apply()
    # else:
    #     fj.login()
    #     fj.pre_apply()
