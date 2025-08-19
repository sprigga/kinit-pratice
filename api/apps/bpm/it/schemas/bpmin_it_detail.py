#!/usr/bin/python
# -*- coding: utf-8 -*-
# @version        : 1.0
# @Create Time    : 2025/08/08 14:50
# @File           : bpmin_it_detail.py
# @IDE            : PyCharm
# @desc           : pydantic 模型，用於數據庫序列化操作

from pydantic import BaseModel, Field, ConfigDict
from core.data_types import DatetimeStr
from datetime import date


class BpminItDetail(BaseModel):
    work_desc: str | None = Field(None, title="工作描述")
    rsn: str | None = Field(None, title="參照序號")
    status: str | None = Field(None, title="狀態")
    create_user: str | None = Field(None, title="建立者")
    update_user: str | None = Field(None, title="更新者")
    delete_user: str | None = Field(None, title="刪除者")


class BpminItDetailSimpleOut(BpminItDetail):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., title="編號")
    create_datetime: DatetimeStr = Field(..., title="創建時間")
    update_datetime: DatetimeStr = Field(..., title="更新時間")
