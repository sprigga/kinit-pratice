from typing import Any
from pydantic import BaseModel, Field
from datetime import date


class SchemaField(BaseModel):
    name: str = Field(..., title="字段名稱")
    field_type: str = Field(..., title="字段類型")
    nullable: bool = Field(False, title="是否可為空")
    default: Any = Field(None, title="默認值")
    title: str | None = Field(None, title="字段描述")
    max_length: int | None = Field(None, title="最大長度")
