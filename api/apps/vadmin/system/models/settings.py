#!/usr/bin/python
# -*- coding: utf-8 -*-
# @version        : 1.0
# @Create Time    : 2022/7/7 13:41
# @File           : settings.py
# @IDE            : PyCharm
# @desc           : 系统字典模型
from sqlalchemy.orm import relationship, Mapped, mapped_column
from db.db_base import BaseModel
from sqlalchemy import String, Integer, ForeignKey, Boolean, Text


class VadminSystemSettingsTab(BaseModel):
    __tablename__ = "vadmin_system_settings_tab"
    __table_args__ = ({'comment': '系统配置分类表'})

    title: Mapped[str] = mapped_column(String(255), comment="標题")
    classify: Mapped[str] = mapped_column(String(255), index=True, nullable=False, comment="分类键")
    tab_label: Mapped[str] = mapped_column(String(255), comment="tab標题")
    tab_name: Mapped[str] = mapped_column(String(255), index=True, nullable=False, unique=True, comment="tab標识符")
    hidden: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否隐藏")
    disabled: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否禁用")

    settings: Mapped[list["VadminSystemSettings"]] = relationship(back_populates="tab")


class VadminSystemSettings(BaseModel):
    __tablename__ = "vadmin_system_settings"
    __table_args__ = ({'comment': '系统配置表'})

    config_label: Mapped[str] = mapped_column(String(255), comment="配置表標籤")
    config_key: Mapped[str] = mapped_column(String(255), index=True, nullable=False, unique=True, comment="配置表键")
    config_value: Mapped[str | None] = mapped_column(Text, comment="配置表内容")
    remark: Mapped[str | None] = mapped_column(String(255), comment="备注信息")
    disabled: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否禁用")

    tab_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("vadmin_system_settings_tab.id", ondelete='CASCADE'),
        comment="關聯tab標籤"
    )
    tab: Mapped[VadminSystemSettingsTab] = relationship(foreign_keys=tab_id, back_populates="settings")
