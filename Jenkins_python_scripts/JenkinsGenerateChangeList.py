#!/usr/bin/env python
# -*- coding=utf-8 -*-
import re

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
    params = ["svn"]
    revision_dict = {}
    project_dict = {}
    project_name_list = None

    def __init__(self, svn_url: str, svn_usr: str, svn_passwd: str, svn_message: str, project_names: str):
        """
        根据SVN提交日志生成变更列表
        :param svn_url:
        :param svn_usr:
        :param svn_passwd:
        :param svn_message: svn提交时候填写的信息
        :param project_names:
        """
        self.url = svn_url
        self.usr = svn_usr
        self.passwd = svn_passwd
        self.message_head = svn_message
        self.project_name_list = project_names.split(',')

    @staticmethod
    def write2file(filename: str, content: str):
        with open(filename, 'w') as fp:
            fp.write(content)

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
                    svn_output = cp.stdout.decode('utf-8')  # .split('\r\n')[3:-4]  # [-1].decode('utf-8')[:-1]
            else:
                print(Fore.RED + "执行SVN出错!【%s】" % (params))
        print(svn_output)
        return svn_output

    def get_revision_list_after_date(self, date='2022-09-06'):
        """
        将指定日期后的SVN日志按天生成列表
        :param date: 日期字符串
        :return: 日志列表
        """
        self.params.extend(('log', self.url, '-r', '{%s}:HEAD' % date, '-v'))
        # pattern_log_split = '-{72,}\r\n(.*?)\r\n-{72,}'
        #pattern_revision = '\r\n(.*?)\r\nChanged paths:\r\n(.*?)\r\n\r\n(.*?)\r\n'
        pattern_revision = '\n(.*?)\n改变的路径: \n(.*?)\n\n(.*?)\n'
        svn_log = self.execute_svn_command(self.params)
        revision_list = re.findall(pattern_revision, svn_log, flags=re.DOTALL)
        print('revision_list', revision_list)
        return revision_list

    def init_revision_dict_by_message_contain(self):
        for info, changelist, message in self.get_revision_list_after_date():
            if not message.startswith(self.message_head):
                print('提交信息头不包含单号【{}】！略过！'.format(self.message_head))
                continue
            info_list = info.split(' | ')
            changelist = changelist.split('\n')
            self.revision_dict[info_list[0]] = {'info_list': info_list, 'changelist': changelist}
        print('self.revision_dict', self.revision_dict)

    def merge_changelist(self):
        """
        按合并变更列表
        :return:
        """
        self.init_revision_dict_by_message_contain()
        for key, value in self.revision_dict.items():
            changelist = value.get('changelist')
            for path in changelist:
                flag, svn_path = re.findall('   ([MDA]) /(.*)', path, flags=re.DOTALL)[0]
                for project_name in self.project_name_list:
                    try:
                        project_name_index = svn_path.index(project_name)
                        project_path = svn_path[project_name_index - 1:]
                        if self.project_dict.get(project_name) is None:
                            self.project_dict[project_name] = [(flag, project_path)]
                        else:
                            self.project_dict.get(project_name).append((flag, project_path))
                    except ValueError:
                        continue
        print('self.project_dict', self.project_dict)

    def generate_changelist_file(self):
        """
        生成变更列表txt
        :return:
        """
        self.merge_changelist()
        for project_name, flag_path in self.project_dict.items():
            temp_dict = {}
            for flag, path in flag_path:
                if temp_dict.get(flag) is None:
                    temp_dict[flag] = [path]
                else:
                    temp_dict.get(flag).append(path)
            text = ''
            for temp_key, temp_value in temp_dict.items():
                if temp_key == 'A':
                    text += '#新增文件\n' + '\n'.join(set(temp_value)) + '\n\n'
                elif temp_key == 'M':
                    text += '#修改文件\n' + '\n'.join(set(temp_value)) + '\n\n'
                elif temp_key == 'D':
                    text += '#删除文件\n#' + '#\n#'.join(set(temp_value)) + '\n\n'
            filename = '{}路径说明.txt'.format(project_name)
            self.write2file(filename, text)


def usage():
    print("""本脚本功能,用于根据svn提交的message头关键字生成给定项目名称的变更列表
            参数1 SVN路径（作为取日志的svn根路径）
            参数2 SVN提交时，message的开头字符（一般为PP系统单号）
            参数3 要生成变更列表的项目名称，以源代码的项目根目录为名称，多个以英文逗号隔开。如： 
            'hztech-web-gd,hztech-module-gdcrtmis-system,hztech-module-gdcrtmis-biz,hztech-module-workflow-biz,' \
            'hztech-cloud-nacos,hztech-boot-eventframework,hztech-boot-tools-jmreport,hztech-boot-tools-obs'
            JenkinsGenerateChangeList.py.py https://10.168.1.202/svn/01.产品and项目/11广东/01广东运政改造项目/05模块代码
             DR20220906001 hztech-web-gd,hztech-module-gdcrtmis-system,hztech-module-gdcrtmis-biz,
             hztech-module-workflow-biz,hztech-cloud-nacos,hztech-boot-eventframework,hztech-boot-tools-jmreport,
             hztech-boot-tools-obs""")
    sys.exit(1)


if __name__ == '__main__':
    import jenkinsconf
    if (len(sys.argv) != 4):
        usage()
    svn = SVN(svn_url=sys.argv[1], svn_usr=jenkinsconf.svnusr, svn_passwd=jenkinsconf.svnpwd, svn_message=sys.argv[2],
              project_names=sys.argv[3])
    svn.generate_changelist_file()
