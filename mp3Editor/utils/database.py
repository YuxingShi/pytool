# encoding: utf-8
import sqlite3


class SQLiteDB:
    def __init__(self, db_file):
        self.db_file = db_file
        self.connection = None

    def connect(self):
        try:
            self.connection = sqlite3.connect(self.db_file)
            print("成功连接到数据库")
        except sqlite3.Error as e:
            print("连接到数据库失败:", e)

    def close(self):
        if self.connection:
            self.connection.close()
            print("数据库连接已关闭")

    def execute_query(self, query):
        result_set = []
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            result_set = cursor.fetchall()
            cursor.close()
        except sqlite3.Error as e:
            print("执行查询失败:", e)

        return result_set

    def execute_update(self, query):
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            self.connection.commit()
            cursor.close()
            # print("执行更新成功")
            return True
        except sqlite3.Error as e:
            print("执行更新失败:", e)
            return False

