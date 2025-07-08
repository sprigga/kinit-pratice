#!/usr/bin/python
# -*- coding: utf-8 -*-
# @version        : 1.0
# @Create Time    : 2022/10/19 15:41 
# @File           : views.py
# @IDE            : PyCharm
# @desc           : 简要说明

from fastapi import APIRouter, Depends
from apps.vadmin.auth.utils.current import AllUserAuth
from apps.vadmin.auth.utils.validation.auth import Auth
from utils.response import SuccessResponse
import datetime
from apps.vadmin.record.crud import LoginRecordDal

app = APIRouter()


###########################################################
#    工作区管理
###########################################################
@app.get("/project", summary="工單項目")
async def get_project():
    data = [
        # {
        #     "name": 'Mysql',
        #     "icon": 'vscode-icons:file-type-mysql',
        #     "message": '最流行的關係型數據庫管理系统',
        #     "personal": 'kinit',
        #     "link": "https://www.mysql.com/",
        #     "time": datetime.datetime.now().strftime("%Y-%m-%d")
        # },
        # {
        #     "name": 'FastAPI',
        #     "icon": 'simple-icons:fastapi',
        #     "message": '一个现代、快速(高性能)的 web 框架',
        #     "personal": 'kinit',
        #     "link": "https://fastapi.tiangolo.com/zh/",
        #     "time": datetime.datetime.now().strftime("%Y-%m-%d")
        # },
        # {
        #     "name": 'Vue',
        #     "icon": 'logos:vue',
        #     "message": '渐進式 JavaScript 框架',
        #     "personal": 'kinit',
        #     "link": "https://cn.vuejs.org/",
        #     "time": datetime.datetime.now().strftime("%Y-%m-%d")
        # },
        # {
        #     "name": 'Element-plus',
        #     "icon": 'logos:element',
        #     "message": '面向设计师和开发者的组件庫',
        #     "personal": 'kinit',
        #     "link": "https://element-plus.org/zh-CN/",
        #     "time": datetime.datetime.now().strftime("%Y-%m-%d")
        # },
        # {
        #     "name": 'Typescript',
        #     "icon": 'vscode-icons:file-type-typescript-official',
        #     "message": 'TypeScript是JavaScript類型的超集',
        #     "personal": 'kinit',
        #     "link": "https://www.typescriptlang.org/",
        #     "time": datetime.datetime.now().strftime("%Y-%m-%d")
        # },
        # {
        #     "name": 'Vite',
        #     "icon": 'vscode-icons:file-type-vite',
        #     "message": 'Vite 下一代的前端工具链',
        #     "personal": 'kinit',
        #     "link": "https://cn.vitejs.dev/",
        #     "time": datetime.datetime.now().strftime("%Y-%m-%d")
        # }
    ]
    return SuccessResponse(data)


@app.get("/dynamic", summary="工單項目")
async def get_dynamic():
    data = [
        # {
        #     "keys": ['workplace.push', 'Github'],
        #     "time": datetime.datetime.now().strftime("%Y-%m-%d")
        # },
    ]
    return SuccessResponse(data)


@app.get("/team", summary="獲取團隊信息")
async def get_team():
    data = [
        {
            "name": '拍賣系統',
            "icon": '管理系統'
        },
    ]
    return SuccessResponse(data)


@app.get("/shortcuts", summary="系統捷徑")
async def get_shortcuts():
    data = [
        {
            "name": "技能排序",
            "link": "https://docs.google.com/spreadsheets/d/1MNS2QHCob2CaqHMvccOhosWxgdSCXUsFrc20Q9eT4Pk/edit?gid=1445865307#gid=1445865307"
        },
        {
            "name": "拍賣價格",
            "link": "https://docs.google.com/spreadsheets/d/1mQjxDN4JiIVIc6q4FBs1JLgxmi4H3HLX-YzrzieKYbk/edit?gid=180665198#gid=180665198"
        },
    ]
    return SuccessResponse(data)
