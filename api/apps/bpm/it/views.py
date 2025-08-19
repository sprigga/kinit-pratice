#!/usr/bin/python
# -*- coding: utf-8 -*-
# @version        : 1.0
# @Create Time    : 2025-08-04 08:47:11
# @File           : views.py
# @IDE            : PyCharm
# @desc           : IT 服務需求單視圖層
from apps.vadmin.auth.utils.current import OpenAuth, AllUserAuth
from core.database import db_getter
from fastapi import Depends, Query, APIRouter, Form
from sqlalchemy.ext.asyncio import AsyncSession
from apps.vadmin.auth.utils.validation.auth import Auth
from utils.response import ErrorResponse, SuccessResponse
from . import schemas, models, params, crud, services
from core.dependencies import IdList



app = APIRouter()




###########################################################
#    IT 服務需求單 CRUD 操作
###########################################################

@app.get("/it", summary="獲取 IT 服務需求單列表")
async def get_bpmin_it_list(p: params.BpminItParams = Depends(), auth: Auth = Depends(OpenAuth())):
    try:
        result = await services.BpminItServices.list_bpmin_it(auth.db, p.dict())
        if result['success']:
            return SuccessResponse(result['data'], count=result.get('count'))
        else:
            return ErrorResponse(message=result['error'])
    except Exception as e:
        return ErrorResponse(message=f"獲取 IT 服務需求單列表失敗: {str(e)}")


@app.post("/it", summary="創建 IT 服務需求單")
async def create_bpmin_it(data: schemas.BpminIt, auth: Auth = Depends(OpenAuth())):
    try:
        result = await services.BpminItServices.create_bpmin_it(auth.db, data)
        if result['success']:
            return SuccessResponse(result['data'], message=result['message'])
        else:
            return ErrorResponse(message=result['error'])
    except Exception as e:
        return ErrorResponse(message=f"創建 IT 服務需求單失敗: {str(e)}")


@app.post("/it/add-from-bmp", summary="從 BPM 表單創建 IT 服務需求單")
async def create_it_from_bmp(
    serial_no: str = Form(..., description="BPM 流程序號"),
    auth: Auth = Depends(OpenAuth())
):
    """從 BPM 表單資料創建 IT 服務需求單"""
    try:
        result = await services.BpminItServices.create_it_request_from_bpm(auth.db, serial_no, auto_create=True)
        if result['success']:
            return SuccessResponse(result['data'], message=result['message'])
        else:
            return ErrorResponse(message=result['error'])
    except Exception as e:
        return ErrorResponse(message=f"從 BPM 創建 IT 服務需求單失敗: {str(e)}")


@app.post("/it/quick-add-from-bmp", summary="快速從 BPM 創建 IT 服務需求單（含表單資料預覽）")
async def quick_create_it_from_bmp(
    serial_no: str = Form(..., description="BPM 流程序號"),
    auto_create: bool = Form(False, description="是否自動創建 IT 服務需求單"),
    auth: Auth = Depends(OpenAuth())
):
    """快速從 BPM 創建 IT 服務需求單，可選擇是否自動創建"""
    # 處理表單資料
    if not serial_no:
        return ErrorResponse(message="BPM 流程序號不能為空")
    
    try:
        result = await services.BpminItServices.create_it_request_from_bpm(auth.db, serial_no, auto_create=auto_create)
        if result['success']:
            return SuccessResponse(result['data'], message=result['message'])
        else:
            return ErrorResponse(message=result['error'])
    except Exception as e:
        return ErrorResponse(message=f"快速創建 IT 服務需求單失敗: {str(e)}")


@app.delete("/it", summary="刪除 IT 服務需求單", description="硬刪除")
async def delete_bpmin_it_list(ids: IdList = Depends(), auth: Auth = Depends(OpenAuth())):
    try:
        result = await services.BpminItServices.delete_bpmin_it(auth.db, ids.ids, soft_delete=False)
        if result['success']:
            return SuccessResponse(message=result['message'])
        else:
            return ErrorResponse(message=result['error'])
    except Exception as e:
        return ErrorResponse(message=f"刪除 IT 服務需求單失敗: {str(e)}")


