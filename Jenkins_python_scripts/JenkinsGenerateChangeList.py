#!/usr/bin/env python
# -*- coding=utf-8 -*-
import re
import os
from colorama import init
from colorama import Fore
import subprocess
import sys
import time

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
    project_name_list = None
    child_working_path_dict = {}

    def __init__(self, svn_url: str, svn_usr: str, svn_passwd: str, project_names: str,
                 working_path: str):
        """
        根据SVN提交日志生成变更列表
        :param svn_url: svn根路径
        :param svn_usr: svn用户
        :param svn_passwd: svn密码
        :param svn_message: svn提交时候填写的信息
        :param project_names: 要生成变更列表的工程名
        :param working_path: 脚本工作路径
        """
        self.url = svn_url
        self.usr = svn_usr
        self.passwd = svn_passwd
        self.project_name_list = project_names.split(',')
        self.working_path = working_path
        self.init_child_working_path()

    @staticmethod
    def write2file(filename: str, content: str):
        with open(filename, 'w') as fp:
            fp.write(content)

    def init_child_working_path(self):
        """
        child_working_path初始化
        :return:
        """
        if not os.path.isdir(self.working_path):
            print(Fore.RED + '【{}】该工作路径非目录！'.format(self.working_path))
            exit(1)
        self.child_working_path_dict.clear()
        for dir_name in os.listdir(self.working_path):
            if dir_name.startswith('DR'):
                dev_match = re.findall('DR(\d{8,})(\d{3,})', dir_name)  # 匹配PP系统开发单号
            else:
                dev_match = re.findall('(.*)', dir_name)  # 非PP系统开发单号
            if len(dev_match) > 0:
                child_dir = os.path.join(self.working_path, dir_name)
                if os.path.isfile(child_dir):
                    continue
                else:
                    if dir_name.startswith('DR'):
                        dev_date, dev_sn = dev_match[0]  # 匹配PP系统开发单号
                    else:
                        dev_date = dev_match[0]  # 非PP系统单号
                        if re.match('20\d{,2}[0-1][0-9][0-3][0-9]', dev_date) is None:
                            day_seconds = 10 * 24 * 60 * 60
                            time_tuple = time.localtime(time.time() - day_seconds)
                            dev_date = time.strftime("%Y%m%d", time_tuple)
                    self.child_working_path_dict[dir_name] = {'path': child_dir, 'date': dev_date}
        # print('self.child_working_path_dict', self.child_working_path_dict)

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
            # print('执行svn命令：{}'.format(' '.join(params)))
            cp = subprocess.run(params, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if cp:
                if cp.returncode != 0:
                    errmsg = parse(cp.stderr.decode('utf-8'))
                elif cp.returncode == 0 and cp.stdout != b'':
                    svn_output = cp.stdout.decode('utf-8')  # .split('\r\n')[3:-4]  # [-1].decode('utf-8')[:-1]
            else:
                print(Fore.RED + "执行SVN出错!【%s】" % (params))
        return svn_output

    def get_revision_list_after_date(self, date: str):
        """
        将指定日期后的SVN日志按天生成列表
        :param date: 日期字符串，如：20220909
        :return: 日志列表
        """
        params = ['svn']
        params.extend(('log', self.url, '-r', '{%s}:HEAD' % date, '-v'))
        # pattern_log_split = '-{72,}\r\n(.*?)\r\n-{72,}'
        # pattern_revision = '\r\n(.*?)\r\nChanged paths:\r\n(.*?)\r\n\r\n(.*?)\r\n'
        pattern_revision = '\n(.*?)\n改变的路径: \n(.*?)\n\n(.*?)\n'
        svn_log = self.execute_svn_command(params)
        revision_list = re.findall(pattern_revision, svn_log, flags=re.DOTALL)
        # print('revision_list', revision_list)
        return revision_list

    @staticmethod
    def get_revision_dict_by_message_contain(message_head: str, revision_list: list):
        revision_dict = {}
        for info, changelist, message in revision_list:
            if not message.count(message_head):
                print(Fore.YELLOW + '提交信息头【{}】不包含单号【{}】！略过！'.format(message, message_head))
                continue
            info_list = info.split(' | ')
            changelist = changelist.split('\n')  # linux下为\n
            revision_dict[info_list[0]] = {'info_list': info_list, 'changelist': changelist}
        # print('revision_dict', revision_dict)
        return revision_dict

    def merge_changelist(self, revision_dict: dict):
        """
        合并变更列表
        :return:
        """
        project_dict = {}
        for key, value in revision_dict.items():
            changelist = value.get('changelist')
            for path in changelist:
                print(path)
                flag, svn_path = re.findall('   ([MDA]) /(\S*)', path)[0]  # , flags=re.DOTALL
                for project_name in self.project_name_list:
                    try:
                        project_name_index = svn_path.index(project_name)
                        project_path = svn_path[project_name_index - 1:]
                        if project_dict.get(project_name) is None:
                            project_dict[project_name] = [(flag, project_path)]
                        else:
                            project_dict.get(project_name).append((flag, project_path))
                    except ValueError:
                        continue
        #print('project_dict', project_dict)
        return project_dict

    def generate_changelist_file(self, project_dict: dict, working_path: str):
        """
        生成变更列表txt
        :return:
        """
        for project_name, flag_path in project_dict.items():
            temp_dict = {'AM': [], 'D': []}
            for flag, path in flag_path:
                if flag == 'D':  # 当标志位删除时候从AM队列中删除对应的文件路径
                    try:
                        temp_dict.get('AM').remove(path)
                    except ValueError as e:
                        temp_dict.get(flag).append(path)
                        continue
                else:  # 新增和变更的文件放到一起
                    temp_dict.get('AM').append(path)
            text = ''
            for temp_key, temp_value in temp_dict.items():
                if temp_key == 'AM':
                    text += '#新增变更文件\n' + '\n'.join(set(temp_value)) + '\n\n'
                elif temp_key == 'D':
                    text += '#删除文件\n#' + '#\n#'.join(set(temp_value)) + '\n\n'
            filename = '{}路径说明.txt'.format(project_name)
            file_path = os.path.join(working_path, filename)
            self.write2file(file_path, text)
            print(Fore.GREEN + '生成变更列表【{}】'.format(file_path))

    def batch_generate_changelist_file(self):
        for key, value in self.child_working_path_dict.items():
            revision_list = self.get_revision_list_after_date(value.get('date'))
            revision_dict = self.get_revision_dict_by_message_contain(key, revision_list)
            project_dict = self.merge_changelist(revision_dict)
            self.generate_changelist_file(project_dict, value.get('path'))


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
    print(sys.argv)
    svn = SVN(svn_url=sys.argv[1], svn_usr=jenkinsconf.svnusr, svn_passwd=jenkinsconf.svnpwd, project_names=sys.argv[2],
              working_path=sys.argv[3])
    svn.batch_generate_changelist_file()
