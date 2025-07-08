# -*- coding: utf-8 -*-
# @version        : 1.0
# @Create Time    : 2021/10/24 16:44
# @File           : current.py
# @IDE            : PyCharm
# @desc           : 獲取認證后的信息工具

from typing import Annotated, Optional, Set
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from apps.vadmin.auth.crud import UserDal
from apps.vadmin.auth.models import VadminUser, VadminRole
from core.exception import CustomException
from utils import status
from .validation import AuthValidation, LoginForm
from fastapi import Request, Depends
from application import settings
from core.database import db_getter
from .validation.auth import Auth


class OpenAuth(AuthValidation):

    """
    开放認證，無認證也可以訪問
    認證了以后可以獲取到用户信息，無認證则獲取不到
    """

    async def __call__(
        self,
        request: Request,
        token: Annotated[str, Depends(settings.oauth2_scheme)],
        db: AsyncSession = Depends(db_getter)
    ):
        """
        每次調用依赖此类的接口會执行該方法
        """
        if not settings.OAUTH_ENABLE:
            return Auth(db=db)
        try:
            telephone, password = self.validate_token(request, token)
            user = await UserDal(db).get_data(telephone=telephone, password=password, v_return_none=True)
            return await self.validate_user(request, user, db, is_all=True)
        except CustomException:
            return Auth(db=db)


class AllUserAuth(AuthValidation):

    """
    支持所有用户認證
    獲取用户基本信息
    """

    async def __call__(
        self,
        request: Request,
        token: str = Depends(settings.oauth2_scheme),
        db: AsyncSession = Depends(db_getter)
    ):
        """
        每次調用依赖此类的接口會执行該方法
        """
        if not settings.OAUTH_ENABLE:
            return Auth(db=db)
        telephone, password = self.validate_token(request, token)
        user = await UserDal(db).get_data(telephone=telephone, password=password, v_return_none=True)
        return await self.validate_user(request, user, db, is_all=True)


class FullAdminAuth(AuthValidation):

    """
    只支持员工用户認證
    獲取员工用户完整信息
    如果有權限，那么會驗證該用户是否包括權限列表中的其中一个權限
    """

    def __init__(self, permissions: list[str] | None = None):
        if permissions:
            self.permissions = set(permissions)
        else:
            self.permissions = None

    async def __call__(
        self,
        request: Request,
        token: str = Depends(settings.oauth2_scheme),
        db: AsyncSession = Depends(db_getter)
    ) -> Auth:
        """
        每次調用依赖此类的接口會执行該方法
        """
        if not settings.OAUTH_ENABLE:
            return Auth(db=db)
        telephone, password = self.validate_token(request, token)
        options = [
            joinedload(VadminUser.roles).subqueryload(VadminRole.menus),
            joinedload(VadminUser.roles).subqueryload(VadminRole.depts),
            joinedload(VadminUser.depts)
        ]
        user = await UserDal(db).get_data(
            telephone=telephone,
            password=password,
            v_return_none=True,
            v_options=options,
            is_staff=True
        )
        result = await self.validate_user(request, user, db, is_all=False)
        permissions = self.get_user_permissions(user)
        if permissions != {'*.*.*'} and self.permissions:
            if not (self.permissions & permissions):
                raise CustomException(msg="無權限操作", code=status.HTTP_403_FORBIDDEN)
        return result



class ManualVerifyAuth:
    """
    ✅ 手動帳密驗證，僅回傳該使用者的權限列表（前端自行判斷是否有權限）
    """

    def __init__(self):
        pass

    async def __call__(
        self,
        data: LoginForm,
        db: AsyncSession = Depends(db_getter)
    ) -> Set[str]:
        user = await UserDal(db).get_data(
            telephone=data.telephone,
            v_return_none=True,
            v_options=[
                joinedload(VadminUser.roles).subqueryload(VadminRole.menus)
            ]
        )

        if not user or not VadminUser.verify_password(data.password, user.password):
            raise CustomException(msg="帳號或密碼錯誤", code=status.HTTP_401_UNAUTHORIZED)

        # 整理使用者擁有的權限
        is_admin = any(getattr(role, "is_admin", False) for role in user.roles)
        if is_admin:
            permission_codes = {"*.*.*"}
        else:
            permission_codes = {
                menu.perms
                for role in user.roles
                for menu in role.menus
                if menu.perms
            }

        return permission_codes
