# -*- coding: utf-8 -*-
# @version        : 1.0
# @Create Time    : 2021/10/18 22:19
# @File           : db_base.py
# @IDE            : PyCharm
# @desc           : 數據庫公共 ORM 模型

from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from core.database import Base
from sqlalchemy import DateTime, Integer, func, Boolean, inspect, String


# 使用命令：alembic init alembic 初始化迁移數據庫环境
# 这時會生成alembic文件夹 和 alembic.ini文件
class BaseModel(Base):
    """
    公共 ORM 模型，基表
    """
    __abstract__ = True


    id:  Mapped[int] = mapped_column(Integer, primary_key=True, comment='主鍵ID')
    create_datetime: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False, comment="創建時間"
    )
    update_datetime: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新時間"
    )
    delete_datetime: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment='刪除時間')
    is_delete: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否軟刪除")

    # 新增 操作用戶 欄位
    create_user: Mapped[str | None] = mapped_column(String(30), nullable=True, comment='建立者')
    update_user: Mapped[str | None] = mapped_column(String(30), nullable=True, comment='更新者')
    delete_user: Mapped[str | None] = mapped_column(String(30), nullable=True, comment='刪除者')


    @classmethod
    def get_column_attrs(cls) -> list:
        """
        獲取模型中除 relationships 外的所有字段名稱
        :return:
        """
        mapper = inspect(cls)

        # for attr_name, column_property in mapper.column_attrs.items():
        #     # 假设它是单列属性
        #     column = column_property.columns[0]
        #     # 訪問各种属性
        #     print(f"属性: {attr_name}")
        #     print(f"類型: {column.type}")
        #     print(f"默认值: {column.default}")
        #     print(f"服務器默认值: {column.server_default}")

        return mapper.column_attrs.keys()

    @classmethod
    def get_attrs(cls) -> list:
        """
        獲取模型所有字段名稱
        :return:
        """
        mapper = inspect(cls)
        return mapper.attrs.keys()

    @classmethod
    def get_relationships_attrs(cls) -> list:
        """
        獲取模型中 relationships 所有字段名稱
        :return:
        """
        mapper = inspect(cls)
        return mapper.relationships.keys()

    # **透過 `__mapper_args__` 檢查是否繼承 `id`**
    @classmethod
    def __declare_last__(cls):
        if "uuid" in cls.__table__.columns:
            cls.__mapper_args__ = {"primary_key": [cls.__table__.c.uuid]}
