#!/usr/bin/env python
# -*- coding=utf-8 -*-
from colorama import init
from colorama import Fore
import subprocess
import sys

init(autoreset=True, strip=False)  # init(autoreset=True,strip=False)初始化color输出

# 兼容处理
_ver = sys.version_info
#: Python 2.x?
is_py2 = (_ver[0] == 2)
#: Python 3.x?
is_py3 = (_ver[0] == 3)
if is_py2:
    import urllib
    parse = urllib.unquote
if is_py3:
    from urllib import parse
    parse = parse.unquote


class SVN(object):

    def runSVN(self, path, url, usr, passwd, subcommand="import", msg="更新补丁包"):
        """["svn","import","/home/jenkins_workspace/workspace/gzrtmis/BUILD630/context","https://10.168.1.112/svn/test/20180329/201803/path_20180402_0001/context","--username","linwanzhi","--password","simsadmin","--non-interactive","--trust-server-cert","-m 备注"]
        控制台执行SVN命令,主要用于签入,移动的操作
        返回最新标签号和错误信息
        """
        if subcommand not in ('move', 'commit', 'import'):
            print(Fore.RED + "SVN 子命令不正常,请重新输入")
            return None
        params = ["svn"]
        params.append(subcommand)
        if subcommand in ("move", "import"):
            params.extend((path, url))

        elif subcommand == 'commit':
            params.append(path)
        params.extend(("-m", msg))
        params.extend(("--username", usr))
        params.extend(("--password", passwd))
        params.extend(("--non-interactive", "--trust-server-cert"))
        errmsg = ''
        svn_revision = 0
        if is_py2:
            cp = subprocess.Popen(params, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            cp.wait()
            er = cp.stderr.read()
            s = cp.stdout.read()
            # e1 = er.decode('utf-8')
            # s1 = s.decode('utf-8')
            if er == '' and s != '' and s.split('\n')[-2].split(' ')[0] == '提交后的版本为':
                svn_revision = int(s.split('\n')[-2].split(' ')[1][:-3])
            else:
                errmsg = parse(er)  # .encode('utf-8')
        if is_py3:
            cp = subprocess.run(params, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if cp:
                if cp.returncode != 0:
                    errmsg = parse(cp.stderr.decode('utf-8'))
                elif cp.returncode == 0 and cp.stdout != b'':
                    svn_revision = cp.stdout.split()[-1].decode('utf-8')[:-1]
            else:
                print(Fore.RED + "执行SVN出错!【%s】" % (params))
        return svn_revision, errmsg