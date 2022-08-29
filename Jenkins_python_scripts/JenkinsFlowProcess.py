#!/usr/bin/env python3
# -*- coding=utf-8 -*-
import pandas as pd
import pymysql
from colorama import Fore
from colorama import init
import sys, os
import subprocess
import traceback

init(autoreset=True, strip=False)
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


class FlowProcess:
    """流程处理,用于控制jenkins流程
    svn propset svn:ignore 'target' .
    svn st | awk '{if ( $1 == "?") { print $2}}' | xargs svn add
    以上命令用于增加需要提交的文件,在提交文件前一定要执行"""

    def getDbConnect(self):
        """
        创建数据库连接
        """
        db = pymysql.connect(host="10.168.7.22", user="test", password="test", db="test", port=3306, charset='utf8')
        return db

    def getBuildSuccess(self, jenkinsjob, itm, module='00'):
        """根据jenkins构建的项目名,查找ITM单构建成功且未发布
        0-构建失败1-构建成功2-开始构建3-取消构建
        patchid=1未发布,大于1为发布
        """

        sql_query = """select JENKINSJOB,ITM,JENKINSBUILDNUMBER from JENKINSBUILD WHERE JENKINSJOB=%s and ITM=%s and STATUS='1' and patchid=1 and  MODULE=%s"""
        try:
            db = self.getDbConnect()
            cur = db.cursor()
            effectrow = cur.execute(sql_query, (jenkinsjob, itm, module))
            if effectrow == 0:
                return []
            return cur.fetchall()
        except Exception as e:
            print("数据库执行异常:%s" % e)
        finally:
            db.close()

    def getBuildStatus(self, jenkinsjob, itm, module='00'):
        """根据jenkins构建的项目名,查找非此ITM单构建开始或构建完成的单"""

        sql_query = """select JENKINSJOB,ITM,JENKINSBUILDNUMBER from JENKINSBUILD WHERE JENKINSJOB=%s and ITM!=%s and (STATUS='1' or STATUS='2') and patchid=1 and  MODULE=%s"""
        try:
            db = self.getDbConnect()
            cur = db.cursor()
            effectrow = cur.execute(sql_query, (jenkinsjob, itm, module))
            if effectrow == 0:
                return []
            return cur.fetchall()
        except Exception as e:
            print("数据库执行异常:%s" % e)
        finally:
            db.close()

    def insertJenkinsBuild(self, jenkinsjob, itm, jenkinsbuildnumber, tester, patchid, status, module='00'):
        """项目开始构建成功后写一条记录构建过程
        """
        try:
            db = self.getDbConnect()
            cur = db.cursor()
            # 记录发布基本信息
            sql_insert = """insert into JENKINSBUILD(JENKINSJOB, ITM, JENKINSBUILDNUMBER, TESTER, PATCHID, STATUS, DATE, MODULE)  select %s,%s,%s,%s,%s,%s,now(),%s from dual"""

            effectrow = cur.execute(sql_insert, (jenkinsjob, itm, jenkinsbuildnumber, tester, patchid, status, module))
            db.commit()
        except Exception as e:
            db.rollback()
            print(e)
        finally:
            db.close()
        return effectrow

    def updateJenkinsBuild(self, jenkinsjob, itm, jenkinsbuildnumber, status, module='00'):
        "更新本次构建的状态"
        try:
            db = self.getDbConnect()
            cur = db.cursor()
            # 更新构建状态
            update_insert = """update JENKINSBUILD set status=%s where JENKINSJOB=%s and ITM=%s and  JENKINSBUILDNUMBER=%s  and  MODULE=%s"""
            effectrow = cur.execute(update_insert, (status, jenkinsjob, itm, jenkinsbuildnumber, module))
            db.commit()
        except Exception as e:
            db.rollback()
            print(e)
        finally:
            db.close()
        return effectrow

    def beginJenkinsBuild(self, jenkinsjob, itm, jenkinsbuildnumber, tester, module='00'):
        """开始构建,status=2"""
        return self.insertJenkinsBuild(jenkinsjob, itm, jenkinsbuildnumber, tester, 1, '2', module)

    def jenkinsBuildSuccess(self, jenkinsjob, itm, jenkinsbuildnumber, moudle='00'):
        """构建成功,status=1"""
        return self.updateJenkinsBuild(jenkinsjob, itm, jenkinsbuildnumber, '1', moudle)

    def jenkinsBuildCancle(self, jenkinsjob, itm, jenkinsbuildnumber, module='00'):
        """构建取消,status=3,用于构建冲突,合并构建时自动取消"""
        return self.updateJenkinsBuild(jenkinsjob, itm, jenkinsbuildnumber, '3', module)

    def releaseJenkinsBuild(self, jenkinsjob, itm, module='00'):
        """发布时更新本次ITM单多次构建的所有的为已经发布"""
        sql_select = """select max(id) as patchid from JENKINSRELEASE  where JENKINSJOB=%s and itm  =%s and id>1 and MODULE=%s"""
        # 先更新所有对应的单为0
        sql_update0 = """update JENKINSBUILD SET PATCHID=0 WHERE JENKINSJOB=%s AND ITM=%s AND PATCHID=1 AND MODULE=%s """
        # 更新对应一个单为发布的记录
        sql_update = """update JENKINSBUILD JL,JENKINSRELEASE JR SET JL.PATCHID=JR.ID WHERE JL.JENKINSJOB=JR.JENKINSJOB AND JL.ITM=JR.ITM AND JL.JENKINSBUILDNUMBER=JR.JENKINSBUILDNUMBER AND JL.MODULE =JR.MODULE AND STATUS='1'AND JR.ID=%s """
        try:
            db = self.getDbConnect()
            cur = db.cursor()
            effectrow = cur.execute(sql_select, (jenkinsjob, itm, module))
            row = cur.fetchone()
            if effectrow == 0:
                return 1
            else:
                id = row[0]
            effectrow = cur.execute(sql_update0, (jenkinsjob, itm, module))
            if effectrow == 0:
                db.rollback()
                return 2
            effectrow = cur.execute(sql_update, (id,))
            if effectrow == 0:
                db.rollback()
                return 3
            db.commit()
        except Exception as e:
            db.rollback()
            print(e)
        finally:
            db.close()
        return 4

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

    def moveSVN(self, itm, itmurl):
        itmlist = itm.split('#')
        itmresult = []
        for item in itmlist:
            sitmurl = fp.urlJoin(itmurl, 'working', item)
            ditmurl = fp.urlJoin(itmurl, 'finished', item)
            svn_revision, errmsg = fp.runSVN(sitmurl, ditmurl, jenkinsconf.svnusr, jenkinsconf.svnpwd, 'move', item)
            itmresult.append((item, svn_revision, errmsg))
        return itmresult

    def logSVN(self, revision, svnurl, usr, passwd):
        """取指定revision的SVN日志,错误信息长度小于7"""
        params = ["svn"]
        params.extend(('log', svnurl))
        params.extend(("-r", revision))
        params.extend(("--username", usr))
        params.extend(("--password", passwd))
        params.extend(("--non-interactive", "--trust-server-cert", "-v"))
        msg = ''
        if is_py2:
            cp = subprocess.Popen(params, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            cp.wait()
            er = cp.stderr.read()
            s = cp.stdout.read()
            if er == '' and s != '':
                msg = s.decode('utf-8').split('\n')
            else:
                msg = parse(er).decode('utf-8').split('\n')  # .encode('utf-8')
        if is_py3:
            cp = subprocess.run(params, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if cp.returncode != 0:
                msg = parse(cp.stderr.decode('utf-8')).split('\n')
            elif cp.returncode == 0 and cp.stdout != b'':
                msg = cp.stdout.decode('utf-8').split('\n')
        return msg

    def compareSvnlogModify(self, svnlog, filename):
        """比较SVN日志与变更列表的
        参数svnlog从svn获取的日志

        参数filename变更列表文件"""
        f = open(filename, 'r')
        lines = f.readlines()
        nlines = []
        for item in lines:
            if item.strip() == '' or item[:2] == '--' or item[:1] == '#':
                pass  # 注释的行直接忽略
            else:
                nlines.append(item.strip())
        nlines = list(set(nlines))  # 去重
        projectname = ''
        if len(nlines) >= 1:
            projectname = nlines[0].split('/')[1]  # 取出变更列表文件的第一个目录名,即项目工程名
        nsvnlog = []
        for item in svnlog:
            index = item.find('/' + projectname + '/') if item.find('/' + projectname + '/') > 0 else -1
            if index==-1: #没有找到工程则跳过
                continue
            nsvnlog.append(item[index:])
        lineset = set(nlines)
        svnlogset = set(nsvnlog)
        print(Fore.CYAN+"变更列表文件数："+str(lineset.__len__())+" 受控成功文件数："+str(svnlogset.__len__()))
        df1=pd.DataFrame(lineset,columns=['nline'])
        df2 = pd.DataFrame(svnlogset, columns=['nsvnlog'])
        df = pd.merge(df1, df2, 'outer', left_on='nline', right_on='nsvnlog')
        diffset=df[(df["nline"].isna()) | (df["nsvnlog"].isna())]
        # diffset = lineset ^ svnlogset  # 对称差
        return diffset

    def urlJoin(self, baseurl, *path):
        """拼接生成url"""
        head = baseurl.split(":")[0]
        urllist = []
        if head not in ("http", "https", "svn"):
            return baseurl
        for item in path:
            if item[0] == '/':
                item = item[1:]
            if item[-1:] == '/':
                item = item[:-1]
            urllist.append(item)
        if baseurl[-1:] == '/':
            baseurl = baseurl[:-1]
        return baseurl + '/' + '/'.join(urllist)


def usage():
    print("""本脚本功能,用于控制jenkins流程,构建前先调用,判断是否有在测试中的ITM单,如果有则退出构建,如果没
            有则先写入流程为开始构建,然后进行构建,如果构建成功状态更新为成功,如果失败,状态保持为开始;
            构建结束后,发布补丁时再调用脚本更新状态为发布
            参数1(jenkinsjob) 
            参数2(本次构建的ITM单,多个单用#分隔,不能有空格) 
            参数3(构建号)
            参数4(测试人员)
            参数5(构建,1-开始构建 2-构建成功,3构建发布)
            参数6(受控码本地目录)
            参数7(受控码url)
            参数8(ITM working中变更单URL)
            参数9(合并后的变更列表,用于与受控的代码进行比较,保证受控的完整性)   
            JenkinsFlowProcess.py   xzrtmis path_hn_20180329_0001#path_hn_20180329_0002 113 张中华  3 /usr/local/jenkins_workspace/workspace/test-rest/finance-restn  https://10.168.1.112/svn/test/finance-rest https://10.168.1.112/svn/test/test
            /usr/local/jenkins_workspace/tools/JenkinsFlowProcess.py quartz-sync REQUEST_20190606_131312 16 林淑清 3 /usr/local/jenkins_workspace/workspace/quartz-sync/quartz-sync https://10.168.1.202/svn/01.产品and项目/20湖南财补/02湖南财政惠农补贴系统省集中项目/08受控代码/quartz-sync https://10.168.1.202/svn/01.产品and项目/20湖南财补/02湖南财政惠农补贴系统省集中项目/07分支管理/2019 /usr/local/jenkins_workspace/workspace/quartz-sync/BUILD43/路径说明quartz-sync.txt """)
    sys.exit(1)


if __name__ == "__main__":
    import jenkinsconf

    # 为了兼容少修改调用的,增加status为1,2时的module参数

    if (len(sys.argv) != 6 and len(sys.argv) != 7 and len(sys.argv) != 10 and len(sys.argv) != 11):
        usage()
    jenkinsjob = sys.argv[1]
    itm = sys.argv[2]
    jenkinsbuildnumber = sys.argv[3]
    tester = sys.argv[4]
    status = sys.argv[5]
    fp = FlowProcess()
    module = '00'
    if status == '1':
        if len(sys.argv) == 7:
            module = sys.argv[6]
        rows = fp.getBuildStatus(jenkinsjob, itm, module)
        if len(rows) > 0:
            unfinished = 0
            for jenkinsjob1, itm1, jenkinsbuildnumber1 in rows:
                if itm1 not in itm:
                    # 如果存在未发布的单没在本次的合并构建中则打印消息后退出,只是输出py2,py3的数据库查询结果不分开处理
                    print(Fore.RED + "【%s】工程【%s】单【%s】构建完成,未发布,不能进行新的构建!!" % (
                        jenkinsjob1.encode('utf-8'), itm1.encode('utf-8'), jenkinsbuildnumber1.encode('utf-8')))
                    unfinished += 1
            if unfinished > 0:
                # 存在着未发布的构建 ,直接退出

                sys.exit(1)
            for jenkinsjob1, itm1, jenkinsbuildnumber1 in rows:
                # if itm1  in itm:由于上一步控制,未发布的单肯定都在本次构建中,所以不用判断,直接取消未发布的单,进行合并发布
                effectcount = fp.jenkinsBuildCancle(jenkinsjob, itm1, jenkinsbuildnumber1, module)

                if effectcount == 1:
                    print(Fore.RED + "【%s】工程【%s】单【%s】构建,自动取消构建,合并到本次构建!!" % (
                        jenkinsjob1.encode('utf-8'), itm1.encode('utf-8'), jenkinsbuildnumber1.encode('utf-8')))
        # 没有未发布的单,则直接开始构建
        effectcount = fp.beginJenkinsBuild(jenkinsjob, itm, jenkinsbuildnumber, tester, module)
        if effectcount == 1:
            print(Fore.GREEN + "【%s】工程【%s】单构建开始!" % (jenkinsjob, itm))
        else:
            print(Fore.RED + "【%s】工程【%s】单开始构建失败,请检查,数据库连接是否正常!" % (jenkinsjob, itm))
            sys.exit(1)
    elif status == "2":
        if len(sys.argv) == 7:
            module = sys.argv[6]
        effectcount = fp.jenkinsBuildSuccess(jenkinsjob, itm, jenkinsbuildnumber, module)
        if effectcount == 1:
            print(Fore.GREEN + "【%s】工程【%s】单构建状态更新成功完成!" % (jenkinsjob, itm))
        else:
            print(Fore.RED + "【%s】工程【%s】单构建状态更新失败,请检查!" % (jenkinsjob, itm))
    elif status == "3":  # 移发布的ITM单,签入SVN代码到受控,更新发布状态
        if (len(sys.argv) != 10 and len(sys.argv) != 11):
            usage()
        try:
            # 移ITM单
            path = sys.argv[6]
            svnurl = sys.argv[7]
            itmurl = sys.argv[8]
            filename = sys.argv[9]  # 合并后的变更列表文件
            if len(sys.argv) == 11:
                module = sys.argv[10]
            if os.path.isdir(path):
                print(Fore.CYAN + "***开始受控代码***")
                svn_revision, errmsg = fp.runSVN(path, '', jenkinsconf.svnusr, jenkinsconf.svnpwd, 'commit', itm)
                if errmsg != '':
                    print(Fore.RED + "受控代码失败!【%s】" % errmsg)
                    sys.exit(1)
                if svn_revision == 0:
                    print(Fore.RED + "警告:没有受控到代码,请检查，确认变更列表文件!!,revision【%s】" % svn_revision)
                else:
                    print(Fore.GREEN + "受控成功,revision【%s】" % svn_revision)
                if svn_revision != 0:  # 有受控代码则进行受控与实例的比较
                    print(Fore.CYAN + "***开始检查受控代码,如果检查结果不正确请根据实际情况核对***")
                    msg = fp.logSVN(str(svn_revision), svnurl, jenkinsconf.svnusr, jenkinsconf.svnpwd)
                    if len(msg) <= 6:
                        print(Fore.RED + "取受控日志失败!【%s】" % msg[0])
                    else:
                        msg = msg[3:-4]
                        diffset = fp.compareSvnlogModify(msg, filename)  # 比较变更列表清单与受控结果
                        if len(diffset) > 0:
                            print(Fore.RED + "受控代码与变更列表文件不一致,请检查是否有问题....")
                            for i in range(len(diffset)):
                                print(Fore.RED +"变更列表与SVN受控差异"+str(diffset.iloc[i]["nline"])+' , '+ str(diffset.iloc[i]["nsvnlog"]))
                            #
                            # for item in diffset:
                            #     print(Fore.RED + "差异文件【%s】" % item)
            else:
                print(Fore.RED + "受控代码失败!本地路径不正确【%s】" % path)
                sys.exit(1)
            print(Fore.RED + "***由于一个ITM单下可能存在多个的工程代码,请全部发布后手动把ITM单移到finished目录下***,")
            # itmresult = fp.moveSVN(itm, itmurl)
            # i = 0
            # for itmno, revision, errmsg in itmresult:
            #     if errmsg != '':
            #         print(Fore.RED + "移动ITM单失败!【%s】,原因【%s】" % (itmno, errmsg))
            #         i += 1
            #     else:
            #         print(Fore.GREEN + "移动ITM单成功【%s】,revision【%s】" % (itmno, revision))
            # if i > 0:
            #     print(Fore.RED + "移动ITM单,失败总数【%s】个,退出发布" % i)
            #     sys.exit(1)
            print(Fore.CYAN + "开始修改流程状态...")
            effectcount = fp.releaseJenkinsBuild(jenkinsjob, itm, module)
            if effectcount == 1:
                print(Fore.RED + "【%s】工程【%s】单,找不到发布记录,请检查看发布记录" % (jenkinsjob, itm))
                sys.exit(1)
            elif effectcount == 2:
                print(Fore.RED + "【%s】工程【%s】单,找不到此单构建完成未发布记录,请检查构建记录" % (jenkinsjob, itm))
                sys.exit(1)
            elif effectcount == 3:
                print(Fore.RED + "【%s】工程【%s】更新构建状态失败,请检查!" % (jenkinsjob, itm))
                sys.exit(1)
            else:
                print(Fore.GREEN + "【%s】工程【%s】单发布成功,请检查!" % (jenkinsjob, itm))

        except Exception as e:
            print(e)
            traceback.print_exc()
