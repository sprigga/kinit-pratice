#!/usr/bin/python
# -*- coding: utf-8 -*-
# @version        : 1.0
# @Create Time    : 2021/10/18 22:19
# @File           : user.py
# @IDE            : PyCharm
# @desc           : 查詢参數-类依赖項

"""
类依赖項-官方文檔：https://fastapi.tiangolo.com/zh/tutorial/dependencies/classes-as-dependencies/
"""
from fastapi import Depends, Query
from core.dependencies import Paging, QueryParams


class UserParams(QueryParams):
    """
    列表分頁
    """

    def __init__(
            self,
            name: str | None = Query(None, title="用户名稱"),
            telephone: str | None = Query(None, title="帳號"),
            email: str | None = Query(None, title="郵箱"),
            is_active: bool | None = Query(None, title="是否可用"),
            is_staff: bool | None = Query(None, title="是否為工作人員"),
            params: Paging = Depends()
    ):
        super().__init__(params)
        self.name = ("like", name)
        self.telephone = ("like", telephone)
        self.email = ("like", email)
        self.is_active = is_active
        self.is_staff = is_staff


