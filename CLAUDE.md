# CLAUDE.md

此檔案為 Claude Code (claude.ai/code) 在處理此專案程式碼時提供指導。

## 專案概述

這是一個多服務企業管理模板，包含 API、網頁前端、行動應用程式和排程任務等獨立模組。系統後端使用 FastAPI，網頁前端使用 Vue.js，行動端開發使用 uni-app，任務管理使用 APScheduler。

## 架構

專案包含四個主要組件：

- **api/**: FastAPI 後端服務，採用模組化架構
- **web/**: Vue.js + Element Plus 管理後台
- **app/**: uni-app 行動應用程式
- **task/**: 基於 APScheduler 的任務排程服務

### 後端架構 (API)

- **FastAPI** 框架，支援 async/await 模式
- **SQLAlchemy 2.0** ORM，支援非同步操作
- **Alembic** 資料庫遷移工具
- **模組化結構** 位於 `apps/vadmin/` 下，包含認證、系統、記錄等獨立模組
- **核心服務** 位於 `core/` 目錄，包含資料庫、中介軟體、驗證等功能
- **工具程式** 位於 `utils/` 目錄，提供通用功能

### 資料庫支援

- **MySQL 8.0+**: 主要資料庫
- **MongoDB**: 文件儲存，用於日誌和分析
- **Redis**: 快取和發布/訂閱訊息

## 開發指令

### API 服務 (FastAPI)

```bash
cd api

# 安裝依賴套件
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# 初始化資料庫（開發環境）
python main.py init --env dev

# 初始化資料庫（正式環境）
python main.py init

# 建立新的應用程式模組
python main.py init-app vadmin/new_module_name
```

### 網頁前端

```bash
cd web

# 安裝依賴套件
pnpm install

# 開發伺服器
pnpm run dev

# 型別檢查
pnpm run ts:check

# 程式碼檢查和格式化
pnpm run lint:eslint
pnpm run lint:format
pnpm run lint:style

# 正式環境建置
pnpm run build:pro

# 開發環境建置
pnpm run build:dev
```

### 行動應用程式 (uni-app)

```bash
cd app

# 開發通常透過 uni-app IDE 或 CLI 工具進行
# package.json 中未定義特定的建置指令
```

### 任務排程器

```bash
cd task

# 安裝依賴套件
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# 執行排程器
python main.py
```

### Docker 部署

```bash
# 啟動所有服務
docker-compose up -d

# 在容器中初始化資料庫
docker-compose exec kinit-api python3 main.py init

# 重新啟動所有服務
docker-compose restart
```

## 重要設定檔案

### 資料庫設定

- `api/alembic.ini`: 資料庫遷移設定
- `api/application/config/development.py`: 開發環境資料庫設定
- `api/application/config/production.py`: 正式環境資料庫設定

### 環境設定

- `api/application/settings.py`: 主要應用程式設定
  - 開發環境設定 `DEBUG = True`
  - 正式環境設定 `DEBUG = False`

## 程式碼產生

專案包含 CRUD 程式碼產生功能：

```bash
cd api
python scripts/crud_generate/main.py
```

此功能會產生：
- 結構序列化程式碼
- DAL（資料存取層）程式碼
- 參數驗證程式碼
- 視圖/API 端點程式碼

## 開發指導原則

### 資料庫操作

- 始終使用 SQLAlchemy 的非同步資料庫操作
- 使用 Alembic 進行結構遷移
- 在開發環境中先測試遷移

### API 開發

- 遵循 `apps/vadmin/` 下的模組化結構
- 每個模組應包含：models、schemas、crud、params、views
- 使用 `core/` 中提供的基礎類別以保持一致性

### 身份驗證

- 基於 JWT 的身份驗證，支援重新整理權杖
- OAuth2 密碼流程實作
- 基於角色的權限系統

## 測試和品質保證

- 執行型別檢查：`pnpm run ts:check`（網頁）
- 執行程式碼檢查：`pnpm run lint:eslint`（網頁）
- 確保資料庫遷移在部署前正常運作
- 測試 Docker compose 設定以進行正式部署

## 預設帳號

- 管理員帳號：`15020221010` / `kinit2022`
- 測試帳號：`15020240125` / `test`

## BPM WSDL 模組依賴問題及解決方式

### 問題描述

在使用 `api/apps/bpm/it/services/bpmin_it.py` 中的 BPM WebService 功能時，可能會遇到以下錯誤：
```
BPM WSDL module is not available. Please install the required dependencies.
```

### 依賴結構

- **BPM WSDL 模組位置**: `api/utils/bpm_wsdl.py`
- **主要類別**: `bpm_wsl` 
- **服務類別**: `api/apps/bpm/it/services/bpmin_it.py` 中的 `BpminItServices`

### 依賴需求

1. **Python 依賴**:
   - `zeep==4.3.1` (已包含在 requirements.txt)
   - `configparser` (Python 內建)
   - `xml.etree.ElementTree` (Python 內建)

2. **系統依賴**:
   - BPM WebService 伺服器連線 (預設: `http://192.168.70.115:8086/NaNaWeb/services/WorkflowService?wsdl`)

### 模組路徑設置

在 `api/apps/bpm/it/services/__init__.py` 中已正確設置路徑：
```python
import sys
import os
# 添加 utils 路徑到 sys.path
utils_path = os.path.join(os.path.dirname(__file__), '../../../../utils')
sys.path.insert(0, utils_path)
```

### 解決方案

#### 1. 確認依賴安裝
```bash
cd api
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
```

#### 2. 測試模組導入
```bash
cd api
python3 -c "
import sys
import os
sys.path.insert(0, 'utils')
from bpm_wsdl import bpm_wsl
print('SUCCESS: BPM WSDL module imported successfully')
"
```

#### 3. 檢查 BPM 服務連線
確認 BPM WebService 伺服器 (`http://192.168.70.115:8086`) 是否可訪問。

#### 4. Docker 環境問題
如果在 Docker 環境中遇到問題，確認：
- 所有 Python 依賴都已正確安裝
- 網路連線可以到達 BPM 伺服器
- 容器內的 Python 路徑設置正確

### 功能特性

BPM WSDL 模組提供以下功能：
- 取得完整表單資料 (`get_all_xml_form`)
- 取得簡單表單資料 (`fetchProcInstanceWithSerialNo`) 
- 接受工作項目 (`acceptWorkItem`)
- 完成工作項目 (`completeWorkItem`)
- 退回重辦 (`reexecuteActivity`)
- 檢查工作項目狀態 (`checkWorkItemState`)
- 取得待辦工作項目 (`fetchToDoWorkItem`)

### 錯誤處理

模組採用條件性導入，當依賴不可用時會優雅降級：
```python
try:
    from bpm_wsdl import bpm_wsl
    import zeep
    BPM_AVAILABLE = True
except ImportError as e:
    BPM_AVAILABLE = False
    print(f"Warning: bpm_wsdl module or its dependencies not available. Error: {e}")
```
## Prettier 格式問題及解決方式

### 問題描述

在開發過程中，特別是修改 Vue.js 元件檔案時，可能會遇到 Prettier 格式化錯誤，常見錯誤訊息如：

```
ERROR [vite] Internal server error:
/path/to/file.vue
  186:1  error  Delete ··  prettier/prettier
✖ 1 problem (1 error, 0 warnings)
```

### 常見問題類型

1. **多餘空格問題**
   - 錯誤：行首或行尾有多餘的空格
   - 表現：`Delete ··` 或 `Delete ⏎⏎` 錯誤

2. **縮排不一致問題** 
   - 錯誤：物件或陣列項目縮排不一致
   - 表現：某些行的縮排與同級元素不符

3. **複雜三元運算子格式問題**
   - 錯誤：過於複雜的嵌套三元運算子
   - 表現：要求換行或簡化邏輯

### 解決方法

#### 1. 檢查空格問題
使用 hexdump 檢查具體的空白字符：
```bash
sed -n '186p' /path/to/file.vue | hexdump -C
```

#### 2. 修正縮排問題
確保陣列或物件中所有項目使用一致的縮排（通常是 2 個空格）：

**錯誤範例：**
```javascript
const tableColumns = reactive<TableColumn[]>([
  {
    field: 'field1',
    // ...
  },
{
    field: 'field2',
    // ...
  }
])
```

**正確範例：**
```javascript
const tableColumns = reactive<TableColumn[]>([
  {
    field: 'field1',
    // ...
  },
  {  // 正確的 2 空格縮排
    field: 'field2',
    // ...
  }
])
```

#### 3. 簡化複雜三元運算子
將複雜的嵌套三元運算子改為 if-else 語句：

**問題程式碼：**
```javascript
const statusType = status === '已完成' ? 'success' : status === '處理中' ? 'primary' : status === '已暫停' ? 'warning' : status === '已取消' ? 'danger' : 'info'
```

**修正程式碼：**
```javascript
let statusType = 'info'
if (status === '已完成') statusType = 'success'
else if (status === '處理中') statusType = 'primary' 
else if (status === '已暫停') statusType = 'warning'
else if (status === '已取消') statusType = 'danger'
```

### 預防措施

1. **使用編輯器擴展**
   - 安裝 Prettier 擴展並啟用自動格式化
   - 設定保存時自動格式化

2. **執行格式化命令**
   ```bash
   cd web
   pnpm run lint:format  # 自動修正格式問題
   ```

3. **開發習慣**
   - 保持一致的縮排習慣
   - 避免過於複雜的三元運算子
   - 定期執行 lint 檢查

### 常用檢查命令

```bash
# 檢查 linting 錯誤
cd web && pnpm run lint:eslint

# 自動修正格式問題  
cd web && pnpm run lint:format

# 檢查 TypeScript 類型
cd web && pnpm run ts:check
```

### 實際案例

在實作 IT 服務需求單的"處理狀態"欄位時遇到的問題：

**問題**：第186行有多餘空格導致 `Delete ··` 錯誤
**原因**：陣列物件縮排不一致，某些物件缺少正確的 2 空格縮排
**解決**：使用 hexdump 檢查並修正縮排，確保所有物件使用一致的 2 空格縮排

**檢查指令**：
```bash
sed -n '186p' /path/to/file.vue | hexdump -C
```

**修正前**：物件缺少縮排或有多餘空格
**修正後**：所有物件使用一致的 2 空格縮排

## Vue.js 歷程記錄刪除功能問題及解決方式

### 問題描述

在實作 IT 服務需求單的歷程記錄刪除功能時，會遇到以下 console 錯誤：

```
It.vue:498 刪除歷程記錄失敗: TypeError: Cannot read properties of undefined (reading 'code')
    at Proxy.deleteHistoryRecord (It.vue:490:13)
```

### 問題分析

錯誤發生在 `deleteHistoryRecord` 函數中訪問 `res.code` 時，`res` 為 `undefined`，這表示 API 調用失敗或參數格式錯誤。

### 根本原因

**API 參數格式錯誤**：
- **錯誤用法**: `delBpminItDetailApi({ ids: [row.id] })`  ❌
- **正確用法**: `delBpminItDetailApi([row.id])`  ✅

根據 `web/src/hooks/web/useTable.ts` 的定義和 `web/src/views/Bpmin/It/Detail/Detail.vue` 的使用範例，`delBpminItDetailApi` 函數接受的參數是 **ID 數組**，而不是包含 `ids` 屬性的物件。

### 技術分析

#### useTable Hook 的 fetchDelApi 定義
```typescript
// 來自 web/src/hooks/web/useTable.ts
fetchDelApi?: (ids: string[] | number[] | number | string) => Promise<boolean>
```

#### Detail.vue 中的正確用法
```typescript
// 來自 web/src/views/Bpmin/It/Detail/Detail.vue
fetchDelApi: async (value) => {
  const res = await delBpminItDetailApi(value)  // value 是 ID 數組
  return res.code === 200
}
```

### 解決方案

#### 修正前的錯誤程式碼
```javascript
const res = await delBpminItDetailApi({ ids: [row.id] })  // ❌ 錯誤格式
if (res.code === 200) {  // TypeError: Cannot read properties of undefined
  ElMessage.success('刪除歷程記錄成功')
  await getHistoryList()
} else {
  ElMessage.error('刪除歷程記錄失敗')
}
```

#### 修正後的正確程式碼
```javascript
const res = await delBpminItDetailApi([row.id])  // ✅ 正確格式：直接傳遞 ID 數組
if (res && res.code === 200) {  // ✅ 先檢查 res 存在再檢查 code
  ElMessage.success('刪除歷程記錄成功')
  await getHistoryList()
} else {
  ElMessage.error('刪除歷程記錄失敗')
}
```

### 完整的修正實作

**文件位置**: `web/src/views/Bpmin/It/It/It.vue`

```javascript
// 刪除歷程記錄
const deleteHistoryRecord = async (row: any) => {
  if (!row.id) {
    ElMessage.error('無效的記錄ID')
    return
  }

  try {
    // 確認刪除
    await ElMessageBox.confirm(
      `確定要刪除這筆歷程記錄嗎？\n承辦人員: ${row.create_user}\n工作描述: ${row.work_desc}`,
      '確認刪除',
      {
        confirmButtonText: '確定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    // API 參數應該是 ids 數組，而不是包含 ids 屬性的對象
    const res = await delBpminItDetailApi([row.id])
    if (res && res.code === 200) {
      ElMessage.success('刪除歷程記錄成功')
      await getHistoryList() // 重新載入列表
    } else {
      ElMessage.error('刪除歷程記錄失敗')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('刪除歷程記錄失敗:', error)
      ElMessage.error('刪除歷程記錄失敗')
    }
  }
}
```

### 相關修改

#### 1. 導入必要的 API 和組件
```javascript
import {
  getBpminItDetailListApi,
  addBpminItDetailApi,
  delBpminItDetailApi  // 新增刪除 API
} from '@/api/bpmin/it/detail'

import {
  ElRow,
  ElCol,
  ElMessage,
  ElMessageBox,  // 新增確認對話框
  // ...其他組件
} from 'element-plus'
```

#### 2. 在歷程記錄表格中新增操作欄
```html
<ElTableColumn label="操作" width="80" align="center">
  <template #default="{ row }">
    <BaseButton
      type="danger"
      size="small"
      link
      @click="deleteHistoryRecord(row)"
    >
      刪除
    </BaseButton>
  </template>
</ElTableColumn>
```

### 最佳實踐

1. **API 參數驗證**: 在調用 API 前先檢查參數格式是否正確
2. **錯誤處理**: 在檢查回應屬性前先確認回應物件存在
3. **用戶體驗**: 提供確認對話框避免誤刪，顯示清楚的成功/失敗訊息
4. **資料同步**: 刪除成功後重新載入列表以保持資料一致性

### 調試技巧

當遇到類似的 API 調用問題時：

1. **檢查 API 定義**: 查看 API 函數的型別定義和參數需求
2. **參考既有用法**: 在專案中搜尋相同 API 的其他使用範例
3. **使用 console.log**: 在 API 調用前後加入日誌檢查參數和回應
4. **錯誤處理**: 加入適當的 try-catch 和 null 檢查

```javascript
console.log('API 參數:', [row.id])  //調試參數
const res = await delBpminItDetailApi([row.id])
console.log('API 回應:', res)  //調試回應
```

## Docker 啟動 Web 前端及 Nginx 設置問題及解決方式

### 問題描述
在使用 Docker 啟動 admin 容器時，容器持續重啟，無法正常運行。

### 問題診斷過程

#### 1. 檢查容器狀態
```bash
docker ps -a
```
發現 car-admin 容器狀態為 `Restarting (1)`，表示容器啟動失敗並持續重啟。

#### 2. 查看容器日誌
```bash
docker logs car-admin
```

#### 3. 錯誤信息分析
日誌顯示以下錯誤：
```
2025/08/20 13:26:38 [emerg] 1#1: "proxy_pass" cannot have URI part in location given by regular expression, or inside named location, or inside "if" statement, or inside "limit_except" block in /etc/nginx/conf.d/default.conf:39
nginx: [emerg] "proxy_pass" cannot have URI part in location given by regular expression, or inside named location, or inside "if" statement, or inside "limit_except" block in /etc/nginx/conf.d/default.conf:39
```

### 根本原因
在 `web/default.conf` 文件中，第 38 行的 nginx 配置有語法錯誤：

```nginx
location ~ /openapi\.json$ {
    proxy_pass http://145.10.0.2:8080/; # 問題：末尾有 URI 部分 "/"
}
```

**錯誤原因：**
- 使用了正則表達式 location（`~` 符號）
- 但 `proxy_pass` 指令包含了 URI 部分（末尾的 `/`）
- 在 nginx 中，當使用正則表達式 location 時，`proxy_pass` 不能包含 URI 部分

### 解決方案

#### 1. 修復 nginx 配置文件
修改 `web/default.conf` 文件：

```nginx
# 修改前（錯誤）
location ~ /openapi\.json$ {
    proxy_pass http://145.10.0.2:8080/; # 末尾有 "/"
}

# 修改後（正確）
location ~ /openapi\.json$ {
    proxy_pass http://145.10.0.2:8080; # 移除末尾的 "/"
}
```

#### 2. 重新構建並啟動容器
```bash
# 停止容器
docker stop car-admin

# 重新構建容器（因為配置文件是在構建時複製的）
docker-compose build admin

# 啟動容器
docker-compose up -d admin
```

#### 3. 驗證修復結果
```bash
# 檢查容器狀態
docker ps | grep car-admin

# 查看最新日誌
docker logs --tail 10 car-admin
```

### 成功結果
修復後的容器狀態：
```
CONTAINER ID   IMAGE                  COMMAND                  CREATED          STATUS          PORTS                                           NAMES
6c8d7f694ca6   kinit-template-admin   "/docker-entrypoint.…"   18 seconds ago   Up 17 seconds   0.0.0.0:8080->80/tcp, [::]:8080->80/tcp         car-admin
```

日誌顯示 nginx 工作進程正常啟動：
```
2025/08/20 13:31:55 [notice] 1#1: start worker process 31
2025/08/20 13:31:55 [notice] 1#1: start worker process 32
...
```

### 重要注意事項

1. **配置文件位置：** 
   - 容器使用的是 `web/default.conf`，不是 `docker_env/kinit-admin/nginx/nginx.conf`
   - 配置文件在 Docker 構建時複製到容器內，需要重新構建才能生效

2. **nginx 正則表達式 location 規則：**
   - 使用 `location ~` 時，`proxy_pass` 不能包含 URI 部分
   - 正確：`proxy_pass http://backend;`
   - 錯誤：`proxy_pass http://backend/;`

3. **Docker 容器配置更新流程：**
   - 修改配置文件 → 重新構建容器 → 重新啟動容器

### 相關文件
- `web/default.conf` - nginx 配置文件
- `web/Dockerfile` - 容器構建文件
- `docker-compose.yml` - 容器編排配置