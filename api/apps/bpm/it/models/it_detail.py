from sqlalchemy.orm import Mapped, mapped_column
from db.db_base import BaseModel
from sqlalchemy import String


class BpminItDetail(BaseModel):
    __tablename__ = "Bpmin_it_detail"
    __table_args__ = ({'comment': 'IT service request details'})

 
    work_desc: Mapped[str | None] = mapped_column(String(500), comment="工作描述")
    rsn: Mapped[str | None] = mapped_column(String(50), comment="參照序號")
    status: Mapped[str | None] = mapped_column(String(50), comment="狀態")

    # Configuration for frontend generation
    column_config = {
        'work_desc': {
            'label': '需求描述',
            'field_type': 'textarea',
            'show_in_list': True,
            'show_in_search': True,
            'required': False
        },
        'rsn': {
            'label': '參照序號',
            'field_type': 'input',
            'show_in_list': True,
            'show_in_search': True,
            'required': False
        },
         'status': {
            'label': '狀態',
            'field_type': 'input',
            'show_in_list': True,
            'show_in_search': True,
            'required': False
        },
        'create_datetime': {
            'label': '創建時間',
            'field_type': 'date',
            'show_in_list': True,
            'show_in_search': False,
            'required': False
        },
        'update_datetime': {
            'label': '更新時間',
            'field_type': 'date',
            'show_in_list': True,
            'show_in_search': False,
            'required': False
        }
    }