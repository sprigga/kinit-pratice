import hashlib
from pathlib import Path
import aiohttp
import asyncio
from application.settings import PLM_URL, PLM_USER, PLM_PASSWORD, PLM_DB, PLM_CLIENT_ID


class PlmAPIClient:
    def __init__(self):
        self.base_url = PLM_URL
        self.client_id = PLM_CLIENT_ID
        self.access_token = None
        self.username = PLM_USER
        self.password = PLM_PASSWORD
        self.database = PLM_DB

    @staticmethod
    def get_md5_hash(password):
        """ 將密碼轉換為 MD5 哈希 """
        md5 = hashlib.md5()
        md5.update(password.encode('utf-8'))
        return md5.hexdigest()

    async def get_access_token(self):
        """ 獲取訪問令牌 """
        token_url = f"{self.base_url}/plm/oauthserver/connect/token"
        hashed_password = self.get_md5_hash(self.password)
        data = {
            "grant_type": "password",
            "client_id": self.client_id,
            "username": self.username,
            "password": hashed_password,
            "database": self.database
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(token_url, data=data) as response:
                response.raise_for_status()
                result = await response.json()
                self.access_token = result.get("access_token")
                return self.access_token

    async def call_api(self, endpoint, params=None):
        """ 使用訪問令牌調用 API """
        if self.access_token is None:
            raise ValueError("訪問令牌不可用，請先驗證。")

        url = f"{self.base_url}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as response:
                response.raise_for_status()
                return await response.json()

    async def fetch_parts(self, item_number_prefix, expand=None):
        """ 根據 ITEM_NUMBER 前綴獲取零件信息 """
        endpoint = "plm/server/odata/Part"
        query_params = {
            "$filter": f"startswith(ITEM_NUMBER, '{item_number_prefix}')",
        }
        if expand:
            query_params.update({"$expand": expand})
        return await self.call_api(endpoint, params=query_params)

    async def fetch_and_download(self, item_number_prefix, expand=None):
        """ 獲取零件信息並下載相關文件 """
        response = await self.fetch_parts(item_number_prefix, expand)
        parts = response.get('value', [])
        print(parts)
        if isinstance(parts, list) and parts:
            for part in parts:
                document_id = part.get("id")
                part_files = part.get("Part Flie", [])
                print(part_files)
                if part_files:
                    for file in part_files:
                        file_id = file.get("id")
                        if document_id and file_id:
                            print(f"Downloading file with Document ID: {document_id}, File ID: {file_id}")
                            # document_id = 'D1957ABE3BE246DFA26CC0D14AAA9F36'
                            # file_id = '8C41DC97B3C745A0816256E172DF5E5A'
                            document_id = 'D1957ABE3BE246DFA26CC0D14AAA9F36'
                            # file_id = '8C41DC97B3C745A0816256E172DF5E5A'
                            await self.download_file(document_id, file_id)
                        else:
                            print(f"缺少 document_id 或 file_id，無法下載")
                else:
                    print("無 Part Flie 資料:", part)
        else:
            print("無效的零件數據:", response)

    async def download_file(self, document_id, file_id, download_dir="downloads"):
        """ 使用 Aras 的 $value 下載文件並保存到指定目錄 """
        if self.access_token is None:
            raise ValueError("訪問令牌不可用，請先驗證。")

        # 構建正確的 OData URL，並加入 "/odata/" 路徑
        download_url = f"{self.base_url.rstrip('/')}/plm/odata/Document('{document_id}')/Document_File('{file_id}')/related_id"
        print(download_url)  # 用於調試 URL 是否正確
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/octet-stream"
        }

        Path(download_dir).mkdir(parents=True, exist_ok=True)

        async with aiohttp.ClientSession() as session:
            async with session.get(download_url, headers=headers) as response:
                print(response)
                if response.status == 404:
                    print(f"文件未找到，文件ID: {file_id}")
                    return
                response.raise_for_status()

                # 判斷文件類型並設置擴展名
                content_type = response.headers.get("Content-Type", "application/octet-stream")
                ext = ".hex" if content_type == "application/octet-stream" else ".bin"
                file_name = f"{file_id}{ext}"
                file_path = Path(download_dir) / file_name

                # 寫入文件
                with open(file_path, "wb") as f:
                    f.write(await response.read())
                print(f"文件已下載並保存在: {file_path}")

async def main():
    item_number_prefix = "ID02-1017-01"  # 替換為實際項目編號
    plm_client = PlmAPIClient()
    await plm_client.get_access_token()
    expand = 'Part Flie'
    await plm_client.fetch_and_download(item_number_prefix, expand)


if __name__ == "__main__":
    asyncio.run(main())