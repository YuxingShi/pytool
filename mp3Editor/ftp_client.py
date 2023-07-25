# coding: utf-8
import os
from ftplib import FTP

SERVER = '192.168.1.106'  # FTP服务器地址
PORT = 2121
# USERNAME = 'anonymous'  # 用户名（匿名方式）
USERNAME = 'shiyx'  # 用户名（匿名方式）
PASSWORD = 'ssyx'  # 密码（留空表示匿名方式）
REMOTE_DIR = '/Music/test'  # 远程目录路径
LOCAL_FILE = r'F:/mp3/把心交出来 - 李琛.mp3'  # 本地文件路径


def create_remote_directory(ftp, remote_dir):
    """递归创建远程目录"""
    if remote_dir == '/':
        return
    try:
        ftp.cwd(remote_dir)
    except:
        parent_dir, current_dir = os.path.split(remote_dir.rstrip('/'))
        create_remote_directory(ftp, parent_dir)
        ftp.mkd(current_dir)
        ftp.cwd(current_dir)


def push_file_to_ftp(server, port, username, password, remote_dir, local_file):
    """将文件推送到FTP服务器"""
    ftp = FTP()
    ftp.connect(server, port)  # 连接到指定的服务器和端口
    ftp.login(username, password)
    create_remote_directory(ftp, remote_dir)
    with open(local_file, 'rb') as file:
        ftp.storbinary(f'STOR {os.path.basename(file.name).encode("utf-8").decode("latin-1")}', file)
    ftp.quit()


if __name__ == '__main__':
    # 推送文件到FTP服务器
    push_file_to_ftp(SERVER, PORT, USERNAME, PASSWORD, REMOTE_DIR, LOCAL_FILE)
