#!/usr/bin/env python
# -*- coding=utf-8 -*-
import pymysql
import time
import os
import sys
import subprocess
import codecs
import re
import copy
import fnmatch
from urllib import parse
from colorama import Fore
from colorama import init

init(autoreset=True, strip=False)


def insertJenkinsRelease(itm, jenkinsjob, svn_revision, svn_path, promotenumber, jenkinsbuildnumber, patchnumber,
                         tester, module='00'):
    """module参数主要用于区分同一job可能构建不同的java工程
    """
    db = pymysql.connect(host="10.168.7.22", user="test", password="test", db="test", port=3306, charset='utf8')
    cur = db.cursor()
    # 记录发布基本信息
    sql_insert = """insert into JENKINSRELEASE(ITM,JENKINSJOB,SVN_REVISION,SVN_PATH,PROMOTENUMBER,JENKINSBUILDNUMBER,PATCHNUMBER,TESTER,DATE,MODULE)   select '%s','%s','%s','%s','%s','%s','%s','%s',now(),'%s' from dual"""
    # 更新本次ITM单多次构建的所有的列表文件为已经发布
    sql_update0 = """update JENKINSMODIFYLIST SET PATCHID=0 WHERE JENKINSJOB='%s' AND ITM='%s' AND PATCHID=1 AND MODULE='%s' """
    # 更新本次构建的发布ID为最新一次发布记录ID
    sql_update = """update JENKINSMODIFYLIST JL,JENKINSRELEASE JR SET JL.PATCHID=JR.ID WHERE JL.JENKINSJOB=JR.JENKINSJOB AND JL.JENKINSBUILDNUMBER=JR.JENKINSBUILDNUMBER AND JL.MODULE =JR.MODULE AND JR.ID=%d """
    try:
        cur.execute(sql_insert % (
            itm, jenkinsjob, svn_revision, svn_path, promotenumber, jenkinsbuildnumber, patchnumber, tester, module))
        tmpid = cur.lastrowid
        cur.execute(sql_update0 % (jenkinsjob, itm, module))  # 把所有同一ITM单的JOB的发布ID都更新为0;
        cur.execute(sql_update % tmpid)
        db.commit()
    except Exception as e:
        db.rollback()
        print(e)
    finally:
        db.close()


