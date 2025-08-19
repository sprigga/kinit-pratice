from sqlalchemy.orm import Mapped, mapped_column
from db.db_base import BaseModel
from sqlalchemy import String, Boolean, Integer, ForeignKey, Float


class BpminIt(BaseModel):
    __tablename__ = "Bpmin_it"
    __table_args__ = ({'comment': 'IT service request form'})

    it_manager: Mapped[str | None] = mapped_column(String(100), comment="IT經理")
    dept: Mapped[str | None] = mapped_column(String(50), comment="部門")
    apply_date: Mapped[str | None] = mapped_column(String(20), comment="申請日期")
    extension: Mapped[str | None] = mapped_column(String(20), comment="分機號碼")
    fillman: Mapped[str | None] = mapped_column(String(100), comment="填表人")
    main_apply_item: Mapped[str | None] = mapped_column(String(200), comment="申請項目")
    sub_apply_item: Mapped[str | None] = mapped_column(String(200), comment="子申請項目")
    request_desc: Mapped[str | None] = mapped_column(String(500), comment="需求描述")
    it_undertaker: Mapped[str | None] = mapped_column(String(100), comment="IT承辦人")
    treatment: Mapped[str | None] = mapped_column(String(500), comment="處理方式")
    serial_number: Mapped[str | None] = mapped_column(String(50), comment="序號")
    datediff: Mapped[float | None] = mapped_column(Float, comment="處理天數")

    create_user: Mapped[str | None] = mapped_column(String(30), comment="建立者工號")
    update_user: Mapped[str | None] = mapped_column(String(30), comment="更新者")
    delete_user: Mapped[str | None] = mapped_column(String(30), comment="刪除者")

    # Configuration for frontend generation
    column_config = {
        'id': {
            'label': '編號',
            'field_type': 'input',
            'show_in_list': True,
            'show_in_search': False,
            'required': False
        },
        'it_manager': {
            'label': 'IT經理',
            'field_type': 'input',
            'show_in_list': True,
            'show_in_search': True,
            'required': False
        },
        'dept': {
            'label': '部門',
            'field_type': 'input',
            'show_in_list': True,
            'show_in_search': True,
            'required': False
        },
        'apply_date': {
            'label': '申請日期',
            'field_type': 'date',
            'show_in_list': True,
            'show_in_search': True,
            'required': False
        },
        'extension': {
            'label': '分機號碼',
            'field_type': 'input',
            'show_in_list': True,
            'show_in_search': True,
            'required': False
        },
        'fillman': {
            'label': '填表人',
            'field_type': 'input',
            'show_in_list': True,
            'show_in_search': True,
            'required': False
        },
        'apply_item': {
            'label': '申請項目',
            'field_type': 'input',
            'show_in_list': True,
            'show_in_search': True,
            'required': False
        },
        'sub_apply_item': {
            'label': '子申請項目',
            'field_type': 'input',
            'show_in_list': True,
            'show_in_search': True,
            'required': False
        },
        'request_desc': {
            'label': '需求描述',
            'field_type': 'textarea',
            'show_in_list': True,
            'show_in_search': True,
            'required': False
        },
        'it_undertaker': {
            'label': 'IT承辦人',
            'field_type': 'input',
            'show_in_list': True,
            'show_in_search': True,
            'required': False
        },
        'treatment': {
            'label': '處理方式',
            'field_type': 'textarea',
            'show_in_list': True,
            'show_in_search': True,
            'required': False
        },
        'serial_number': {
            'label': '序號',
            'field_type': 'input',
            'show_in_list': True,
            'show_in_search': True,
            'required': False
        },
         'datediff': {
            'label': '處理天數',
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