#!/usr/bin/python
# -*- coding: utf-8 -*-
# @version        : 1.0
# @Create Time    : 2022/2/24 10:21 
# @File           : crud.py
# @IDE            : PyCharm
# @desc           : 增删改查

from typing import Any
from redis.asyncio import Redis
from fastapi import UploadFile
from sqlalchemy.exc import StatementError
from sqlalchemy.orm import joinedload, aliased
from sqlalchemy.orm.strategy_options import _AbstractLoad, contains_eager
from core.exception import CustomException
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, false, and_
from core.crud import DalBase
from sqlalchemy.ext.asyncio import AsyncSession
from core.validator import vali_telephone
from utils.file.aliyun_oss import AliyunOSS, BucketConf
from utils.excel.import_manage import ImportManage, FieldType
from utils.excel.write_xlsx import WriteXlsx
from utils.send_email import EmailSender
from utils.sms.reset_passwd import ResetPasswordSMS
from .params import UserParams
from utils.tools import test_password, generate_string
from . import models, schemas
from application import settings
from utils.excel.excel_manage import ExcelManage
from apps.vadmin.system import crud as vadmin_system_crud
from apps.vadmin.help import models as vadmin_help_models
import copy
from utils import status
from utils.wx.oauth import WXOAuth
from datetime import datetime


