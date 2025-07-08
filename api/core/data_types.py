#!/usr/bin/python
# -*- coding: utf-8 -*-
# @version        : 1.0
# @Create Time    : 2023/7/16 12:42
# @File           : data_types.py
# @IDE            : PyCharm
# @desc           : 自定义數據類型

"""
自定义數據類型 - 官方文檔：https://docs.pydantic.dev/dev-v2/usage/types/custom/#adding-validation-and-serialization
"""
import datetime
from typing import Annotated, Any
from bson import ObjectId
from pydantic import AfterValidator, PlainSerializer, WithJsonSchema
from .validator import *


def datetime_str_vali(value: str | datetime.datetime | int | float | dict):
    """
    日期時間字符串驗證
    如果我傳入的是字符串，那么直接返回，如果我傳入的是一个日期類型，那么會转為字符串格式后返回
    因為在 pydantic 2.0 中是支持 int 或 float 自動转换類型的，所以我这里添加進去，但是在处理時會使这两种類型報錯

    官方文檔：https://docs.pydantic.dev/dev-v2/usage/types/datetime/
    """
    if isinstance(value, str):
        pattern = "%Y-%m-%d %H:%M:%S"
        try:
            datetime.datetime.strptime(value, pattern)
            return value
        except ValueError:
            pass
    elif isinstance(value, datetime.datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    elif isinstance(value, dict):
        # 用于处理 mongodb 日期時間數據類型
        date_str = value.get("$date")
        date_format = '%Y-%m-%dT%H:%M:%S.%fZ'
        # 将字符串转换為datetime.datetime類型
        datetime_obj = datetime.datetime.strptime(date_str, date_format)
        # 将datetime.datetime對象转换為指定的字符串格式
        return datetime_obj.strftime('%Y-%m-%d %H:%M:%S')
    raise ValueError("無效的日期時間或字符串數據")


# 实现自定义一个日期時間字符串的數據類型
DatetimeStr = Annotated[
    str | datetime.datetime | int | float | dict,
    AfterValidator(datetime_str_vali),
    PlainSerializer(lambda x: x, return_type=str),
    WithJsonSchema({'type': 'string'}, mode='serialization')
]


# 实现自定义一个帳號類型
Telephone = Annotated[
    str,
    AfterValidator(lambda x: vali_telephone(x)),
    PlainSerializer(lambda x: x, return_type=str),
    WithJsonSchema({'type': 'string'}, mode='serialization')
]


# 实现自定义一个郵箱類型
Email = Annotated[
    str,
    AfterValidator(lambda x: vali_email(x)),
    PlainSerializer(lambda x: x, return_type=str),
    WithJsonSchema({'type': 'string'}, mode='serialization')
]


def date_str_vali(value: str | datetime.date | int | float):
    """
    日期字符串驗證
    如果我傳入的是字符串，那么直接返回，如果我傳入的是一个日期類型，那么會转為字符串格式后返回
    因為在 pydantic 2.0 中是支持 int 或 float 自動转换類型的，所以我这里添加進去，但是在处理時會使这两种類型報錯

    官方文檔：https://docs.pydantic.dev/dev-v2/usage/types/datetime/
    """
    if isinstance(value, str):
        pattern = "%Y-%m-%d"
        try:
            datetime.datetime.strptime(value, pattern)
            return value
        except ValueError:
            pass
    elif isinstance(value, datetime.date):
        return value.strftime("%Y-%m-%d")
    raise ValueError("無效的日期時間或字符串數據")


# 实现自定义一个日期字符串的數據類型
DateStr = Annotated[
    str | datetime.date | int | float,
    AfterValidator(date_str_vali),
    PlainSerializer(lambda x: x, return_type=str),
    WithJsonSchema({'type': 'string'}, mode='serialization')
]


def object_id_str_vali(value: str | dict | ObjectId):
    """
    官方文檔：https://docs.pydantic.dev/dev-v2/usage/types/datetime/
    """
    if isinstance(value, str):
        return value
    elif isinstance(value, dict):
        return value.get("$oid")
    elif isinstance(value, ObjectId):
        return str(value)
    raise ValueError("無效的 ObjectId 數據類型")


ObjectIdStr = Annotated[
    Any,  # 这里不能直接使用 any，需要使用 typing.Any
    AfterValidator(object_id_str_vali),
    PlainSerializer(lambda x: x, return_type=str),
    WithJsonSchema({'type': 'string'}, mode='serialization')
]
