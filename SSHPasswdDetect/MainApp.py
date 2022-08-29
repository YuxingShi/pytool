# coding:utf-8
import os
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import paramiko

def init_hosts():
    with open('hosts.json', 'r')as fp:
        try:
            dict_obj = json.load(fp)
            return dict_obj
        except json.decoder.JSONDecodeError as e:
            dict_obj = {}
            return dict_obj


def write_dict2json(obj: dict):
    with open('hosts.json', 'w')as fp:
        json.dump(obj, fp)


def get_passwd_list():
    with open('passwd.txt', 'r') as fp:
        lines = [line.strip('\n') for line in fp.readlines()]
        print(lines)
        return lines


def connect_host_test(ip, port=22, user='root', password='root'):
    ip_port = '{}:{}'.format(ip, port)
    try:
        # 创建ssh客户端
        client = paramiko.SSHClient()
        # 第一次ssh远程时会提示输入yes或者no
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # 密码方式远程连接
        client.connect(ip, port, username=user, password=password, timeout=60)
        # transport = paramiko.SSHClient(sock=ip_port)
        # transport.start_client()
        # transport.auth_password(username=user, password=password)
        client.close()
        return 0, (ip, port, user, password)
    except paramiko.AuthenticationException as e:
        return 1, '{} {} {} 密码错误'.format(ip_port, user, password)
    except Exception as e:
        return 2, '{} {} {} 主机连接失败！'.format(ip_port, user, password)


if __name__ == "__main__":
    hosts_dict = init_hosts()
    password_list = get_passwd_list()
    tpe = ThreadPoolExecutor(max_workers=password_list.__len__())
    all_tasks = [tpe.submit(connect_host_test, '10.168.7.79', password=passwd) for passwd in password_list]
    for task in as_completed(all_tasks):
        ret, result = task.result()
        if ret:
            # print(msg)
            continue
        else:
            print(result)
            hosts_dict[result[0]] = {'port': result[1], 'user': result[2], 'passwd': result[3]}
            write_dict2json(hosts_dict)
            break
