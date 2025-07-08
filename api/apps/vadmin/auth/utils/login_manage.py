#!/usr/bin/python
# -*- coding: utf-8 -*-
# @version        : 1.0
# @Create Time    : 2022/8/8 11:02
# @File           : auth_util.py
# @IDE            : PyCharm
# @desc           : 简要说明

from datetime import datetime, timedelta
from fastapi import Request
from application import settings
import jwt
from apps.vadmin.auth import models
from core.database import redis_getter
from utils.sms.code import CodeSMS
from .validation import LoginValidation, LoginForm, LoginResult


class LoginManage:
    """
    登錄認證工具
    """

    @LoginValidation
    async def password_login(self, data: LoginForm, user: models.VadminUser, **kwargs) -> LoginResult:
        """
        驗證用户密碼
        """
        result = models.VadminUser.verify_password(data.password, user.password)
        if result:
            return LoginResult(status=True, msg="驗證成功")
        return LoginResult(status=False, msg="帳號或密碼錯誤")

    @LoginValidation
    async def sms_login(self, data: LoginForm, request: Request, **kwargs) -> LoginResult:
        """
        驗證用户短信驗證碼
        """
        rd = redis_getter(request)
        sms = CodeSMS(data.telephone, rd)
        result = await sms.check_sms_code(data.password)
        if result:
            return LoginResult(status=True, msg="驗證成功")
        return LoginResult(status=False, msg="驗證碼錯誤")

    @staticmethod
    def create_token(payload: dict, expires: timedelta = None):
        """
        創建一个生成新的訪問令牌的工具函數。

        pyjwt：https://github.com/jpadilla/pyjwt/blob/master/docs/usage.rst
        jwt 博客：https://geek-docs.com/python/python-tutorial/j_python-jwt.html

        #TODO 傳入的時間為UTC時間datetime.datetime類型，但是在解碼時獲取到的是本机時間的時間戳
        """
        if expires:
            expire = datetime.utcnow() + expires
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        payload.update({"exp": expire})
        encoded_jwt = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