def runSVN(path, url, usr, passwd, subcommand="import", msg="更新补丁包"):
    """["svn","import","/home/jenkins_workspace/workspace/gzrtmis/BUILD630/context","https://10.168.1.112/svn/test/20180329/201803/path_20180402_0001/context","--username","linwanzhi","--password","simsadmin","--non-interactive","--trust-server-cert","-m 备注"]
    控制台执行SVN命令,主要用于导入的操作
    返回CompletedProcess类的对象
    """
    if subcommand not in ("import", "del", "remove", "rm", "list", "info"):
        print(Fore.RED + "SVN 子命令不正常,请重新输入")
        return None
    params = ["svn"]
    params.append(subcommand)
    if subcommand == "import":
        params.extend((path, url))
        params.extend(("-m", msg))
    else:
        params.append(url)
    params.extend(("--username", usr))
    params.extend(("--password", passwd))
    params.extend(("--non-interactive", "--trust-server-cert"))
    cp = subprocess.run(params, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return cp


def versionUpdateLogFile(buildpath, user, modulename, patchnumber='1.0.0.0', updes='测试'):
    updateinsertsql = """INSERT INTO VERSIONUPGRADELOG( LOGID ,VERSIONNUM,MODULNAME ,UPDES,UPDATETIME)
SELECT SEQ_LOGID.NEXTVAL,'%s','%s','%s',to_number(to_char(sysdate,'YYYYMMDDHH24MISS')) from dual;
commit;
""" % (patchnumber, modulename, updes)
    if os.path.isdir(os.path.join(buildpath, modulename, 'ORACLE')):
        vuf = open(os.path.join(buildpath, modulename, 'ORACLE', user, 'Init', 'UPATE_VERSIONUPGRADELOG.sql'), 'wb')
        vuf.write(updateinsertsql.encode('gbk', errors='ignore'))
        vuf.close()
        inicontext = readFile2(os.path.join(buildpath, modulename, 'ORACLE', user, 'Init', 'Update_Init.sql'), 1)
        lenini = len(inicontext)
        i = 0
        for line in inicontext:
            if line.strip() in ('@@UPATE_VERSIONUPGRADELOG.sql', '@@UPATE_VERSIONUPGRADELOG.sql;'):
                break
            elif line.strip() == 'exit;':
                inicontext.insert(i, '@@UPATE_VERSIONUPGRADELOG.sql' + '\n')
                break
            elif i == lenini:
                inicontext.insert(i, '@@UPATE_VERSIONUPGRADELOG.sql' + '\n')
                inicontext.insert(i + 1, 'exit;\n')
            i += 1
        inifile = open(os.path.join(buildpath, modulename, 'ORACLE', user, 'Init', 'Update_Init.sql'), 'w+')
        inifile.writelines(inicontext)
        inifile.close()
        print(Fore.GREEN + "升级日志脚本更新成功!")

    else:
        print(Fore.RED + "::>_<:: 未能成功生成升级日志脚本,请检查JENKNIS项目是否正确配置了ORACLE脚本模板!发布终止!")
        sys.exit(1)


def zipPathFile(zipfile, path, childpath):
    """
    压缩path目录下的childpath所有文件,压缩包中以pathorfile开始为相对路径存储
    zipPathFile('行政端.zip','E:/workspace/gzrtmis/build3','context')
    压缩文件夹
    """
    os.chdir(path)
    params = ["zip"]
    params.extend((zipfile, childpath, "-r", "-q"))
    cp = subprocess.run(params, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return cp


def comparePathlistAndOsFiles(pathfile, buildpath, web_root_name):
    """
    pathfile变更列表清单文件
    buildpath补丁包路径,为web_root的上一些目录,即通常不包含context
    返回比较完成不一致的2维列表

    """
    pattern = '\$\d+.class$'  # 内部类文件正则表达式
    patchfiles = getAllPathFile(os.path.join(buildpath, web_root_name))
    pathlistfiles = getALLModifyPathFile(pathfile, buildpath, web_root_name)
    lenpatchfiles = len(patchfiles)
    lenpathlistfiles = len(pathlistfiles)
    if lenpatchfiles == 0 and lenpathlistfiles != 0:
        return (1, patchfiles, pathlistfiles)
    elif lenpatchfiles == 0 and lenpathlistfiles == 0:
        return (2, patchfiles, pathlistfiles)
    elif lenpatchfiles != 0 and lenpathlistfiles == 0:
        return (3, patchfiles, pathlistfiles)
    else:
        dpatchfiles = patchfiles - pathlistfiles  # 补丁文件与列表文件的差集
        cdpatchfiles = copy.copy(dpatchfiles)
        for innerclass in dpatchfiles:  # 判断内部类文件
            classname = re.sub(pattern, '.class', innerclass)
            if classname in pathlistfiles:
                cdpatchfiles.remove(innerclass)
        dpathlistfiles = pathlistfiles - patchfiles  # 列表文件与补丁文件的差集
        lendpatchfiles = len(cdpatchfiles)
        lendpathlistfiles = len(dpathlistfiles)
        if lendpathlistfiles != 0 and lendpatchfiles == 0:
            return (4, cdpatchfiles, dpathlistfiles)
        elif lendpathlistfiles == 0 and lendpatchfiles != 0:
            return (5, cdpatchfiles, dpathlistfiles)
        elif lendpathlistfiles != 0 and lendpatchfiles != 0:
            return (6, cdpatchfiles, dpathlistfiles)
        else:
            return (0, cdpatchfiles, dpathlistfiles)


def findInnerClassFiles(classfile):
    """
    返回内部类文件清单
    """
    result = []
    try:
        filepath, filename = os.path.split(classfile)
        pattern = os.path.splitext(filename)[0] + '$' + '*' + '.class'
        for filename in os.listdir(filepath):
            if fnmatch.fnmatch(filename, pattern):
                inerclass = os.path.normpath(os.path.join(filepath, filename)).replace("\\", "/")
                result.append(inerclass)
    except Exception as err:
        print(Fore.RED + "%s" % err)
    return result


def getAllPathFile(pathfile):
    """
    返回路径下所有文件
    pathfile 路径
    """
    path_collection = set()
    for dirpath, dirnames, filenames in os.walk(pathfile):
        for file in filenames:
            path_collection.add(os.path.join(dirpath, file).replace("\\", "/"))
    return path_collection


def getALLModifyPathFile(pathfile, buildpath, web_root_name):
    """
    返回文件列表的全路径,java文件为类的路径
    :param buildpath:生成包的临时路径 E:/workspace/gzrtmis,通常为context的上一级目录
    :param pathfile:修改清单文件  E:/workspace/gzrtmis/新增修改文件代码清单.txt
    :return:返回不重复的发布文件修改清单列表 (绝对路径)
    a=getALLModifyPathFile('E:/workspace/gzrtmis/新增修改文件代码清单.txt','E:/workspace/gzrtmis')
    """
    pathfiles = getUniqueModifyFile(pathfile)
    abspathfiles = set()
    for item in pathfiles:
        pathl = item.split('/')
        dpath = ''
        filename, extname = os.path.splitext(pathl.pop())  # 取出文件和扩展名，并在列表中删除
        if extname.upper() == '.JAVA':
            sdfile = filename + '.class'
        else:
            sdfile = filename + extname
        if web_root_name == pathl[2]:
            if extname.upper() == '.JAVA':
                print(Fore.RED + ">>>>>>>>>>>>>>>%s下不应该包含JAVA文件 , 列表文件路径:%s" % (web_root_name, item))
            else:
                dpath = '/'.join(pathl[2:])
                dpath = os.path.join(buildpath, dpath, sdfile)
        else:
            dpath = '/'.join(pathl[3:])
            dpath = os.path.join(buildpath, web_root_name, 'WEB-INF', 'classes', dpath, sdfile)
        if dpath != '':
            dpath = os.path.normpath(dpath).replace("\\", "/")
            abspathfiles.add(dpath)
    return abspathfiles


def getUniqueModifyFile(pathfile):
    """
    返回不重复的修改文件列表
    :param self:
    :param pathfile:修改清单文件
    :return:不重复的文件修改清单列表 (相对路径)
    """
    files = set()
    if (os.path.isfile(pathfile)):
        lines = readFile2(pathfile, 1)
        for line in lines:
            tmp = _delutf8bom(line)
            tmp = tmp.strip()
            if ((tmp[:2] != '--') and (tmp[:1] != '#') and (tmp != '')):
                files.add(tmp)
    return files


def readFile2(pathfile, lineflag=0):
    data = None
    try:
        infile = open(pathfile, 'r', encoding='utf-8')
        if lineflag == 1:
            data = infile.readlines()
        else:
            data = infile.read()
        infile.close()
    except UnicodeDecodeError as E:
        try:
            if (not infile.closed):
                infile.close()
            infile = open(pathfile, 'r', encoding='GBK')
            if lineflag == 1:
                data = infile.readlines()
            else:
                data = infile.read()
            infile.close()
        except UnicodeDecodeError as E:
            try:
                if (not infile.closed):
                    infile.close()
                infile = open(pathfile, 'r', encoding='ascii')
                if lineflag == 1:
                    data = infile.readlines()
                else:
                    data = infile.read()
                infile.close()
            except Exception as E:
                print(Fore.RED + "unknow error:{1},{0}".format(E, pathfile))

    finally:
        if (not infile.closed):
            infile.close()
    return data


def checkRelevance(itm, jenkinsjob, jenkinsbuildnumber, module='00'):
    """
    :itm itm中的单号
    jenkinsjob jenkins中项目名称  jenkinsbuildnumber jenkins构建号
     查询同一job同时进行测试时,未出包的冲突文件
     :return:[['/jlrtmis/context/platform/mainv3comm/main.jsp'],['REQUEST_20180411_126112#1691#59508,REQUEST_20180315_125754#1692#59513,20171213#1398#54809']]
    """
    svn_revision_sql = """select max(SVN_REVISION)  svn_revision from JENKINSMODIFYLIST   WHERE ITM='%s' AND JENKINSJOB='%s' AND JENKINSBUILDNUMBER='%s' AND MODULE ='%s'
    """
    relevance_sql = """SELECT CONCAT_WS('/',gt.path,gt.file) path_file,group_concat(CONCAT_WS('#',gt.itm,gt.jenkinsbuildnumber,gt.svn_revision)) itm_number_revision
                 from (select nt.itm,nt.path,nt.file,max(nt.svn_revision) svn_revision,max(nt.jenkinsbuildnumber) jenkinsbuildnumber
                 from (SELECT * from JENKINSMODIFYLIST where  JENKINSJOB='%s' and patchid=1 and (path,file) in
                 (select path,file from JENKINSMODIFYLIST  A WHERE A.ITM='%s' AND A.JENKINSJOB='%s' AND A.JENKINSBUILDNUMBER='%s' AND MODULE ='%s')
                 and ITM!='%s'AND MODULE ='%s' ) nt GROUP BY  nt.itm,nt.path,nt.file) as gt GROUP BY gt.path,gt.file
    """
    db = pymysql.connect(host="10.168.7.22", user="test", password="test", db="test", port=3306, charset='utf8')
    cur = db.cursor()
    results = []
    relevance = []
    try:
        cur.execute(svn_revision_sql % (itm, jenkinsjob, jenkinsbuildnumber, module))
        svn_revision = int(cur.fetchone()[0])
        cur.execute(relevance_sql % (jenkinsjob, itm, jenkinsjob, jenkinsbuildnumber, module, itm, module))

        results = cur.fetchall()
        for row in results:
            if row[0][:1] == '\ufeff':
                path_file = row[0][1:]
            else:
                path_file = row[0]
            for item in row[1].split(','):
                jitm, jbn, jsvn = item.split('#')
                if (int(jsvn) < svn_revision):
                    relevance.append([path_file, jitm, jbn, jsvn])
        if len(relevance) > 0:
            print(Fore.RED + ".....本次构建发布的包ITM单【%s】构建号【%s】SVN版本号【%d】与未发布的构建存在冲突,......" % (
                itm, jenkinsbuildnumber, svn_revision))
            for i1, i2, i3, i4 in relevance:
                print(Fore.RED + "文件【%s 】与ITM单【%s】构建号【%s】SVN版本号【%s】文件冲突" % (i1, i2, i3, i4))
            return 1
        else:
            return 0
    except TypeError as e:
        print(Fore.RED + "未找到本次构建的清单列表数据,构建未配置入库操作? or 输入参数有误?【%s】【%s】【%s】【%s】 " % (
        itm, jenkinsjob, jenkinsbuildnumber, module))
        return 1
    except Exception as e:
        print(e)
    finally:
        db.close()


def _delutf8bom(line):
    """
    去除文件中多余的bom字符
    :param self:
    :param line:
    :return:
    """
    tline = line
    bomtag = tline[:1]
    while True:
        if bomtag == '\ufeff' or bomtag == '\ufffe':
            tline = tline[1:]
            bomtag = tline[:1]
        else:
            break
    return tline


if __name__ == "__main__":
    """  根据输入的清单文件与磁盘上WEB工程的文件进行比较,如果不一致则提示;如果一致则进行压缩,压缩文件包含
    数据库脚本(如果有)和WEB工程的文件(如果有);压缩包中以web和数据库脚本在二级目录下,顶级目录为builpath下的目录,如:
    BUILD10
      行政端
         context\...
         ORACLE\...
         行政端-路径说明.txt
    """
    import jenkinsconf

    if (len(sys.argv) != 15 and len(sys.argv) != 16):
        print(
            Fore.RED + """参数个数必需14或15个,格式顺序如下:
            ITM单号 Jenkins工程名  SVN路径 发布buildid 构建buildid 补丁编号 测试人员  web_context_root 变更列表文件名 构建路径  压缩包名称 web_context_root上级名(如行政端) 业务库用户名 升级简要说明   模块标识
            如:
            'D:\Anaconda3\python.exe D:/workspace/hzpython/JenkinsRelease.py REQUEST_20171128_124652 JLYZ_XZD https://10.168.1.112/svn/test/20180329/path_hn_20180329_0001 1 1332 patch_jl_20180329_0001_ts 陈艳萍 context 新增修改文件代码清单.txt E:\workspace\gzrtmis\BUILD4 行政端.zip 行政端 CRTMIS 升级部分测试功能  00""")
        sys.exit(1)
    itm = sys.argv[1]
    jenkinsjob = sys.argv[2]
    svn_path = sys.argv[3]
    promotenumber = sys.argv[4]
    jenkinsbuildnumber = sys.argv[5]
    patchnumber = sys.argv[6]
    tester = sys.argv[7]
    web_root_name = sys.argv[8]
    listfile = sys.argv[9]
    buildpath = sys.argv[10]
    zipfile = sys.argv[11]
    modulename = sys.argv[12]
    user = sys.argv[13]
    updes = sys.argv[14][:500]
    module = '00'
    if svn_path[:8] != 'https://':
        print(Fore.RED + "输入的SVN_URL参数错误【%s】,退出发布" % svn_path)
        sys.exit(1)
    if patchnumber[:6] != 'patch_':
        print(Fore.RED + "输入的补丁号格式不正确【%s】,退出发布" % patchnumber)
        sys.exit(1)
    if len(sys.argv) == 16:
        try:
            int(sys.argv[15])
            module = sys.argv[15][:2]
        except ValueError as e:
            print(Fore.RED + "模块名称参数不正确【%s】,应该输入形如【00】这样的参数,退出发布...." % module)
            sys.exit(1)
    print(Fore.CYAN + "受控发布入库开始!")
    # 第一步比较变更列表清单与补丁文件是否一致,如果不一致打印提示,并终止
    print(Fore.CYAN + "开始检查清单文件与补丁文件是否一致....")
    start = time.clock()
    compareresult = comparePathlistAndOsFiles(os.path.join(buildpath, modulename, listfile),
                                              os.path.join(buildpath, modulename), web_root_name)
    if compareresult[0] == 1:
        print(Fore.RED + "web工程的补丁包为空,而变更列表不为空,请检查BUILD是否出错,本次上传终止!")
        sys.exit(1)
    elif compareresult[0] == 2:
        print(Fore.RED + "变更列表文件为空,web工程的补丁包为空,请检查是否不需要WEB补丁包,只需要数据库脚本")
    elif compareresult[0] == 3:
        print(Fore.RED + "web工程的补丁包不为空,而变更列表为空,请检查BUILD是否出错,本次上传终止")
        sys.exit(1)
    elif compareresult[0] == 4:
        print(Fore.RED + "变更列表清单文件比生成的补丁文件数量更多,文件列表如下,本次上传终止")
        for item in compareresult[2]:
            print(Fore.RED + "清单文件【%s】" % item)
        sys.exit(1)
    elif compareresult[0] == 5:
        print(Fore.RED + "补丁文件比变更列表清单文件数量更多,文件列表如下,本次上传终止")
        for item in compareresult[1]:
            print(Fore.RED + "补丁文件【%s】" % item)
        sys.exit(1)
    elif compareresult[0] == 6:
        print(Fore.RED + "变更清单文件列表与补丁文件差异较多,清单如下,本次上传终止")
        for item in compareresult[1]:
            print(Fore.RED + "补丁文件【%s】" % item)
        for item in compareresult[2]:
            print(Fore.RED + "清单文件【%s】" % item)
        sys.exit(1)
    if compareresult[0] == 0:  # 清单文件不为空,需要增加对构建中未发布的文件进行检查
        print(Fore.GREEN + "完成,检查结果:清单文件与补丁文件一致,耗时 %f " % (time.clock() - start))
        print(Fore.GREEN + "开始检查构建中未发布的版本文件是否有冲突....")
        rt = checkRelevance(itm, jenkinsjob, jenkinsbuildnumber, module)
        if rt != 0:
            print(Fore.RED + "检查完成,构建中未发布的版本文件存在冲突,退出发布....")
            sys.exit(1)
        else:
            print(Fore.GREEN + "恭喜!检查完成,构建中未发布的版本与本次发布文件不存在冲突....")
    # 生成数据库的升级日志脚本,只有生成脚本的用户名不为00才生成库的
    if user != '00':
        print(Fore.GREEN + '开始生成升级日志脚本文件...')
        versionUpdateLogFile(buildpath, user, modulename, patchnumber, updes)
    # 压缩文件
    print(Fore.GREEN + '开始压缩补丁文件...')
    zipresult = zipPathFile(zipfile, buildpath, modulename)
    if zipresult.returncode != 0:
        print(Fore.RED + "压缩补丁文件失败,压缩目录【%s】,本次上传终止" % os.path.join(buildpath, modulename))
        sys.exit(1)
    print(Fore.GREEN + '成功压缩补丁文件【%s】' % os.path.join(buildpath, zipfile))
    # 上传文件到SVN
    print(Fore.GREEN + '开始上传补丁文件...')
    runsvnresult = runSVN(os.path.join(buildpath, zipfile), svn_path + '/' + zipfile, jenkinsconf.svnusr,
                          jenkinsconf.svnpwd)
    if runsvnresult.returncode != 0:
        print(Fore.RED + '(*@^@*〉上传补丁包出错:' + parse.unquote(runsvnresult.stderr.decode('utf-8')))
        sys.exit(1)
    svn_revision = runsvnresult.stdout.split()[-1].decode('utf-8')[:-1]
    print(Fore.GREEN + '补丁上传成功文件【%s】' % (svn_path + '/' + zipfile))
    # 更新数据库发布记录
    print(Fore.GREEN + '本次操作日志入库...')
    insertJenkinsRelease(itm, jenkinsjob, svn_revision, svn_path + '/' + zipfile, promotenumber, jenkinsbuildnumber,
                         patchnumber, tester, module)
    print(Fore.GREEN + '本次操作日志入库完成...')
    print(Fore.CYAN + "Y(^_^)Y Y(^_^)Y 恭喜!成功,受控发布入库结束,耗时%f s!!Y(^_^)Y Y(^_^)Y " % (time.clock() - start))
