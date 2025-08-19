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

# Run database migrations
python main.py migrate --env dev

# Start development server
python main.py run

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
{  // 缺少正確縮排
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

**問題代碼：**
```javascript
const statusType = status === '已完成' ? 'success' : status === '處理中' ? 'primary' : status === '已暫停' ? 'warning' : status === '已取消' ? 'danger' : 'info'
```

**修正代碼：**
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
