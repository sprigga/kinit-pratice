#!/usr/bin/python
# -*- coding: utf-8 -*-
# @version        : 1.0
# @Create Time    : 2025/08/08 14:50
# @File           : bpmin_it_detail.py
# @IDE            : PyCharm
# @desc           : 資訊需求單歷程

from fastapi import Depends, Query
from core.dependencies import Paging, QueryParams


class BpminItDetailParams(QueryParams):
    def __init__(self, params: Paging = Depends(), rsn: str = Query(None, description="參照序號")):
        super().__init__(params)
        self.rsn = rsn
