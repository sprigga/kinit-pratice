# -*- coding: utf-8 -*-
# @version        : 1.0
# @Update Time    : 2023/8/18 9:00
# @File           : database.py
# @IDE            : PyCharm
# @desc           : SQLAlchemy 部分

"""
导入 SQLAlchemy 部分
安装： pip install sqlalchemy[asyncio]
官方文檔：https://docs.sqlalchemy.org/en/20/intro.html#installation
"""
from typing import AsyncGenerator
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, declared_attr
from application.settings import SQLALCHEMY_DATABASE_URL, REDIS_DB_ENABLE, MONGO_DB_ENABLE
from fastapi import Request
from core.exception import CustomException
from motor.motor_asyncio import AsyncIOMotorDatabase

# 官方文檔：https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html#sqlalchemy.ext.asyncio.create_async_engine

# database_url  dialect+driver://username:password@host:port/database

# echo：如果為True，引擎将记錄所有语句以及它们的参數列表的repr()到默认的日誌处理程序，該处理程序默认為sys.stdout。如果设置為字符串"debug"，
# 结果行也将打印到標准输出。Engine的echo属性可以随時修改以打开和关闭日誌记錄；也可以使用標准的Python logging模块来直接控制日誌记錄。

# echo_pool=False：如果為True，连接池将记錄信息性输出，如何時使连接失效以及何時将连接回收到默认的日誌处理程序，該处理程序默认為sys.stdout。
# 如果设置為字符串"debug"，记錄将包括池的检出和检入。也可以使用標准的Python logging模块来直接控制日誌记錄。

# pool_pre_ping：布尔值，如果為True，将启用连接池的"pre-ping"功能，該功能在每次检出時测试连接的活動性。

# pool_recycle=-1：此设置导致池在给定的秒數后重新使用连接。默认為-1，即没有超時。例如，将其设置為3600意味着在一小時后重新使用连接。
# 請注意，特别是MySQL會在检测到连接8小時内没有活動時自動断开连接（尽管可以通過MySQLDB连接自身和服務器配置進行配置）。

# pool_size=5：在连接池内保持打开的连接數。与QueuePool以及SingletonThreadPool一起使用。
# 對于QueuePool，pool_size设置為0表示没有限制；要禁用连接池，請将poolclass设置為NullPool。

# pool_timeout=30：在从池中獲取连接之前等待的秒數。仅在QueuePool中使用。这可以是一个浮点數，但受Python時間函數的限制，可能在几十毫秒内不可靠

# max_overflow 参數用于配置连接池中允许的连接 "溢出" 數量。这个参數用于在高负載情况下处理连接請求的峰值。
# 當连接池的所有连接都在使用中時，如果有新的连接請求到达，连接池可以創建额外的连接来满足这些請求，最多創建的數量由 max_overflow 参數决定。

# 創建數據庫连接
async_engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=False,
    echo_pool=False,
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_size=5,
    max_overflow=5,
    connect_args={}
)

# 創建數據庫會話
session_factory = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=async_engine,
    expire_on_commit=True,
    class_=AsyncSession
)


class Base(AsyncAttrs, DeclarativeBase):
    """
    創建基本映射类
    稍后，我们将继承該类，創建每个 ORM 模型
    """

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """
        将表名改為小写
        如果有自定义表名就取自定义，没有就取小写类名
        """
        table_name = cls.__tablename__
        if not table_name:
            model_name = cls.__name__
            ls = []
            for index, char in enumerate(model_name):
                if char.isupper() and index != 0:
                    ls.append("_")
                ls.append(char)
            table_name = "".join(ls).lower()
        return table_name


async def db_getter() -> AsyncGenerator[AsyncSession, None]:
    """
    獲取主數據庫會話

    數據庫依赖項，它将在單個請求中使用，然后在請求完成后将其关闭。

    函數的返回類型被注解為 AsyncGenerator[int, None]，其中 AsyncSession 是生成的值的類型，而 None 表示异步生成器没有终止條件。
    """
    async with session_factory() as session:
        # 創建一个新的事務，半自動 commit
        async with session.begin():
            yield session


def redis_getter(request: Request) -> Redis:
    """
    獲取 redis 數據庫對象

    全局挂載，使用一个數據庫對象
    """
    if not REDIS_DB_ENABLE:
        raise CustomException("請先配置Redis數據庫链接並启用！", desc="請启用 application/settings.py: REDIS_DB_ENABLE")
    return request.app.state.redis


def mongo_getter(request: Request) -> AsyncIOMotorDatabase:
    """
    獲取 mongo 數據庫對象

    全局挂載，使用一个數據庫對象
    """
    if not MONGO_DB_ENABLE:
        raise CustomException(
            msg="請先開啟 MongoDB 數據庫連接！",
            desc="請啟用 application/settings.py: MONGO_DB_ENABLE"
        )
    return request.app.state.mongo
