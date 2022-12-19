# coding: utf-8 -*-
import time
from datetime import datetime

import cx_Oracle


class Oracle(object):

    def __init__(self, user: str, passwd: str, tsn: str):
        self._user = user
        self._passwd = passwd
        self._oracle_tsn = tsn
        self._database_connect = None
        self._cursor = None
        self._connect_database_server()

    def _connect_database_server(self) -> None:
        self._database_connect = cx_Oracle.connect(self._user, self._passwd, self._oracle_tsn)
        self._cursor = self._database_connect.cursor()

    def close_connect(self) -> None:
        self._cursor.close()
        self._database_connect.close()
        self._cursor = None
        self._database_connect = None

    def _verify_connection(self) -> None:
        ret = False
        try:
            self._database_connect.ping()
            ret = True
        except Exception as err:
            self.close_connect()
            self._connect_database_server()
        return ret

    def execute_sql(self, sql: str, field_title=True, rownum=None):
        """
        sql语句执行
        :param sql: 查询语句
        :param field_title: 是否返回字段标题
        :return:
        """
        try:
            if rownum:
                sql = sql + '\nand rownum<{}'.format(rownum)
            self._cursor.execute(sql)
            data_tup = self._cursor.fetchall()
            if field_title:
                field_list = [field[0] for field in self._cursor.description]
                return field_list, data_tup
            else:
                return data_tup
        except Exception as e:
            self._database_connect.rollback()
            print(str(e))

    def test(self):
        sql = '''select * from TF_BS_HLHTDATA_EX '''
        title, data_tup = self.execute_sql(sql)
        for row in data_tup:
            if type(row[6]) is cx_Oracle.LOB:
                c_sql = str(row[6])
                print(self.execute_sql(c_sql))


if __name__ == "__main__":
    me = Oracle(user='CRTMIS', passwd='CRTMIS', tsn='10.168.6.8:1521/GZRTMIS')
    sql = '''
SELECT A.LINPERREG_ID,
       SUBSTR(A.DOCDEPCODE, 0, 2) || '0000' AS PROVINCECODE,
       A.LINPERREG_ID OPERLINEID,
       T1.LINE_NAME OPERLINENAME,
       A.OWNER_ID OWNERID,
       CRTMIS.GETDATADICT('LINTYPE', T1.LINTYPE) LINEOPTYPE,
       T1.LINTYPE LINEOPTYPECODE,
       T1.STADEPOT STARTSTATIONZONE,
       CRTMIS.F_GET_DEPOTNAME(T1.STADEPOT) STARTSTATION,
       CRTMIS.F_GET_DEPOTNAME(T1.ENDDEPOT) ENDSTATION,
       T1.ENDDEPOT ENDSTATIONZONE,
       T1.BERTH LINETRANSPLACE,
       T1.TIMES || '次/' || A.DAYS || '日' LINEFREQUENCY,
       T1.SUMMIL LINEMILEAGE,
       T1.HEIMIL LINEEXPRESSWAYMILEAGE,
       T1.BUSAREA LINEAREACODE,
       CRTMIS.GETDATADICT('BUSAREA', T1.BUSAREA) LINEAREA,
       A.IS_COUNTRY COUNTRYSIDEFLAG,
       CRTMIS.GETDATADICT('LINESTATUS', A.LINESTATUS) LINEOPSTATUS,
       A.LINESTATUS LINEOPSTATUSCODE,
       REPLACE(T1.STADATE, '-', '') LINEVALIDBEGIN,
       REPLACE(T1.ENDDATE, '-', '') LINEVALIDEND,
       REPLACE(A.CREDATE, '-', '') ISSUEDATE,
       SUBSTR(to_char(A.SYSOPERTIME), 0, 14) BUSINESSCOMPLETIONTIME,
       SUBSTR(TO_CHAR(A.SYSOPERTIME), 0, 14) AS OPERTIME,
       DECODE(A.HLHT_OPERTYPE, NULL, '2', A.HLHT_OPERTYPE) OPERTYPE
  FROM CRTMIS.TF_BS_LINPERREG A
  LEFT JOIN CRTMIS.TF_BS_PERMIT_LINCARD T1
    ON A.LINPERREG_ID = T1.LINPERREG_ID
  LEFT JOIN CRTMIS.TF_EV_APPLINPER A
    ON A.PER_ID = A.PER_ID
 WHERE A.DOCDEPCODE IS NOT NULL
   AND A.LINPERREG_ID IS NOT NULL
    '''
    print(me.execute_sql(sql))

