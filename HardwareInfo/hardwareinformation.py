import asyncio
import re
import sys
import os
import socket
import subprocess

import websockets
import json

curPath = os.path.abspath(os.path.dirname(__file__))
sys.path.append(curPath)
data_dict = None


def cmd_executor(cmd: str):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p.communicate()[0].decode('UTF-8')  # 不用调用标准输出


def get_localhost_ip(ip_port):
    soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        soc.connect(ip_port)
        ip = soc.getsockname()[0]
    except Exception as e:
        ip = None
    finally:
        soc.close()
    return ip


def get_serial_number():
    cmd_bios = "sudo dmidecode -t system|grep 'Serial Number'|awk -F ':' '{print $NF}'"
    cmd_cpu = "sudo dmidecode -t processor|grep 'ID'|awk -F ':' '{print $NF}'"
    cmd_baseboard = "sudo dmidecode -t baseboard|grep 'Serial Number'|awk -F ':' '{print $NF}'"
    cmd_list = [cmd_bios, cmd_baseboard, cmd_cpu]
    return_list = []
    for cmd in cmd_list:
        output = cmd_executor(cmd).strip('\n')
        return_list.append(output)
    return return_list


@asyncio.coroutine
def information(websocket, path):
    global data_dict
    while True:
        # rec_message = yield from websocket.recv()
        if path == '/information':
            message = json.dumps(data_dict)
        else:
            message = ''
        yield from websocket.send(message)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        exit(1)
    cb_server_ip = sys.argv[1]
    cb_server_port = sys.argv[2]
    # 把ip换成自己本地的ip
    ip_port = (cb_server_ip, int(cb_server_port))
    host_ip = get_localhost_ip(ip_port)
    biosSn, baseboardSn, cpuSn = get_serial_number()
    data_dict = {"ip": host_ip, "biosSn": biosSn, "baseboardSn": baseboardSn, "cpuSn": cpuSn}
    start_server = websockets.serve(information, '127.0.0.1', 8765)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
