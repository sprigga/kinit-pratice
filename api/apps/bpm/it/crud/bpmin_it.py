#!/usr/bin/python
# -*- coding: utf-8 -*-
# @version        : 1.0
# @Create Time    : 2025/08/04 13:34
# @File           : bpmin_it.py
# @IDE            : PyCharm
# @desc           : 資料存取層

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update, select
from core.crud import DalBase
from .. import models, schemas
from typing import Dict, Any


class BpminItDal(DalBase):

    def __init__(self, db: AsyncSession):
        super(BpminItDal, self).__init__()
        self.db = db
        self.model = models.BpminIt
        self.schema = schemas.BpminItSimpleOut

    async def update_data_by_serial_number(self, serial_number: str, data_dict: Dict[str, Any]) -> Any:
        """根據 serial_number 更新資料"""
        # 先查找要更新的物件
        stmt = select(self.model).where(self.model.serial_number == serial_number)
        result_obj = await self.db.execute(stmt)
        obj = result_obj.scalar_one_or_none()
        
        if not obj:
            raise Exception(f"找不到序號為 {serial_number} 的 IT 服務需求單")
        
        # 更新物件屬性
        for key, value in data_dict.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        
        # 使用 flush 而不是 commit，讓上層管理事務
        await self.flush(obj)
        
        # 回傳更新後的資料
        if self.schema:
            return self.schema.model_validate(obj).model_dump()
        return obj
