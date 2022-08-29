#!/usr/bin/env python3
# -*- coding=utf-8 -*-
"""根据输入的开发单路径及开发单号"""
import pandas as pd
import os, sys, shutil
import chardet
from colorama import Fore
from colorama import init

init(autoreset=True, strip=False)
# 兼容处理
_ver = sys.version_info
#: Python 2.x?
is_py2 = (_ver[0] == 2)
#: Python 3.x?
is_py3 = (_ver[0] == 3)
if is_py2:
    FileNotFoundError = IOError
if is_py3:
    FileNotFoundError = FileNotFoundError


class CheckChangeFile:

    def getListFileContext(self, itm, path):
        '''获取变更列表文件的明细内容(行不重复),删除注释空行以及特殊字符
        对应ITM单号增加到第0列,并返回DataFrame数据类型
        project用于检验变更列表文件的内容是否正确'''
        yzlines = []
        try:
            yzf = open(path, 'rb')
            for item in yzf.readlines():
                # 可信度大小0.8的取自动识别的，否则按默认的GBK来处理
                encoding = chardet.detect(item).get('encoding') if chardet.detect(item).get(
                    'confidence') >= 0.75 else 'gbk'
                line = item.decode(encoding, errors='ignore')
                line = line.strip()
                if line != '' and line[:1] != '#' and line[:2] != '--':
                    yzlines.append(line)
        except FileNotFoundError as E:
            print(Fore.CYAN + "错误：未找到变更列表文件【%s】，请检查SVN提交的路径是否正确:\n" % E.filename)
        except Exception as E:
            print(Fore.RED + "Error: " + repr(E))
        else:
            yzf.close()
        df = pd.DataFrame(yzlines, columns=("file",))  # list转为dataframe
        df = df.drop_duplicates(subset="file", keep='first')  # 删除重复的文件,保留第一个
        df["itm"] = itm  # 增加ITM列
        return df

    def writeModifyFile(self, sflist, filename):
        """根据合并后的列表,重新生成变更列表文件"""
        sortlist = sflist.sort_values(by="itm", axis=0, ascending=False).reindex(
            columns=["itm", "file"]).values.tolist()
        if is_py2:
            f = open(filename, 'w')
        if is_py3:
            f = open(filename, 'w', encoding='utf-8')
        itmno = ''
        for itm, file in sortlist:
            if (itmno == '' or itmno != itm):  # 增加注释,列表是哪个ITM单
                f.write("\n--" + itm + "\n\n")
                itmno = itm
            # if is_py2:
            f.write(file + "\n")
            # if is_py3:
            #     f.write(file.decode("utf-8") + "\n")
        f.close()

    def resourceFile(self, sflist, filename, resource):  # resourceflag, flagposition=3):

        """根据合并后的列表,生成资源文件变更列表文件
        由于山东执法resource目录下的文件没有打包到jar中，需要单独生成列表进行拷贝
        resourceflag资源标识,flagposition资源标识位置"""

        sortlist = sflist.sort_values(by="itm", axis=0, ascending=False).reindex(
            columns=["itm", "file"]).values.tolist()
        if is_py2:
            f = open(filename, 'w')
        if is_py3:
            f = open(filename, 'w', encoding='utf-8')
        itmno = ''
        for itm, file in sortlist:
            if (itmno == '' or itmno != itm):  # 增加注释,列表是哪个ITM单
                f.write("\n--" + itm + "\n\n")
                itmno = itm
            for key, value in resource:
                try:
                    if len(file.split('/')) > 3 and file.split('/')[value] == key:  # 文件在资源列表且没在项目根目录下
                        f.write(file + "\n")
                        break
                except IndexError as e:
                    f.write(file + "\n")
        f.close()

    def checkProject(self, sflist, project):
        """检查变更列表中是否存在非法的路径"""
        invalidpath = sflist[~sflist.file.str.contains(r'^/' + project + '.*')]
        return invalidpath

    def copyFile(self, sfilePath, dfilePath, sflist):
        """根据原路径及目录路径拷贝sflist中的文件到指定位置,
        由于checkProject对非法的路径已经检查了,这里直接执行拷贝
         返回拷贝成功的数量,忽略的目录以及找不到的文件列表"""
        sortlist = sflist.sort_values(by="itm", axis=0, ascending=False).reindex(
            columns=["itm", "file"]).values.tolist()
        errpath = []
        ignorepath = []
        success = 0
        for itm, filename in sortlist:
            newpath = '/'.join(filename.split('/')[2:])
            nsfilePath = os.path.join(sfilePath, newpath)
            ndfilePath = os.path.join(dfilePath, newpath)
            if os.path.isdir(nsfilePath):  # 目录则忽略
                ignorepath.append((itm, nsfilePath))
                continue
            elif os.path.isfile(nsfilePath):
                nndfilePath = os.path.split(ndfilePath)[0]
                if not os.path.exists(nndfilePath):
                    os.makedirs(nndfilePath)  # 目标目录不存在先创建
                try:
                    shutil.copyfile(nsfilePath, ndfilePath)
                    success += 1
                except FileNotFoundError:
                    errpath.append((itm, nsfilePath))
            else:
                errpath.append((itm, nsfilePath))
        return success, errpath, ignorepath