class UserDal(DalBase):
    import_headers = [
        {"label": "姓名", "field": "name", "required": True},
        {"label": "職稱", "field": "nickname", "required": False},
        {"label": "帳號", "field": "telephone", "required": True, "rules": [vali_telephone]},
        {"label": "性别", "field": "gender", "required": False},
        {"label": "關聯角色", "field": "role_ids", "required": True, "type": FieldType.list},
    ]

    def __init__(self, db: AsyncSession):
        super(UserDal, self).__init__()
        self.db = db
        self.model = models.VadminUser
        self.schema = schemas.UserSimpleOut

    async def recursion_get_dept_ids(
            self,
            user: models.VadminUser,
            depts: list[models.VadminDept] = None,
            dept_ids: list[int] = None
    ) -> list:
        """
        递归獲取所有關聯部門 id
        :param user:
        :param depts: 所有部門实例
        :param dept_ids: 父级部門 id 列表
        :return:
        """
        if not depts:
            depts = await DeptDal(self.db).get_datas(limit=0, v_return_objs=True)
            result = []
            for i in user.depts:
                result.append(i.id)
            result.extend(await self.recursion_get_dept_ids(user, depts, result))
            return list(set(result))
        elif dept_ids:
            result = [i.id for i in filter(lambda item: item.parent_id in dept_ids, depts)]
            result.extend(await self.recursion_get_dept_ids(user, depts, result))
            return result
        else:
            return []

    async def update_login_info(self, user: models.VadminUser, last_ip: str) -> None:
        """
        更新當前登錄信息
        :param user: 用户對象
        :param last_ip: 最近一次登錄 IP
        :return:
        """
        user.last_ip = last_ip
        user.last_login = datetime.now()
        await self.db.flush()

    async def create_data(
            self,
            data: schemas.UserIn,
            v_options: list[_AbstractLoad] = None,
            v_return_obj: bool = False,
            v_schema: Any = None
    ) -> Any:
        """
        創建用户
        :param data:
        :param v_options:
        :param v_return_obj:
        :param v_schema:
        :return:
        """
        unique = await self.get_data(telephone=data.telephone, v_return_none=True)
        if unique:
            raise CustomException("帳號已存在！", code=status.HTTP_ERROR)
        password = data.telephone if settings.DEFAULT_PASSWORD == "0" else settings.DEFAULT_PASSWORD
        data.password = self.model.get_password_hash(password)
        data.avatar = data.avatar if data.avatar else settings.DEFAULT_AVATAR
        obj = self.model(**data.model_dump(exclude={'role_ids', "dept_ids"}))
        if data.role_ids:
            roles = await RoleDal(self.db).get_datas(limit=0, id=("in", data.role_ids), v_return_objs=True)
            for role in roles:
                obj.roles.add(role)
        if data.dept_ids:
            depts = await DeptDal(self.db).get_datas(limit=0, id=("in", data.dept_ids), v_return_objs=True)
            for dept in depts:
                obj.depts.add(dept)
        await self.flush(obj)
        return await self.out_dict(obj, v_options, v_return_obj, v_schema)

    async def put_data(
            self,
            data_id: int,
            data: schemas.UserUpdate,
            v_options: list[_AbstractLoad] = None,
            v_return_obj: bool = False,
            v_schema: Any = None
    ) -> Any:
        """
        更新用户信息
        :param data_id:
        :param data:
        :param v_options:
        :param v_return_obj:
        :param v_schema:
        :return:
        """
        obj = await self.get_data(data_id, v_options=[joinedload(self.model.roles), joinedload(self.model.depts)])
        data_dict = jsonable_encoder(data)
        for key, value in data_dict.items():
            if key == "role_ids":
                if value:
                    roles = await RoleDal(self.db).get_datas(limit=0, id=("in", value), v_return_objs=True)
                    if obj.roles:
                        obj.roles.clear()
                    for role in roles:
                        obj.roles.add(role)
                continue
            elif key == "dept_ids":
                if value:
                    depts = await DeptDal(self.db).get_datas(limit=0, id=("in", value), v_return_objs=True)
                    if obj.depts:
                        obj.depts.clear()
                    for dept in depts:
                        obj.depts.add(dept)
                continue
            setattr(obj, key, value)
        await self.flush(obj)
        return await self.out_dict(obj, None, v_return_obj, v_schema)

    async def reset_current_password(self, user: models.VadminUser, data: schemas.ResetPwd) -> None:
        """
        重置密碼
        :param user:
        :param data:
        :return:
        """
        if data.password != data.password_two:
            raise CustomException(msg="两次密碼不一致", code=400)
        result = test_password(data.password)
        if isinstance(result, str):
            raise CustomException(msg=result, code=400)
        user.password = self.model.get_password_hash(data.password)
        user.is_reset_password = True
        await self.flush(user)

    async def update_current_info(self, user: models.VadminUser, data: schemas.UserUpdateBaseInfo) -> Any:
        """
        更新當前用户基本信息
        :param user:
        :param data:
        :return:
        """
        if data.telephone != user.telephone:
            unique = await self.get_data(telephone=data.telephone, v_return_none=True)
            if unique:
                raise CustomException("帳號已存在！", code=status.HTTP_ERROR)
            else:
                user.telephone = data.telephone
        user.name = data.name
        user.nickname = data.nickname
        user.gender = data.gender
        await self.flush(user)
        return await self.out_dict(user)

    async def export_query_list(self, header: list, params: UserParams) -> dict:
        """
        导出用户查詢列表為 excel
        :param header:
        :param params:
        :return:
        """
        datas = await self.get_datas(
            **params.dict(),
            v_return_objs=True,
            v_options=[joinedload(self.model.depts), joinedload(self.model.roles)]
        )
        # 獲取表头
        row = list(map(lambda i: i.get("label"), header))
        rows = []
        options = await self.get_export_headers_options()
        for user in datas:
            data = []
            for item in header:
                field = item.get("field")
                # 通過反射獲取對应的属性值
                value = getattr(user, field, "")
                if field == "is_active":
                    value = "可用" if value else "停用"
                elif field == "is_staff":
                    value = "是" if value else "否"
                elif field == "gender":
                    result = list(filter(lambda i: i["value"] == value, options["gender_options"]))
                    value = result[0]["label"] if result else ""
                elif field == "roles":
                    value = ",".join([i.name for i in value])
                elif field == "depts":
                    value = ",".join([i.name for i in value])
                data.append(value)
            rows.append(data)
        em = ExcelManage()
        em.create_excel("用户列表")
        em.write_list(rows, row)
        remote_file_url = em.save_excel().get("remote_path")
        em.close()
        return {"url": remote_file_url, "filename": "用户列表.xlsx"}

    async def get_export_headers_options(self, include: list[str] = None) -> dict[str, list]:
        """
        獲取导出所需選擇項
        :param include: 包括的選擇項
        :return:
        """
        options = {}
        # 性别選擇項
        if include is None or 'gender' in include:
            gender_objs = await vadmin_system_crud.DictTypeDal(self.db).get_dicts_details(["sys_vadmin_gender"])
            sys_vadmin_gender = gender_objs.get("sys_vadmin_gender", [])
            gender_options = [{"label": i["label"], "value": i["value"]} for i in sys_vadmin_gender]
            options["gender_options"] = gender_options
        return options

    async def get_import_headers_options(self) -> None:
        """
        补全表头數據選項
        :return:
        """
        # 角色選擇項
        role_options = await RoleDal(self.db).get_datas(limit=0, v_return_objs=True, disabled=False, is_admin=False)
        role_item = self.import_headers[4]
        assert isinstance(role_item, dict)
        role_item["options"] = [{"label": role.name, "value": role.id} for role in role_options]

        # 性别選擇項
        gender_options = await vadmin_system_crud.DictTypeDal(self.db).get_dicts_details(["sys_vadmin_gender"])
        gender_item = self.import_headers[3]
        assert isinstance(gender_item, dict)
        sys_vadmin_gender = gender_options.get("sys_vadmin_gender")
        gender_item["options"] = [{"label": item["label"], "value": item["value"]} for item in sys_vadmin_gender]

    async def download_import_template(self) -> dict:
        """
        下載用户最新版导入模板
        :return:
        """
        await self.get_import_headers_options()
        em = WriteXlsx()
        em.create_excel(sheet_name="用户导入模板", save_static=True)
        em.generate_template(copy.deepcopy(self.import_headers))
        em.close()
        return {"url": em.get_file_url(), "filename": "用户导入模板.xlsx"}

    async def import_users(self, file: UploadFile) -> dict:
        """
        批量导入用户數據
        :param file:
        :return:
        """
        await self.get_import_headers_options()
        im = ImportManage(file, copy.deepcopy(self.import_headers))
        await im.get_table_data()
        im.check_table_data()
        for item in im.success:
            old_data_list = item.pop("old_data_list")
            data = schemas.UserIn(**item)
            try:
                await self.create_data(data)
            except ValueError as e:
                old_data_list.append(e.__str__())
                im.add_error_data(old_data_list)
            except Exception:
                old_data_list.append("創建失敗，請聯繫管理员！")
                im.add_error_data(old_data_list)
        return {
            "success_number": im.success_number,
            "error_number": im.error_number,
            "error_url": im.generate_error_url()
        }

    async def init_password(self, ids: list[int]) -> list:
        """
        初始化所選用户密碼
        将用户密碼改為系统默认密碼，並将初始化密碼状態改為false
        :param ids:
        :return:
        """
        users = await self.get_datas(limit=0, id=("in", ids), v_return_objs=True)
        result = []
        for user in users:
            # 重置密碼
            data = {"id": user.id, "telephone": user.telephone, "name": user.name, "email": user.email}
            password = generate_string(6)
            user.password = self.model.get_password_hash(password)
            user.is_reset_password = False
            self.db.add(user)
            data["reset_password_status"] = True
            data["password"] = password
            result.append(data)
        await self.db.flush()
        return result

    async def init_password_send_sms(self, ids: list[int], rd: Redis) -> list:
        """
        初始化所選用户密碼並發送通知短信
        将用户密碼改為系统默认密碼，並将初始化密碼状態改為false
        :param ids:
        :param rd:
        :return:
        """
        result = await self.init_password(ids)
        for user in result:
            if not user["reset_password_status"]:
                user["send_sms_status"] = False
                user["send_sms_msg"] = "重置密碼失敗"
                continue
            password = user.pop("password")
            sms = ResetPasswordSMS([user.get("telephone")], rd)
            try:
                send_result = (await sms.main_async(password=password))[0]
                user["send_sms_status"] = send_result
                user["send_sms_msg"] = "" if send_result else "短信發送失敗，請聯繫管理员"
            except CustomException as e:
                user["send_sms_status"] = False
                user["send_sms_msg"] = e.msg
        return result

    async def init_password_send_email(self, ids: list[int], rd: Redis) -> list:
        """
        初始化所選用户密碼並發送通知郵件
        将用户密碼改為系统默认密碼，並将初始化密碼状態改為false
        :param ids:
        :param rd:
        :return:
        """
        result = await self.init_password(ids)
        for user in result:
            if not user["reset_password_status"]:
                user["send_sms_status"] = False
                user["send_sms_msg"] = "重置密碼失敗"
                continue
            password: str = user.pop("password")
            email: str = user.get("email", None)
            if email:
                subject = "冰點智能-自助重置密碼"
                body = f"您好，您的 BDMES 密碼已經重置為{password}，請即時登錄並修改密碼。"
                es = EmailSender(rd)
                try:
                    send_result = await es.send_email([email], subject, body)
                    user["send_sms_status"] = send_result
                    user["send_sms_msg"] = "" if send_result else "短信發送失敗，請聯繫管理员"
                except CustomException as e:
                    user["send_sms_status"] = False
                    user["send_sms_msg"] = e.msg
            else:
                user["send_sms_status"] = False
                user["send_sms_msg"] = "未獲取到郵箱地址"
        return result

    async def update_current_avatar(self, user: models.VadminUser, file: UploadFile) -> str:
        """
        更新當前用户头像
        :param user:
        :param file:
        :return:
        """
        result = await AliyunOSS(BucketConf(**settings.ALIYUN_OSS)).upload_image("avatar", file)
        user.avatar = result
        await self.flush(user)
        return result

    async def update_wx_server_openid(self, code: str, user: models.VadminUser, redis: Redis) -> bool:
        """
        更新用户服務端微信平台openid
        :param code:
        :param user:
        :param redis:
        :return:
        """
        wx = WXOAuth(redis, 0)
        openid = await wx.parsing_openid(code)
        if not openid:
            return False
        user.is_wx_server_openid = True
        user.wx_server_openid = openid
        await self.flush(user)
        return True

    async def delete_datas(self, ids: list[int], v_soft: bool = False, **kwargs) -> None:
        """
        刪除多个用户，软刪除
        刪除后清空所關聯的角色
        :param ids: 數據集
        :param v_soft: 是否执行软刪除
        :param kwargs: 其他更新字段
        """
        options = [joinedload(self.model.roles)]
        objs = await self.get_datas(limit=0, id=("in", ids), v_options=options, v_return_objs=True)
        for obj in objs:
            if obj.roles:
                obj.roles.clear()
        return await super(UserDal, self).delete_datas(ids, v_soft, **kwargs)


