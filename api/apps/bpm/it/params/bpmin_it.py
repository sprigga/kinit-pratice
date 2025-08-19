#!/usr/bin/python
# -*- coding: utf-8 -*-
# @version        : 1.0
# @Create Time    : 2025/08/04 13:34
# @File           : bpmin_it.py
# @IDE            : PyCharm
# @desc           : 資訊需求單

from fastapi import Depends, Query
from core.dependencies import Paging, QueryParams


class BpminItParams(QueryParams):
    def __init__(
            self,
            serial_number: str | None = Query(None, title="表單序號"),
            apply_date: str | None = Query(None, title="申請日期"),
            it_undertaker: str | None = Query(None, title="IT承辦人"),
            params: Paging = Depends()
    ):
        super().__init__(params)
        self.serial_number = ("like", serial_number)
        self.apply_date = ("date", apply_date) if apply_date else None
        self.it_undertaker = ("like", it_undertaker)
