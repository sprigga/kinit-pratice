# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a multi-service enterprise management template with separate modules for API, web frontend, mobile app, and scheduled tasks. The system uses FastAPI for the backend, Vue.js for the web frontend, uni-app for mobile development, and APScheduler for task management.

## Architecture

The project consists of four main components:

- **api/**: FastAPI backend service with modular architecture
- **web/**: Vue.js + Element Plus admin dashboard
- **app/**: uni-app mobile application
- **task/**: APScheduler-based task scheduler service

### Backend Architecture (API)

- **FastAPI** framework with async/await patterns
- **SQLAlchemy 2.0** ORM with async support
- **Alembic** for database migrations
- **Modular structure** under `apps/vadmin/` with separate modules for auth, system, records, etc.
- **Core services** in `core/` for database, middleware, validation, etc.
- **Utilities** in `utils/` for common functions

### Database Support

- **MySQL 8.0+**: Primary database
- **MongoDB**: Document storage for logs and analytics
- **Redis**: Caching and pub/sub messaging

## Development Commands

### API Service (FastAPI)

```bash
cd api

# Install dependencies
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# Initialize database (development)
python main.py init --env dev

# Initialize database (production)
python main.py init

# Create new app module
python main.py init-app vadmin/new_module_name
```

### Web Frontend

```bash
cd web

# Install dependencies
pnpm install

# Development server
pnpm run dev

# Type checking
pnpm run ts:check

# Linting and formatting
pnpm run lint:eslint
pnpm run lint:format
pnpm run lint:style

# Build for production
pnpm run build:pro

# Build for development
pnpm run build:dev
```

### Mobile App (uni-app)

```bash
cd app

# Development typically done through uni-app IDE or CLI tools
# No specific build commands defined in package.json
```

### Task Scheduler

```bash
cd task

# Install dependencies
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# Run scheduler
python main.py
```

### Docker Deployment

```bash
# Start all services
docker-compose up -d

# Initialize database in container
docker-compose exec kinit-api python3 main.py init

# Restart all services
docker-compose restart
```

## Key Configuration Files

### Database Configuration

- `api/alembic.ini`: Database migration settings
- `api/application/config/development.py`: Development database settings
- `api/application/config/production.py`: Production database settings

### Environment Settings

- `api/application/settings.py`: Main application settings
  - Set `DEBUG = True` for development
  - Set `DEBUG = False` for production

## Code Generation

The project includes CRUD code generation capabilities:

```bash
cd api
python scripts/crud_generate/main.py
```

This generates:
- Schema serialization code
- DAL (Data Access Layer) code  
- Parameter validation code
- View/API endpoint code

## Development Guidelines

### Database Operations

- Always use async database operations with SQLAlchemy
- Use Alembic for schema migrations
- Test migrations in development environment first

### API Development

- Follow the modular structure under `apps/vadmin/`
- Each module should have: models, schemas, crud, params, views
- Use the provided base classes in `core/` for consistency

### Authentication

- JWT-based authentication with refresh tokens
- OAuth2 password flow implementation
- Role-based permissions system

## Testing and Quality Assurance

- Run type checking: `pnpm run ts:check` (web)
- Run linting: `pnpm run lint:eslint` (web)
- Ensure database migrations work before deployment
- Test Docker compose setup for production deployment

## Default Credentials

- Admin account: `15020221010` / `kinit2022`
- Test account: `15020240125` / `test`

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