class RoleDal(DalBase):

    def __init__(self, db: AsyncSession):
        super(RoleDal, self).__init__()
        self.db = db
        self.model = models.VadminRole
        self.schema = schemas.RoleSimpleOut

    async def create_data(
            self,
            data: schemas.RoleIn,
            v_options: list[_AbstractLoad] = None,
            v_return_obj: bool = False,
            v_schema: Any = None
    ) -> Any:
        """
        創建數據
        :param data:
        :param v_options:
        :param v_return_obj:
        :param v_schema:
        :return:
        """
        obj = self.model(**data.model_dump(exclude={'menu_ids', 'dept_ids'}))
        if data.menu_ids:
            menus = await MenuDal(db=self.db).get_datas(limit=0, id=("in", data.menu_ids), v_return_objs=True)
            for menu in menus:
                obj.menus.add(menu)
        if data.dept_ids:
            depts = await DeptDal(db=self.db).get_datas(limit=0, id=("in", data.dept_ids), v_return_objs=True)
            for dept in depts:
                obj.depts.add(dept)
        await self.flush(obj)
        return await self.out_dict(obj, v_options, v_return_obj, v_schema)

    async def put_data(
            self,
            data_id: int,
            data: schemas.RoleIn,
            v_options: list[_AbstractLoad] = None,
            v_return_obj: bool = False,
            v_schema: Any = None
    ) -> Any:
        """
        更新單個數據
        :param data_id:
        :param data:
        :param v_options:
        :param v_return_obj:
        :param v_schema:
        :return:
        """
        obj = await self.get_data(data_id, v_options=[joinedload(self.model.menus), joinedload(self.model.depts)])
        obj_dict = jsonable_encoder(data)
        for key, value in obj_dict.items():
            if key == "menu_ids":
                if value:
                    menus = await MenuDal(db=self.db).get_datas(limit=0, id=("in", value), v_return_objs=True)
                    if obj.menus:
                        obj.menus.clear()
                    for menu in menus:
                        obj.menus.add(menu)
                continue
            elif key == "dept_ids":
                if value:
                    depts = await DeptDal(db=self.db).get_datas(limit=0, id=("in", value), v_return_objs=True)
                    if obj.depts:
                        obj.depts.clear()
                    for dept in depts:
                        obj.depts.add(dept)
                continue
            setattr(obj, key, value)
        await self.flush(obj)
        return await self.out_dict(obj, None, v_return_obj, v_schema)

    async def get_role_menu_tree(self, role_id: int) -> list:
        role = await self.get_data(role_id, v_options=[joinedload(self.model.menus)])
        return [i.id for i in role.menus]

    async def get_select_datas(self) -> list:
        """
        獲取選擇數據，全部數據
        :return:
        """
        sql = select(self.model)
        queryset = await self.db.scalars(sql)
        return [schemas.RoleOptionsOut.model_validate(i).model_dump() for i in queryset.all()]

    async def delete_datas(self, ids: list[int], v_soft: bool = False, **kwargs) -> None:
        """
        刪除多个角色，硬刪除
        如果存在用户關聯则無法刪除
        :param ids: 數據集
        :param v_soft: 是否执行软刪除
        :param kwargs: 其他更新字段
        """
        user_count = await UserDal(self.db).get_count(v_join=[["roles"]], v_where=[models.VadminRole.id.in_(ids)])
        if user_count > 0:
            raise CustomException("無法刪除存在用户關聯的角色", code=400)
        return await super(RoleDal, self).delete_datas(ids, v_soft, **kwargs)


