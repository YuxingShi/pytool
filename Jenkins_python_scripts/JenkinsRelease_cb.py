#!/usr/bin/env python
# -*- coding=utf-8 -*-
"""python2.7财补相关微服务全量更新补丁包"""
import pymysql
import time
import os
import sys
import subprocess
from lxml import etree
from colorama import Fore
from colorama import init
import tarfile

init(autoreset=True, strip=False)
_ver = sys.version_info

#: Python 2.x?
is_py2 = (_ver[0] == 2)

#: Python 3.x?
is_py3 = (_ver[0] == 3)
if is_py2:
    import urllib
if is_py3:
    from urllib import parse


def insertJenkinsRelease(itm, jenkinsjob, svn_revision, svn_path, promotenumber, jenkinsbuildnumber, patchnumber,
                         tester, module='00', imgid=''):
    """module参数主要用于区分同一job可能构建不同的java工程
    """
    db = pymysql.connect(host="10.168.7.22", user="test", password="test", db="test", port=3306, charset='utf8')
    cur = db.cursor()
    # 记录发布基本信息
    sql_insert = """insert into JENKINSRELEASE(ITM,JENKINSJOB,SVN_REVISION,SVN_PATH,PROMOTENUMBER,JENKINSBUILDNUMBER,PATCHNUMBER,TESTER,DATE,MODULE,IMGID)   select '%s','%s','%s','%s','%s','%s','%s','%s',now(),'%s','%s' from dual"""
    try:
        exe_sql = sql_insert % (
            itm, jenkinsjob, svn_revision, svn_path, promotenumber, jenkinsbuildnumber, patchnumber, tester, module,
            imgid)
        cur.execute(exe_sql)
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
    if subcommand not in ("import", "del", "remove", "rm", "list", "info", 'move', 'commit'):
        print(Fore.RED + "SVN 子命令不正常,请重新输入")
        return None
    params = ["svn"]
    params.append(subcommand)
    if subcommand in ("commit", "move", "import"):
        params.extend((path, url))
        params.extend(("-m", msg))
    else:
        params.append(url)
    params.extend(("--username", usr))
    params.extend(("--password", passwd))
    params.extend(("--non-interactive", "--trust-server-cert"))
    if is_py2:
        print(params)
        cp = subprocess.Popen(params, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        cp.wait()

    if is_py3:
        cp = subprocess.run(params, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return cp


def tarPathFile(tarfilename, path, childpath):
    """
    打包path目录下的childpath所有文件,打包包中以pathorfile开始为相对路径存储
    tarPathFile('finance-web.tar','/usr/local/jenkins_workspace/workspace/scxccmp-web','scxccmp-web')
    打包文件夹
    """
    os.chdir(path)
    params = ["tar"]
    params.extend((tarfilename, childpath, "-zvcf"))
    if is_py2:
        cp = subprocess.Popen(params, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if is_py3:
        cp = subprocess.Popen(params, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return cp


def zipPathFile(zipfile, path, childpath):
    """
    打包path目录下的childpath所有文件,打包包中以pathorfile开始为相对路径存储
    zipPathFile('行政端.zip','E:/workspace/gzrtmis/build3','context')
    打包文件夹
    """
    os.chdir(path)
    params = ["zip"]
    params.extend((zipfile, childpath, "-r", "-q"))
    if is_py2:
        cp = subprocess.Popen(params, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        cp.wait()
    if is_py3:
        cp = subprocess.run(params, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return cp


def getTargetName(pomfile):
    """取pom.xml文件中的<artifactId>fdfs-rest</artifactId>
    <version>0.0.6-SNAPSHOT</version>
    <packaging>war</packaging>节点用于重命名版本号,用于打包war或jar包;
    由于xml文件存在命名空间,所以xpath取时需要处理"""
    tree = etree.parse(pomfile, etree.XMLParser())
    d = tree.getroot().nsmap
    d.update(a=d.pop(None))
    artifactId = tree.xpath("//a:project/a:artifactId", namespaces=d)[0].text
    version = tree.xpath("//a:project/a:version", namespaces=d)[0].text
    packaging = tree.xpath("//a:project/a:packaging", namespaces=d)[0].text

    return artifactId + "-" + version + "." + packaging


exclude_names = ['.svn']


def filter_func(tarinfo):
    if tarinfo.name not in exclude_names and tarinfo.isdir():
        return None
    else:
        return tarinfo


def tarProject(tarfilename, path, subpath):
    if os.path.isdir(path) and os.path.isdir(os.path.join(path, subpath)):
        tarpathfile = os.path.join(path, tarfilename)
        tar = tarfile.open(tarpathfile, 'w:gz')
        for root, spath, files in os.walk(os.path.join(path, subpath)):
            if ".svn" in spath or ".svn" in os.path.split(root)[1]:  # 打包过滤掉.svn的目录下的所有
                continue
            root_ = os.path.relpath(root, start=path)
            for file in files:
                fullpath = os.path.join(root, file)
                tar.add(fullpath, arcname=os.path.join(root_, file))
        tar.close()
        return True
    else:
        return False


if __name__ == "__main__":
    """  打包指定目录,并上传到SVN
    根据提供的包路径 需打包的目录 包名称来判断:如果包名是.war并且包文件已经存在则直接上传war文件到SVN
    如果包名称为.tar则先打包后再上传,切换到包路径下,打包命令"tar -zvcf 包名称.tar 需打包的目录"
    """
    import jenkinsconf

    if (len(sys.argv) != 12 and len(sys.argv) != 13 and len(sys.argv) != 14):
        print(
            Fore.RED + """参数个数必需11个,格式顺序如下:
            ITM单号(财补先用000) Jenkins工程名  SVN路径 发布buildid 构建buildid 补丁编号 测试人员  包路径 需打包的路径 包名称  包镜像ID 模块代码默认为00
            如:python /usr/local/jenkins_workspace/tools/JenkinsRelease_cb.py 0000 ax-rest https://10.168.1.202/svn/01.产品and项目/20湖南财补/02湖南财政惠农补贴系统省集中项目/06测试发布补丁包/patch_cb_201809030_0001 4 178 patch_cb_201809030_0001 林万枝 /usr/local/jenkins_workspace/workspace/ax-rest/ax-rest/target target axrest-0.0.1-SNAPSHOT.war 07e502c6ce77 01
            """)
        sys.exit(1)
    itm = sys.argv[1]
    jenkinsjob = sys.argv[2]
    svn_path = sys.argv[3]
    promotenumber = sys.argv[4]
    jenkinsbuildnumber = sys.argv[5]
    patchnumber = sys.argv[6]
    tester = sys.argv[7]
    buildpath = sys.argv[8]
    subbuildpath = sys.argv[9]
    zipfile = sys.argv[10]
    imgid = sys.argv[11]
    #module = '00'
    module = sys.argv[12]
    istarflag = "1"  # 是否需要执行打包标识，默认打包,JAR与war也不打包
    start = time.clock()
    # 打包文件
    if len(sys.argv) == 13:
        module = sys.argv[12]
    if len(sys.argv) == 14:
        module = sys.argv[12]
        istarflag = sys.argv[13]
    extname = os.path.splitext(zipfile)[1]
    if istarflag == "1":
        if (extname == '.gz' or extname == '.tar'):
            if os.path.isdir(os.path.join(buildpath, subbuildpath)):
                print(Fore.GREEN + '开始打包补丁文件...')
                p = tarProject(zipfile, buildpath, subbuildpath)
                if p:
                    print(Fore.GREEN + '成功打包补丁文件【%s】' % os.path.join(buildpath, zipfile))
                else:
                    print(Fore.RED + "打包补丁文件失败,打包目录【%s】,本次上传终止" % os.path.join(buildpath, subbuildpath))
                    sys.exit(1)
            else:
                print(Fore.RED + "打包补丁文件失败,不存在打包的目录【%s】,本次上传终止!" % os.path.join(buildpath, subbuildpath))
                sys.exit(1)
        elif extname == '.zip':
            if os.path.isdir(os.path.join(buildpath, subbuildpath)):
                print(Fore.GREEN + '开始打包补丁文件...')
                p = zipPathFile(zipfile, buildpath, subbuildpath)
                if p:
                    print(Fore.GREEN + '成功打包补丁文件【%s】' % os.path.join(buildpath, zipfile))
                else:
                    print(Fore.RED + "打包补丁文件失败,打包目录【%s】,本次上传终止" % os.path.join(buildpath, subbuildpath))
                    sys.exit(1)
            else:
                print(Fore.RED + "打包补丁文件失败,不存在打包的目录【%s】,本次上传终止!" % os.path.join(buildpath, subbuildpath))
                sys.exit(1)
    if extname == '.jar' or extname == '.war':  # 这2种类型不打包，直接取现在的
        # 根据pom文件中定义的版本号修改包文件
        pomfile = os.path.join(os.path.dirname(buildpath), "pom.xml")
        if os.path.isfile(pomfile):
            zipfile = getTargetName(pomfile)
    if os.path.isfile(os.path.join(buildpath, zipfile)):
        # 上传文件到SVN
        print(Fore.GREEN + '开始上传补丁文件...')
        try:
            p = runSVN(os.path.join(buildpath, zipfile), svn_path + '/' + zipfile, jenkinsconf.svnusr,
                       jenkinsconf.svnpwd, msg=imgid)
            if is_py2:
                er = p.stderr.read()
                s = p.stdout.read()
                # e1 = er.decode('utf-8')
                # s1 = s.decode('utf-8')
                if er == '' and s.split('\n\n')[1].split(' ')[0] == '提交后的版本为':
                    svn_revision = int(s.split('\n\n')[1].split(' ')[1][:-4])
                else:
                    errmsg = urllib.unquote(er)
                    print(Fore.RED + '(*@^@*〉上传补丁包出错1:' + errmsg)
                    sys.exit(1)
            if is_py3:
                if p.returncode != 0:
                    print(Fore.RED + '(*@^@*〉上传补丁包出错:' + parse.unquote(p.stderr.decode('utf-8')))
                    sys.exit(1)
                svn_revision = p.stdout.split()[-1].decode('utf-8')[:-1]
        except OSError as e:
            print(Fore.RED + '(*@^@*〉上传补丁包出错,命令不正确:' + e)
            sys.exit(1)
        except ValueError as e:
            print(Fore.RED + '(*@^@*〉上传补丁包出错,参数不正确:' + e)
            sys.exit(1)
        print(Fore.GREEN + '补丁上传成功文件【%s】' % (svn_path + '/' + zipfile))
        # 更新数据库发布记录
        print(Fore.GREEN + '本次操作日志入库...')
        insertJenkinsRelease(itm, jenkinsjob, svn_revision, svn_path + '/' + zipfile, promotenumber, jenkinsbuildnumber,
                             patchnumber, tester, module, imgid)
        print(Fore.GREEN + '本次操作日志入库完成...')
        print(Fore.CYAN + "Y(^_^)Y Y(^_^)Y 恭喜!成功,受控发布入库结束,耗时%f s!!Y(^_^)Y Y(^_^)Y " % (time.clock() - start))
    else:
        print(Fore.RED + "(*@^@*〉失败了,找不到上传到SVN的文件:\r\n【%s】" % os.path.join(buildpath, zipfile))
