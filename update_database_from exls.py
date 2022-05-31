# coding:utf-8
import csv
import cx_Oracle


def update():
    con = cx_Oracle.connect("CRTMIS/CRTMIS@10.168.6.33:1521/CRTMISGZ")
    # 创建一个游标对象
    cur = con.cursor()
    # 使用execute执行sql语句
    sql = '''update td_bs_elicence_busi_config t set t.change_reason_code='',t.change_detail='' where t.busi_code='' '''
    result = cur.execute(sql)
    # 使用fetchall()获取所有数据，并将结果打印出来
    print(cur.fetchall())
    con.commit()
    cur.close()
    con.close()


def get_list_form_csv(file_path, headless=False):
    result_list = []
    with open(file_path, 'r', encoding='utf-8') as fp:
        csv_f = csv.reader(fp)
        for item in csv_f:
            result_list.append(item)
    if headless:
        result_list.pop(0)
    return result_list


if __name__ == '__main__':
    row_list = get_list_form_csv('RAW.CSV')
    con = cx_Oracle.connect("CRTMIS/CRTMIS@10.168.6.33:1521/CRTMISGZ")
    # 创建一个游标对象
    cur = con.cursor()
    for row in row_list:
        # 使用execute执行sql语句
        sql = '''update td_bs_elicence_busi_config t set t.change_reason_code='{}',t.change_detail='{}' where t.busi_code='{}' '''.format(
            row[1], row[2], row[0])
        result = cur.execute(sql)
        con.commit()
    cur.close()
    con.close()
