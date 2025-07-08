#!/usr/bin/python
# -*- coding: utf-8 -*-
# @version        : 1.0
# @Create Time    : 2021/10/18 22:19
# @File           : validator.py
# @IDE            : PyCharm
# @desc           : pydantic 模型重用驗證器

"""
官方文檔：https://pydantic-docs.helpmanual.io/usage/validators/#reuse-validators
"""

import re


def vali_telephone(value: str) -> str:
    """
    帳號驗證器
    :param value: 帳號
    :return: 帳號
    """
    if not value or len(value) < 3:
        raise ValueError("最少需要三位中英文單字")

    # regex = r'^1(3\d|4[4-9]|5[0-35-9]|6[67]|7[013-8]|8[0-9]|9[0-9])\d{8}$'
    regex = r'^[a-zA-Z0-9]{3,}$'

    if not re.match(regex, value):
        raise ValueError("最少需要三位中英文單字")

    return value


def vali_email(value: str) -> str:
    """
    郵箱地址驗證器
    :param value: 郵箱
    :return: 郵箱
    """
    if not value:
        raise ValueError("請輸入郵箱地址")

    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    if not re.match(regex, value):
        raise ValueError("請輸入正確郵箱地址")

    return value




