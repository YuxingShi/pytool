# coding: utf-8
import re
import os
import socket
import sys
import subprocess

PLATFORM = sys.platform
if PLATFORM == 'win32':
    cmd = 'wmic bios get serialnumber'
    cmd = 'ipconfig'
    sys_code = 'GBK'
elif PLATFORM == 'darwin':
    cmd = "/usr/sbin/system_profiler SPHardwareDataType |fgrep 'Serial'|awk '{print $NF}'"
    sys_code = 'UTF-8'
elif PLATFORM.count('linux'):
    cmd = "sudo dmidecode -t system|grep 'Serial Number'"
    sys_code = 'UTF-8'


def run(cmd_str):
    proc = subprocess.Popen(cmd_str, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return proc.stdout.read().decode(sys_code)


def get_serial_number():
    return run(cmd)


if __name__ == '__main__':
    print(get_serial_number())