class MenuDal(DalBase):

    def __init__(self, db: AsyncSession):
        super(MenuDal, self).__init__()
        self.db = db
        self.model = models.VadminMenu
        self.schema = schemas.MenuSimpleOut

    async def get_tree_list(self, mode: int) -> list:
        """
        1：獲取選單树列表
        2：獲取選單树選擇項，添加/修改選單時使用
        3：獲取選單树列表，角色添加選單權限時使用
        :param mode:
        :return:
        """
        if mode == 3:
            sql = select(self.model).where(self.model.disabled == 0, self.model.is_delete == false())
        else:
            sql = select(self.model).where(self.model.is_delete == false())
        queryset = await self.db.scalars(sql)
        datas = list(queryset.all())
        roots = filter(lambda i: not i.parent_id, datas)
        if mode == 1:
            menus = self.generate_tree_list(datas, roots)
        elif mode == 2 or mode == 3:
            menus = self.generate_tree_options(datas, roots)
        else:
            raise CustomException("獲取選單失敗，無可用選項", code=400)
        return self.menus_order(menus)

    async def get_routers(self, user: models.VadminUser) -> list:
        """
        獲取路由表
        declare interface AppCustomRouteRecordRaw extends Omit<RouteRecordRaw, 'meta'> {
            name: string
            meta: RouteMeta
            component: string
            path: string
            redirect: string
            children?: AppCustomRouteRecordRaw[]
        }
        :param user:
        :return:
        """
        if any([i.is_admin for i in user.roles]):
            sql = select(self.model) \
                .where(self.model.disabled == 0, self.model.menu_type != "2", self.model.is_delete == false())
            queryset = await self.db.scalars(sql)
            datas = list(queryset.all())
        else:
            options = [joinedload(models.VadminUser.roles).subqueryload(models.VadminRole.menus)]
            user = await UserDal(self.db).get_data(user.id, v_options=options)
            datas = set()
            for role in user.roles:
                for menu in role.menus:
                    # 該路由没有被禁用，並且選單不是按钮
                    if not menu.disabled and menu.menu_type != "2":
                        datas.add(menu)
        roots = filter(lambda i: not i.parent_id, datas)
        menus = self.generate_router_tree(datas, roots)
        return self.menus_order(menus)

    def generate_router_tree(self, menus: list[models.VadminMenu], nodes: filter, name: str = "") -> list:
        """
        生成路由树
        :param menus: 总選單列表
        :param nodes: 节点選單列表
        :param name: name拼接，切记Name不能重复
        :return:
        """
        data = []
        for root in nodes:
            router = schemas.RouterOut.model_validate(root)
            router.name = name + "".join(name.capitalize() for name in router.path.split("/"))
            router.meta = schemas.Meta(
                title=root.title,
                icon=root.icon,
                hidden=root.hidden,
                alwaysShow=root.alwaysShow,
                noCache=root.noCache
            )
            if root.menu_type == "0":
                sons = filter(lambda i: i.parent_id == root.id, menus)
                router.children = self.generate_router_tree(menus, sons, router.name)
            data.append(router.model_dump())
        return data

    def generate_tree_list(self, menus: list[models.VadminMenu], nodes: filter) -> list:
        """
        生成選單树列表
        :param menus: 总選單列表
        :param nodes: 每层节点選單列表
        :return:
        """
        data = []
        for root in nodes:
            router = schemas.MenuTreeListOut.model_validate(root)
            if root.menu_type == "0" or root.menu_type == "1":
                sons = filter(lambda i: i.parent_id == root.id, menus)
                router.children = self.generate_tree_list(menus, sons)
            data.append(router.model_dump())
        return data

    def generate_tree_options(self, menus: list[models.VadminMenu], nodes: filter) -> list:
        """
        生成選單树選擇項
        :param menus:总選單列表
        :param nodes:每层节点選單列表
        :return:
        """
        data = []
        for root in nodes:
            router = {"value": root.id, "label": root.title, "order": root.order}
            if root.menu_type == "0" or root.menu_type == "1":
                sons = filter(lambda i: i.parent_id == root.id, menus)
                router["children"] = self.generate_tree_options(menus, sons)
            data.append(router)
        return data

    @classmethod
    def menus_order(cls, datas: list, order: str = "order", children: str = "children") -> list:
        """
        選單排序
        :param datas:
        :param order:
        :param children:
        :return:
        """
        result = sorted(datas, key=lambda menu: menu[order])
        for item in result:
            if item[children]:
                item[children] = sorted(item[children], key=lambda menu: menu[order])
        return result

    async def delete_datas(self, ids: list[int], v_soft: bool = False, **kwargs) -> None:
        """
        刪除多个選單
        如果存在角色關聯则無法刪除
        :param ids: 數據集
        :param v_soft: 是否执行软刪除
        :param kwargs: 其他更新字段
        :return:
        """
        count = await RoleDal(self.db).get_count(v_join=[["menus"]], v_where=[self.model.id.in_(ids)])
        if count > 0:
            raise CustomException("無法刪除存在角色關聯的選單", code=400)
        await super(MenuDal, self).delete_datas(ids, v_soft, **kwargs)


