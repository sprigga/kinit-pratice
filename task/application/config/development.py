# -*- coding: utf-8 -*-
# @version        : 1.0
# @Create Time    : 2021/10/19 15:47
# @File           : development.py
# @IDE            : PyCharm
# @desc           : 数据库生产配置文件

"""
Redis 数据库配置

与接口是同一个数据库

格式："redis://:密码@地址:端口/数据库名称"
"""
REDIS_DB_ENABLE = True
REDIS_DB_URL = "redis://:@127.0.0.1:6379/1"
REDIS_DB_IP = "127.0.0.1"

"""
MongoDB 数据库配置

与接口是同一个数据库

格式：mongodb://用户名:密码@地址:端口/?authSource=数据库名称
"""
MONGO_DB_ENABLE = True
MONGO_DB_NAME = "mes"
MONGO_DB_URL = f"mongodb://afu:Y05os5352@127.0.0.1:27017/?authSource={MONGO_DB_NAME}"

"""
APS版本引擎設定
"""

# APS_JOB_ID = "666d69f055f2eca89bad923e"
APS_JOB_ID = "666f8247f5c41e3e798db310"
APS_API_LOCK_KEY = "api_aps_run"
APS_TASK_LOCK_KEY = "task_aps進度"
APS_RUN_TIMEOUT = 1800
APS_JOB_CODE = "cwssp004"

"""
T100主機設定
"""

T100_IP = "192.168.70.107"
T100_OS_USER = "root"
T100_OS_PASSWORD = "root#DSC2022"
T100_ENV = "toptst"

"""
API主機設定
"""

API_URL = "http://127.0.0.1:9000"
API_TIMEOUT = 60