# @app.put("/it/{data_id}", summary="更新 IT 服務需求單")
# async def put_bpmin_it(data_id: int, data: schemas.BpminIt, auth: Auth = Depends(OpenAuth())):
#     try:
#         result = await services.BpminItServices.update_bpmin_it(auth.db, data_id, data)
#         if result['success']:
#             return SuccessResponse(result['data'], message=result['message'])
#         else:
#             return ErrorResponse(message=result['error'])
#     except Exception as e:
#         return ErrorResponse(message=f"更新 IT 服務需求單失敗: {str(e)}")


@app.put("/it/update-treatment-by-sn", summary="根據序號更新 IT 服務需求單處理方式")
async def put_bpmin_it_treatment_by_sn(
    serial_no: str = Form(..., description="序號"),
    treatment: str = Form("", description="處理方式（可選，優先使用BPM表單中的資料）"),
    auth: Auth = Depends(OpenAuth())
):
    """根據序號更新 IT 服務需求單的處理方式，會先從BPM表單讀取資料"""
    try:
        # 建立資料物件，treatment 可以為空，函式內部會從 BPM 表單讀取
        data = schemas.BpminIt(treatment=treatment if treatment else None)
        result = await services.BpminItServices.update_bpmin_it_by_sn(auth.db, serial_no, data)
        if result['success']:
            return SuccessResponse(result['data'], message=result['message'])
        else:
            return ErrorResponse(message=result['error'])
    except Exception as e:
        return ErrorResponse(message=f"根據序號更新 IT 服務需求單處理方式失敗: {str(e)}")


@app.post("/it/update-case-close-status", summary="更新結案狀態")
async def update_case_close_status(
    serial_no: str = Form(..., description="序號"),
    auth: Auth = Depends(OpenAuth())
):
    """檢查 BPM 流程是否已結案並更新資料庫狀態"""
    try:
        result = await services.BpminItServices.update_case_close_status(auth.db, serial_no)
        if result['success']:
            return SuccessResponse(result.get('data'), message=result['message'])
        else:
            return ErrorResponse(message=result['error'])
    except Exception as e:
        return ErrorResponse(message=f"更新結案狀態失敗: {str(e)}")


@app.get("/it/{data_id}", summary="獲取 IT 服務需求單信息")
async def get_bpmin_it(data_id: int, db: AsyncSession = Depends(db_getter)):
    try:
        result = await services.BpminItServices.get_bpmin_it(db, data_id)
        if result['success']:
            return SuccessResponse(result['data'], message=result['message'])
        else:
            return ErrorResponse(message=result['error'])
    except Exception as e:
        return ErrorResponse(message=f"獲取 IT 服務需求單信息失敗: {str(e)}")


###########################################################
#    BPM WebService API
###########################################################

@app.post("/bmp/work-items/accept", summary="接受 IT 服務需求工作項目")
async def accept_work_item(
    work_item_oid: str = Form(..., description="工作項目 OID"),
    user_id: str = Form(..., description="使用者 ID"),
    auth: Auth = Depends(OpenAuth())
):
    """接受 IT 服務需求工作項目"""
    try:
        result = await services.BpminItServices.accept_work_item(work_item_oid, user_id)
        
        if result['success']:
            return SuccessResponse(result['data'], message="接受 IT 服務需求工作項目成功")
        else:
            return ErrorResponse(message=f"接受工作項目失敗: {result['error']}")
    except Exception as e:
        return ErrorResponse(message=f"接受工作項目異常: {str(e)}")


