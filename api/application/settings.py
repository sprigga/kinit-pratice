# -*- coding: utf-8 -*-
# @version        : 1.0
# @Create Time    : 2021/10/19 15:47
# @File           : settings.py
# @IDE            : PyCharm
# @desc           : 主配置文件

import os
from fastapi.security import OAuth2PasswordBearer

"""
系统版本
"""
VERSION = "3.10.1"

"""安全警告: 不要在生產中打開調試運行!"""
DEBUG = True

"""是否開啟演示功能：取消所有POST,DELETE,PUT操作權限"""
DEMO = False
"""演示功能白名单"""
DEMO_WHITE_LIST_PATH = [
    "/auth/login",
    "/verify/login",
    "/auth/token/refresh",
    "/auth/wx/login",
    "/vadmin/system/dict/types/details",
    "/vadmin/system/settings/tabs",
    "/vadmin/resource/images",
    "/vadmin/auth/user/export/query/list/to/excel",
    "/vadmin/test/test"
]
"""演示功能黑名單（觸發異常 status_code=403），黑名单優先級更高"""
DEMO_BLACK_LIST_PATH = [
    "/auth/api/login"
]

"""
引入數據庫配置
"""
if DEBUG:
    from application.config.development import *
else:
    from application.config.production import *

"""項目根目錄"""
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

"""
是否開啟登陸認證
只適用于簡單的接口
如果是與認證關聯性比較強的接口，則無法使用
"""
OAUTH_ENABLE = True
"""
配置 OAuth2 密碼流認證方式
官方文檔：https://fastapi.tiangolo.com/zh/tutorial/security/first-steps/#fastapi-oauth2passwordbearer
auto_error:(bool) 可選參數，默認為 True。當驗證失敗時，如果設置為 True，FastAPI 將自動返回一個 401 未授權的響應，如果設置為 False，你需要自己處理身份驗證失敗的情况。
这里的 auto_error 设置為 False 是因為存在 OpenAuth：开放認證，無認證也可以訪問，
如果设置為 True，那么 FastAPI 會自動報錯，即無認證時 OpenAuth 會失效，所以不能使用 True。
"""
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/api/login", auto_error=False) if OAUTH_ENABLE else lambda: ""
"""安全的随机密钥，該密钥将用于對 JWT 令牌進行签名"""
SECRET_KEY = 'vgb0tnl9d58+6n-6h-ea&u^1#s0ccp!794=kbvqacjq75vzps$'
"""用于设定 JWT 令牌签名算法"""
ALGORITHM = "HS256"
"""access_token 過期時間，一天"""
ACCESS_TOKEN_EXPIRE_MINUTES = 1440
"""refresh_token 過期時間，用于刷新token使用，两天"""
REFRESH_TOKEN_EXPIRE_MINUTES = 1440 * 2
"""access_token 缓存時間，用于刷新token使用，30分鐘"""
ACCESS_TOKEN_CACHE_MINUTES = 30

"""
挂載临時文件目錄，並添加路由訪問，此路由不會在接口文檔中显示
TEMP_DIR：临時文件目錄绝對路径
官方文檔：https://fastapi.tiangolo.com/tutorial/static-files/
"""
TEMP_DIR = os.path.join(BASE_DIR, "temp")

"""
挂載静態目錄，並添加路由訪問，此路由不會在接口文檔中显示
STATIC_ENABLE：是否启用静態目錄訪問
STATIC_URL：路由訪問
STATIC_ROOT：静態文件目錄绝對路径
官方文檔：https://fastapi.tiangolo.com/tutorial/static-files/
"""
STATIC_ENABLE = True
STATIC_URL = "/media"
STATIC_DIR = "static"
STATIC_ROOT = os.path.join(BASE_DIR, STATIC_DIR)


"""
跨域解决
詳細解释：https://cloud.tencent.com/developer/article/1886114
官方文檔：https://fastapi.tiangolo.com/tutorial/cors/
"""
# 是否启用跨域
CORS_ORIGIN_ENABLE = True
# 只允许訪問的域名列表，* 代表所有
ALLOW_ORIGINS = ["*"]
# 是否支持携带 cookie
ALLOW_CREDENTIALS = True
# 设置允许跨域的http方法，比如 get、post、put等。
ALLOW_METHODS = ["*"]
# 允许携带的headers，可以用来鉴别来源等作用。
ALLOW_HEADERS = ["*"]

"""
全局事件配置
"""
EVENTS = [
    "core.event.connect_mongo" if MONGO_DB_ENABLE else None,
    "core.event.connect_redis" if REDIS_DB_ENABLE else None,
]

"""
其他項目配置
"""
# 默认密碼，"0" 默认為帳號后六位
DEFAULT_PASSWORD = "0"
# 默认头像
DEFAULT_AVATAR = "https://vv-reserve.oss-cn-hangzhou.aliyuncs.com/avatar/2023-01-27/1674820804e81e7631.png"
# 默认登陆時最大输入密碼或驗證碼錯误次數
DEFAULT_AUTH_ERROR_MAX_NUMBER = 5
# 是否开启保存登錄日誌
LOGIN_LOG_RECORD = True
# 是否开启保存每次請求日誌到本地
REQUEST_LOG_RECORD = True
# 是否开启每次操作日誌记錄到MongoDB數據庫
OPERATION_LOG_RECORD = True
# 只记錄包括的請求方式操作到MongoDB數據庫
OPERATION_RECORD_METHOD = ["POST", "PUT", "DELETE"]
# 忽略的操作接口函數名稱，列表中的函數名稱不會被记錄到操作日誌中
IGNORE_OPERATION_FUNCTION = ["post_dicts_details"]

"""
中間件配置
"""
# Polo add 2024-12-09: 是否開啟詳細請求調試日誌（開發環境建議開啟）
DEBUG_REQUEST_LOG = DEBUG  # 跟隨DEBUG設定，生產環境會自動關閉

MIDDLEWARES = [
    "core.middleware.register_debug_request_middleware" if DEBUG_REQUEST_LOG else None,  # Polo add 2024-12-09
    "core.middleware.register_request_log_middleware" if REQUEST_LOG_RECORD else None,
    "core.middleware.register_operation_record_middleware" if OPERATION_LOG_RECORD and MONGO_DB_ENABLE else None,
    "core.middleware.register_demo_env_middleware" if DEMO else None,
    "core.middleware.register_jwt_refresh_middleware"
]

"""
定時任務配置
"""
# 发布/订阅通道，与定時任務程序相互關聯，請勿随意更改
SUBSCRIBE = 'kinit_queue'
