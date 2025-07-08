#!/usr/bin/python
# -*- coding: utf-8 -*-
# @version        : 1.0
# @Create Time    : 2021/10/18 22:18
# @File           : crud.py
# @IDE            : PyCharm
# @desc           : 數據庫 增删改查操作

import json
import os
from enum import Enum
from typing import Any

from fastapi import Request
from fastapi.encoders import jsonable_encoder
from motor.motor_asyncio import AsyncIOMotorDatabase
from redis.asyncio import Redis
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from application.settings import STATIC_ROOT, SUBSCRIBE, REDIS_DB_ENABLE
from core.crud import DalBase
from core.database import redis_getter
from core.exception import CustomException
from core.mongo_manage import MongoManage
from utils import status
from utils.file.file_manage import FileManage
from . import models, schemas


class DictTypeDal(DalBase):

    def __init__(self, db: AsyncSession):
        super(DictTypeDal, self).__init__()
        self.db = db
        self.model = models.VadminDictType
        self.schema = schemas.DictTypeSimpleOut

    async def get_dicts_details(self, dict_types: list[str]) -> dict:
        """
        獲取多个字典類型下的字典元素列表
        """
        data = {}
        options = [joinedload(self.model.details)]
        objs = await DictTypeDal(self.db).get_datas(
            limit=0,
            v_return_objs=True,
            v_options=options,
            dict_type=("in", dict_types)
        )
        for obj in objs:
            if not obj:
                data[obj.dict_type] = []
                continue
            else:
                data[obj.dict_type] = [schemas.DictDetailsSimpleOut.model_validate(i).model_dump() for i in obj.details]
        return data

    async def get_select_datas(self) -> list:
        """獲取選擇數據，全部數據"""
        sql = select(self.model)
        queryset = await self.db.execute(sql)
        return [schemas.DictTypeOptionsOut.model_validate(i).model_dump() for i in queryset.scalars().all()]


class DictDetailsDal(DalBase):

    def __init__(self, db: AsyncSession):
        super(DictDetailsDal, self).__init__()
        self.db = db
        self.model = models.VadminDictDetails
        self.schema = schemas.DictDetailsSimpleOut


class SettingsDal(DalBase):

    def __init__(self, db: AsyncSession):
        super(SettingsDal, self).__init__()
        self.db = db
        self.model = models.VadminSystemSettings
        self.schema = schemas.SettingsSimpleOut

    async def get_tab_values(self, tab_id: int) -> dict:
        """
        獲取系统配置標籤下的信息
        """
        datas = await self.get_datas(limit=0, tab_id=tab_id, v_return_objs=True)
        result = {}
        for data in datas:
            if not data.disabled:
                result[data.config_key] = data.config_value
        return result

    async def update_datas(self, datas: dict, request: Request) -> None:
        """
        更新系统配置信息

        更新ico圖標步骤：先将文件上傳到本地，然后点击提交后，獲取到文件地址，将上傳的新文件覆盖原有文件
        原因：ico圖標的路径是在前端的index.html中固定的，所以目前只能改变圖片，不改变路径
        """
        for key, value in datas.items():
            if key == "web_ico":
                continue
            elif key == "web_ico_local_path":
                if not value:
                    continue
                ico = await self.get_data(config_key="web_ico", tab_id=1)
                web_ico = datas.get("web_ico")
                if ico.config_value == web_ico:
                    continue
                # 将上傳的ico路径替换到static/system/favicon.ico文件
                await FileManage.async_copy_file(value, os.path.join(STATIC_ROOT, "system/favicon.ico"))
                sql = update(self.model).where(self.model.config_key == "web_ico").values(config_value=web_ico)
                await self.db.execute(sql)
            else:
                sql = update(self.model).where(self.model.config_key == str(key)).values(config_value=value)
                await self.db.execute(sql)
        if "wx_server_app_id" in datas and REDIS_DB_ENABLE:
            rd = redis_getter(request)
            await rd.client().set("wx_server", json.dumps(datas))
        elif "sms_access_key" in datas and REDIS_DB_ENABLE:
            rd = redis_getter(request)
            await rd.client().set('aliyun_sms', json.dumps(datas))

    async def get_base_config(self) -> dict:
        """
        獲取系统基本信息
        """
        ignore_configs = ["wx_server_app_id", "wx_server_app_secret"]
        datas = await self.get_datas(limit=0, tab_id=("in", ["1", "9"]), disabled=False, v_return_objs=True)
        result = {}
        for config in datas:
            if config.config_key not in ignore_configs:
                result[config.config_key] = config.config_value
        return result