@app.get("/bmp/work-items/todo", summary="取得 IT 服務需求待辦工作項目")
async def fetch_todo_work_item(
    user_id: str = Query(..., description="使用者 ID"),
    process_ids: str = Query('', description="流程 ID (可選)"),
    auth: Auth = Depends(OpenAuth())
):
    """取得 IT 服務需求待辦工作項目"""
    try:
        result = await services.BpminItServices.fetch_todo_work_item(user_id, process_ids)
        
        if result['success']:
            return SuccessResponse(result, message="取得 IT 服務需求待辦工作項目成功")
        else:
            return ErrorResponse(message=f"取得待辦工作項目失敗: {result['error']}")
    except Exception as e:
        return ErrorResponse(message=f"取得待辦工作項目異常: {str(e)}")


@app.get("/bmp/check-work-item-state", summary="檢查 IT 服務需求工作項目狀態")
async def check_work_item_state(
    work_item_oid: str = Query(..., description="工作項目 OID"),
    auth: Auth = Depends(OpenAuth())
):
    """檢查 IT 服務需求工作項目狀態"""
    try:
        result = await services.BpminItServices.check_work_item_state(work_item_oid)
        
        if result['success']:
            return SuccessResponse(result['data'], message="檢查 IT 服務需求工作項目狀態成功")
        else:
            return ErrorResponse(message=f"檢查工作項目狀態失敗: {result['error']}")
    except Exception as e:
        return ErrorResponse(message=f"檢查工作項目狀態異常: {str(e)}")


@app.post("/bmp/work-items/complete", summary="完成 IT 服務需求工作項目")
async def complete_work_item(
    work_item_oid: str = Form(..., description="工作項目 OID"),
    user_id: str = Form(..., description="使用者 ID"),
    comment: str = Form('IT需求處理完成', description="意見或註解"),
    auth: Auth = Depends(OpenAuth())
):
    """完成 IT 服務需求工作項目"""
    try:
        result = await services.BpminItServices.complete_work_item(work_item_oid, user_id, comment)
        
        if result['success']:
            return SuccessResponse(result['data'], message="完成 IT 服務需求工作項目成功")
        else:
            return ErrorResponse(message=f"完成工作項目失敗: {result['error']}")
    except Exception as e:
        return ErrorResponse(message=f"完成工作項目異常: {str(e)}")


@app.get("/bmp/get-all-xml-form", summary="取得 IT 服務需求完整表單資料")
async def get_all_xml_form(
    serial_no: str = Query(..., description="流程序號"),
    auth: Auth = Depends(OpenAuth())
):
    """取得 IT 服務需求完整表單資料"""
    try:
        result = await services.BpminItServices.get_all_xml_form(serial_no)
        
        if result['success']:
            return SuccessResponse(result['data'], message="取得 IT 服務需求完整表單資料成功")
        else:
            return ErrorResponse(message=f"取得完整表單資料失敗: {result['error']}")
    except Exception as e:
        return ErrorResponse(message=f"取得完整表單資料異常: {str(e)}")


@app.get("/bmo/process-instances/{serial_no}", summary="取得 IT 服務需求簡單表單資料")
async def fetch_proc_instance_with_serial_no(
    serial_no: str,
    auth: Auth = Depends(OpenAuth())
):
    """取得 IT 服務需求簡單表單資料"""
    try:
        result = await services.BpminItServices.fetch_proc_instance_with_serial_no(serial_no)
        
        if result['success']:
            return SuccessResponse(result['data'], message="取得 IT 服務需求簡單表單資料成功")
        else:
            return ErrorResponse(message=f"取得簡單表單資料失敗: {result['error']}")
    except Exception as e:
        return ErrorResponse(message=f"取得簡單表單資料異常: {str(e)}")


@app.post("/bmp/activities/reexecute", summary="IT 服務需求取回重辦")
async def reexecute_activity(
    process_serial_no: str = Form(..., description="流程序號"),
    reexecute_activity_id: str = Form(..., description="重辦活動 ID"),
    ask_reexecute_user_id: str = Form(..., description="要求重辦的使用者 ID"),
    reexecute_comment: str = Form('IT需求退回', description="重辦註解"),
    auth: Auth = Depends(OpenAuth())
):
    """IT 服務需求取回重辦"""
    try:
        result = await services.BpminItServices.reexecute_activity(
            process_serial_no, reexecute_activity_id, ask_reexecute_user_id, reexecute_comment
        )
        
        if result['success']:
            return SuccessResponse(result['data'], message="IT 服務需求取回重辦成功")
        else:
            return ErrorResponse(message=f"取回重辦失敗: {result['error']}")
    except Exception as e:
        return ErrorResponse(message=f"取回重辦異常: {str(e)}")


