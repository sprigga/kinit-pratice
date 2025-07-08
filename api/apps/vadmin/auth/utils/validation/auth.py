# -*- coding: utf-8 -*-
# @version        : 1.0
# @Create Time    : 2021/10/24 16:44
# @File           : auth.py
# @IDE            : PyCharm
# @desc           : 用户凭證驗證装饰器

from fastapi import Request
import jwt
from pydantic import BaseModel
from application import settings
from sqlalchemy.ext.asyncio import AsyncSession
from apps.vadmin.auth.models import VadminUser
from core.exception import CustomException
from utils import status
from datetime import timedelta, datetime
from apps.vadmin.auth.crud import UserDal


class Auth(BaseModel):
    user: VadminUser = None
    db: AsyncSession
    data_range: int | None = None
    dept_ids: list | None = []

    class Config:
        # 接收任意類型
        arbitrary_types_allowed = True


class AuthValidation:
    """
    用于用户每次調用接口時，驗證用户提交的token是否正确，並从token中獲取用户信息
    """

    # status_code = 401 時，表示强制要求重新登錄，因账号已冻结，账号已過期，帳號碼錯误，刷新token無效等問题导致
    # 只有 code = 401 時，表示 token 過期，要求刷新 token
    # 只有 code = 錯误值時，只是報錯，不重新登陆
    error_code = status.HTTP_401_UNAUTHORIZED
    warning_code = status.HTTP_ERROR

    # status_code = 403 時，表示强制要求重新登錄，因無系统權限，而進入到系统訪問等問题导致

    @classmethod
    def validate_token(cls, request: Request, token: str | None) -> tuple[str, bool]:
        """
        驗證用户 token
        """
        if not token:
            raise CustomException(
                msg="請您先登錄！",
                code=status.HTTP_403_FORBIDDEN,
                status_code=status.HTTP_403_FORBIDDEN
            )
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            telephone: str = payload.get("sub")
            exp: int = payload.get("exp")
            is_refresh: bool = payload.get("is_refresh")
            password: bool = payload.get("password")
            if not telephone or is_refresh or not password:
                raise CustomException(
                    msg="未認證，請您重新登錄",
                    code=status.HTTP_403_FORBIDDEN,
                    status_code=status.HTTP_403_FORBIDDEN
                )
            # 计算當前時間 + 缓冲時間是否大于等于 JWT 過期時間
            buffer_time = (datetime.now() + timedelta(minutes=settings.ACCESS_TOKEN_CACHE_MINUTES)).timestamp()
            # print("過期時間", exp, datetime.fromtimestamp(exp))
            # print("當前時間", buffer_time, datetime.fromtimestamp(buffer_time))
            # print("剩余時間", exp - buffer_time)
            if buffer_time >= exp:
                request.scope["if-refresh"] = 1
            else:
                request.scope["if-refresh"] = 0
        except (jwt.exceptions.InvalidSignatureError, jwt.exceptions.DecodeError):
            raise CustomException(
                msg="無效認證，請您重新登錄",
                code=status.HTTP_403_FORBIDDEN,
                status_code=status.HTTP_403_FORBIDDEN
            )
        except jwt.exceptions.ExpiredSignatureError:
            raise CustomException(msg="認證已失效，請您重新登錄", code=cls.error_code, status_code=cls.error_code)
        return telephone, password

    @classmethod
    async def validate_user(cls, request: Request, user: VadminUser, db: AsyncSession, is_all: bool = True) -> Auth:
        """
        驗證用户信息
        :param request:
        :param user:
        :param db:
        :param is_all: 是否所有人訪問，不加權限
        :return:
        """
        if user is None:
            raise CustomException(msg="未認證，請您重新登陸", code=cls.error_code, status_code=cls.error_code)
        elif not user.is_active:
            raise CustomException(msg="用户已被凍結！", code=cls.error_code, status_code=cls.error_code)
        request.scope["telephone"] = user.telephone
        request.scope["user_id"] = user.id
        request.scope["user_name"] = user.name
        try:
            request.scope["body"] = await request.body()
        except RuntimeError:
            request.scope["body"] = "獲取失敗"
        if is_all:
            return Auth(user=user, db=db)
        data_range, dept_ids = await cls.get_user_data_range(user, db)
        return Auth(user=user, db=db, data_range=data_range, dept_ids=dept_ids)

    @classmethod
    def get_user_permissions(cls, user: VadminUser) -> set:
        """
        獲取员工用户所有權限列表
        :param user: 用户实例
        :return:
        """
        if user.is_admin():
            return {'*.*.*'}
        permissions = set()
        for role_obj in user.roles:
            for menu in role_obj.menus:
                if menu.perms and not menu.disabled:
                    permissions.add(menu.perms)
        return permissions

    @classmethod
    async def get_user_data_range(cls, user: VadminUser, db: AsyncSession) -> tuple:
        """
        獲取用户數據范围
        0 仅本人數據權限  create_user_id 查詢
        1 本部門數據權限  部門 id 左连接查詢
        2 本部門及以下數據權限 部門 id 左连接查詢
        3 自定义數據權限  部門 id 左连接查詢
        4 全部數據權限  無
        :param user:
        :param db:
        :return:
        """
        if user.is_admin():
            return 4, ["*"]
        data_range = max([i.data_range for i in user.roles])
        dept_ids = set()
        if data_range == 0:
            pass
        elif data_range == 1:
            for dept in user.depts:
                dept_ids.add(dept.id)
        elif data_range == 2:
            # 递归獲取部門列表
            dept_ids = await UserDal(db).recursion_get_dept_ids(user)
        elif data_range == 3:
            for role_obj in user.roles:
                for dept in role_obj.depts:
                    dept_ids.add(dept.id)
        elif data_range == 4:
            dept_ids.add("*")
        return data_range, list(dept_ids)
