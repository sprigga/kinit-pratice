#!/usr/bin/python
# -*- coding: utf-8 -*-
# @version        : 1.0
# @Create Time    : 2022/12/12 14:31 
# @File           : file_base.py
# @IDE            : PyCharm
# @desc           : 简要说明

import datetime
import os
from pathlib import Path
from aiopathlib import AsyncPath
from fastapi import UploadFile
from application.settings import TEMP_DIR, STATIC_ROOT
from core.exception import CustomException
from utils import status
from utils.tools import generate_string


class FileBase:

    IMAGE_ACCEPT = ["image/png", "image/jpeg", "image/gif", "image/x-icon"]
    VIDEO_ACCEPT = ["video/mp4", "video/mpeg"]
    AUDIO_ACCEPT = ["audio/wav", "audio/mp3", "audio/m4a", "audio/wma", "audio/ogg", "audio/mpeg", "audio/x-wav"]
    ALL_ACCEPT = [*IMAGE_ACCEPT, *VIDEO_ACCEPT, *AUDIO_ACCEPT]

    @classmethod
    def get_random_filename(cls, suffix: str) -> str:
        """
        生成随机文件名稱，生成规则：當前時間戳 + 8位随机字符串拼接
        :param suffix: 文件后缀
        :return:
        """
        if not suffix.startswith("."):
            suffix = "." + suffix
        return f"{str(int(datetime.datetime.now().timestamp())) + str(generate_string(8))}{suffix}"

    @classmethod
    def get_today_timestamp(cls) -> str:
        """
        獲取當天時間戳
        :return:
        """
        return str(int((datetime.datetime.now().replace(hour=0, minute=0, second=0)).timestamp()))

    @classmethod
    def generate_relative_path(cls, path: str, filename: str = None, suffix: str = None) -> str:
        """
        生成相對路径，生成规则：自定义目錄/當天日期時間戳/随机文件名稱
        1. filename 参數或者 suffix 参數必须填写一个
        2. filename 参數和 suffix 参數都存在则优先取 suffix 参數為后缀
        :param path: static 指定目錄类别
        :param filename: 文件名稱，只用户獲取后缀，不做真实文件名稱，避免文件重复問题
        :param suffix: 文件后缀
        """
        if not filename and not suffix:
            raise ValueError("filename 參數或者 suffix 參數必須填寫一個")
        elif not suffix and filename:
            suffix = os.path.splitext(filename)[-1]
        path = path.replace("\\", "/")
        if path[0] == "/":
            path = path[1:]
        if path[-1] == "/":
            path = path[:-1]
        today = datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d")
        return f"{path}/{today}/{cls.get_random_filename(suffix)}"

    @classmethod
    def generate_static_file_path(cls, path: str, filename: str = None, suffix: str = None) -> str:
        """
        生成 static 静態文件路径，生成规则：自定义目錄/當天日期時間戳/随机文件名稱
        1. filename 参數或者 suffix 参數必须填写一个
        2. filename 参數和 suffix 参數都存在则优先取 suffix 参數為后缀
        :param path: static 指定目錄类别
        :param filename: 文件名稱，只用户獲取后缀，不做真实文件名稱，避免文件重复問题
        :param suffix: 文件后缀
        :return:
        """
        return f"{STATIC_ROOT}/{cls.generate_relative_path(path, filename, suffix)}"

    @classmethod
    def generate_temp_file_path(cls, filename: str = None, suffix: str = None) -> str:
        """
        生成临時文件路径，生成规则：
        1. filename 参數或者 suffix 参數必须填写一个
        2. filename 参數和 suffix 参數都存在则优先取 suffix 参數為后缀
        :param filename: 文件名稱
        :param suffix: 文件后缀
        :return:
        """
        if not filename and not suffix:
            raise ValueError("filename 參數或者 suffix 參數必須填寫一個")
        elif not suffix and filename:
            suffix = os.path.splitext(filename)[-1]
        return f"{cls.generate_temp_dir_path()}/{cls.get_random_filename(suffix)}"

    @classmethod
    def generate_temp_dir_path(cls) -> str:
        """
        生成临時目錄路径
        :return:
        """
        date = datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d")
        file_dir = Path(TEMP_DIR) / date
        if not file_dir.exists():
            file_dir.mkdir(parents=True, exist_ok=True)
        return str(file_dir).replace("\\", "/")

    @classmethod
    async def async_generate_temp_file_path(cls, filename: str) -> str:
        """
        生成临時文件路径
        :param filename: 文件名稱
        :return:
        """
        return f"{await cls.async_generate_temp_dir_path()}/{filename}"

    @classmethod
    async def async_generate_temp_dir_path(cls) -> str:
        """
        生成临時目錄路径
        :return:
        """
        date = datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d")
        file_dir = AsyncPath(TEMP_DIR) / date
        path = file_dir / (generate_string(4) + str(int(datetime.datetime.now().timestamp())))
        if not await path.exists():
            await path.mkdir(parents=True, exist_ok=True)
        return str(path).replace("\\", "/")

    @classmethod
    async def validate_file(cls, file: UploadFile, max_size: int = None, mime_types: list = None) -> bool:
        """
        驗證文件是否符合格式

        :param file: 文件
        :param max_size: 文件最大值，单位 MB
        :param mime_types: 支持的文件類型
        """
        if max_size:
            size = len(await file.read()) / 1024 / 1024
            if size > max_size:
                raise CustomException(f"上傳文件過大，不能超過{max_size}MB", status.HTTP_ERROR)
            await file.seek(0)
        if mime_types:
            if file.content_type not in mime_types:
                raise CustomException(f"上傳文件格式錯誤，只支持 {'/'.join(mime_types)} 格式!", status.HTTP_ERROR)
        return True