@app.get("/bmp/wsdl-functions", summary="取得所有 WSDL 功能列表")
async def get_wsdl_fun_list(auth: Auth = Depends(OpenAuth())):
    """取得所有 WSDL 功能列表"""
    try:
        result = await services.BpminItServices.get_wsdl_fun_list()
        
        if result['success']:
            return SuccessResponse(result['data'], message="取得 WSDL 功能列表成功")
        else:
            return ErrorResponse(message=f"取得 WSDL 功能列表失敗: {result['error']}")
    except Exception as e:
        return ErrorResponse(message=f"取得 WSDL 功能列表異常: {str(e)}")


###########################################################
#    IT 服務需求單歷程 CRUD 操作
###########################################################

@app.get("/detail", summary="獲取資訊需求單歷程列表")
async def get_bpmin_it_detail_list(p: params.BpminItDetailParams = Depends(), auth: Auth = Depends(OpenAuth())):
    try:
        result = await services.BpminItDetailServices.list_bpmin_it_detail(auth.db, p.dict())
        if result['success']:
            return SuccessResponse(result['data'], count=result.get('count'))
        else:
            return ErrorResponse(message=result['error'])
    except Exception as e:
        return ErrorResponse(message=f"獲取資訊需求單歷程列表失敗: {str(e)}")


@app.post("/detail", summary="創建資訊需求單歷程")
async def create_bpmin_it_detail(data: schemas.BpminItDetail, auth: Auth = Depends(OpenAuth())):
    try:
        result = await services.BpminItDetailServices.create_bpmin_it_detail(auth.db, data)
        if result['success']:
            return SuccessResponse(result['data'], message=result['message'])
        else:
            return ErrorResponse(message=result['error'])
    except Exception as e:
        return ErrorResponse(message=f"創建資訊需求單歷程失敗: {str(e)}")


@app.delete("/detail", summary="刪除資訊需求單歷程", description="硬刪除")
async def delete_bpmin_it_detail_list(ids: IdList = Depends(), auth: Auth = Depends(OpenAuth())):
    try:
        result = await services.BpminItDetailServices.delete_bpmin_it_detail(auth.db, ids.ids, soft_delete=False)
        if result['success']:
            return SuccessResponse(message=result['message'])
        else:
            return ErrorResponse(message=result['error'])
    except Exception as e:
        return ErrorResponse(message=f"刪除資訊需求單歷程失敗: {str(e)}")


@app.put("/detail/{data_id}", summary="更新資訊需求單歷程")
async def put_bpmin_it_detail(data_id: int, data: schemas.BpminItDetail, auth: Auth = Depends(OpenAuth())):
    try:
        result = await services.BpminItDetailServices.update_bpmin_it_detail(auth.db, data_id, data)
        if result['success']:
            return SuccessResponse(result['data'], message=result['message'])
        else:
            return ErrorResponse(message=result['error'])
    except Exception as e:
        return ErrorResponse(message=f"更新資訊需求單歷程失敗: {str(e)}")


@app.get("/detail/{data_id}", summary="獲取資訊需求單歷程信息")
async def get_bpmin_it_detail(data_id: int, db: AsyncSession = Depends(db_getter)):
    try:
        result = await services.BpminItDetailServices.get_bpmin_it_detail(db, data_id)
        if result['success']:
            return SuccessResponse(result['data'], message=result['message'])
        else:
            return ErrorResponse(message=result['error'])
    except Exception as e:
        return ErrorResponse(message=f"獲取資訊需求單歷程信息失敗: {str(e)}")
