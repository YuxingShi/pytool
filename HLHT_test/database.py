# coding: utf-8 -*-
import time
import json
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
                sql = sql + '\nand rownum<={}'.format(rownum)
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
    db = Oracle(user='CRTMIS', passwd='CRTMIS', tsn='10.168.6.33:1521/CRTMISGZ')

    hlht_data_sql = '''select INPUT from TF_BS_HLHTDATA_RB where intf_code='{}' '''.format('RB0107')
    data_tup = db.execute_sql(hlht_data_sql, field_title=False, rownum=1)
    if data_tup:
        input_str = data_tup[0][0]
        input_dict = json.loads(input_str)
        body_str = input_dict.get('body')
        body_dict = json.loads(body_str)
        req_info = body_dict.get('reqInfo')
        print(req_info.keys())

