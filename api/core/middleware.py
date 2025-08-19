# -*- coding: utf-8 -*-
# @version        : 1.0
# @Create Time    : 2021/10/19 15:47
# @File           : middleware.py
# @IDE            : PyCharm
# @desc           : 中間件

"""
官方文檔——中間件：https://fastapi.tiangolo.com/tutorial/middleware/
官方文檔——高级中間件：https://fastapi.tiangolo.com/advanced/middleware/
"""
import datetime
import json
import time
from fastapi import Request, Response
from core.logger import logger
from fastapi import FastAPI
from fastapi.routing import APIRoute
from user_agents import parse
from application.settings import OPERATION_RECORD_METHOD, MONGO_DB_ENABLE, IGNORE_OPERATION_FUNCTION, \
    DEMO_WHITE_LIST_PATH, DEMO, DEMO_BLACK_LIST_PATH
from utils.response import ErrorResponse
from apps.vadmin.record.crud import OperationRecordDal
from core.database import mongo_getter
from utils import status
import traceback  # Polo add 2024-12-09


def write_request_log(request: Request, response: Response):
    http_version = f"http/{request.scope['http_version']}"
    content_length = response.raw_headers[0][1]
    process_time = response.headers["X-Process-Time"]
    content = f"basehttp.log_message: '{request.method} {request.url} {http_version}' {response.status_code}" \
              f"{response.charset} {content_length} {process_time}"
    logger.info(content)


