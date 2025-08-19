#!/usr/bin/python
# -*- coding: utf-8 -*-
# @version        : 1.0
# @Create Time    : 2022/3/21 11:03 
# @File           : event.py
# @IDE            : PyCharm
# @desc           : 全局事件


from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from application.settings import REDIS_DB_URL, MONGO_DB_URL, MONGO_DB_NAME, EVENTS
from utils.cache import Cache
from redis import asyncio as aioredis
from redis.exceptions import AuthenticationError, TimeoutError, RedisError
from contextlib import asynccontextmanager
from utils.tools import import_modules_async
from sqlalchemy.exc import ProgrammingError
from core.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):

    await import_modules_async(EVENTS, "全局事件", app=app, status=True)

    yield

    await import_modules_async(EVENTS, "全局事件", app=app, status=False)


async def connect_redis(app: FastAPI, status: bool):
    """
    把 redis 挂載到 app 對象上面

    博客：https://blog.csdn.net/wgPython/article/details/107668521
    博客：https://www.cnblogs.com/emunshe/p/15761597.html
    官网：https://aioredis.readthedocs.io/en/latest/getting-started/
    Github: https://github.com/aio-libs/aioredis-py

    aioredis.from_url(url, *, encoding=None, parser=None, decode_responses=False, db=None, password=None, ssl=None,
    connection_cls=None, loop=None, **kwargs) 方法是 aioredis 庫中用于从 Redis 连接 URL 創建 Redis 连接對象的方法。

    以下是該方法的参數说明：
    url：Redis 连接 URL。例如 redis://localhost:6379/0。
    encoding：可選参數，Redis 编碼格式。默认為 utf-8。
    parser：可選参數，Redis 數據解析器。默认為 None，表示使用默认解析器。
    decode_responses：可選参數，是否将 Redis 响应解碼為 Python 字符串。默认為 False。
    db：可選参數，Redis 數據庫編號。默认為 None。
    password：可選参數，Redis 認證密碼。默认為 None，表示無需認證。
    ssl：可選参數，是否使用 SSL/TLS 加密连接。默认為 None。
    connection_cls：可選参數，Redis 连接类。默认為 None，表示使用默认连接类。
    loop：可選参數，用于創建连接對象的事件循环。默认為 None，表示使用默认事件循环。
    **kwargs：可選参數，其他连接参數，用于傳递给 Redis 连接类的构造函數。

    aioredis.from_url() 方法的主要作用是将 Redis 连接 URL 转换為 Redis 连接對象。
    除了 URL 参數外，其他参數用于指定 Redis 连接的各种選項，例如 Redis 數據庫編號、密碼、SSL/TLS 加密等等。可以根據需要選擇使用这些選項。

    health_check_interval 是 aioredis.from_url() 方法中的一个可選参數，用于设置 Redis 连接的健康检查間隔時間。
    健康检查是指在 Redis 连接池中使用的连接對象會定期向 Redis 服務器發送 PING 命令来检查连接是否仍然有效。
    該参數的默认值是 0，表示不進行健康检查。如果需要启用健康检查，则可以将該参數设置為一个正整數，表示检查間隔的秒數。
    例如，如果需要每隔 5 秒對 Redis 连接進行一次健康检查，则可以将 health_check_interval 设置為 5
    :param app:
    :param status:
    :return:
    """
    if status:
        rd = aioredis.from_url(REDIS_DB_URL, decode_responses=True, health_check_interval=1)
        app.state.redis = rd
        try:
            response = await rd.ping()
            if response:
                print("Redis 連接成功")
            else:
                print("Redis 連接失敗")
        except AuthenticationError as e:
            raise AuthenticationError(f"Redis 連接認證失敗，用户名或密碼錯誤: {e}")
        except TimeoutError as e:
            raise TimeoutError(f"Redis ＝連接超時，地址或者端口錯誤: {e}")
        except RedisError as e:
            raise RedisError(f"Redis 連接失敗: {e}")
        try:
            await Cache(app.state.redis).cache_tab_names()
        except ProgrammingError as e:
            logger.error(f"sqlalchemy.exc.ProgrammingError: {e}")
            print(f"sqlalchemy.exc.ProgrammingError: {e}")
    else:
        print("Redis 連接關閉")
        await app.state.redis.close()


async def connect_mongo(app: FastAPI, status: bool):
    """
    把 mongo 挂載到 app 對象上面

    博客：https://www.cnblogs.com/aduner/p/13532504.html
    mongodb 官网：https://www.mongodb.com/docs/drivers/motor/
    motor 文檔：https://motor.readthedocs.io/en/stable/
    :param app:
    :param status:
    :return:
    """
    if status:
        client: AsyncIOMotorClient = AsyncIOMotorClient(
            MONGO_DB_URL,
            maxPoolSize=10,
            minPoolSize=10,
            serverSelectionTimeoutMS=5000
        )
        app.state.mongo_client = client
        app.state.mongo = client[MONGO_DB_NAME]
        # 尝试连接並捕获可能的超時异常
        try:
            # 触发一次服務器通信来确认连接
            data = await client.server_info()
            print("MongoDB 連接成功", data)
        except Exception as e:
            raise ValueError(f"MongoDB 連接失敗: {e}")
    else:
        print("MongoDB 連接關閉")
        app.state.mongo_client.close()