class SettingsTabDal(DalBase):

    def __init__(self, db: AsyncSession):
        super(SettingsTabDal, self).__init__(db, models.VadminSystemSettingsTab, schemas.SettingsTabSimpleOut)

    async def get_classify_tab_values(self, classify: list[str], hidden: bool | None = False) -> dict:
        """
        獲取系统配置分类下的標籤信息
        """
        model = models.VadminSystemSettingsTab
        options = [joinedload(model.settings)]
        datas = await self.get_datas(
            limit=0,
            v_options=options,
            classify=("in", classify),
            disabled=False,
            v_return_objs=True,
            hidden=hidden
        )
        return self.__generate_values(datas)

    async def get_tab_name_values(self, tab_names: list[str], hidden: bool | None = False) -> dict:
        """
        獲取系统配置標籤下的標籤信息
        """
        model = models.VadminSystemSettingsTab
        options = [joinedload(model.settings)]
        datas = await self.get_datas(
            limit=0,
            v_options=options,
            tab_name=("in", tab_names),
            disabled=False,
            v_return_objs=True,
            hidden=hidden
        )
        return self.__generate_values(datas)

    @classmethod
    def __generate_values(cls, datas: list[models.VadminSystemSettingsTab]) -> dict:
        """
        生成字典值
        """
        return {
            tab.tab_name: {
                item.config_key: item.config_value
                for item in tab.settings
                if not item.disabled
            }
            for tab in datas
        }


