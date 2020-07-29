import pymysql


class Mysqlhelper():
    # 需要有Mysql的连接
    # 还需要cursor游标
    def __init__(self):
        self.conn = pymysql.connect(host='localhost',port = 3306,
                                    user='root', password='123456 ',
                                    db='spider', charset='utf8')
        self.cursor =self.conn.cursor()

    def execute_modify_sql(self,sql,data):
        self.cursor.execute(sql,data)
        self.conn.commit()

    def __del__(self):
        self.cursor.close()
        self.conn.close()