def usage():
    print("""本脚本功能,合并指定目录下构建的ITM单变更列表文件,并根据合并后的列表与所有未发布的文件进行比较
            ,如果有冲突则打印出冲突内容,根据参数4,如果是jar,war包则选择1,有冲突则退出,没有冲突则合并变更列表文件,
            把列表文件指定的代码拷贝到指定目录;如果选择其他则只提示冲突或不冲突,不生成合并变更列表,并退出.配合JenkinsFlowProcess.py
            参数1(开发单路径) 
            参数2(本次构建的开发单号) 
            参数3(变更列表文件名)
            参数4(1:财补等jar,war包按全量出的会合并,其他运政增量出只提示),参数为1时必须指定参数5,参数6,参数7,参数8
            参数5(本次构建的本地最新代码路径,从开发库取)
            参数6(上次发布后本地受控的代码路径,从受控库取)
            参数7(本次构建的目录通常为工程路径加BUILD_ID)
            参数8(工程名,用于校验变更列表是否合法)
                JenkinsITMCheck.py   /home/文件或目录
REQUEST_20190325_130670,REQUEST_20190322_130645,REQUEST_20190325_130669#REQUEST_20190329_130736#REQUEST_20190402_130784
行政端-路径说明.txt 1 /usr/local/jenkins_workspace/workspace/xzrtmis/xzrtmis /usr/local/jenkins_workspace/workspace/xzrtmis/xzrtmisn /usr/local/jenkins_workspace/workspace/xzrtmis/BUILD333 xzrtmis""")
    sys.exit(1)


