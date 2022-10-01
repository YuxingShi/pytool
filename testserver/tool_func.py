# coding: utf-8 -*- coding: utf-8
import base64
import binascii
import json
import os
import re
import time
from ftplib import FTP  # 加载ftp模块
import sys

import cv2
import paramiko
import stat
import numpy as np
from gmssl import sm2, sm3, func
from gmssl.sm4 import CryptSM4, SM4_ENCRYPT, SM4_DECRYPT


class FtpTool(object):
    """
    @note: upload local file or dirs recursively to ftp server
    """
    ftp = None
    _XFER_FILE = 'FILE'
    _XFER_DIR = 'DIR'

    def __init__(self, ip, uname, pwd, port=2100, timeout=60):
        self.ip = ip
        self.uname = uname
        self.pwd = pwd
        self.port = port
        self.timeout = timeout
        self.init_env()

    def __del__(self):
        self.clear_env()

    def init_env(self):
        if self.ftp is None:
            self.ftp = FTP()
            print('### connect ftp server: %s ...' % self.ip)
            self.ftp.connect(self.ip, self.port, self.timeout)
            self.ftp.login(self.uname, self.pwd)
            self.ftp.getwelcome()

    def clear_env(self):
        if self.ftp:
            self.ftp.close()
            print('### disconnect ftp server: %s!' % self.ip)
            self.ftp = None

    def uploadDir(self, local_dir='./', remote_dir='./'):
        if not os.path.isdir(local_dir):
            return
        self.ftp.cwd(remote_dir)
        for file in os.listdir(local_dir):
            src = os.path.join(local_dir, file)
            if os.path.isfile(src):
                self.uploadFile(src, file)
            elif os.path.isdir(src):
                try:
                    self.ftp.mkd(file)
                except:
                    sys.stderr.write('the dir is exists %s' % file)
                self.uploadDir(src, file)
        self.ftp.cwd('..')

    def uploadFile(self, localpath, remotepath='./'):
        if not os.path.isfile(localpath):
            return
        print('+++ upload %s to %s:%s' % (localpath, self.ip, remotepath))
        self.ftp.storbinary('STOR ' + remotepath, open(localpath, 'rb'))

    def __filetype(self, src):
        if os.path.isfile(src):
            index = src.rfind('\\')
            if index == -1:
                index = src.rfind('/')
            return self._XFER_FILE, src[index + 1:]
        elif os.path.isdir(src):
            return self._XFER_DIR, ''

    def upload(self, src):
        filetype, filename = self.__filetype(src)
        if filetype == self._XFER_DIR:
            self.uploadDir(src)
        elif filetype == self._XFER_FILE:
            self.uploadFile(src, filename)


class SMUtils:
    secret_key = None

    def __init__(self, secret_key):
        # 定义key值
        self.secret_key = secret_key

    # SM4加密方法
    def SM4encryptData_ECB(self, plain_text):
        # 创建 SM4对象
        crypt_sm4 = CryptSM4()
        # 设置key
        crypt_sm4.set_key(self.secret_key, SM4_ENCRYPT)
        # 调用加密方法加密(十六进制的bytes类型)
        encrypt_value = crypt_sm4.crypt_ecb(plain_text)
        # 用base64.b64encode转码（编码后的bytes）
        cipher_text = base64.b64encode(encrypt_value)
        # 返回加密后的字符串
        return cipher_text.decode('utf-8', 'ignore')

    # SM4解密方法
    def SM4decryptData_ECB(self, cipher_text):
        crypt_sm4 = CryptSM4()
        crypt_sm4.set_key(self.secret_key, SM4_DECRYPT)
        # 将转入参数base64.b64decode解码成十六进制的bytes类型
        byt_cipher_text = base64.b64decode(cipher_text)
        # 调用加密方法解密，解密后为bytes类型
        decrypt_value = crypt_sm4.crypt_ecb(byt_cipher_text)
        return decrypt_value.decode('utf-8', 'ignore')

    # SM3 字符串摘要计算
    @staticmethod
    def getSM3(text, upper=True):
        result = sm3.sm3_hash(func.bytes_to_list(bytes(text, encoding='utf-8')))
        if upper:
            return result.upper()
        else:
            return result


