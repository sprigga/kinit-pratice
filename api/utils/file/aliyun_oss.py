#!/usr/bin/python
# -*- coding: utf-8 -*-
# @version        : 1.0
# @Create Time    : 2022/4/28 22:32 
# @File           : aliyun_oss.py
# @IDE            : PyCharm
# @desc           : 阿里云對象存储

import os.path
from fastapi import UploadFile
from pydantic import BaseModel
import oss2  # 安装依赖庫：pip install oss2
from oss2.models import PutObjectResult
from core.exception import CustomException
from core.logger import logger
from utils import status
from utils.file.file_manage import FileManage
from utils.file.file_base import FileBase


class BucketConf(BaseModel):
    accessKeyId: str
    accessKeySecret: str
    endpoint: str
    bucket: str
    baseUrl: str


class AliyunOSS(FileBase):
    """
    阿里云對象存储

    常见報錯：https://help.aliyun.com/document_detail/185228.htm?spm=a2c4g.11186623.0.0.6de530e5pxNK76#concept-1957777
    官方文檔：https://help.aliyun.com/document_detail/32026.html

    使用Python SDK時，大部分操作都是通過oss2.Service和oss2.Bucket两个类進行。
    oss2.Service类用于列举存储空間。
    oss2.Bucket类用于上傳、下載、刪除文件以及對存储空間進行各种配置。
    """

    def __init__(self, bucket: BucketConf):
        # 阿里云账号AccessKey拥有所有API的訪問權限，风险很高。强烈建议您創建並使用RAM用户進行API訪問或日常运维，請登錄RAM控制台創建RAM用户。
        auth = oss2.Auth(bucket.accessKeyId, bucket.accessKeySecret)
        # yourEndpoint填写Bucket所在地域對应的Endpoint。以华东1（杭州）為例，Endpoint填写為https://oss-cn-hangzhou.aliyuncs.com。
        # 填写Bucket名稱。
        self.bucket = oss2.Bucket(auth, bucket.endpoint, bucket.bucket)
        self.baseUrl = bucket.baseUrl

    async def upload_image(self, path: str, file: UploadFile, max_size: int = 10) -> str:
        """
        上傳圖片

        :param path: path由包含文件后缀，不包含Bucket名稱组成的Object完整路径，例如abc/efg/123.jpg。
        :param file: 文件對象
        :param max_size: 圖片文件最大值，单位 MB，默认 10MB
        :return: 上傳后的文件oss链接
        """
        # 驗證圖片類型
        await self.validate_file(file, max_size, self.IMAGE_ACCEPT)
        # 生成文件路径
        path = self.generate_relative_path(path, file.filename)
        file_data = await file.read()
        return await self.__upload_file_to_oss(path, file_data)

    async def upload_video(self, path: str, file: UploadFile, max_size: int = 100) -> str:
        """
        上傳視頻

        :param path: path由包含文件后缀，不包含Bucket名稱组成的Object完整路径，例如abc/efg/123.jpg。
        :param file: 文件對象
        :param max_size: 視頻文件最大值，单位 MB，默认 100MB
        :return: 上傳后的文件oss链接
        """
        # 驗證圖片類型
        await self.validate_file(file, max_size, self.VIDEO_ACCEPT)
        # 生成文件路径
        path = self.generate_relative_path(path, file.filename)
        file_data = await file.read()
        return await self.__upload_file_to_oss(path, file_data)

    async def upload_file(self, path: str, file: UploadFile) -> str:
        """
        上傳文件

        :param path: path由包含文件后缀，不包含Bucket名稱组成的Object完整路径，例如abc/efg/123.jpg。
        :param file: 文件對象
        :return: 上傳后的文件oss链接
        """
        path = self.generate_relative_path(path, file.filename)
        file_data = await file.read()
        return await self.__upload_file_to_oss(path, file_data)

    async def __upload_file_to_oss(self, path: str, file_data: bytes) -> str:
        """
        上傳文件到OSS

        :param path: path由包含文件后缀，不包含Bucket名稱组成的Object完整路径，例如abc/efg/123.jpg。
        :param file_data: 文件數據
        :return: 上傳后的文件oss链接
        """
        raise CustomException("沒有開啟上傳阿里雲服務", code=400)
        # TODO 要設計一個本地存放的地方
        # result = self.bucket.put_object(path, file_data)
        # assert isinstance(result, PutObjectResult)
        # if result.status != 200:
        #     logger.error(f"文件上傳到OSS失敗，狀態碼：{result.status}")
        #     raise CustomException("上傳文件失敗", code=status.HTTP_ERROR)
        # return self.baseUrl + path