class TaskDal(MongoManage):
    class JobOperation(Enum):
        add = "add_job"

    def __init__(self, db: AsyncIOMotorDatabase):
        super(TaskDal, self).__init__(db, "vadmin_system_task", schemas.TaskSimpleOut)

    async def get_task(
            self,
            _id: str = None,
            v_return_none: bool = False,
            v_schema: Any = None,
            **kwargs
    ) -> dict | None:
        """
        獲取單個數據，默认使用 ID 查詢，否则使用关键词查詢

        包括临時字段 last_run_datetime，is_active
        is_active: 只有在 scheduler_task_jobs 任務运行表中存在相同 _id 才表示任務添加成功，任務状態才為 True
        last_run_datetime: 在 scheduler_task_record 中獲取該任務最近一次执行完成的時間

        :param _id: 數據 ID
        :param v_return_none: 是否返回空 None，否则抛出异常，默认抛出异常
        :param v_schema: 指定使用的序列化對象
        """
        if _id:
            kwargs["_id"] = ("ObjectId", _id)

        params = self.filter_condition(**kwargs)
        pipeline = [
            {
                '$addFields': {
                    'str_id': {'$toString': '$_id'}
                }
            },
            {
                '$lookup': {
                    'from': 'scheduler_task_jobs',
                    'localField': 'str_id',
                    'foreignField': '_id',
                    'as': 'matched_jobs'
                }
            },
            {
                '$lookup': {
                    'from': 'scheduler_task_record',
                    'localField': 'str_id',
                    'foreignField': 'job_id',
                    'as': 'matched_records'
                }
            },
            {
                '$addFields': {
                    'is_active': {
                        '$cond': {
                            'if': {'$ne': ['$matched_jobs', []]},
                            'then': True,
                            'else': False
                        }
                    },
                    'last_run_datetime': {
                        '$ifNull': [
                            {'$arrayElemAt': ['$matched_records.create_datetime', -1]},
                            None
                        ]
                    }
                }
            },
            {
                '$project': {
                    'matched_records': 0,
                    'matched_jobs': 0
                }
            },
            {
                '$match': params
            },
            {
                '$facet': {
                    'documents': [
                        {'$limit': 1},
                    ]
                }
            }
        ]
        # 执行聚合查詢
        cursor = self.collection.aggregate(pipeline)
        result = await cursor.to_list(length=None)
        data = result[0]['documents']
        if not data and v_return_none:
            return None
        elif not data:
            raise CustomException("未查找到對应數據", code=status.HTTP_404_NOT_FOUND)
        data = data[0]
        if data and v_schema:
            return jsonable_encoder(v_schema(**data))
        return data

    async def get_tasks(
            self,
            page: int = 1,
            limit: int = 10,
            v_schema: Any = None,
            v_order: str = None,
            v_order_field: str = None,
            **kwargs
    ) -> tuple:
        """
        獲取任務信息列表

        添加了两个临時字段
        is_active: 只有在 scheduler_task_jobs 任務运行表中存在相同 _id 才表示任務添加成功，任務状態才為 True
        last_run_datetime: 在 scheduler_task_record 中獲取該任務最近一次执行完成的時間
        """
        v_order_field = v_order_field if v_order_field else 'create_datetime'
        v_order = -1 if v_order in self.ORDER_FIELD else 1
        params = self.filter_condition(**kwargs)
        pipeline = [
            {
                '$addFields': {
                    'str_id': {'$toString': '$_id'}
                }
            },
            {
                '$lookup': {
                    'from': 'scheduler_task_jobs',
                    'localField': 'str_id',
                    'foreignField': '_id',
                    'as': 'matched_jobs'
                }
            },
            {
                '$lookup': {
                    'from': 'scheduler_task_record',
                    'localField': 'str_id',
                    'foreignField': 'job_id',
                    'as': 'matched_records'
                }
            },
            {
                '$addFields': {
                    'is_active': {
                        '$cond': {
                            'if': {'$ne': ['$matched_jobs', []]},
                            'then': True,
                            'else': False
                        }
                    },
                    'last_run_datetime': {
                        '$ifNull': [
                            {'$arrayElemAt': ['$matched_records.create_datetime', -1]},
                            None
                        ]
                    }
                }
            },
            {
                '$project': {
                    'matched_records': 0,
                    'matched_jobs': 0
                }
            },
            {
                '$match': params
            },
            {
                '$facet': {
                    'documents': [
                        {'$sort': {v_order_field: v_order}},
                        {'$limit': limit},
                        {'$skip': (page - 1) * limit}
                    ],
                    'count': [{'$count': 'total'}]
                }
            }
        ]

        # 执行聚合查詢
        cursor = self.collection.aggregate(pipeline)
        result = await cursor.to_list(length=None)
        datas = result[0]['documents']
        count = result[0]['count'][0]['total'] if result[0]['count'] else 0
        if count == 0:
            return [], 0
        elif v_schema:
            datas = [jsonable_encoder(v_schema(**data)) for data in datas]
        elif self.schema:
            datas = [jsonable_encoder(self.schema(**data)) for data in datas]
        return datas, count

    async def add_task(self, rd: Redis, data: dict) -> int:
        """
        添加任務到消息隊列

        使用消息無保留策略：無保留是指當發送者向某个频道發送消息時，如果没有订阅該频道的調用方，就直接将該消息丢弃。

        :param rd: redis 對象
        :param data: 行數據字典
        :return: 接收到消息的订阅者數量。
        """
        exec_strategy = data.get("exec_strategy")
        job_params = {
            "name": data.get("_id"),
            "job_class": data.get("job_class"),
            "expression": data.get("expression")
        }
        if exec_strategy == "interval" or exec_strategy == "cron":
            job_params["start_date"] = data.get("start_date")
            job_params["end_date"] = data.get("end_date")
        message = {
            "operation": self.JobOperation.add.value,
            "task": {
                "exec_strategy": data.get("exec_strategy"),
                "job_params": job_params
            }
        }
        return await rd.publish(SUBSCRIBE, json.dumps(message).encode('utf-8'))

    async def create_task(self, rd: Redis, data: schemas.Task) -> dict:
        """
        創建任務
        """
        data_dict = data.model_dump()
        is_active = data_dict.pop('is_active')
        insert_result = await super().create_data(data_dict)
        obj = await self.get_task(insert_result.inserted_id, v_schema=schemas.TaskSimpleOut)

        # 如果分组不存在则新增分组
        group = await TaskGroupDal(self.db).get_data(value=data.group, v_return_none=True)
        if not group:
            await TaskGroupDal(self.db).create_data({"value": data.group})

        result = {
            "subscribe_number": 0,
            "is_active": is_active
        }

        if is_active:
            # 創建任務成功后, 如果任務状態為 True，则向消息隊列中發送任務
            result['subscribe_number'] = await self.add_task(rd, obj)
        return result

    async def put_task(self, rd: Redis, _id: str, data: schemas.Task) -> dict:
        """
        更新任務
        """
        data_dict = data.model_dump()
        is_active = data_dict.pop('is_active')
        await super(TaskDal, self).put_data(_id, data)
        obj: dict = await self.get_task(_id, v_schema=schemas.TaskSimpleOut)

        # 如果分组不存在则新增分组
        group = await TaskGroupDal(self.db).get_data(value=data.group, v_return_none=True)
        if not group:
            await TaskGroupDal(self.db).create_data({"value": data.group})

        try:
            # 刪除正在运行中的 Job
            await SchedulerTaskJobsDal(self.db).delete_data(_id)
        except CustomException as e:
            pass

        result = {
            "subscribe_number": 0,
            "is_active": is_active
        }

        if is_active:
            # 更新任務成功后, 如果任務状態為 True，则向消息隊列中發送任務
            result['subscribe_number'] = await self.add_task(rd, obj)
        return result

    async def delete_task(self, _id: str) -> bool:
        """
        刪除任務
        """
        result = await super(TaskDal, self).delete_data(_id)

        try:
            # 刪除正在运行中的 Job
            await SchedulerTaskJobsDal(self.db).delete_data(_id)
        except CustomException as e:
            pass
        return result

    async def run_once_task(self, rd: Redis, _id: str) -> int:
        """
        执行一次任務
        """
        obj: dict = await self.get_data(_id, v_schema=schemas.TaskSimpleOut)
        message = {
            "operation": self.JobOperation.add.value,
            "task": {
                "exec_strategy": "once",
                "job_params": {
                    "name": obj.get("_id"),
                    "job_class": obj.get("job_class")
                }
            }
        }

        return await rd.publish(SUBSCRIBE, json.dumps(message).encode('utf-8'))


class TaskGroupDal(MongoManage):

    def __init__(self, db: AsyncIOMotorDatabase):
        super(TaskGroupDal, self).__init__(db, "vadmin_system_task_group")


class TaskRecordDal(MongoManage):

    def __init__(self, db: AsyncIOMotorDatabase):
        super(TaskRecordDal, self).__init__(db, "scheduler_task_record")


class SchedulerTaskJobsDal(MongoManage):

    def __init__(self, db: AsyncIOMotorDatabase):
        super(SchedulerTaskJobsDal, self).__init__(db, "scheduler_task_jobs", is_object_id=False)
