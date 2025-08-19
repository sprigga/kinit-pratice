#!/usr/bin/python
# -*- coding: utf-8 -*-
# @version        : 1.0
# @Create Time    : 2025/08/04 13:34
# @File           : bpmin_it.py
# @IDE            : PyCharm
# @desc           : 資訊需求單服務層

from typing import Dict, Any
from .. import models, schemas, crud
import re
from datetime import datetime
from sqlalchemy import select, desc
from sqlalchemy.sql.selectable import Select
from ..models.it_detail import BpminItDetail

# 條件性導入 BPM WSDL 模組
try:
    from utils.bpm_wsdl import bpm_wsl
    # 檢查 zeep 依賴是否可用
    import zeep
    BPM_AVAILABLE = True
except ImportError as e:
    BPM_AVAILABLE = False
    print(f"Warning: bpm_wsdl module or its dependencies not available. Error: {e}. BPM functionality will be limited.")


class BpminItServices:
    # apply_item 顯示值映射字典
    SUB_APPLY_ITEM_MAPPING = {
        "AD帳號申請": "ad_account",
        "NAS帳號申請": "nas_account", 
        "NAS檔案復原": "nas_recovery",
        "T100申請相關": "t100_apply",
        "文中系統": "winton",
        "office無法啟用": "office_disable",
        "電腦帳號密碼鎖定,無法登入": "account_disable",
        "標籤機相關設定": "label_machine",
        "硬碟升級SSD系統": "ssd_upgrade",
        "作業系統升級或重灌": "os_upgrade",
        "印表機格式設定(發票或中一刀)": "printer_setting",
        "VPN申請": "vpn_apply",
        "網域開通": "network_open",
        "程式修改": "pragrame_modify",
    }
    
    APPLY_ITEM_MAPPING = {
        "程式修改": "pragram",
        "軟體安裝": "software_install",
        "軟體問題": "software_problem",
        "一般電腦問題": "computer_problem",
        "權限申請": "access_apply",
        "資料異動": "data_transfer",
        "其它":"other"
    }
    
    # 反向映射字典（從代碼到顯示名稱）
    APPLY_ITEM_REVERSE_MAPPING = {v: k for k, v in APPLY_ITEM_MAPPING.items()}
    SUB_APPLY_ITEM_REVERSE_MAPPING = {v: k for k, v in SUB_APPLY_ITEM_MAPPING.items()}
    
    # treatment 顯示值映射字典
    TREATMENT_MAPPING = {
        "自行處理": "do_self",
        "委外開發": "outsourcing", 
        "不建議執行": "do_nothing",
        "其它": "other"
    }
    
    # treatment 反向映射字典（從代碼到顯示名稱）
    TREATMENT_REVERSE_MAPPING = {v: k for k, v in TREATMENT_MAPPING.items()}
    
     # complete_status 顯示值映射字典
    COMPLETE_STATUS_MAPPING = {
        "未結案": False,
        "已結案": True
    }

    # complete_status 反向映射字典（從代碼到顯示名稱）
    COMPLETE_STATUS_REVERSE_MAPPING = {v: k for k, v in COMPLETE_STATUS_MAPPING.items()}

    @classmethod
    def _get_bpm_client(cls):
        """獲取 BPM WebService 客戶端"""
        if not BPM_AVAILABLE:
            raise ImportError("BPM WSDL module is not available. Please install the required dependencies.")
        return bpm_wsl()
    
    @classmethod
    def _get_apply_item_display_name(cls, apply_item_code: str) -> str:
        """將 apply_item 代碼轉換為顯示名稱"""
        if not apply_item_code:
            return apply_item_code
        
        # 檢查是否包含多個項目（以逗號分隔）
        if ',' in apply_item_code:
            # 分割並轉換每個項目
            display_names = []
            for code in apply_item_code.split(','):
                code = code.strip()
                display_name = cls.APPLY_ITEM_REVERSE_MAPPING.get(code, code)
                display_names.append(display_name)
            result = ';'.join(display_names)
        else:
            # 除錯用：打印反向映射字典
            # print(f"反向映射字典: {cls.APPLY_ITEM_REVERSE_MAPPING}")
            # print(f"要轉換的代碼: '{apply_item_code}'")
            
            result = cls.APPLY_ITEM_REVERSE_MAPPING.get(apply_item_code, apply_item_code)
        
        # print(f"最終轉換結果: '{result}'")
        return result
    
    @classmethod
    def _get_sub_apply_item_display_name(cls, sub_apply_item_code: str) -> str:
        """將 sub_apply_item 代碼轉換為顯示名稱"""
        if not sub_apply_item_code:
            return sub_apply_item_code
        
        # 檢查是否包含多個項目（以逗號分隔）
        if ',' in sub_apply_item_code:
            # 分割並轉換每個項目
            display_names = []
            for code in sub_apply_item_code.split(','):
                code = code.strip()
                display_name = cls.SUB_APPLY_ITEM_REVERSE_MAPPING.get(code, code)
                display_names.append(display_name)
            result = ';'.join(display_names)
        else:
            result = cls.SUB_APPLY_ITEM_REVERSE_MAPPING.get(sub_apply_item_code, sub_apply_item_code)
        
        return result
    
    @classmethod
    def _get_sub_apply_item_code(cls, sub_apply_item_display: str) -> str:
        """將 sub_apply_item 顯示名稱轉換為代碼"""
        if not sub_apply_item_display:
            return sub_apply_item_display
        
        # 檢查是否包含多個項目（以逗號或分號分隔）
        if ',' in sub_apply_item_display or ';' in sub_apply_item_display:
            # 優先處理分號分隔，如果沒有分號則處理逗號
            separator = ';' if ';' in sub_apply_item_display else ','
            # 分割並轉換每個項目
            item_codes = []
            for item in sub_apply_item_display.split(separator):
                item = item.strip()
                code = cls.SUB_APPLY_ITEM_MAPPING.get(item, item)
                item_codes.append(code)
            return ','.join(item_codes)
        else:
            return cls.SUB_APPLY_ITEM_MAPPING.get(sub_apply_item_display, sub_apply_item_display)
    
    @classmethod
    def _get_apply_item_code(cls, apply_item_display: str) -> str:
        """將 apply_item 顯示名稱轉換為代碼"""
        if not apply_item_display:
            return apply_item_display
        
        # 檢查是否包含多個項目（以逗號或分號分隔）
        if ',' in apply_item_display or ';' in apply_item_display:
            # 優先處理分號分隔，如果沒有分號則處理逗號
            separator = ';' if ';' in apply_item_display else ','
            # 分割並轉換每個項目
            item_codes = []
            for item in apply_item_display.split(separator):
                item = item.strip()
                code = cls.APPLY_ITEM_MAPPING.get(item, item)
                item_codes.append(code)
            return ','.join(item_codes)
        else:
            return cls.APPLY_ITEM_MAPPING.get(apply_item_display, apply_item_display)
    
    @classmethod
    def _get_treatment_display_name(cls, treatment_code: str) -> str:
        """將 treatment 代碼轉換為顯示名稱"""
        if not treatment_code:
            return treatment_code
        
        # 檢查是否包含多個項目（以逗號分隔）
        if ',' in treatment_code:
            # 分割並轉換每個項目
            display_names = []
            for code in treatment_code.split(','):
                code = code.strip()
                display_name = cls.TREATMENT_REVERSE_MAPPING.get(code, code)
                display_names.append(display_name)
            result = ';'.join(display_names)
        else:
            result = cls.TREATMENT_REVERSE_MAPPING.get(treatment_code, treatment_code)
        
        return result
    
    @classmethod
    def _get_treatment_code(cls, treatment_display: str) -> str:
        """將 treatment 顯示名稱轉換為代碼"""
        if not treatment_display:
            return treatment_display
        
        # 檢查是否包含多個項目（以逗號或分號分隔）
        if ',' in treatment_display or ';' in treatment_display:
            # 優先處理分號分隔，如果沒有分號則處理逗號
            separator = ';' if ';' in treatment_display else ','
            # 分割並轉換每個項目
            treatment_codes = []
            for item in treatment_display.split(separator):
                item = item.strip()
                code = cls.TREATMENT_MAPPING.get(item, item)
                treatment_codes.append(code)
            return ','.join(treatment_codes)
        else:
            return cls.TREATMENT_MAPPING.get(treatment_display, treatment_display)
        
    @classmethod
    def _get_complete_status_display_name(cls, complete_status_code) -> str:
        """將 complete_status 代碼轉換為顯示名稱"""
        if complete_status_code is None:
            return complete_status_code

        # 直接使用反向映射字典進行轉換
        result = cls.COMPLETE_STATUS_REVERSE_MAPPING.get(complete_status_code, complete_status_code)
        return result
    
    @classmethod
    def _get_complete_status_code(cls, complete_status_display) -> bool:
        """將 complete_status 顯示名稱轉換為代碼"""
        if complete_status_display is None:
            return complete_status_display

        # 直接使用映射字典進行轉換
        result = cls.COMPLETE_STATUS_MAPPING.get(complete_status_display, complete_status_display)
        return result

    @classmethod
    async def _calculate_processing_days(cls, db, serial_number: str, apply_date: str) -> float:
        """計算處理天數: 最新歷程記錄的create_datetime - 申請日期apply_date"""
        if not serial_number or not apply_date:
            return 0.0
        
        try:
            # 查詢該序號的最新歷程記錄
            stmt = select(BpminItDetail).where(
                BpminItDetail.rsn == serial_number
            ).order_by(desc(BpminItDetail.create_datetime)).limit(1)
            
            result = await db.execute(stmt)
            latest_record = result.scalar_one_or_none()
            
            if not latest_record:
                return 0.0
            
            # 解析申請日期 (假設格式為 YYYY-MM-DD)
            try:
                apply_datetime = datetime.strptime(apply_date, '%Y-%m-%d')
            except ValueError:
                # 如果格式不匹配，嘗試其他常見格式
                try:
                    apply_datetime = datetime.strptime(apply_date, '%Y/%m/%d')
                except ValueError:
                    return 0.0
            
            # 計算天數差異
            if latest_record.create_datetime:
                latest_datetime = latest_record.create_datetime
                if isinstance(latest_datetime, str):
                    try:
                        latest_datetime = datetime.fromisoformat(latest_datetime.replace('Z', '+00:00'))
                    except ValueError:
                        return 0.0
                
                diff = latest_datetime - apply_datetime
                return round(diff.total_seconds() / (24 * 60 * 60), 1)  # 轉換為天數，保留1位小數
            
            return 0.0
            
        except Exception as e:
            print(f"計算處理天數時發生錯誤: {str(e)}")
            return 0.0

    @classmethod
    async def _get_latest_processing_status(cls, db, serial_number: str) -> str:
        """獲取最新處理歷程狀態"""
        if not serial_number:
            return None
        
        try:
            # 查詢該序號的最新歷程記錄
            stmt = select(BpminItDetail).where(
                BpminItDetail.rsn == serial_number
            ).order_by(desc(BpminItDetail.create_datetime)).limit(1)
            
            result = await db.execute(stmt)
            latest_record = result.scalar_one_or_none()
            
            if latest_record and latest_record.status:
                return latest_record.status
            
            return None
            
        except Exception as e:
            print(f"獲取最新處理狀態時發生錯誤: {str(e)}")
            return None

    @classmethod
    def _calculate_elapsed_days(cls, apply_date: str) -> float:
        """計算經過天數: 當前時間 - 申請日期apply_date"""
        if not apply_date:
            return 0.0
        
        try:
            # 解析申請日期 (假設格式為 YYYY-MM-DD)
            try:
                apply_datetime = datetime.strptime(apply_date, '%Y-%m-%d')
            except ValueError:
                # 如果格式不匹配，嘗試其他常見格式
                try:
                    apply_datetime = datetime.strptime(apply_date, '%Y/%m/%d')
                except ValueError:
                    return 0.0
            
            # 計算當前時間與申請日期的差異天數
            current_datetime = datetime.now()
            diff = current_datetime - apply_datetime
            return round(diff.total_seconds() / (24 * 60 * 60), 1)  # 轉換為天數，保留1位小數
            
        except Exception as e:
            print(f"計算經過天數時發生錯誤: {str(e)}")
            return 0.0

    @classmethod
    def _process_data_for_output(cls, data: Any) -> Any:
        """處理輸出資料中的 apply_item 和 treatment，將代碼轉換為顯示名稱"""
        import copy
        
        # 🔍 DEBUG: 記錄輸入資料類型和內容
        print(f"🔍 DEBUG [_process_data_for_output] 輸入資料類型: {type(data)}")
        if isinstance(data, dict):
            print(f"🔍 DEBUG [_process_data_for_output] 單筆資料鍵值: {list(data.keys())}")
            print(f"🔍 DEBUG [_process_data_for_output] is_delete 值: {data.get('is_delete', '不存在')}")
        elif isinstance(data, list):
            print(f"🔍 DEBUG [_process_data_for_output] 列表資料筆數: {len(data)}")
            if data and isinstance(data[0], dict):
                print(f"🔍 DEBUG [_process_data_for_output] 第一筆資料鍵值: {list(data[0].keys())}")
                print(f"🔍 DEBUG [_process_data_for_output] 第一筆 is_delete 值: {data[0].get('is_delete', '不存在')}")
        
        if isinstance(data, dict):
            # 創建深拷貝避免修改原始資料
            result = copy.deepcopy(data)

            # 處理 main_apply_item 欄位
            if 'main_apply_item' in result and result['main_apply_item']:
                original_code = result['main_apply_item']
                display_name = cls._get_apply_item_display_name(original_code)
                print(f"🔍 DEBUG [main_apply_item] {original_code} → {display_name}")
                result['main_apply_item'] = display_name

            # 處理 sub_apply_item 欄位
            if 'sub_apply_item' in result and result['sub_apply_item']:
                original_code = result['sub_apply_item']
                display_name = cls._get_sub_apply_item_display_name(original_code)
                print(f"🔍 DEBUG [sub_apply_item] {original_code} → {display_name}")
                result['sub_apply_item'] = display_name
            
            # 處理 treatment 欄位
            if 'treatment' in result and result['treatment']:
                original_code = result['treatment']
                display_name = cls._get_treatment_display_name(original_code)
                print(f"🔍 DEBUG [treatment] {original_code} → {display_name}")
                result['treatment'] = display_name
            
            # 處理 complete_status 欄位
            if 'is_delete' in result and result['is_delete'] is not None:
                original_code = result['is_delete']
                print(f"🔍 DEBUG [is_delete] 原始值: {original_code} (類型: {type(original_code)})")
                print(f"🔍 DEBUG [REVERSE_MAPPING] 映射表: {cls.COMPLETE_STATUS_REVERSE_MAPPING}")
                display_name = cls._get_complete_status_display_name(original_code)
                print(f"🔍 DEBUG [is_delete] {original_code} → {display_name}")
                result['is_delete'] = display_name
            else:
                print(f"🔍 DEBUG [is_delete] 欄位不存在或為 None")

            return result
            
        elif isinstance(data, list):
            result = []
            for index, item in enumerate(data):
                if isinstance(item, dict):
                    processed_item = copy.deepcopy(item)
                    print(f"🔍 DEBUG [列表項目 {index}] is_delete 原始值: {processed_item.get('is_delete', '不存在')}")

                    # 處理 main_apply_item 欄位
                    if 'main_apply_item' in processed_item and processed_item['main_apply_item']:
                        original_code = processed_item['main_apply_item']
                        display_name = cls._get_apply_item_display_name(original_code)
                        processed_item['main_apply_item'] = display_name

                    # 處理 sub_apply_item 欄位
                    if 'sub_apply_item' in processed_item and processed_item['sub_apply_item']:
                        original_code = processed_item['sub_apply_item']
                        display_name = cls._get_sub_apply_item_display_name(original_code)
                        processed_item['sub_apply_item'] = display_name
                    
                    # 處理 treatment 欄位
                    if 'treatment' in processed_item and processed_item['treatment']:
                        original_code = processed_item['treatment']
                        display_name = cls._get_treatment_display_name(original_code)
                        processed_item['treatment'] = display_name
                    
                    # 處理 complete_status 欄位 (使用 is_delete 作為數據源)
                    if 'is_delete' in processed_item and processed_item['is_delete'] is not None:
                        original_code = processed_item['is_delete']
                        print(f"🔍 DEBUG [列表項目 {index} is_delete] 原始值: {original_code} (類型: {type(original_code)})")
                        display_name = cls._get_complete_status_display_name(original_code)
                        print(f"🔍 DEBUG [列表項目 {index} is_delete] {original_code} → {display_name}")
                        processed_item['is_delete'] = display_name
                    else:
                        print(f"🔍 DEBUG [列表項目 {index} is_delete] 欄位不存在或為 None")
                        
                    result.append(processed_item)
                else:
                    result.append(item)
            
            print(f"🔍 DEBUG [_process_data_for_output] 處理完成，返回 {len(result)} 筆資料")
            return result
        else:
            return data
    
    @classmethod
    def _format_bmp_response(cls, success: bool, data: Any, method: str, error: str = None) -> Dict[str, Any]:
        """格式化 BPM 響應結果"""
        if success:
            return {
                'success': True,
                'data': data,
                'method': method
            }
        else:
            return {
                'success': False,
                'error': error or 'Unknown error',
                'method': method
            }
    
    # === BPM WebService 相關方法 ===
    
    @classmethod
    async def accept_work_item(cls, work_item_oid: str, user_id: str) -> Dict[str, Any]:
        """接受 IT 服務需求工作項目"""
        try:
            client = cls._get_bpm_client()
            success, result = client.acceptWorkItem(work_item_oid, user_id)
            return cls._format_bmp_response(success, result, 'acceptWorkItem', 
                                          None if success else result)
        except Exception as e:
            return cls._format_bmp_response(False, None, 'acceptWorkItem', str(e))
    
    @classmethod
    async def fetch_todo_work_item(cls, user_id: str, process_ids: str = '') -> Dict[str, Any]:
        """取得 IT 服務需求待辦工作項目"""
        try:
            client = cls._get_bpm_client()
            success, result = client.fetchToDoWorkItem(user_id, process_ids)
            return cls._format_bmp_response(success, result, 'fetchToDoWorkItem',
                                          None if success else result)
        except Exception as e:
            return cls._format_bmp_response(False, None, 'fetchToDoWorkItem', str(e))
    
    @classmethod
    async def check_work_item_state(cls, work_item_oid: str) -> Dict[str, Any]:
        """檢查 IT 服務需求工作項目狀態"""
        try:
            client = cls._get_bpm_client()
            success, result = client.checkWorkItemState(work_item_oid)
            return cls._format_bmp_response(success, result, 'checkWorkItemState',
                                          None if success else result)
        except Exception as e:
            return cls._format_bmp_response(False, None, 'checkWorkItemState', str(e))
    
    @classmethod
    async def complete_work_item(cls, work_item_oid: str, user_id: str, comment: str = 'IT需求處理完成') -> Dict[str, Any]:
        """完成 IT 服務需求工作項目"""
        try:
            client = cls._get_bpm_client()
            success, result = client.completeWorkItem(work_item_oid, user_id, comment)
            return cls._format_bmp_response(success, result, 'completeWorkItem',
                                          None if success else result)
        except Exception as e:
            return cls._format_bmp_response(False, None, 'completeWorkItem', str(e))
    
    @classmethod
    async def get_all_xml_form(cls, serial_no: str) -> Dict[str, Any]:
        """取得 IT 服務需求完整表單資料"""
        try:
            client = cls._get_bpm_client()
            success, result = client.get_all_xml_form(serial_no)
            return cls._format_bmp_response(success, result, 'get_all_xml_form',
                                          None if success else result)
        except Exception as e:
            return cls._format_bmp_response(False, None, 'get_all_xml_form', str(e))
    
    @classmethod
    async def fetch_proc_instance_with_serial_no(cls, serial_no: str) -> Dict[str, Any]:
        """取得 IT 服務需求簡單表單資料"""
        try:
            client = cls._get_bpm_client()
            success, result = client.fetchProcInstanceWithSerialNo(serial_no)
            return cls._format_bmp_response(success, result, 'fetchProcInstanceWithSerialNo',
                                          None if success else result)
        except Exception as e:
            return cls._format_bmp_response(False, None, 'fetchProcInstanceWithSerialNo', str(e))
    
    @classmethod
    async def reexecute_activity(cls, process_serial_no: str, reexecute_activity_id: str, 
                                ask_reexecute_user_id: str, reexecute_comment: str = 'IT需求退回') -> Dict[str, Any]:
        """IT 服務需求取回重辦"""
        try:
            client = cls._get_bpm_client()
            success, result = client.reexecuteActivity(process_serial_no, reexecute_activity_id, 
                                                     ask_reexecute_user_id, reexecute_comment)
            return cls._format_bmp_response(success, result, 'reexecuteActivity',
                                          None if success else result)
        except Exception as e:
            return cls._format_bmp_response(False, None, 'reexecuteActivity', str(e))
    
    @classmethod
    async def get_wsdl_fun_list(cls) -> Dict[str, Any]:
        """取得所有 WSDL 功能列表"""
        try:
            client = cls._get_bpm_client()
            result = client.get_wsdl_fun_list()
            return cls._format_bmp_response(True, result, 'get_wsdl_fun_list')
        except Exception as e:
            return cls._format_bmp_response(False, None, 'get_wsdl_fun_list', str(e))
    
    # === IT 服務需求表單資料處理方法 ===
    @classmethod
    def _extract_it_form_data(cls, bpm_data: Dict[str, Any], serial_no: str) -> Dict[str, Any]:
        """從 BPM 表單資料中提取 IT 服務需求相關欄位"""
        extracted_data = {
            'oid': bpm_data.get('OID', ''),
            'serial_no': bpm_data.get('serialNo', serial_no),
            'it_manager': None,
            'dept': None,
            'apply_date': None,
            'extension': None,
            'fillman': None,
            'main_apply_item': None,
            'sub_apply_item': None,
            'request_desc': None,
            'it_undertaker': None,
            'treatment': None
        }
        
        try:
            form_list = bpm_data.get('form_list', [])
            if form_list:
                field_values = form_list[0].get('fieldValues', '')
                
                # 定義需要提取的欄位對應關係
                field_mappings = {
                    'ItManager': 'it_manager',
                    'Dept': 'dept', 
                    'ApplyDate': 'apply_date',
                    'Extension': 'extension',
                    'fillman': 'fillman',
                    'MainApplyItem': 'main_apply_item',
                    'SubApplyItem': 'sub_apply_item',
                    'RequestDesc': 'request_desc',
                    'ItUndertaker': 'it_undertaker',
                    'Treatment': 'treatment'
                }
                
                # 從 XML 格式的 fieldValues 中提取各欄位
                for xml_field, dict_field in field_mappings.items():
                    pattern = rf'<{xml_field}[^>]*>([^<]+)</{xml_field}>'
                    match = re.search(pattern, field_values)
                    if match:
                        value = match.group(1).strip()
                        # 處理包含工號和姓名的格式 (如: "1080401004_翁進福")
                        if '_' in value and dict_field in ['it_manager', 'fillman', 'it_undertaker']:
                            # 保留完整格式或只取工號，根據需求決定
                            extracted_data[dict_field] = value
                        else:
                            extracted_data[dict_field] = value
                
                # apply_item 直接使用原始值，不做轉換
        except Exception as e:
            print(f"提取 IT 表單資料時發生錯誤: {e}")
        
        return extracted_data
    
    @classmethod
    async def create_it_request_from_bpm(cls, db, serial_no: str, auto_create: bool = True) -> Dict[str, Any]:
        """從 BPM 表單資料創建 IT 服務需求單"""
        # 1. 從 BPM 取得完整表單資料
        bmp_result = await cls.get_all_xml_form(serial_no)
        
        if not bmp_result['success']:
            return {
                'success': False,
                'error': f"取得 BPM 表單資料失敗: {bmp_result['error']}"
            }
        
        bpm_data = bmp_result['data']
        
        # 2. 提取 IT 服務需求相關欄位
        extracted_data = cls._extract_it_form_data(bpm_data, serial_no)
        
        response_data = {
            'bpm_data': bpm_data,
            'extracted_fields': extracted_data,
            'mapping_info': {
                'description': 'BPM 表單欄位對應 IT 服務需求單欄位',
                'oid_to': 'BPM OID',
                'serial_no_to': 'BPM 流程序號'
            }
        }
        
        # 3. 如果要求自動創建，則創建 IT 服務需求單
        if auto_create:
            try:
                # 建立 IT 服務需求資料
                it_data = schemas.BpminIt(
                    serial_number=extracted_data['serial_no'],
                    it_manager=extracted_data['it_manager'],
                    dept=extracted_data['dept'],
                    apply_date=extracted_data['apply_date'],
                    extension=extracted_data['extension'],
                    fillman=extracted_data['fillman'],
                    main_apply_item=extracted_data['main_apply_item'],
                    sub_apply_item=extracted_data['sub_apply_item'],
                    request_desc=extracted_data['request_desc'],
                    it_undertaker=extracted_data['it_undertaker'],
                    treatment=extracted_data['treatment'],
                    create_user=extracted_data.get('fillman', '').split('_')[0] if extracted_data.get('fillman') and '_' in extracted_data.get('fillman') else None
                )
                
                # 創建資料記錄
                created_result = await crud.BpminItDal(db).create_data(data=it_data)
                
                response_data['created_it_request'] = created_result
                
                return {
                    'success': True,
                    'data': response_data,
                    'message': f"成功從 BPM 表單創建 IT 服務需求單 (Serial No: {serial_no})"
                }
                
            except Exception as e:
                return {
                    'success': False,
                    'error': f"創建 IT 服務需求單失敗: {str(e)}",
                    'bpm_data': response_data
                }
        
        # 4. 僅回傳 BPM 資料供預覽
        return {
            'success': True,
            'data': response_data,
            'message': "成功取得 BPM 表單資料，可用於創建 IT 服務需求單"
        }
    
    # === 傳統 CRUD 操作方法 ===
    
    @classmethod
    async def create_bpmin_it(cls, db, data: schemas.BpminIt) -> Dict[str, Any]:
        """創建 IT 服務需求單"""
        try:
            result = await crud.BpminItDal(db).create_data(data=data)
            
            return {
                'success': True,
                'data': result,
                'message': "創建 IT 服務需求單成功"
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"創建 IT 服務需求單失敗: {str(e)}"
            }
    
    @classmethod
    async def get_bpmin_it(cls, db, data_id: int) -> Dict[str, Any]:
        """獲取 IT 服務需求單詳情"""
        try:
            # 使用自定義查詢來顯示所有記錄（包括已結案的 is_delete=True）
            # from sqlalchemy import select
            # from sqlalchemy.sql.selectable import Select
            
            # 創建不過濾 is_delete 的查詢
            custom_sql: Select = select(crud.BpminItDal(db).model)
            
            result = await crud.BpminItDal(db).get_data(
                data_id, 
                v_start_sql=custom_sql,
                v_schema=schemas.BpminItSimpleOut
            )
            # 處理 apply_item 和 treatment 顯示值
            if result:
                result = cls._process_data_for_output(result)
            return {
                'success': True,
                'data': result,
                'message': "獲取 IT 服務需求單成功"
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"獲取 IT 服務需求單失敗: {str(e)}"
            }
    
    @classmethod
    async def list_bpmin_it(cls, db, params_dict: dict) -> Dict[str, Any]:
        """獲取 IT 服務需求單列表"""
        try:
            # 使用自定義查詢來顯示所有記錄（包括已結案的 is_delete=True）
            # from sqlalchemy import select
            # from sqlalchemy.sql.selectable import Select
            
            # 創建不過濾 is_delete 的查詢
            custom_sql: Select = select(crud.BpminItDal(db).model)
            
            datas, count = await crud.BpminItDal(db).get_datas(
                v_start_sql=custom_sql,
                **params_dict, 
                v_return_count=True
            )
            
            # 處理列表中每個項目的 apply_item、treatment 顯示值和計算處理天數、經過天數、獲取最新處理狀態
            if datas:
                # 先計算處理天數、經過天數和獲取最新處理狀態
                if isinstance(datas, list):
                    for item in datas:
                        if isinstance(item, dict) and 'serial_number' in item and 'apply_date' in item:
                            # 計算處理天數（最新歷程記錄時間 - 申請日期）
                            processing_days = await cls._calculate_processing_days(
                                db, item['serial_number'], item['apply_date']
                            )
                            item['datediff'] = processing_days
                            
                            # 計算經過天數（當前時間 - 申請日期）
                            elapsed_days = cls._calculate_elapsed_days(item['apply_date'])
                            item['elapsed_days'] = elapsed_days
                            
                            # 獲取最新處理狀態
                            latest_status = await cls._get_latest_processing_status(
                                db, item['serial_number']
                            )
                            item['latest_processing_status'] = latest_status
                elif isinstance(datas, dict) and 'serial_number' in datas and 'apply_date' in datas:
                    # 計算處理天數（最新歷程記錄時間 - 申請日期）
                    processing_days = await cls._calculate_processing_days(
                        db, datas['serial_number'], datas['apply_date']
                    )
                    datas['datediff'] = processing_days
                    
                    # 計算經過天數（當前時間 - 申請日期）
                    elapsed_days = cls._calculate_elapsed_days(datas['apply_date'])
                    datas['elapsed_days'] = elapsed_days
                    
                    # 獲取最新處理狀態
                    latest_status = await cls._get_latest_processing_status(
                        db, datas['serial_number']
                    )
                    datas['latest_processing_status'] = latest_status
                
                # 然後處理顯示值
                datas = cls._process_data_for_output(datas)
            return {
                'success': True,
                'data': datas,
                'count': count,
                'message': "獲取 IT 服務需求單列表成功"
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"獲取 IT 服務需求單列表失敗: {str(e)}"
            }
    
    @classmethod
    async def update_bpmin_it(cls, db, data_id: int, data: schemas.BpminIt) -> Dict[str, Any]:
        """更新 IT 服務需求單"""
        try:
            result = await crud.BpminItDal(db).put_data(data_id, data)
            
            return {
                'success': True,
                'data': result,
                'message': "更新 IT 服務需求單成功"
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"更新 IT 服務需求單失敗: {str(e)}"
            }
    
    @classmethod
    async def update_bpmin_it_by_sn(cls, db, serial_number: str, data: schemas.BpminIt) -> Dict[str, Any]:
        """根據 serial_number 更新 IT 服務需求單的 treatment 欄位"""
        try:
            # 1. 先從 BPM 系統取得完整表單資料
            bmp_result = await cls.get_all_xml_form(serial_number)
            
            if not bmp_result['success']:
                return {
                    'success': False,
                    'error': f"取得 BPM 表單資料失敗: {bmp_result['error']}"
                }
            
            # 2. 提取 BPM 表單中的 treatment 欄位
            bmp_data = bmp_result['data']
            extracted_data = cls._extract_it_form_data(bmp_data, serial_number)
            
            # 3. 取得從 BPM 表單中提取的 treatment 值
            bmp_treatment = extracted_data.get('treatment', '')
            
            # 4. 如果 BPM 表單中沒有 treatment 資料，使用傳入的資料
            data_dict = data.model_dump(exclude_unset=True)
            final_treatment = bmp_treatment if bmp_treatment and bmp_treatment.strip() else data_dict.get('treatment', '')
            
            # 5. 驗證 treatment 欄位
            if not final_treatment or not final_treatment.strip():
                return {
                    'success': False,
                    'error': "BPM 表單和傳入資料中都沒有找到有效的 treatment 欄位值"
                }
            
            # 6. 準備更新資料
            treatment_data = {'treatment': final_treatment.strip()}
            
            # 7. 更新資料庫
            result = await crud.BpminItDal(db).update_data_by_serial_number(serial_number, treatment_data)
            
            return {
                'success': True,
                'data': result,
                'message': f"根據序號成功更新 IT 服務需求單的處理方式 (來源: {'BMP表單' if bmp_treatment else '傳入參數'})",
                'treatment_source': 'bmp_form' if bmp_treatment else 'input_data',
                'treatment_value': final_treatment.strip()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"根據序號更新 IT 服務需求單處理方式失敗: {str(e)}"
            }
    
    @classmethod
    async def update_case_close_status(cls, db, serial_number: str) -> Dict[str, Any]:
        """結案狀態更新 - 檢查 BPM 流程是否已結案並更新資料庫"""
        try:
            # 1. 從 BPM 系統取得完整表單資料
            bmp_result = await cls.get_all_xml_form(serial_number)
            
            if not bmp_result['success']:
                return {
                    'success': False,
                    'error': f"取得 BPM 表單資料失敗: {bmp_result['error']}"
                }
            
            bmp_data = bmp_result['data']
            
            # 2. 檢查活動清單中的"使用者測試"狀態
            is_case_closed = False
            user_test_activity = None
            
            try:
                activities = bmp_data.get('activity_list', [])
                print(f"檢查流程 {serial_number} 的活動清單，共 {len(activities)} 個活動")
                
                for activity in activities:
                    activity_name = activity.get('activity_name', '')
                    state = activity.get('state', '')
                    
                    print(f"檢查活動: '{activity_name}', 狀態: '{state}'")
                    
                    if activity_name == "使用者測試":
                        user_test_activity = activity
                        if state == "closed.completed":
                            is_case_closed = True
                            print(f"找到結案活動: {activity_name}, 狀態: {state}")
                            break
                
                if not user_test_activity:
                    print(f"流程 {serial_number} 中未找到'使用者測試'活動")
                    
            except Exception as e:
                print(f"解析活動清單時發生錯誤: {e}")
                return {
                    'success': False,
                    'error': f"解析 BPM 活動清單失敗: {str(e)}"
                }
            
            # 3. 如果已結案，更新資料庫的 is_delete 欄位為 1
            if is_case_closed:
                try:
                    # 更新 is_delete 欄位為 True (表示結案)
                    update_data = {'is_delete': True}
                    result = await crud.BpminItDal(db).update_data_by_serial_number(serial_number, update_data)
                    
                    return {
                        'success': True,
                        'data': result,
                        'message': f"流程 {serial_number} 已結案，成功更新結案狀態",
                        'case_status': 'closed',
                        'activity_info': {
                            'activity_name': user_test_activity.get('activity_name'),
                            'state': user_test_activity.get('state'),
                            'complete_time': user_test_activity.get('complete_time', '')
                        }
                    }
                    
                except Exception as e:
                    return {
                        'success': False,
                        'error': f"更新結案狀態失敗: {str(e)}"
                    }
            else:
                # 流程尚未結案
                return {
                    'success': True,
                    'message': f"流程 {serial_number} 尚未結案，無需更新狀態",
                    'case_status': 'in_progress',
                    'user_test_activity': user_test_activity.get('state') if user_test_activity else 'not_found'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f"結案狀態更新失敗: {str(e)}"
            }
    
    @classmethod
    async def delete_bpmin_it(cls, db, ids: list, soft_delete: bool = True) -> Dict[str, Any]:
        """刪除 IT 服務需求單"""
        try:
            await crud.BpminItDal(db).delete_datas(ids=ids, v_soft=soft_delete)
            delete_type = "軟刪除" if soft_delete else "硬刪除"
            return {
                'success': True,
                'message': f"IT 服務需求單{delete_type}成功"
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"刪除 IT 服務需求單失敗: {str(e)}"
            }