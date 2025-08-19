#!/usr/bin/python
# -*- coding: utf-8 -*-
# @version        : 1.0
# @Create Time    : 2023/5/6 9:29
# @File           : task.py
# @IDE            : PyCharm
# @desc           : 任務基礎类

import re
import pymysql
from application.settings import SQLALCHEMY_DATABASE_URL
from core.logger import logger


class DBGetter:

    def __init__(self):
        self.mysql_cursor = None
        self.mysql_conn = None

    def conn_mysql(self) -> None:
        """
        连接系统中配置的 mysql 數據庫
        """
        try:
            connection_string = SQLALCHEMY_DATABASE_URL.split("//")[1]
            pattern = r'^(?P<username>[^:]+):(?P<password>[^@]+)@(?P<host>[^:/]+):(?P<port>\d+)/(?P<database>[^/]+)$'
            match = re.match(pattern, connection_string)

            username = match.group('username')
            password = match.group('password')
            host = match.group('host')
            port = int(match.group('port'))
            database = match.group('database')

            self.mysql_conn = pymysql.connect(
                host=host,
                port=port,
                user=username,
                password=password,
                database=database
            )
            self.mysql_cursor = self.mysql_conn.cursor()
        except pymysql.err.OperationalError as e:
            logger.error(f"數據庫連接失敗，{e}")
            raise ValueError("數據庫連接失敗！")
        except AttributeError as e:
            logger.error(f"數據庫連接解析失敗，{e}")
            raise ValueError("數據庫連接解析失敗！")

    def close_mysql(self) -> None:
        """
        关闭 mysql 链接
        """
        try:
            self.mysql_cursor.close()
            self.mysql_conn.close()
        except AttributeError as e:
            logger.error(f"未連接數據庫，無須關閉！，{e}")
            raise ValueError("未連接數據庫，無須關閉！")


if __name__ == '__main__':
    t = DBGetter()
    t.conn_mysql()
    t.close_mysql()
