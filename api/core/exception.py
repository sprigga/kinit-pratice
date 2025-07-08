# -*- coding: utf-8 -*-
# @version        : 1.0
# @Create Time    : 2021/10/19 15:47
# @File           : exception.py
# @IDE            : PyCharm
# @desc           : 全局异常处理

from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError
from starlette import status
from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi import FastAPI
from core.logger import logger
from application.settings import DEBUG


class CustomException(Exception):

    def __init__(
            self,
            msg: str,
            code: int = status.HTTP_400_BAD_REQUEST,
            status_code: int = status.HTTP_200_OK,
            desc: str = None
    ):
        self.msg = msg
        self.code = code
        self.status_code = status_code
        self.desc = desc


def register_exception(app: FastAPI):
    """
    异常捕捉
    """

    @app.exception_handler(CustomException)
    async def custom_exception_handler(request: Request, exc: CustomException):
        """
        自定义异常
        """
        if DEBUG:
            print("請求地址", request.url.__str__())
            print("捕捉到重寫CustomException異常：custom_exception_handler")
            print(exc.desc)
            print(exc.msg)
        # 打印栈信息，方便追踪排查异常
        logger.exception(exc)
        return JSONResponse(
            status_code=exc.status_code,
            content={"message": exc.msg, "code": exc.code},
        )

    @app.exception_handler(StarletteHTTPException)
    async def unicorn_exception_handler(request: Request, exc: StarletteHTTPException):
        """
        重写HTTPException异常处理器
        """
        if DEBUG:
            print("請求地址", request.url.__str__())
            print("捕捉到重寫HTTPException異常：unicorn_exception_handler")
            print(exc.detail)
        # 打印栈信息，方便追踪排查异常
        logger.exception(exc)
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "code": exc.status_code,
                "message": exc.detail,
            }
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """
        重写請求驗證异常处理器
        """
        if DEBUG:
            print("請求地址", request.url.__str__())
            print("捕捉到重寫請求驗證異常：validation_exception_handler")
            print(exc.errors())
        # 打印栈信息，方便追踪排查异常
        logger.exception(exc)

        # 初始化默認的錯誤訊息
        error_details = exc.errors()[0]
        loc = " -> ".join(map(str, error_details.get("loc", [])))
        msg = error_details.get("msg")

        # 根據不同的錯誤訊息定義具體的中文返回內容
        if msg == "field required":
            msg = f"請求失敗，缺少必填項：{loc}"
        elif msg == "value is not a valid list":
            msg = f"類型錯誤，提交參數 '{loc}' 應該為列表！"
        elif msg == "value is not a valid int" or "integer" in msg:
            msg = f"類型錯誤，參數 '{loc}' 應該為整數！無法將字串解析為整數。"
        elif msg == "value could not be parsed to a boolean":
            msg = f"類型錯誤，參數 '{loc}' 應該為布爾值！"
        elif msg == "Input should be a valid list":
            msg = f"類型錯誤，輸入 '{loc}' 應該是一個有效的列表！"
        elif msg == "Input should be a valid string":
            msg = f"類型錯誤，輸入 '{loc}' 應該為有效的字符串！"
        elif "string_type" in error_details["type"]:
            msg = f"類型錯誤，欄位 '{loc}' 應為字符串"
        elif "int_type" in error_details["type"]:
            msg = f"類型錯誤，欄位 '{loc}' 應為整數"
        # 增加更多的錯誤類型
        else:
            msg = f"請求參數錯誤：{msg}，欄位：{loc}"

        return JSONResponse(
            status_code=200,
            content=jsonable_encoder(
                {
                    "message": msg,
                    "body": exc.body,
                    "code": status.HTTP_400_BAD_REQUEST
                }
            ),
        )

    @app.exception_handler(ValueError)
    async def value_exception_handler(request: Request, exc: ValueError):
        """
        捕获值异常
        """
        if DEBUG:
            print("請求地址", request.url.__str__())
            print("捕捉到值異常：value_exception_handler")
            print(exc.__str__())
        # 打印栈信息，方便追踪排查异常
        logger.exception(exc)
        return JSONResponse(
            status_code=200,
            content=jsonable_encoder(
                {
                    "message": exc.__str__(),
                    "code": status.HTTP_400_BAD_REQUEST
                }
            ),
        )

    @app.exception_handler(Exception)
    async def all_exception_handler(request: Request, exc: Exception):
        """
        捕获全部异常
        """
        if DEBUG:
            print("請求地址", request.url.__str__())
            print("捕捉到全局異常：all_exception_handler")
            print(exc.__str__())
        # 打印栈信息，方便追踪排查异常
        logger.exception(exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=jsonable_encoder(
                {
                    "message": "接口異常！",
                    "code": status.HTTP_500_INTERNAL_SERVER_ERROR
                }
            ),
        )