if __name__ == "__main__":
    if (len(sys.argv) != 5 and len(sys.argv) != 9):
        usage()
    filepath = sys.argv[1]
    itmno = sys.argv[2]
    itmno = itmno.replace('\u200b', '')  # 替换见鬼的不可见字符,
    filename = sys.argv[3]
    flag = sys.argv[4]
    change_file = os.path.join(filepath, filename)

    if flag == "1":  # 1:财补等jar,war包按全量出的会合并,其他运政增量出只提示),参数为1时必须指定参数5,参数6,参数7,参数8
        if len(sys.argv) != 9:
            usage()
        sourpath = sys.argv[5]
        controlledpath = sys.argv[6]

        buildid = sys.argv[7]
        project = sys.argv[8]
        success = 0
        print(Fore.CYAN + "###########开始变更列表冲突检查，请注意以下检查内容##########：")
        if not os.path.exists(change_file):
            print(Fore.RED + "找不到变更列表文件【%s】,退出测试" % filename)
            sys.exit(1)
        if not os.path.isdir(sourpath):
            print(Fore.RED + "找不到源码目录【%s】,退出测试" % sourpath)
            sys.exit(1)
        if not os.path.isdir(controlledpath):
            print(Fore.RED + "找不到受控代码目录【%s】,退出测试" % controlledpath)
            sys.exit(1)
    ccf = CheckChangeFile()
    syzlist = ccf.getListFileContext(itmno, change_file)
    if flag == "1":  #
        print(Fore.CYAN + "######无冲突,开始检查变更列表明细是否合法######")
        invalidpath = ccf.checkProject(syzlist, project)  # 检查变更列表是否合法
        if len(invalidpath) > 0:
            for itm, invaildfile in invalidpath.reindex(columns=["itm", "file"]).values.tolist():
                print(Fore.RED + "*****错误*****ITM文件【%s】中存在非法路径【%s】,请提交人修改后再构建!!" % (itm, invaildfile))
            sys.exit(1)
        print(Fore.CYAN + "######列表合法,开始生成合并列表文件######")
        newfilename = os.path.join(buildid, filename)  # 把合并后的文件存放到构建目录下
        resfilename = os.path.join(buildid, 'res_' + filename)  # 把合并后的资源列表文件存放到构建目录下,山东执行特别
        print("buildid{%s},filename{%s},newfilename{%s}" % (buildid, filename, newfilename))
        ccf.writeModifyFile(syzlist, newfilename)
        print(Fore.GREEN + "***恭喜***生成成功,合并变更列表文件为【%s】" % newfilename)
        print(Fore.CYAN + "***准备生成资源列表文件***")
        #resource = {'resources': 3, 'commLibs': 4, 'commLibs': 3, 'config': 3, 'law-web': 1, 'crt-web': 1, 'ent-web': 1, 'safety-web': 1, 'jlads-web': 1}  # 资源列表标识,先在脚本中写死，有变化根据情况修改
        resource = [('resources', 3), ('commLibs', 4), ('commLibs', 3), ('config', 3), ('law-web', 1), ('crt-web', 1), ('ent-web', 1), ('safety-web', 1), ('jlads-web', 1), ('el-web', 1)]  # 资源列表标识,先在脚本中写死，有变化根据情况修改
        ccf.resourceFile(syzlist, resfilename, resource)
        print(Fore.GREEN + "***恭喜***生成成功,合并资源变更列表文件为【%s】" % resfilename)
        print(Fore.CYAN + "...根据合并变量列表文件更新本地受控代码,更新情况...")
        uniquesyzlist = syzlist.drop_duplicates("file")  # 生成不重复的文件列表,进行拷贝
        allfilesum = len(uniquesyzlist)
        success, errpath, ignorepath = ccf.copyFile(sourpath, controlledpath, uniquesyzlist)
        ignorepathsum = len(ignorepath)
        print(Fore.GREEN + "***不重复的文件(含目录)总数【%s】,目录数【%s】,拷贝成功数【%s】" % (allfilesum, ignorepathsum, success))
        if len(ignorepath) > 0:
            for itm, errname in ignorepath:
                print(Fore.CYAN + "*****忽略****拷贝目录:ITM单【%s】目录【%s】" % (itm, errname))
        if len(errpath) > 0:
            for itm, errname in errpath:
                print(Fore.RED + "*****错误****拷贝代码文件失败:ITM单【%s】文件【%s】" % (itm, errname))
        if (allfilesum == (ignorepathsum + success)):
            print(Fore.GREEN + "***恭喜***更新文件成功!")
            sys.exit(0)
        else:
            print(Fore.RED + "@@@错误@@@更新文件失败@@@!")
            sys.exit(1)
    else:
        # 如运政系统,出的增量包,编译所有代码,通过JenkinsPathFileBuild.py从编译后的产物生成增量包
        print(Fore.GREEN + "***恭喜***没有冲突,可以开始测试!")
