#!/usr/bin/python
# -*- coding: utf-8 -*-
# @version        : 1.0
# @Create Time    : 2023/08/24 22:19
# @File           : excel_schema.py
# @IDE            : PyCharm
# @desc           :

from pydantic import BaseModel, Field


class AlignmentModel(BaseModel):
    horizontal: str = Field('center', description="水平對齊方式。可選值：'left'、'center'、'right'、'justify'、'distributed'")
    vertical: str = Field('center', description="垂直對齊方式。可選值：'top'、'center'、'bottom'、'justify'、'distributed'")
    textRotation: int = Field(0, description="文本旋轉角度（以度為單位）。默認為 0。")
    wrapText: bool = Field(None, description="自動換行文本。設置為 True 時，如果文本內容超出儲存格寬度，會自動換行顯示。")
    shrinkToFit: bool = Field(
        None,
        description="縮小字體以適應儲存格。設置為 True 時，如果文本內容超出儲存格寬度，會自動縮小字體大小以適應。"
    )
    indent: int = Field(0, description="文本縮排級別。默認為 0。")
    relativeIndent: int = Field(0, description="相對縮排級別。默認為 0。")
    justifyLastLine: bool = Field(
        None,
        description="對齊換行文本的末尾行。設置為 True 時，如果設置了文本換行，末尾的行也會被對齊。"
    )
    readingOrder: int = Field(0, description="閱讀順序。默認為 0。")

    class Config:
        title = "對齊設置模型"
        description = "用於設置儲存格內容的對齊樣式。"


class FontModel(BaseModel):
    name: str = Field(None, description="字體名稱")
    size: float = Field(None, description="字體大小（磅為單位）")
    bold: bool = Field(None, description="是否加粗")
    italic: bool = Field(None, description="是否斜體")
    underline: str = Field(None, description="下劃線樣式。可選值：'single'、'double'、'singleAccounting'、'doubleAccounting'")
    strikethrough: bool = Field(None, description="是否有刪除線")
    outline: bool = Field(None, description="是否輪廓字體")
    shadow: bool = Field(None, description="是否陰影字體")
    condense: bool = Field(None, description="是否壓縮字體")
    extend: bool = Field(None, description="是否擴展字體")
    vertAlign: str = Field(None, description="垂直對齊方式。可選值：'superscript'、'subscript'、'baseline'")
    color: dict = Field(None, description="字體顏色")
    scheme: str = Field(None, description="字體方案。可選值：'major'、'minor'")
    charset: int = Field(None, description="字符集編號")
    family: int = Field(None, description="字體族編號")

    class Config:
        title = "字體設置模型"
        description = "用於設置儲存格內容的字體樣式"


class PatternFillModel(BaseModel):
    start_color: str = Field("FFFFFF", description="起始顏色（RGB 值或顏色名稱）")
    end_color: str = Field("FFFFFF", description="結束顏色（RGB 值或顏色名稱）")
    fill_type: str = Field("solid", description="填充類型（'none'、'solid'、'darkDown' 等）")

    class Config:
        title = "填充模式設置模型"
        description = "儲存格的填充模式設置"
