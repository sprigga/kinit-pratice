#!/usr/bin/python
# -*- coding: utf-8 -*-
# @version        : 1.0
# @Create Time    : 2025/08/08 14:50
# @File           : bpmin_it_detail.py
# @IDE            : PyCharm
# @desc           : 資料存取層

from sqlalchemy.ext.asyncio import AsyncSession
from core.crud import DalBase
from .. import models, schemas


class BpminItDetailDal(DalBase):

    def __init__(self, db: AsyncSession):
        super(BpminItDetailDal, self).__init__()
        self.db = db
        self.model = models.BpminItDetail
        self.schema = schemas.BpminItDetailSimpleOut
