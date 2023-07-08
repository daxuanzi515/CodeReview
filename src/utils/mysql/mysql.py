import pymysql
from src.config.config import Config
# 建议不要用QtSql,会出很多问题,建议直接用pymysql！pip install pymysql
# qt5.15.2

class SQL:
    def __init__(self, config_ini):
        super(SQL, self).__init__()
        self.config_ini = config_ini

        self.host = self.config_ini['mysql']['db_host']
        self.port = self.config_ini['mysql']['db_port']
        self.port = int(self.port)
        self.username = self.config_ini['mysql']['db_username']
        self.password = self.config_ini['mysql']['db_password']
        self.dbname = self.config_ini['mysql']['db_name']
        self.db = None
        self.cursor = None

    def connect_db(self):
        self.db = pymysql.connect(host=self.host,
                                  port=self.port,
                                  user=self.username,
                                  password=self.password,
                                  db=self.dbname,
                                  charset="utf8")
        self.cursor = self.db.cursor()

    def close_db(self):
        self.db.close()
        self.cursor.close()

    def execute_query(self, query):
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def execute_command(self, command, values=None):
        if values:
            self.cursor.execute(command, values)
        else:
            self.cursor.execute(command)
        self.db.commit()

    # 通过字典方式插入数据
    def insert(self, table_name, data):
        keys = ', '.join(data.keys())
        values = ', '.join(['%s'] * len(data))
        query = f"INSERT INTO {table_name} ({keys}) VALUES ({values})"
        self.execute_command(query, tuple(data.values()))

    def update(self, table_name, data, condition):
        set_query = ', '.join([f"{key} = %s" for key in data])
        query = f"UPDATE {table_name} SET {set_query} WHERE {condition}"
        self.execute_command(query, tuple(data.values()))

    def delete(self, table_name, condition):
        query = f"DELETE FROM {table_name} WHERE {condition}"
        self.execute_command(query)

    def select(self, table_name, columns, condition):
        query = f"SELECT {columns} FROM {table_name}"
        if condition:
            query += f" WHERE {condition}"
        return self.execute_query(query)



# if __name__ == '__main__':
#
    #
    # # dict = {'id':'10000222','username':'uiuiui','password':'1234556','salt':b'\0x...','private_key':str(random.randint(0,10000))}
    # # 插入数据
    # data = {'id': '100'+str(random.randint(0, 10000)), 'username': 'xiaohong', 'password': '909090', 'private_key':str(random.randint(0, 10000))}
    # sql_obj.insert('user', data)
    #
    # # # 更新数据
    # # data = {'username': 'xiaohuang', 'password': '123123'}
    # # condition = "username = 'xiaohong'"
    # # sql_obj.update('user', data, condition)
    # #
    # # 删除数据
    # condition = "username = 'xiaohong'"
    # sql_obj.delete('user', condition)
    #
    # # 查询数据
    # columns = '*'
    # # condition = "username = 'xiaohuang'"
    # result = sql_obj.select('user', columns, condition = '')
    # print('查看更新数据')
    # for row in result:
    #     print(row)

    # sql_obj.close_db()
