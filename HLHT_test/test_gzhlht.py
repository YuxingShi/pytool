# coding:utf-8
import pytest
from database import Oracle


class TestHlht:
    db = None
    test_items = None

    def setup(self):
        self.db = Oracle(user='CRTMIS', passwd='CRTMIS', tsn='10.168.6.8:1521/GZRTMIS')
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
            intf_name, intf_code, intf_sql = item[0], item[1], str(item[6])
            print('开始校验', intf_name, intf_code, 'sql语句执行结果……')
            if intf_sql is None or intf_sql == '':
                print('校验结果', intf_name, intf_code, 'sql语句未配置！')
                failure_count += 1
                continue
            data_tup = self.db.execute_sql(intf_sql, field_title=False, rownum=5000)
            if data_tup is None:
                print('校验结果', intf_name, intf_code, 'sql:\n{}\n查询报错！'.format(intf_sql))
                failure_count += 1
            elif len(data_tup) > 0:
                print('校验结果', intf_name, intf_code, '校验通过！')
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
            intf_name, intf_code, intf_sql = item[0], item[1], str(item[6])
            print('开始校验', intf_name, intf_code, 'sql语句执行结果……')
            if intf_sql is None or intf_sql == '':
                print('校验结果', intf_name, intf_code, 'sql语句未配置！')
                failure_count += 1
                continue
            field_list, data_tup = self.db.execute_sql(intf_sql, field_title=True, rownum=1)
            if data_tup is None:
                print('校验结果', intf_name, intf_code, 'sql:\n{}\n查询报错！'.format(intf_sql))
                failure_count += 1
            elif len(data_tup) > 0:
                print('校验结果', intf_name, intf_code, '校验通过！')
                success_count += 1
            elif data_tup is None:
                print('校验结果', intf_name, intf_code, '查询返回None')
                failure_count += 1
            else:
                print('校验结果', intf_name, intf_code, 'sql语句执行查询结果为空！')
                failure_count += 1
        assert failure_count == 0

if __name__ == '__main__':
    pytest.main(["-s", "test_gzhlht.py", "--html=report/test_one_func.html"])