class DeptDal(DalBase):

    def __init__(self, db: AsyncSession):
        super(DeptDal, self).__init__()
        self.db = db
        self.model = models.VadminDept
        self.schema = schemas.DeptSimpleOut

    async def get_tree_list(self, mode: int) -> list:
        """
        1：獲取部門树列表
        2：獲取部門树選擇項，添加/修改部門時使用
        3：獲取部門树列表，用户添加部門權限時使用
        :param mode:
        :return:
        """
        if mode == 3:
            sql = select(self.model).where(self.model.disabled == 0, self.model.is_delete == false())
        else:
            sql = select(self.model).where(self.model.is_delete == false())
        queryset = await self.db.scalars(sql)
        datas = list(queryset.all())
        roots = filter(lambda i: not i.parent_id, datas)
        if mode == 1:
            menus = self.generate_tree_list(datas, roots)
        elif mode == 2 or mode == 3:
            menus = self.generate_tree_options(datas, roots)
        else:
            raise CustomException("獲取部門失敗，無可用選項", code=400)
        return self.dept_order(menus)

    def generate_tree_list(self, depts: list[models.VadminDept], nodes: filter) -> list:
        """
        生成部門树列表
        :param depts: 总部門列表
        :param nodes: 每层节点部門列表
        :return:
        """
        data = []
        for root in nodes:
            router = schemas.DeptTreeListOut.model_validate(root)
            sons = filter(lambda i: i.parent_id == root.id, depts)
            router.children = self.generate_tree_list(depts, sons)
            data.append(router.model_dump())
        return data

    def generate_tree_options(self, depts: list[models.VadminDept], nodes: filter) -> list:
        """
        生成部門树選擇項
        :param depts: 总部門列表
        :param nodes: 每层节点部門列表
        :return:
        """
        data = []
        for root in nodes:
            router = {"value": root.id, "label": root.name, "order": root.order}
            sons = filter(lambda i: i.parent_id == root.id, depts)
            router["children"] = self.generate_tree_options(depts, sons)
            data.append(router)
        return data

    @classmethod
    def dept_order(cls, datas: list, order: str = "order", children: str = "children") -> list:
        """
        部門排序
        :param datas:
        :param order:
        :param children:
        :return:
        """
        result = sorted(datas, key=lambda dept: dept[order])
        for item in result:
            if item[children]:
                item[children] = sorted(item[children], key=lambda dept: dept[order])
        return result


