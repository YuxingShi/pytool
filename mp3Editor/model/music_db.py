# coding:utf-8
from mp3Editor.utils.database import SQLiteDB


class MusicDB(object):

    def __init__(self, db_path: str):
        self.db = SQLiteDB(db_path)
        self.db.connect()

    def get_data_dict(self):
        sql = '''select classify, code, name from t_data_dict '''
        data_tuple = self.db.execute_query(sql)
        result_dict = {}
        for item in data_tuple:
            if len(item) != 3:
                raise Exception('查询结果列不等于3，无法生成字典数据')
            key = item[0].upper()
            if result_dict.get(key) is None:
                result_dict[key] = {item[1]: item[2]}
            else:
                result_dict.get(key).update({item[1]: item[2]})
        return result_dict

    def get_singer_id(self, name):
        sql = '''select id from t_singer where name='{}' '''.format(name)
        result = self.db.execute_query(sql)
        if result:
            return result[0][0]
        else:
            return None

    def get_album_year(self, singer_name: str, album_name: str):
        sql = '''
         select year
            from t_album t1
                     left join t_singer t2 on t1.singer = t2.id
            where t2.name = '{}'
              and t1.name = '{}'
         '''.format(singer_name, album_name)
        data_tuple = self.db.execute_query(sql)
        if data_tuple:
            return data_tuple[0][0]
        else:
            return '未知'

    def insert_album(self, name, singer, year, pub_date):
        singer_id = self.get_singer_id(singer)
        if singer_id:
            sql = '''insert into t_album(name, singer, year, publish_date)values ('{}', {}, {}, '{}') '''.format(name, singer_id, year, pub_date)
            return self.db.execute_update(sql)


if __name__ == '__main__':
    db = MusicDB('E:\PyCharmProj\pytool\mp3Editor\music.sqlite')
    # print(db.get_album_year('陈粒', '如也'))
    print(db.insert_album('如也', '陈粒', '2015'))
