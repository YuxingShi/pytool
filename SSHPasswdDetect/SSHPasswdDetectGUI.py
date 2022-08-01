# coding:utf-8
import os
import json
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
import paramiko


class SSHClient(object):
    path_ssh = os.path.abspath('./OpenSSH-Win64')
    path_hosts = os.path.abspath('hosts.json')
    path_passwd = os.path.abspath('passwd.txt')
    dict_hosts = None
    list_passwd = None

    def __init__(self):
        self.dict_hosts = self.read_json(self.path_hosts)
        self.list_passwd = self.get_line_from_file(self.path_passwd)

    @staticmethod
    def read_json(file_name):
        with open(file_name, 'r')as fp:
            try:
                dict_obj = json.load(fp)
                return dict_obj
            except json.decoder.JSONDecodeError as e:
                dict_obj = {}
                return dict_obj

    @staticmethod
    def write_dict2json(obj: dict, file_name: str):
        with open(file_name, 'w')as fp:
            json.dump(obj, fp)

    @staticmethod
    def get_line_from_file(file_name: str):
        with open(file_name, 'r') as fp:
            return [line.strip('\n') for line in fp.readlines()]

    def connect_host_test(self, ip='10.168.1.173', port=22, user='root', password='root'):
        ip_port = '{}:{}'.format(ip, port)
        try:
            # 创建ssh客户端
            client = paramiko.SSHClient()
            # 第一次ssh远程时会提示输入yes或者no
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            # 密码方式远程连接
            client.connect(ip, port, username=user, password=password, timeout=60)
            client.close()
            return 0, (ip, port, user, password)
        except paramiko.AuthenticationException as e:
            return 1, '{} {} {} 密码错误'.format(ip_port, user, password)
        except Exception as e:
            return 2, '{} {} {} 主机连接失败！'.format(ip_port, user, password)


if __name__ == "__main__":
    client = SSHClient()
    print(client.connect_host_test())
