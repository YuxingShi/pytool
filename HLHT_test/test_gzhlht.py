# coding:utf-8
import re
import json
import pytest
from database import Oracle


class TestHlht:
    db = None
    test_items = None

    def setup(self):
        # self.db = Oracle(user='CRTMIS', passwd='CRTMIS', tsn='10.168.6.33:1521/CRTMISGZ')
        self.db = Oracle(user='CRTMIS', passwd='JLCRTMIS', tsn='10.168.1.54:1521/JLCS')
        # self.db = Oracle(user='CRTMIS', passwd='CRTMIS', tsn='10.168.7.54:1521/HNYZ')
        # self.db = Oracle(user='HYT2LINEFJ', passwd='HYT2LINEFJ', tsn='10.168.7.79:1521/FJYZ')
        sql = '''select * from TF_BS_HLHTDATA_EX '''
        self.test_items = self.db.execute_sql(sql, field_title=False)

    def teardown(self):
        self.db.close_connect()

    def test_request_gram_fields_config(self):
        """
        测试接口请求报文配置表
        :return:
        """
        success_count = 0
        failure_count = 0
        for item in self.test_items:
            intf_name, intf_code = item[0], item[1]
            sql = '''select * from TF_BS_HLHTDATA_FIELD_CONFIG where intf_code='{}' '''.format(intf_code)
            data_tup = self.db.execute_sql(sql, field_title=False)
            if data_tup is None:
                print(intf_name, intf_code, '查询报错！')
                failure_count += 1
                continue
            if len(data_tup) > 0:
                success_count += 1
            else:
                print(intf_name, intf_code, '表【TF_BS_HLHTDATA_FIELD_CONFIG】请求报文配置不存在！')
                failure_count += 1
        assert failure_count == 0

    def test_sql_execute_result(self):
        """
        sql 语句执行结果校验
        :return:
        """
        success_count = 0
        failure_count = 0
        for item in self.test_items:
            intf_name, intf_code, intf_sql = item[0], item[1], str(item[3])
            print('开始校验', intf_name, intf_code, 'sql语句执行结果')
            if intf_sql is None or intf_sql == '':
                print('校验结果', intf_name, intf_code, 'sql语句未配置！')
                failure_count += 1
                continue
            data_tup = self.db.execute_sql(intf_sql, field_title=False, rownum=5000)
            if data_tup is None:
                print('校验结果', intf_name, intf_code, 'sql:\n{}\n查询报错！'.format(intf_sql))
                failure_count += 1
            elif len(data_tup) > 0:
                # print('校验结果', intf_name, intf_code, '校验通过！')
                success_count += 1
            elif data_tup is None:
                print('校验结果', intf_name, intf_code, '查询返回None')
                failure_count += 1
            else:
                print('校验结果', intf_name, intf_code, 'sql语句执行查询结果为空！')
                failure_count += 1
        assert failure_count == 0

    def test_sql_execute_result_field_check(self):
        """
        sql 语句执行结果字段校验
        :return:
        """
        success_count = 0
        failure_count = 0
        for item in self.test_items:
            intf_name, intf_code, intf_sql = item[0], item[1], str(item[3])
            hlht_data_field_sql = '''select field from TF_BS_HLHTDATA_FIELD_CONFIG where intf_code='{}' '''.format(
                intf_code)
            config_data_field_tup = self.db.execute_sql(hlht_data_field_sql, field_title=False)
            config_field_list = [field[0] for field in config_data_field_tup]
            if intf_code.startswith('RA'):
                hlht_data_sql = '''select INPUT from TF_BS_HLHTDATA_RA where intf_code='{}' '''.format(intf_code)
            elif intf_code.startswith('RB'):
                hlht_data_sql = '''select INPUT from TF_BS_HLHTDATA_RB where intf_code='{}' '''.format(intf_code)
            elif intf_code.startswith('RC'):
                hlht_data_sql = '''select INPUT from TF_BS_HLHTDATA_RC where intf_code='{}' '''.format(intf_code)
            elif intf_code.startswith('RE'):
                hlht_data_sql = '''select INPUT from TF_BS_HLHTDATA_RE where intf_code='{}' '''.format(intf_code)
            elif intf_code.startswith('RJ'):
                hlht_data_sql = '''select INPUT from TF_BS_HLHTDATA_RJ where intf_code='{}' '''.format(intf_code)
            else:
                failure_count += 1
                return
            data_tup = self.db.execute_sql(hlht_data_sql, field_title=False, rownum=1)
            if data_tup:
                input_str = data_tup[0][0]
                input_dict = json.loads(input_str)
                body_str = input_dict.get('body')
                body_dict = json.loads(body_str)
                req_info = body_dict.get('reqInfo')
                req_info_keys = list(req_info.keys())
                for key in req_info_keys:
                    if key not in config_field_list:
                        print('【{}】【{}】请求报文中不存在配置的关键字【{}】【{}】'.format(intf_name, intf_code, key, input_str))
                        failure_count += 1
                for key in config_field_list:
                    if key not in req_info_keys:
                        if key == 'reqInfo':
                            continue
                        print('【{}】【{}】配置的关键字【{}】不在请求的报文中【{}】'.format(intf_name, intf_code, key, input_str))
                        failure_count += 1
        assert failure_count == 0


if __name__ == '__main__':
    pytest.main(["-s", "test_gzhlht.py", "--html=report/test_one_func.html"])


