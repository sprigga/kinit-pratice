from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional

import httpx

from application.settings import T100_IP, T100_ENV, T100_LANG, T100_SITE, T100_PROD, T100_ACCT, T100_ENT
from core.logger import logger


@dataclass
class ApiResponse:
    success: bool
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


class T100APIClient:
    def __init__(self):
        self.server_ip = T100_IP
        self.env = T100_ENV
        self.prod = T100_PROD
        self.site = T100_SITE
        self.ent = T100_ENT
        self.lang = T100_LANG

    @staticmethod
    def handle_response(response_data: Dict[str, Any], action: str) -> ApiResponse:
        """
        通用 ERP API 回應處理方法，包含:
        1. 檢查 `srvcode` 是否成功 (`srvcode == "000"`)
        2. 確保 `code` 和 `sql_code` 是否為 `"0"`
        3. 失敗時記錄錯誤日誌，並返回 `ErrorResponse`
        4. 成功時回傳 `data`
        """

        # ✅ 解析 `srvcode`
        srvcode = response_data.get("srvcode", "999")  # 預設為失敗
        execution: Dict[str, Any] = response_data.get("payload", {}).get("std_data", {}).get("execution", {}) or {}

        # ✅ 解析 `code`、`sql_code` 和 `description`
        code = execution.get("code", "-1")  # 預設錯誤
        sql_code = execution.get("sql_code", "-1")  # 預設錯誤
        description = execution.get("description", "未知錯誤")

        # ❌ `srvcode` 失敗，直接記錄錯誤
        if srvcode != "000":
            logger.error(f"❌ ERP API `{action}` 失敗 | SRVCODE: {srvcode} | 描述: {description}")
            return ApiResponse(success=False, error_code=srvcode, error_message=description)

        # ❌ `code` 或 `sql_code` 失敗
        if code != "0" or sql_code != "0":
            logger.error(f"❌ T100 API `{action}` 失敗 | CODE: {code} | SQL_CODE: {sql_code} | 描述: {description}")
            return ApiResponse(success=False, error_code=code, error_message=description)

        # ✅ 成功，提取 `parameter` 並返回
        data = response_data.get("payload", {}).get("std_data", {}).get("parameter", None)

        # ❌ `parameter` 為 None 或空值，直接拋錯
        if not data:
            logger.error(f"❌ ERP API {action} 回應缺少 `parameter`，完整回應: {response_data}")
            return ApiResponse(success=False, error_code="MISSING_PARAMETER", error_message="ERP API 回應缺少 `parameter`")

        logger.info(f"✅ ERP API {action} 執行成功")
        return ApiResponse(success=True, data=data)


    async def fetch_data(self, fun: str, action: Optional[str] = None, parameter: Dict[str, Any] = None) -> ApiResponse:
        """
        調用T100 API，並處理請求及回應數據
        """
        url = f"http://{self.server_ip}/w{self.env}/ws/r/awsp920"

        if parameter is None:
            parameter = {}

        request_data = {
            "key": 'f5458f5c0f9022db743a7c0710145903',
            "type": "sync",
            "host": {
                "prod": self.prod,
                "ip": "",
                "lang": self.lang,
                "acct": T100_ACCT,
                "timestamp": datetime.now().strftime("%Y%m%d%H%M%S%f")
            },
            "service": {
                "prod": "T100",
                "name": fun,
                "ip": self.server_ip,
                "id": self.env
            },
            "datakey": {
                "EntId": self.ent,
                "CompanyId": self.site
            },
            "payload": {
                "std_data": {
                    "parameter": parameter
                }
            }
        }

        if action:
            request_data["service"]["action"] = action

        logger.debug(f"發送 T100 API 請求: {request_data}")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=request_data, timeout=60.0)

                response_data = response.json()
                logger.debug(f"T100 API 回應: {response_data}")

                # ✅ 使用 `handle_response()` 來統一檢查 API 成功與否
                return self.handle_response(response_data, action)

        except httpx.TimeoutException:
            logger.error("ERP API 請求超時")
            return ApiResponse(success=False, error_code="TIMEOUT", error_message="API 請求超時")
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP 請求錯誤: {str(e)}")
            return ApiResponse(success=False, error_code="HTTP_ERROR", error_message=str(e))
        except Exception as e:
            logger.error(f"ERP API未知錯誤: {str(e)}")
            return ApiResponse(success=False, error_code="API_ERROR", error_message=str(e))

if __name__ == "__main__":
    import asyncio


    async def main():
        parameter = {}
        fun = "bd.mes.aps_run"
        client = T100APIClient()
        action = "get_mo_list"
        api_response = await client.fetch_data(fun, action, parameter)

        if api_response.success:
            parsed_data = {}
            serial_number = 1
            for item in api_response.data.get("master", []):  # 增加安全存取
                print(f"{serial_number}. {item}")
                serial_number += 1
                # TODO: 將數據寫入 MES DB，並更新 sfaaua001 = 'Y'
            return parsed_data
        else:
            print("❌ 錯誤回應解析結果:")
            print(f"🔹 錯誤代碼: {api_response.error_code}")
            print(f"🔹 錯誤訊息: {api_response.error_message}")


    # 運行主函數
    asyncio.run(main())