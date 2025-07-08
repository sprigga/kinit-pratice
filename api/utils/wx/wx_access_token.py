#!/usr/bin/python
# -*- coding: utf-8 -*-
# @version        : 1.0
# @Create Time    : 2021/11/27 18:37
# @File           : wx_access_token.py
# @IDE            : PyCharm
# @desc           : 獲取小程序全局唯一后台接口調用凭據

import requests
from redis.asyncio import Redis
from core.logger import logger


class WxAccessToken:
    """
    獲取到的access_token存储在redis數據庫中

    獲取小程序全局唯一后台接口調用凭據（access_token）。調用绝大多數后台接口時都需使用 access_token，开发者需要進行妥善保存。

    官方文檔：https://developers.weixin.qq.com/miniprogram/dev/api-backend/open-api/access-token/auth.getAccessToken.html
    """

    def __init__(self, appid: str, secret: str, redis: Redis, grant_type: str = "client_credential", *args, **kwargs):
        self.__url = "https://api.weixin.qq.com/cgi-bin/token"
        self.__method = "get"
        self.appidKey = f"{appid}_access_token"
        self.redis = redis
        self.params = {
            "appid": appid,
            "secret": secret,
            "grant_type": grant_type
        }

    async def get(self) -> dict:
        """
        獲取小程序access_token
        """
        token = await self.redis.get(self.appidKey)
        if not token:
            return await self.update()
        return {"status": True, "token": token}

    async def update(self) -> dict:
        """
        更新小程序access_token
        """
        print("开始更新 access_token")
        method = getattr(requests, self.__method)
        response = method(url=self.__url, params=self.params)
        result = response.json()

        if result.get("errcode", "0") != "0":
            print("獲取access_token失敗", result)
            logger.error(f"獲取access_token失敗：{result}")
            return {"status": False, "token": None}

        print("成功獲取到", result)
        await self.redis.set(self.appidKey, result.get("access_token"), ex=2000)
        logger.info(f"獲取access_token成功：{result}")

        return {"status": True, "token": result.get("access_token")}
