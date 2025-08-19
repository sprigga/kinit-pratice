#!/usr/bin/python
# -*- coding: utf-8 -*-
# @version        : 1.0
# @Create Time    : 2025/08/04 13:34
# @File           : bpmin_it.py
# @IDE            : PyCharm
# @desc           : pydantic 模型，用於數據庫序列化操作

from pydantic import BaseModel, Field, ConfigDict
from core.data_types import DatetimeStr
from datetime import date


class BpminIt(BaseModel):
    it_manager: str | None = Field(None, title="IT經理")
    dept: str | None = Field(None, title="部門")
    apply_date: str | None = Field(None, title="申請日期")
    extension: str | None = Field(None, title="分機號碼")
    fillman: str | None = Field(None, title="填表人")
    main_apply_item: str | None = Field(None, title="申請項目")
    sub_apply_item: str | None = Field(None, title="子申請項目")
    request_desc: str | None = Field(None, title="需求描述")
    it_undertaker: str | None = Field(None, title="IT承辦人")
    treatment: str | None = Field(None, title="處理方式")
    create_user: str | None = Field(None, title="建立者工號")
    update_user: str | None = Field(None, title="更新者")
    delete_user: str | None = Field(None, title="刪除者")
    serial_number: str | None = Field(None, title="表單序號")


class BpminItSimpleOut(BpminIt):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., title="編號")
    create_datetime: DatetimeStr = Field(..., title="創建時間")
    update_datetime: DatetimeStr = Field(..., title="更新時間")
    is_delete: bool = Field(False, title="是否軟刪除")