class TestDal(DalBase):

    def __init__(self, db: AsyncSession):
        super(TestDal, self).__init__()
        self.db = db
        self.model = models.VadminUser

    async def test_session_cache(self):
        """
        SQLAlchemy 會話（Session）缓存机制：
        當你通過一个會話查詢數據庫時，SQLAlchemy 首先检查这个對象是否已經在會話缓存中。如果是，它會直接从缓存中返回對象，而不是从數據庫重新加載。
        在一个會話中，對于具有相同主键的实体，會話缓存确保只有一个唯一的對象实例。这有助于维护數據的一致性。

        會話（Session）缓存：https://blog.csdn.net/k_genius/article/details/135491059
        :return:
        """
        print("==================================會話缓存====================================")
        await self.test_session_cache1()
        print("=============查詢出單個對象结果后，即使没有通過.訪問属性，同樣會產生缓存=============")
        await self.test_session_cache2()
        print("=============================數據列表會話缓存==================================")
        await self.test_session_cache3()
        print("=============================expire 單個對象過期==============================")
        await self.test_session_cache4()
        print("=========expire 單個對象過期后，重新訪問之前對象的属性也會重新查詢數據庫，但是不會重新加載關係==========")
        await self.test_session_cache5()

    async def test_session_cache1(self):
        """
        SQLAlchemy 會話（Session）缓存机制：
        當你通過一个會話查詢數據庫時，SQLAlchemy 首先检查这个對象是否已經在會話缓存中。如果是，它會直接从缓存中返回對象，而不是从數據庫重新加載。
        在一个會話中，對于具有相同主键的实体，會話缓存确保只有一个唯一的對象实例。这有助于维护數據的一致性。

        會話（Session）缓存：https://blog.csdn.net/k_genius/article/details/135491059

        示例：會話缓存

        :return:
        """
        # 第一次查詢，並加載用户的所有關聯部門項
        sql1 = select(models.VadminUser).where(models.VadminUser.id == 1).options(joinedload(models.VadminUser.depts))
        queryset1 = await self.db.scalars(sql1)
        user1 = queryset1.unique().first()
        print(f"用户編號：{user1.id} 用户姓名：{user1.name} 關聯部門 {[i.name for i in user1.depts]}")

        # 第二次即使没有加載用户關聯的部門，同樣可以訪問，因為这里會默认从會話缓存中獲取
        sql2 = select(models.VadminUser).where(models.VadminUser.id == 1)
        queryset2 = await self.db.scalars(sql2)
        user2 = queryset2.first()
        print(f"用户編號：{user2.id} 用户姓名：{user2.name} 關聯部門 {[i.name for i in user2.depts]}")

    async def test_session_cache2(self):
        """
        SQLAlchemy 會話（Session）缓存机制：
        當你通過一个會話查詢數據庫時，SQLAlchemy 首先检查这个對象是否已經在會話缓存中。如果是，它會直接从缓存中返回對象，而不是从數據庫重新加載。
        在一个會話中，對于具有相同主键的实体，會話缓存确保只有一个唯一的對象实例。这有助于维护數據的一致性。

        會話（Session）缓存：https://blog.csdn.net/k_genius/article/details/135491059

        示例：查詢出單個對象结果后，即使没有通過.訪問属性，同樣會產生缓存

        :return:
        """
        # 第一次查詢，並加載用户的所有關聯部門項，但是不訪問用户的属性
        sql1 = select(models.VadminUser).where(models.VadminUser.id == 1).options(joinedload(models.VadminUser.depts))
        queryset1 = await self.db.scalars(sql1)
        user1 = queryset1.unique().first()
        print(f"没有訪問属性，也會產生缓存")

        # 第二次即使没有加載用户關聯的部門，同樣可以訪問，因為这里會默认从會話缓存中獲取
        sql2 = select(models.VadminUser).where(models.VadminUser.id == 1)
        queryset2 = await self.db.scalars(sql2)
        user2 = queryset2.first()
        print(f"用户編號：{user2.id} 用户姓名：{user2.name} 關聯部門 {[i.name for i in user2.depts]}")

    async def test_session_cache3(self):
        """
        SQLAlchemy 會話（Session）缓存机制：
        當你通過一个會話查詢數據庫時，SQLAlchemy 首先检查这个對象是否已經在會話缓存中。如果是，它會直接从缓存中返回對象，而不是从數據庫重新加載。
        在一个會話中，對于具有相同主键的实体，會話缓存确保只有一个唯一的對象实例。这有助于维护數據的一致性。

        會話（Session）缓存：https://blog.csdn.net/k_genius/article/details/135491059

        示例：數據列表會話缓存

        :return:
        """
        # 第一次查詢出所有用户，並加載用户的所有關聯部門項
        sql1 = select(models.VadminUser).options(joinedload(models.VadminUser.depts))
        queryset1 = await self.db.scalars(sql1)
        datas1 = queryset1.unique().all()
        for data in datas1:
            print(f"用户編號：{data.id} 用户姓名：{data.name} 關聯部門 {[i.name for i in data.depts]}")

        # 第二次即使没有加載用户關聯的部門，同樣可以訪問，因為这里會默认从會話缓存中獲取
        sql2 = select(models.VadminUser)
        queryset2 = await self.db.scalars(sql2)
        datas2 = queryset2.all()
        for data in datas2:
            print(f"用户編號：{data.id} 用户姓名：{data.name} 關聯部門 {[i.name for i in data.depts]}")

    async def test_session_cache4(self):
        """
        SQLAlchemy 會話（Session）缓存机制：
        當你通過一个會話查詢數據庫時，SQLAlchemy 首先检查这个對象是否已經在會話缓存中。如果是，它會直接从缓存中返回對象，而不是从數據庫重新加載。
        在一个會話中，對于具有相同主键的实体，會話缓存确保只有一个唯一的對象实例。这有助于维护數據的一致性。

        會話（Session）缓存：https://blog.csdn.net/k_genius/article/details/135491059

        示例：expire 單個對象過期

        :return:
        """
        # 第一次查詢，並加載用户的所有關聯部門項
        sql1 = select(models.VadminUser).where(models.VadminUser.id == 1).options(joinedload(models.VadminUser.depts))
        queryset1 = await self.db.scalars(sql1)
        user1 = queryset1.unique().first()
        print(f"用户編號：{user1.id} 用户姓名：{user1.name} 關聯部門 {[i.name for i in user1.depts]}")

        # 使當前會話（Session）中的 user1 對象過期，再次訪問就會重新查詢數據庫數據
        self.db.expire(user1)

        # 第二次查詢會发现會話中没有該對象的缓存，會重新在數據庫中查詢
        sql2 = select(models.VadminUser).where(models.VadminUser.id == 1)
        queryset2 = await self.db.scalars(sql2)
        user2 = queryset2.first()
        try:
            print(f"用户編號：{user2.id} 用户姓名：{user2.name} 關聯部門 {[i.name for i in user2.depts]}")
        except StatementError:
            print("訪問部門報錯了！！！！！")

    async def test_session_cache5(self):
        """
        SQLAlchemy 會話（Session）缓存机制：
        當你通過一个會話查詢數據庫時，SQLAlchemy 首先检查这个對象是否已經在會話缓存中。如果是，它會直接从缓存中返回對象，而不是从數據庫重新加載。
        在一个會話中，對于具有相同主键的实体，會話缓存确保只有一个唯一的對象实例。这有助于维护數據的一致性。

        會話（Session）缓存：https://blog.csdn.net/k_genius/article/details/135491059

        示例：expire 單個對象過期后，重新訪問之前對象的属性也會重新查詢數據庫，但是不會重新加載關係

        :return:
        """
        # 第一次查詢，並加載用户的所有關聯部門項
        sql = select(models.VadminUser).where(models.VadminUser.id == 1).options(joinedload(models.VadminUser.depts))
        queryset = await self.db.scalars(sql)
        user = queryset.unique().first()
        print(f"用户編號：{user.id} 用户姓名：{user.name} 關聯部門 {[i.name for i in user.depts]}")

        # 使當前會話（Session）中的 user9 對象過期，再次訪問就會重新查詢數據庫數據
        self.db.expire(user)

        # 第二次查詢會发现會話中没有該對象的缓存，會重新在數據庫中查詢，但是不會重新加載關係
        try:
            print(f"用户編號：{user.id} 用户姓名：{user.name} 關聯部門 {[i.name for i in user.depts]}")
        except StatementError:
            print("訪問部門報錯了！！！！！")

    async def test_join_form(self):
        """
        join_form 使用示例：通過關聯表的查詢條件反查詢出主表的數據

        官方描述：在當前 Select 的左侧不符合我们想要从中進行连接的情况下，可以使用 Select.join_from() 方法
        官方文檔：https://docs.sqlalchemy.org/en/20/orm/queryguide/select.html#setting-the-leftmost-from-clause-in-a-join

        查詢條件：獲取指定用户所關聯的所有部門列表數據，只返回關聯的部門列表數據
        :return:
        """
        # 设定用户編號為：1
        user_id = 1

        sql = select(models.VadminDept).where(models.VadminDept.is_delete == false())
        sql = sql.join_from(models.VadminUser, models.VadminUser.depts).where(models.VadminUser.id == user_id)
        queryset = await self.db.scalars(sql)
        result = queryset.unique().all()
        for dept in result:
            print(f"部門編號：{dept.id} 部門名稱：{dept.name} 部門負責人：{dept.owner}")

        # 转换后的 SQL：
        # SELECT
        # 	vadmin_auth_dept.NAME,
        # 	vadmin_auth_dept.dept_key,
        # 	vadmin_auth_dept.disabled,
        # 	vadmin_auth_dept.order,
        # 	vadmin_auth_dept.desc,
        # 	vadmin_auth_dept.OWNER,
        # 	vadmin_auth_dept.phone,
        # 	vadmin_auth_dept.email,
        # 	vadmin_auth_dept.parent_id,
        # 	vadmin_auth_dept.id,
        # 	vadmin_auth_dept.create_datetime,
        # 	vadmin_auth_dept.update_datetime,
        # 	vadmin_auth_dept.delete_datetime,
        # 	vadmin_auth_dept.is_delete
        # FROM
        # 	vadmin_auth_user
        # 	JOIN vadmin_auth_user_depts ON vadmin_auth_user.id = vadmin_auth_user_depts.user_id
        # 	JOIN vadmin_auth_dept ON vadmin_auth_dept.id = vadmin_auth_user_depts.dept_id
        # WHERE
        # 	vadmin_auth_dept.is_delete = FALSE
        # 	AND vadmin_auth_user.id = 1

    async def test_left_join(self):
        """
        多對多左连接查詢示例：
        查詢出所有用户信息，並加載用户關聯所有部門，左连接條件：只需要查詢出該用户關聯的部門負責人為"張偉"的部門即可，其他部門不需要显示，
        :return:
        """
        # 封装查詢语句
        dept_alias = aliased(models.VadminDept)
        v_options = [contains_eager(self.model.depts, alias=dept_alias)]
        v_outer_join = [
            [models.vadmin_auth_user_depts, self.model.id == models.vadmin_auth_user_depts.c.user_id],
            [dept_alias, and_(dept_alias.id == models.vadmin_auth_user_depts.c.dept_id, dept_alias.owner == "張偉")]
        ]
        datas: list[models.VadminUser] = await self.get_datas(
            limit=0,
            v_outer_join=v_outer_join,
            v_options=v_options,
            v_return_objs=True,
            v_expire_all=True
        )
        for data in datas:
            print(f"用户編號：{data.id} 用户名稱：{data.name} 共查詢出關聯的部門負責人為‘張偉’的部門有如下：")
            for dept in data.depts:
                print(f"      部門編號：{dept.id} 部門名稱：{dept.name} 部門負責人：{dept.owner}")

        # 原查詢语句：
        # DeptAlias = aliased(models.VadminDept)
        # sql = select(self.model).where(self.model.is_delete == false())
        # sql = sql.options(contains_eager(self.model.depts, alias=DeptAlias))
        # sql = sql.outerjoin(models.vadmin_auth_user_depts, self.model.id == models.vadmin_auth_user_depts.c.user_id)
        # sql = sql.outerjoin(
        #     DeptAlias,
        #     and_(DeptAlias.id == models.vadmin_auth_user_depts.c.dept_id, DeptAlias.owner == "張偉")
        # )
        # self.db.expire_all()
        # queryset = await self.db.scalars(sql)
        # result = queryset.unique().all()
        # for data in result:
        #     print(f"用户編號：{data.id} 用户名稱：{data.name} 共查詢出關聯的部門負責人為‘張偉’的部門有如下：")
        #     for dept in data.depts:
        #         print(f"      部門編號：{dept.id} 部門名稱：{dept.name} 部門負責人：{dept.owner}")

    async def get_user_depts(self):
        """
        獲取用户部門列表
        :return:
        """
        sql1 = select(models.VadminUser).options(joinedload(models.VadminUser.depts))
        queryset1 = await self.db.scalars(sql1)
        datas1 = queryset1.unique().all()
        for data in datas1:
            print(f"用户編號：{data.id} 用户姓名：{data.name} 關聯部門 {[i.name for i in data.depts]}")

    async def relationship_where_operations_any(self):
        """
        關係运算符操作：any 方法使用示例
        官方文檔： https://docs.sqlalchemy.org/en/20/orm/queryguide/select.html#relationship-where-operators

        any 方法用于一對多關係中，允许在 any 方法中指定一个條件，該條件會生成一个 SQL 表达式，只有满足該條件的元素才會被查詢出来。
        :return:
        """
        print("==============================any 方法使用案例1=========================================")
        # 用户表（models.VadminUser）与 部門表（VadminDept）為多對多關係
        # 查找出只有满足關聯了部門名稱為 "人事一部" 的所有用户，没有關聯的则不會查詢出来
        sql1 = select(models.VadminUser).where(models.VadminUser.depts.any(models.VadminDept.name == "人事一部"))
        queryset1 = await self.db.scalars(sql1)
        result1 = queryset1.unique().all()
        for data in result1:
            print(f"用户編號：{data.id} 用户名稱：{data.name}")

        print("==============================any 方法使用案例2=========================================")
        # 案例1 取反，查找出只有满足没有關聯了部門名稱為 "人事一部" 的所有用户，關聯的则不會查詢出来
        sql2 = select(models.VadminUser).where(~models.VadminUser.depts.any(models.VadminDept.name == "人事一部"))
        queryset2 = await self.db.scalars(sql2)
        result2 = queryset2.unique().all()
        for data in result2:
            print(f"用户編號：{data.id} 用户名稱：{data.name}")

        print("==============================any 方法使用案例3=========================================")
        # 查詢出没有關聯部門的所有用户
        sql3 = select(models.VadminUser).where(~models.VadminUser.depts.any())
        queryset3 = await self.db.scalars(sql3)
        result3 = queryset3.unique().all()
        for data in result3:
            print(f"用户編號：{data.id} 用户名稱：{data.name}")

    async def relationship_where_operations_has(self):
        """
        關係运算符操作： has 方法使用示例
        官方文檔： https://docs.sqlalchemy.org/en/20/orm/queryguide/select.html#relationship-where-operators

        has 方法用于多對一關係中，与 any 方法使用方式同理，只有满足條件的元素才會被查詢出来。

        對多關係中使用 has 方法會報錯，報錯内容如下：
        sqlalchemy.exc.InvalidRequestError: 'has()' not implemented for collections.  Use any().
        :return:
        """
        print("==============================has 方法使用案例1=========================================")
        # 用户（models.VadminUser）与 帮助問题（models.VadminIssue）為多對一關係
        # 查找出只有满足關聯了用户名稱為 "kinit" 的所有帮助問题，没有關聯的则不會查詢出来
        sql1 = select(vadmin_help_models.VadminIssue).where(
            vadmin_help_models.VadminIssue.create_user.has(models.VadminUser.name == "kinit")
        )
        queryset1 = await self.db.scalars(sql1)
        result1 = queryset1.unique().all()
        for data in result1:
            print(f"問题編號：{data.id} 問题標题：{data.title}")
