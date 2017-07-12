# -*-coding:utf-8-*-

from sqlalchemy import create_engine


class MySQLClient(object):

    def __init__(self, host, port, username, password, db, charset='utf8'):
        """ 初始化MySQL客户端连接池

        :参数 host: MySQL服务器地址
        :参数 port: MySQL服务器端口
        :参数 username: MySQL数据库用户名
        :参数 password: MySQL数据库密码
        :参数 db: MySQL数据库名
        :参数 charset: 连接MySQL使用的字符集，默认: utf8
        """

        self.engine = create_engine(
            "mysql://" + username + ":" + password + "@" + host + ":" + str(port) + "/" + db + "?charset=" + charset,
            pool_size = 50,
            pool_recycle = 60,
            strategy = 'threadlocal'
        )


    def query(self, sql):
        """ 数据库DQL语句

        :参数 sql: 指定查询数据库的SQL语句
        :返回: 查询的行数, 查询的数据
        """

        cursor = self.engine.execute(sql)
        rows = cursor.rowcount
        data = cursor.fetchall()
        cursor.close()
        
        return rows, data


    def modify(self, sql):
        """ 数据库DML语句

        :参数 sql: 指定修改数据库的SQL语句
        :返回: 被修改的行数, 主键id
        """

        self.engine.begin()

        try:
            cursor = self.engine.execute(sql)
            rows = cursor.rowcount
            pkid = cursor.lastrowid
        
        except:
            self.engine.rollback()
        
        else:
            self.engine.commit()

        cursor.close()
        
        return rows, pkid


if __name__ == "__main__":
    mysql = MySQLClient(host="127.0.0.1", port=3306, username="test", password="test", db="test")
    mysql.query("SELECT 1+1")
    mysql.modify("INSERT INTO test (id, name) VALUES (1, 'test')")
    mysql.modify("UPDATE test set name='test1' WHERE id = 1")
    mysql.modify("DELETE FROM test WHERE id = 1")