def save2file(filename: str, content: str):
    with open(filename, 'w', encoding='utf-8') as fp:
        fp.write(content)


def check_directory(directory: str):
    if not os.path.exists(directory):
        os.makedirs(directory)


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


def sm2_password(message, pubkey):
    """
    慧舟科技密码加密算法
    :param message: 明文
    :param pubkey: 公钥
    :return: 密文
    """
    pubkey = pubkey[2:]  # 取掉头部的两个字节
    message_bytes = bytes(message, encoding='utf-8')
    sm2_crypt = sm2.CryptSM2(public_key=pubkey, private_key='')
    password_bytes = sm2_crypt.encrypt(message_bytes, CipherMode=0)  # 加密
    password = '04' + binascii.b2a_hex(password_bytes).decode('utf-8')
    return password


# 判断sftp服务端中文件路径是否存在，若不存在则创建
def create_dir(sftp, remoteDir):
    try:
        if stat.S_ISDIR(sftp.stat(remoteDir).st_mode):  # 如果remoteDir存在且为目录，则返回True
            pass
    except Exception as e:
        sftp.mkdir(remoteDir)
        print("在远程sftp上创建目录：{}".format(remoteDir))


# 上传
def sftp_upload(sftp, localDir, remoteDir):
    if os.path.isdir(localDir):  # 判断本地localDir是否为目录
        for file in os.listdir(localDir):
            remoteDirTmp = os.path.join(remoteDir, file)
            localDirTmp = os.path.join(localDir, file)
            if os.path.isdir(localDirTmp):  # 如果本地localDirTmp为目录，则对远程sftp服务器进行判断
                create_dir(sftp, remoteDirTmp)  # 判断sftp服务端文件目录是否存在,若不存在则创建
            sftp_upload(sftp, localDirTmp, remoteDirTmp)
    else:
        print("upload file:", localDir)
        try:
            sftp.put(localDir, remoteDir)
        except Exception as e:
            print('upload error:', e)


# 连接ftp并登录
def ftp_connect(host, port, username, password):
    ftp = FTP()
    # ftp.set_debuglevel(2)         # 打开调试级别2，显示详细信息
    ftp.connect(host, port)  # 连接
    ftp.login(username, password)  # 登录，如果匿名登录则用空串代替即可
    return ftp


# 下载文件
# def downloadfile(ftp, remotepath, localpath):  # remotepath：上传服务器路径；localpath：本地路径；
#     bufsize = 1024                # 设置缓冲块大小
#     fp = open(localpath,'wb')     # 以写模式在本地打开文件
#     ftp.retrbinary('RETR ' + remotepath, fp.write, bufsize) # 接收服务器上文件并写入本地文件
#     ftp.set_debuglevel(0)         # 关闭调试
#     fp.close()                    # 关闭文件

# 上传文件
def uploadfile(ftp, remotepath, localpath):
    bufsize = 1024
    fp = open(localpath, 'rb')
    ftp.storbinary('STOR '+ remotepath , fp, bufsize)    # 上传文件
    ftp.set_debuglevel(0)
    fp.close()


def ftp_upload_file():
    ftp = ftp_connect('10.168.7.74', 2100, 'hncb', 'Fnc9293')
    uploadfile(ftp, "'/430205/20220930/", "./test.txt")


if __name__ == '__main__':
    # vsftp登录
    # host = '10.168.7.74'  # sftp主机
    # port = 2100  # 端口
    # username = 'hncb'  # sftp用户名
    # password = 'Fnc9293'  # 密码
    # localDir = './logs/checkcode.log'  # 本地文件或目录
    # remoteDir = '/430205/20220930'  # 远程文件或目录（注意远程路径要存在）
    # sf = paramiko.Transport((host, port))
    # sf.connect(username=username, password=password)
    # sftp = paramiko.SFTPClient.from_transport(sf)
    # sftp_upload(sftp, localDir, remoteDir)
    # sf.close()
    ftp_tool = FtpTool('10.168.7.74', 'hncb', 'Fnc9293')
    ftp_tool.upload('./logs')
