# -*- coding: utf-8 -*-
# @version        : 1.0
# @Create Time    : 2021/10/19 15:47
# @File           : development.py
# @IDE            : PyCharm
# @desc           : 數據庫生產配置文件

import urllib.parse


"""
SERVER 本機設定
"""
PROJECT_NAME = "oa"
SERVER_PORT = 8080
SERVER_TITLE = '智能管理系統'
SERVER_DESCRIPTION = '管理後台'




"""
Mysql 數據庫配置項
连接引擎官方文檔：https://www.osgeo.cn/sqlalchemy/core/engines.html
數據庫链接配置说明：mysql+asyncmy://數據庫用户名:數據庫密碼@數據庫地址:數據庫端口/數據庫名稱
"""
USE_GCP_DB = False  # 如果是 True，使用 GCP DB；如果是 False，使用本機 DB
MYSQL_USER = urllib.parse.quote_plus('oa-admin')
MYSQL_SERVER_IP = urllib.parse.quote_plus('192.168.30.20')
# MYSQL_SERVER_IP = urllib.parse.quote_plus('145.10.0.7')
MYSQL_PORT = '3306'
MYSQL_PASSWORD = 'Bdfrost168'
MYSQL_DB = urllib.parse.quote_plus(PROJECT_NAME)
MYSQL_GCP_INS = 'tdg-ball:asia-east1:tkg-mysql'
# 動態生成 SQLAlchemy 資料庫 URL
SQLALCHEMY_ALEMBIC_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_SERVER_IP}:{MYSQL_PORT}/{MYSQL_DB}"

# 資料庫配置
if USE_GCP_DB:
    # 設定 Cloud SQL UNIX 套接字的路徑
    unix_socket = '/cloudsql/' + MYSQL_GCP_INS
    # 使用 UNIX 套接字來設定 SQLAlchemy 連接字串
    SQLALCHEMY_DATABASE_URL = f"mysql+asyncmy://{MYSQL_USER}:{MYSQL_PASSWORD}@/{MYSQL_DB}?unix_socket={unix_socket}"
else:
    # 設定 SQLAlchemy 連接字串
    SQLALCHEMY_DATABASE_URL = f"mysql+asyncmy://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_SERVER_IP}:{MYSQL_PORT}/{MYSQL_DB}"


"""
Redis 數據庫配置
格式："redis://:密碼@地址:端口/數據庫名稱"
"""
REDIS_DB_ENABLE = True
REDIS_DB_URL = "redis://:123456@192.168.30.20:6379/1"
# REDIS_DB_URL = "redis://:123456@192.168.30.20:6379/1"

"""
MongoDB 數據庫配置
格式：mongodb://用户名:密碼@地址:端口/?authSource=數據庫名稱
"""
MONGO_DB_ENABLE = True
MONGO_DB_NAME = "bd-oa"
# MONGO_DB_NAME = "oa"
MONGO_DB_USERNAME = "oa-admin"
MONGO_DB_PASSWORD = "Bdfrost168"
# MONGO_DB_USERNAME = "afu"
# MONGO_DB_PASSWORD = "Y05os@5352"
# 這是雲端服務用的
# MONGO_DB_URL = f"mongodb+srv://{MONGO_DB_USERNAME}:{MONGO_DB_PASSWORD}@{MONGO_DB_NAME}.i1bhh.mongodb.net/?retryWrites=true&w=majority&tls=true&tlsAllowInvalidCertificates=true"
# MONGO_DB_URL = f"mongodb://{MONGO_DB_USERNAME}:{MONGO_DB_PASSWORD}@127.0.0.1:27017/?authSource={MONGO_DB_NAME}"
# MONGO_DB_URL = f"mongodb://oa-admin:Bdfrost168@127.0.0.1:27017/?authSource=oa"
MONGO_DB_URL = f"mongodb://{MONGO_DB_USERNAME}:{MONGO_DB_PASSWORD}@192.168.30.20:27017/?authSource={MONGO_DB_NAME}"
# MONGO_DB_URL = f"mongodb://{MONGO_DB_USERNAME}:{MONGO_DB_PASSWORD}@145.10.0.6:27017/?authSource={MONGO_DB_NAME}"

# 145.10.0.6
"""
EMQX MQTT配置
格式：mongodb://用户名:密碼@地址:端口/?authSource=數據庫名稱
"""
MQTT_ENABLE = False
MQTT_NAME = "admin"
MQTT_PASSWORD = "public"
MQTT_URL = "127.0.0.1"

"""
阿里云對象存储OSS配置
阿里云账号AccessKey拥有所有API的訪問權限，风险很高。强烈建议您創建並使用RAM用户進行API訪問或日常运维，請登錄RAM控制台創建RAM用户。
yourEndpoint填写Bucket所在地域對应的Endpoint。以华东1（杭州）為例，Endpoint填写為https://oss-cn-hangzhou.aliyuncs.com。
 *  [accessKeyId] {String}：通過阿里云控制台創建的AccessKey。
 *  [accessKeySecret] {String}：通過阿里云控制台創建的AccessSecret。
 *  [bucket] {String}：通過控制台或PutBucket創建的bucket。
 *  [endpoint] {String}：bucket所在的区域， 默认oss-cn-hangzhou。
"""
ALIYUN_OSS = {
    "accessKeyId": "accessKeyId",
    "accessKeySecret": "accessKeySecret",
    "endpoint": "endpoint",
    "bucket": "bucket",
    "baseUrl": "baseUrl"
}

"""
獲取IP地址归属地
文檔：https://user.ip138.com/ip/doc
"""
IP_PARSE_ENABLE = False
IP_PARSE_TOKEN = "IP_PARSE_TOKEN"


"""
APS版本引擎設定
"""

APS_NO = ""
# APS_JOB_ID = "666d69f055f2eca89bad923e"
APS_JOB_ID = "666f8247f5c41e3e798db310"
APS_API_LOCK_KEY = "api_aps_run"
APS_RUN_TIMEOUT = 1800

"""
T100 API主機設定
"""

T100_ENT = '1'
T100_LANG = 'zh_TW'
T100_SITE = 'BD01'
T100_IP = '192.168.70.107'
T100_ENV = 'toptst'
T100_PROD = 'bMES'
T100_ACCT = 'tiptop'

"""
PLM API主機設定
"""
PLM_URL = 'http://192.168.70.113/'
PLM_USER = 'root'
PLM_PASSWORD = 'innovator'
PLM_DB = 'BingDian_Test'# 測試區
PLM_CLIENT_ID = 'IOMApp'


"""
MES 列印主機設定
"""
MES_PRINT_URL = 'http://localhost:8080/mes/sn/print'