def register_request_log_middleware(app: FastAPI):
    """
    记錄請求日誌中間件
    :param app:
    :return:
    """

    @app.middleware("http")
    async def request_log_middleware(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        write_request_log(request, response)
        return response


def register_operation_record_middleware(app: FastAPI):
    """
    操作记錄中間件
    用于将使用認證的操作全部记錄到 mongodb 數據庫中
    :param app:
    :return:
    """

    @app.middleware("http")
    async def operation_record_middleware(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        if not MONGO_DB_ENABLE:
            return response
        telephone = request.scope.get('telephone', None)
        user_id = request.scope.get('user_id', None)
        user_name = request.scope.get('user_name', None)
        route = request.scope.get('route')
        if not telephone:
            return response
        elif request.method not in OPERATION_RECORD_METHOD:
            return response
        elif route.name in IGNORE_OPERATION_FUNCTION:
            return response
        process_time = time.time() - start_time
        user_agent = parse(request.headers.get("user-agent"))
        system = f"{user_agent.os.family} {user_agent.os.version_string}"
        browser = f"{user_agent.browser.family} {user_agent.browser.version_string}"
        query_params = dict(request.query_params.multi_items())
        path_params = request.path_params
        if isinstance(request.scope.get('body'), str):
            body = request.scope.get('body')
        else:
            body = request.scope.get('body').decode()
            if body:
                body = json.loads(body)
        params = {
            "body": body,
            "query_params": query_params if query_params else None,
            "path_params": path_params if path_params else None,
        }
        content_length = response.raw_headers[0][1]
        assert isinstance(route, APIRoute)
        
        # polo add at 2024-12-19: 為未認證用戶提供預設值
        document = {
            "process_time": process_time,
            "telephone": telephone if telephone else "anonymous",  # polo add at 2024-12-19: 未認證用戶標記為 anonymous
            "user_id": user_id if user_id else None,  # polo add at 2024-12-19: 未認證用戶 user_id 為 None
            "user_name": user_name if user_name else "匿名用戶",  # polo add at 2024-12-19: 未認證用戶顯示為匿名用戶
            "request_api": request.url.__str__(),
            "client_ip": request.client.host,
            "system": system,
            "browser": browser,
            "request_method": request.method,
            "api_path": route.path,
            "summary": route.summary,
            "description": route.description,
            "tags": route.tags,
            "route_name": route.name,
            "status_code": response.status_code,
            "content_length": content_length,
            "create_datetime": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "params": json.dumps(params),
            "is_authenticated": bool(telephone)  # polo add at 2024-12-19: 新增欄位標記是否為認證用戶
        }
        await OperationRecordDal(mongo_getter(request)).create_data(document)
        return response


def register_demo_env_middleware(app: FastAPI):
    """
    演示环境中間件
    :param app:
    :return:
    """

    @app.middleware("http")
    async def demo_env_middleware(request: Request, call_next):
        path = request.scope.get("path")
        if request.method != "GET":
            print("路由：", path, request.method)
        if DEMO and request.method != "GET":
            if path in DEMO_BLACK_LIST_PATH:
                return ErrorResponse(
                    status=status.HTTP_403_FORBIDDEN,
                    code=status.HTTP_403_FORBIDDEN,
                    msg="演示环境，禁止操作"
                )
            elif path not in DEMO_WHITE_LIST_PATH:
                return ErrorResponse(msg="演示環境，禁止操作")
        return await call_next(request)


def register_debug_request_middleware(app: FastAPI):  # Polo add 2024-12-09
    """
    調試請求中間件 - 詳細記錄headers和payload
    Polo add 2024-12-09: 新增調試中間件用於查看完整的headers和payload詳細資訊
    :param app:
    :return:
    """

    @app.middleware("http")
    async def debug_request_middleware(request: Request, call_next):
        try:
            # Polo add 2024-12-09: 詳細記錄請求資訊的邏輯開始
            # 記錄請求開始時間
            start_time = time.time()
            
            # 獲取完整的headers
            headers = dict(request.headers)
            
            # 獲取請求路徑和方法
            path = request.url.path
            method = request.method
            
            # 獲取query parameters
            query_params = dict(request.query_params)
            
            # 獲取path parameters
            path_params = request.path_params
            
            # 讀取request body (payload)
            body = None
            if method in ["POST", "PUT", "PATCH"]:
                try:
                    body_bytes = await request.body()
                    if body_bytes:
                        body = body_bytes.decode('utf-8')
                        # 嘗試解析JSON
                        try:
                            body_json = json.loads(body)
                            body = body_json
                        except json.JSONDecodeError:
                            # 如果不是JSON，保持原始字符串
                            pass
                except Exception as e:
                    body = f"無法讀取body: {str(e)}"
            
            # 記錄詳細的請求資訊
            logger.info("=" * 80)
            logger.info(f"🔍 DEBUG REQUEST - {method} {path}")
            logger.info("=" * 80)
            logger.info(f"📍 完整URL: {request.url}")
            logger.info(f"🌐 客戶端IP: {request.client.host if request.client else 'Unknown'}")
            logger.info(f"🔗 User-Agent: {headers.get('user-agent', 'Unknown')}")
            
            # 記錄所有headers
            logger.info("📋 REQUEST HEADERS:")
            for key, value in headers.items():
                # 隱藏敏感資訊
                if key.lower() in ['authorization', 'cookie', 'x-api-key']:
                    value = f"{value[:10]}..." if len(value) > 10 else "***"
                logger.info(f"   {key}: {value}")
            
            # 記錄query parameters
            if query_params:
                logger.info("🔍 QUERY PARAMETERS:")
                for key, value in query_params.items():
                    logger.info(f"   {key}: {value}")
            
            # 記錄path parameters
            if path_params:
                logger.info("🛤️ PATH PARAMETERS:")
                for key, value in path_params.items():
                    logger.info(f"   {key}: {value}")
            
            # 記錄request body (payload)
            if body is not None:
                logger.info("📦 REQUEST PAYLOAD:")
                if isinstance(body, dict):
                    # 美化JSON輸出
                    logger.info(json.dumps(body, indent=2, ensure_ascii=False))
                else:
                    logger.info(f"   {body}")
            
            # 處理請求
            response = await call_next(request)
            
            # 計算處理時間
            process_time = time.time() - start_time
            
            # 記錄響應資訊
            logger.info("📤 RESPONSE INFO:")
            logger.info(f"   Status Code: {response.status_code}")
            logger.info(f"   Process Time: {process_time:.4f}s")
            
            # 記錄響應headers
            logger.info("📋 RESPONSE HEADERS:")
            for name, value in response.headers.items():
                logger.info(f"   {name}: {value}")
            
            logger.info("=" * 80)
            logger.info("✅ DEBUG REQUEST END")
            logger.info("=" * 80)
            # Polo add 2024-12-09: 詳細記錄請求資訊的邏輯結束
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Debug middleware error: {str(e)}")
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            # 即使出錯也要繼續處理請求
            return await call_next(request)


def register_jwt_refresh_middleware(app: FastAPI):
    """
    JWT刷新中間件
    :param app:
    :return:
    """

    @app.middleware("http")
    async def jwt_refresh_middleware(request: Request, call_next):
        response = await call_next(request)
        refresh = request.scope.get('if-refresh', 0)
        response.headers["if-refresh"] = str(refresh)
        return response
