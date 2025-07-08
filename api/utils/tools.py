#!/usr/bin/python
# -*- coding: utf-8 -*-
# @version        : 1.0
# @Create Time    : 2022/10/9 17:09 
# @File           : tools.py
# @IDE            : PyCharm
# @desc           : 工具类

import datetime
import random
import re
import string
from typing import List, Union
import importlib
from core.logger import logger


def test_password(password: str) -> Union[str, bool]:
    """
    检测密碼强度
    """
    if len(password) < 8 or len(password) > 16:
        return '長度需為8-16个字符,請重新輸入。'
    else:
        for i in password:
            if 0x4e00 <= ord(i) <= 0x9fa5 or ord(i) == 0x20:  # Ox4e00等十六進制數分别為中文字符和空格的Unicode编碼
                return '不能使用空格、中文，請重新輸入。'
        else:
            key = 0
            key += 1 if bool(re.search(r'\d', password)) else 0
            key += 1 if bool(re.search(r'[A-Za-z]', password)) else 0
            key += 1 if bool(re.search(r"\W", password)) else 0
            if key >= 2:
                return True
            else:
                return '至少含數字/字母/字符2種组合，請重新輸入。'


def list_dict_find(options: List[dict], key: str, value: any) -> Union[dict, None]:
    """
    字典列表查找
    """
    return next((item for item in options if item.get(key) == value), None)


def get_time_interval(start_time: str, end_time: str, interval: int, time_format: str = "%H:%M:%S") -> List:
    """
    獲取時間間隔
    :param end_time: 结束時間
    :param start_time: 开始時間
    :param interval: 間隔時間（分）
    :param time_format: 字符串格式化，默认：%H:%M:%S
    """
    if start_time.count(":") == 1:
        start_time = f"{start_time}:00"
    if end_time.count(":") == 1:
        end_time = f"{end_time}:00"
    start_time = datetime.datetime.strptime(start_time, "%H:%M:%S")
    end_time = datetime.datetime.strptime(end_time, "%H:%M:%S")
    time_range = []
    while end_time > start_time:
        time_range.append(start_time.strftime(time_format))
        start_time = start_time + datetime.timedelta(minutes=interval)
    return time_range


def generate_string(length: int = 8) -> str:
    """
    生成随机字符串
    :param length: 字符串长度
    """
    return ''.join(random.sample(string.ascii_letters + string.digits, length))


def import_modules(modules: list, desc: str, **kwargs):
    for module in modules:
        if not module:
            continue
        try:
            # 動態导入模块
            module_pag = importlib.import_module(module[0:module.rindex(".")])
            getattr(module_pag, module[module.rindex(".") + 1:])(**kwargs)
        except ModuleNotFoundError:
            logger.error(f"AttributeError：導入{desc}失敗，未找到該模組：{module}")
        except AttributeError:
            logger.error(f"ModuleNotFoundError：導入{desc}失敗，未找到該模組下的方法：{module}")


async def import_modules_async(modules: list, desc: str, **kwargs):
    for module in modules:
        if not module:
            continue
        try:
            # 動態导入模块
            module_pag = importlib.import_module(module[0:module.rindex(".")])
            await getattr(module_pag, module[module.rindex(".") + 1:])(**kwargs)
        # except TimeoutError:
        #     logger.error(f"asyncio.exceptions.TimeoutError：连接Mysql數據庫超時")
        #     print(f"asyncio.exceptions.TimeoutError：连接Mysql數據庫超時")
        except ModuleNotFoundError:
            logger.error(f"AttributeError：導入{desc}失敗，未找到該模組：{module}")
        except AttributeError:
            logger.error(f"ModuleNotFoundError：導入{desc}失敗，未找到該模組下的方法：{module}")
