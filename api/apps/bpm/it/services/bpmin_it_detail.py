#!/usr/bin/python
# -*- coding: utf-8 -*-
# @version        : 1.0
# @Create Time    : 2025/08/08 14:50
# @File           : bpmin_it_detail.py
# @IDE            : PyCharm
# @desc           : 資訊需求單歷程

from .. import models, schemas, crud
from sqlalchemy.ext.asyncio import AsyncSession


class BpminItDetailServices:
    @classmethod
    async def create_bpmin_it_detail(cls, db: AsyncSession, data: schemas.BpminItDetail):
        """創建資訊需求單歷程"""
        try:
            dal = crud.BpminItDetailDal(db)
            result = await dal.create_data(data=data.dict())
            return {'success': True, 'data': result, 'message': '創建資訊需求單歷程成功'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @classmethod
    async def get_bpmin_it_detail(cls, db: AsyncSession, data_id: int):
        """獲取單個資訊需求單歷程"""
        try:
            dal = crud.BpminItDetailDal(db)
            result = await dal.get_data(data_id=data_id)
            if result:
                return {'success': True, 'data': result, 'message': '獲取資訊需求單歷程成功'}
            else:
                return {'success': False, 'error': '未找到該資訊需求單歷程'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @classmethod
    async def list_bpmin_it_detail(cls, db: AsyncSession, params_dict: dict):
        """獲取資訊需求單歷程列表"""
        try:
            dal = crud.BpminItDetailDal(db)
            
            # 構建查詢條件
            filters = []
            if params_dict.get('rsn'):
                filters.append(models.BpminItDetail.rsn == params_dict['rsn'])
            
            # 使用與主服務相同的方式處理參數
            datas, count = await dal.get_datas(
                v_where=filters,
                **params_dict,
                v_return_count=True
            )
            
            return {'success': True, 'data': datas, 'count': count, 'message': '獲取資訊需求單歷程列表成功'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    @classmethod
    async def update_bpmin_it_detail(cls, db: AsyncSession, data_id: int, data: schemas.BpminItDetail):
        """更新資訊需求單歷程"""
        try:
            dal = crud.BpminItDetailDal(db)
            result = await dal.put_data(data_id=data_id, data=data.dict())
            if result:
                return {'success': True, 'data': result, 'message': '更新資訊需求單歷程成功'}
            else:
                return {'success': False, 'error': '未找到該資訊需求單歷程'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    @classmethod
    async def delete_bpmin_it_detail(cls, db: AsyncSession, ids: list, soft_delete: bool = True):
        """刪除資訊需求單歷程"""
        try:
            dal = crud.BpminItDetailDal(db)
            if soft_delete:
                await dal.delete_datas(ids=ids)
            else:
                await dal.delete_datas(ids=ids, is_delete=True)
            return {'success': True, 'message': f'刪除 {len(ids)} 筆資訊需求單歷程成功'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

