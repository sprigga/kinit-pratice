import datetime
import json
from typing import Any
from bson import ObjectId
from bson.errors import InvalidId
from bson.json_util import dumps
from fastapi.encoders import jsonable_encoder
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.results import InsertOneResult, UpdateResult
from core.exception import CustomException
from utils import status


class MongoManage:
    """
    mongodb 數據庫管理器
    博客：https://www.cnblogs.com/aduner/p/13532504.html
    mongodb 官网：https://www.mongodb.com/docs/drivers/motor/
    motor 文檔：https://motor.readthedocs.io/en/stable/
    """

    # 倒叙
    ORDER_FIELD = ["desc", "descending"]

    def __init__(
            self,
            db: AsyncIOMotorDatabase = None,
            collection: str = None,
            schema: Any = None,
            is_object_id: bool = True
    ):
        """
        初始化
        :param db:
        :param collection: 集合
        :param schema:
        :param is_object_id: _id 列是否為 ObjectId 格式
        """
        self.db = db
        self.collection = db[collection] if collection else None
        self.schema = schema
        self.is_object_id = is_object_id

    async def get_data(
            self,
            _id: str = None,
            v_return_none: bool = False,
            v_schema: Any = None,
            **kwargs
    ) -> dict | None:
        """
        獲取單個數據，默认使用 ID 查詢，否则使用关键词查詢
        :param _id: 數據 ID
        :param v_return_none: 是否返回空 None，否则抛出异常，默认抛出异常
        :param v_schema: 指定使用的序列化對象
        """
        if _id and self.is_object_id:
            kwargs["_id"] = ObjectId(_id)
        params = self.filter_condition(**kwargs)
        data = await self.collection.find_one(params)
        if not data and v_return_none:
            return None
        elif not data:
            raise CustomException("查找失敗，未查找到對應數據", code=status.HTTP_404_NOT_FOUND)
        elif data and v_schema:
            return jsonable_encoder(v_schema(**data))
        return data

    async def create_data(self, data: dict | Any) -> InsertOneResult:
        """
        創建數據
        """
        if not isinstance(data, dict):
            data = jsonable_encoder(data)
        data['create_datetime'] = datetime.datetime.now()
        data['update_datetime'] = datetime.datetime.now()
        result = await self.collection.insert_one(data)
        # 判断插入是否成功
        if result.acknowledged:
            return result
        else:
            raise CustomException("創建新數據失敗", code=status.HTTP_ERROR)

    async def put_data(self, _id: str, data: dict | Any) -> UpdateResult:
        """
        更新數據
        """
        if not isinstance(data, dict):
            data = jsonable_encoder(data)
        new_data = {'$set': data}
        result = await self.collection.update_one({'_id': ObjectId(_id) if self.is_object_id else _id}, new_data)

        if result.matched_count > 0:
            return result
        else:
            raise CustomException("更新失敗，未查找到對應數據", code=status.HTTP_404_NOT_FOUND)

    async def delete_data(self, _id: str):
        """
        刪除數據
        """
        result = await self.collection.delete_one({'_id': ObjectId(_id) if self.is_object_id else _id})

        if result.deleted_count > 0:
            return True
        else:
            raise CustomException("刪除失敗，未查找到對應數據", code=status.HTTP_404_NOT_FOUND)

    async def get_datas(
            self,
            page: int = 1,
            limit: int = 10,
            v_schema: Any = None,
            v_order: str = None,
            v_order_field: str = None,
            v_return_objs: bool = False,
            **kwargs
    ):
        """
        使用 find() 要查詢的一组文檔。 find() 没有I / O，也不需要 await 表达式。它只是創建一个 AsyncIOMotorCursor 实例
        當您調用 to_list() 或為循环执行异步時 (async for) ，查詢实际上是在服務器上执行的。
        """

        params = self.filter_condition(**kwargs)
        cursor = self.collection.find(params)

        if v_order or v_order_field:
            v_order_field = v_order_field if v_order_field else 'create_datetime'
            v_order = -1 if v_order in self.ORDER_FIELD else 1
            cursor.sort(v_order_field, v_order)

        if limit != 0:
            # 對查詢应用排序(sort)，跳過(skip)或限制(limit)
            cursor.skip((page - 1) * limit).limit(limit)

        datas = []
        async for row in cursor:
            data = json.loads(dumps(row))
            datas.append(data)

        if not datas or v_return_objs:
            return datas
        elif v_schema:
            datas = [jsonable_encoder(v_schema(**data)) for data in datas]
        elif self.schema:
            datas = [jsonable_encoder(self.schema(**data)) for data in datas]
        return datas

    async def get_count(self, **kwargs) -> int:
        """
        獲取统计數據
        """
        params = self.filter_condition(**kwargs)
        return await self.collection.count_documents(params)

    @classmethod
    def filter_condition(cls, **kwargs):
        """
        過滤條件
        """
        params = {}
        for k, v in kwargs.items():
            if not v:
                continue
            elif isinstance(v, tuple):
                if v[0] == "like" and v[1]:
                    params[k] = {'$regex': v[1]}
                elif v[0] == "between" and len(v[1]) == 2:
                    params[k] = {'$gte': f"{v[1][0]} 00:00:00", '$lt': f"{v[1][1]} 23:59:59"}
                elif v[0] == "ObjectId" and v[1]:
                    try:
                        params[k] = ObjectId(v[1])
                    except InvalidId:
                        raise CustomException("任務編號格式不正確！")
            else:
                params[k] = v
        return params
