#!/usr/bin/env python
# -*- coding=utf-8 -*-
"""
 *按照给定的清单文件将指定路径文件拷贝到目标路径
 *
"""
import os
import time
import shutil
import sys
import codecs
from colorama import init
from colorama import Fore

init(autoreset=True, strip=False)  # init(autoreset=True,strip=False)初始化color输出


class PathFileCopy:
    def __init__(self, src_path, project_name, source_list, des_path):
        self.src_path = src_path  # 根目录(要修改:工程所在的目录)
        self.project_name = project_name  # 工程名(要修改:工程名称)
        self.sour_file_path = source_list  # 补丁列表(要修改:补丁列表文件)
        self.des_path = des_path  # 目的地目录(要修改:生成的补丁文件所放的目录)
        self.ruleout = []  # 不需要拷贝的关键字
        self.ruleoutLines = 0  # 删除不需要拷贝
        self.keyfile = ['web.xml']
        self.keyfilelist = []  # 关键文件，检查结果
        self.totalRow = 0  # 总行数
        self.emptyLines = 0  # 总空行数
        self.repeatTotal = 0  # 重复总行数
        self.commtLines = 0  # 注释总行数
        self.totalFile = 0  # 总文件数
        self.totalFileSuccess = 0  # 拷贝成功总数
        self.totalFileFail = 0  # 拷贝失败总数

    def ctime(self, FMT='%Y-%m-%d %H:%M:%S'):
        return time.strftime(FMT, time.localtime())

    def readLines(self):
        print("----------------统计信息说明---------------")
        print("所有文件拷贝成功标志: E=F 且 G=0,I=0")
        if not (os.path.isfile(self.sour_file_path)):
            print(Fore.RED + '不存在变更列表文件：%s' % self.sour_file_path)
            sys.exit(1)
        print("变更列表文件名:  %s" % self.sour_file_path)
        linelist = []
        with open(self.sour_file_path, 'rb') as pfile:
            for item in pfile.readlines():
                linelist.append(self._delutf8bom(item))
        self.totalRow = len(linelist)
        if self.totalRow == 0:
            print(Fore.RED + "变量列表为空，无法生成增加部署包，请检查...")
            sys.exit(0)
        i = 0
        repeatlines = []
        for line in linelist:
            i += 1
            line = line.strip()
            if line == b'':
                self.emptyLines += 1
                continue
            elif (line[:2] == b'--') or (line[:1] == b'#'):
                self.commtLines += 1
                continue
            elif (line[:1] != b'/'):
                print(Fore.RED + '！！！！非法路径开始，拷贝终止，请以修改路径，以/开始后重新执行！！！！！')
                print(Fore.RED + '非法路径：%s' % line)
                sys.exit(1)
            flagruleout = 0
            for item in self.ruleout:  # 不拷贝列表中的文件
                if item in line.decode('utf-8', errors='ignore'):
                    self.ruleoutLines += 1
                    flagruleout = 1
                    continue
            if flagruleout == 1:
                print("不拷贝规则列表内的文件【%s】：" % line)
                continue
            try:
                line = line.decode('utf-8')
            except UnicodeDecodeError as e:
                line = line.decode('gbk')
            for item in self.keyfile:  # 关键文件检查
                if item in line:
                    self.keyfilelist.append(line)
                    continue
            if line.upper() not in repeatlines:  # 不是重复的行
                for tmpline in linelist[i:]:
                    tmpline = tmpline.strip()
                    if tmpline.upper() == line.upper():  # 判断重复
                        repeatlines.append(tmpline.upper())
                        self.repeatTotal += 1
                self.build(line)
        if len(repeatlines) >= 1:
            print("------------------重复行信息开始-----------------")
            self._printrepeat(repeatlines)
            print("------------------重复行信息结束-----------------")
        if len(self.keyfilelist) >= 1:
            print("\n--------------此次更新包含关键文件，请与开发沟通是否出包对系统有影响-------------------")
        for item in self.keyfilelist:
            print(Fore.CYAN + "-------------关键文件【%s】---------------\n" % item)
        print("------------------统计信息-----------------")
        print("A:文件总行数:%s" % self.totalRow)
        print(
            "B:%s B=B1+B2, B1总空行数:%s, B2注释行%s," % (self.emptyLines + self.commtLines, self.emptyLines, self.commtLines))
        print("C1:重复总行数:%s" % self.repeatTotal)
        print("C2:忽略总行数:%s" % self.ruleoutLines)
        print("D:有效行数:%s" % (self.totalRow - self.emptyLines - self.repeatTotal - self.commtLines - self.ruleoutLines))
        print("E:总文件数:%s" % self.totalFile)
        print("F:普通文件拷贝成功>>>总数:%s" % self.totalFileSuccess)
        print("G:普通文件拷贝失败<<<总数:%s" % self.totalFileFail)
        if (self.totalFile == self.totalFileSuccess and self.totalFileFail == 0 and
                (self.totalRow - self.emptyLines - self.repeatTotal) > 0):
            print(Fore.GREEN + ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>成功")
            print(Fore.GREEN + ">>>>>>>>>>>源目录：%s>>>>>>>>>>>>>>>>>" % self.src_path)
            print(Fore.GREEN + ">>>>>>>>>>>目标目录：%s>>>>>>>>>>>>>>>>>" % self.des_path)
        else:
            print(Fore.RED + "<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<失败")
            sys.exit(1)

    def build(self, lineString=0):
        self.totalFile += 1  # 总文件数
        pathsep = os.path.sep
        if (not lineString.count('/' + self.project_name)):
            self.totalFileFail += 1
            print(Fore.RED + ">>>>>>>>>>>>>>>不是有效的%s , 工程文件,拷贝失败:%s！" % (self.project_name, lineString))
            print(Fore.RED + "###################终止生成增加包###################")
            sys.exit(1)
        pathl = lineString.split('/')
        if len(pathl) == 1:
            pathl = lineString.split('\\')
        if len(pathl) == 1:
            sys.exit(1)
        if pathl[0] == '':  # 删除多余的/路径
            pathl.pop(0)
        filename, extname = os.path.splitext(pathl.pop())  # 取出文件和扩展名，并在列表中删除
        if self.project_name in pathl:  # 判断路径是否包含web_root_name
            spath = pathsep.join(pathl[1:])
            spath = os.path.join(self.src_path, spath)
            dpath = pathsep.join(pathl[1:])
            dpath = os.path.join(self.des_path, dpath)
            sdfile = filename + extname
            if (self.xcopyFile(spath, dpath, sdfile, sdfile)):
                self.totalFileSuccess += 1
                # print("文件拷贝成功!:原%s，目标%s%s%s" %(lineString,dpath,pathsep,sdfile))
            else:
                self.totalFileFail += 1
                print(Fore.RED + "++++++++++++++++++++++>>文件拷贝失败:%s" % lineString)

    def xcopyFile(self, sfilePath, dfilePath, sfile, dfile):
        sfilename = os.path.join(sfilePath, sfile)
        dfilename = os.path.join(dfilePath, dfile)
        if os.path.isfile(sfilename):
            if not os.path.exists(dfilePath):
                os.makedirs(dfilePath)
            print('拷贝文件{}>>>>{}'.format(sfilename, dfilename))
            shutil.copyfile(sfilename, dfilename)
        if os.path.isfile(dfilename):
            return True
        else:
            print(sfilePath, dfilePath, sfile, dfile)
            return False

    def _printrepeat(self, repeatlines):
        newlines = list(set(repeatlines))
        for item in newlines:
            print("重复行：【%s】，重复次数：【%d】，" % (item, repeatlines.count(item)))

    def _delutf8bom(self, line):
        bomtag = line[:3]
        while True:
            if bomtag == codecs.BOM_UTF8:
                line = line[3:]
                bomtag = line[:3]
            else:
                break
        return line


if __name__ == "__main__":
    if len(sys.argv) != 5 and len(sys.argv) != 6:
        print("""example:
                pathfilecopy srcpath project_name source_list des_path  ComponentFlag""")
        sys.exit(1)
    src_path = sys.argv[1]  # 根目录(要修改:工程所在的目录)
    project_name = sys.argv[2]  # 工程名(要修改:工程名称)
    source_list = sys.argv[3]  # 补丁列表(要修改:补丁列表文件)
    des_path = sys.argv[4]  # 目的地目录(要修改:生成的补丁文件所放的目录)
    path_file_copy = PathFileCopy(src_path, project_name, source_list, des_path)
    print(Fore.BLUE + "%s: ^^^^^..........^^^^^准备开始增量包的生成^^^^^..........^^^^^" % path_file_copy.ctime())
    path_file_copy.readLines()
