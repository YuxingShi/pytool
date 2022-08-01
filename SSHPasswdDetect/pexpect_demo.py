# coding: utf-8
from pexpect.pxssh import pxssh
import pexpect

def login_host(host):
    ssh = pxssh()
    if ssh.login(host[0], host[1], host[2]):
        return ssh

def get_cpu_num(ssh):
    ssh.sendline('cat /proc/cpuinfo')
    res = ssh.expect(['cpu cores.*\r\n', pexpect.EOF])
    if res == 0:
        data = ssh.after.split('\r\n')[0]
        data = data[data.index(':') + 1:]
        cpu_cores = int(data)
        ssh.prompt()
        return cpu_cores

def get_cpu_load(ssh):
    ssh.sendline('uptime')
    if ssh.prompt():
        data = ssh.before
        data = data.strip('\r\n')
        data = data[data.rfind(':')+1:]
        data = data.split(',')
        return (float(data[0]), float(data[1]), float(data[2]))

def get_cpu_stat(ssh):
    ssh.sendline('vmstat')
    ssh.prompt()
    print(ssh.before)

def user_deal(host, file_name):
    s = login_host(host)
    if not s:
        print('Login failed: ', host[0])
        return
    try:
        cpu_cores = get_cpu_num(s)
        if not cpu_cores:
            print('Do not get cpu cores: ', host[0])
            return
        cpu_load = get_cpu_load(s)
        if cpu_load[2] >= cpu_cores:
            get_cpu_stat(s)
            print('system is not healthy. Do you want to deal? (yes/no)')
            yn = input()
            if yn == 'yes':
                with open(file_name, 'ab+') as f:
                    s.logfile = f
                    s.interact()
                    s.prompt()
                    s.logfile = None
        else:
            print('system is healthy: ', host[0])
    except Exception as e:
        print('failed: ', host[0])
    finally:
        s.logout()


if __name__ == '__main__':
    hosts = [('10.168.1.173', 'root', 'd&4tq1T8*')]
    file_name = 'log.txt'
    for host in hosts:
        user_deal(host, file_name)
