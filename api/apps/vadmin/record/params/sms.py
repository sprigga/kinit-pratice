#!/usr/bin/python
# -*- coding: utf-8 -*-
# @version        : 1.0
# @Create Time    : 2021/10/18 22:19
# @File           : sms.py
# @IDE            : PyCharm
# @desc           : 查詢参數-类依赖項

"""
类依赖項-官方文檔：https://fastapi.tiangolo.com/zh/tutorial/dependencies/classes-as-dependencies/
"""
from fastapi import Depends
from core.dependencies import Paging, QueryParams


class SMSParams(QueryParams):
    """
    列表分頁
    """
    def __init__(self, telephone: str = None, params: Paging = Depends()):
        super().__init__(params)
        self.telephone = ("like", telephone)
