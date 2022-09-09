#!/usr/bin/env python
# -*- coding=utf-8 -*-
import re

from colorama import init
from colorama import Fore
import subprocess
import sys
from jenkinsconf import svnusr, svnpwd

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
    params = ["svn"]
    revision_dict = {}
    project_dict = {}
    project_name_list = ['hztech-web-gd']

    def __init__(self, url, usr, passwd):
        self.url = url
        self.usr = usr
        self.passwd = passwd
        self._init_project_dict()

    def _init_project_dict(self):
        self.project_dict.clear()
        for project_name in self.project_name_list:
            self.project_dict[project_name] = None

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

    def execute_svn_command(self, params: list):
        svn_output = ''
        errmsg = ''
        params.extend(("--username", self.usr))
        params.extend(("--password", self.passwd))
        params.extend(("--non-interactive", "--trust-server-cert"))
        if is_py2:
            cp = subprocess.Popen(params, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            cp.wait()
            er = cp.stderr.read()
            s = cp.stdout.read()
            if er == '' and s != '' and s.split('\n')[-2].split(' ')[0] == '提交后的版本为':
                svn_output = int(s.split('\n')[-2].split(' ')[1][:-3])
            else:
                errmsg = parse(er)  # .encode('utf-8')
        if is_py3:
            cp = subprocess.run(params, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if cp:
                if cp.returncode != 0:
                    errmsg = parse(cp.stderr.decode('utf-8'))
                elif cp.returncode == 0 and cp.stdout != b'':
                    svn_output = cp.stdout.decode('GBK')  # .split('\r\n')[3:-4]  # [-1].decode('utf-8')[:-1]
            else:
                print(Fore.RED + "执行SVN出错!【%s】" % (params))
        return svn_output

    def get_revision_list_after_date(self, date='2022-09-06'):
        self.params.extend(('log', self.url, '-r', '{%s}:HEAD' % date, '-v'))
        # pattern_log_split = '-{72,}\r\n(.*?)\r\n-{72,}'
        pattern_revision = '\r\n(.*?)\r\nChanged paths:\r\n(.*?)\r\n\r\n(.*?)\r\n'
        svn_log = self.execute_svn_command(self.params)
        revision_list = re.findall(pattern_revision, svn_log, flags=re.DOTALL)
        return revision_list

    def init_revision_dict_by_message_contain(self, dev_id: str):
        for info, changelist, message in self.get_revision_list_after_date():
            if not message.startswith(dev_id):
                print('提交信息头不包含单号【{}】！略过！'.format(dev_id))
                continue
            self.revision_dict[message] = {'info': info.split(' | '), 'changelist': changelist.split('\r\n')}
        print(self.revision_dict)

    def merge_changelist(self):
        """
        合并变更列表
        :return:
        """
        for key, value in self.revision_dict.items():
            changelist = value.get('changelist')
            for path in changelist:
                print(path)
                print(re.findall('   ([MDA]) /(.*?)', path, flags=re.DOTALL))



    def gen_changelist_file(self, file_name, split_flag='05模块代码'):
        """
        生成变更列表txt
        /11广东/01广东运政改造项目/05模块代码/hztech-web-gd/src/components/hztech/HUpload.vue
        :param file_name: 变更列表文件名
        :param split_flag: 判断工程代代码路径的标志
        :return:
        """
        pass


if __name__ == '__main__':
    svn = SVN(url='https://10.168.1.202/svn/01.产品and项目/11广东/01广东运政改造项目/05模块代码',
              usr=svnusr, passwd=svnpwd)
    svn.init_revision_dict_by_message_contain('密码')
    svn.merge_changelist()


