# 系統分析：kinit-template

本文檔提供了 `kinit-template` 專案的系統分析，這是一個單一儲存庫（monorepo），旨在管理多個相互連接的服務，以實現全面的業務應用程式。

## 1. 整體架構

該專案採用單一儲存庫結構，包含四個主要子系統：API 服務、基於網頁的前端、任務排程模組和行動應用程式模組。這些組件透過 Docker Compose 在開發和生產環境中進行協調。

## 2. 子系統

### 2.1. API 服務 (`api`)

*   **目的：** 作為整個系統的後端 API，處理業務邏輯、資料持久化和外部整合。
*   **技術棧：**
    *   **語言：** Python 3.10
    *   **網頁框架：** FastAPI (用於建構高效能 API)
    *   **ORM：** SQLAlchemy 2.0 (用於關聯式資料庫互動)
    *   **資料庫遷移：** Alembic
    *   **CLI 工具：** Typer (用於資料庫初始化等命令列工具)
    *   **主要功能：**
        *   使用者、角色和選單管理
        *   部門和字典管理
        *   檔案上傳 (整合阿里雲 OSS)
        *   登入驗證 (支援手機/密碼和簡訊驗證)
        *   動態系統配置
        *   使用者分佈視覺化 (整合高德地圖 API)
        *   資料概覽和智慧螢幕顯示
        *   全面的日誌記錄 (登入和操作日誌)
        *   互動式 API 文件 (Swagger UI, ReDoc)
        *   資料匯入/匯出功能
        *   自動化 CRUD 程式碼生成 (用於快速 API 開發)
*   **部署：** 使用 Docker 容器化。

### 2.2. 前端網頁系統 (`web`)

*   **目的：** 提供基於網頁的管理介面和 PC 客戶端，用於系統管理和使用者互動。
*   **技術棧：**
    *   **語言：** TypeScript, JavaScript (ES6+)
    *   **框架：** Vue 3
    *   **建置工具：** Vite (用於快速開發和優化建置)
    *   **UI 庫：** Element-Plus (一個流行的 Vue 3 UI 工具包)
    *   **狀態管理：** Pinia
    *   **路由：** Vue Router
    *   **主要庫/功能：**
        *   Axios (HTTP 客戶端)
        *   Echarts (資料視覺化)
        *   Day.js (日期和時間工具)
        *   NProgress (進度條)
        *   Cropper.js (圖片裁剪)
        *   WangEditor (富文本編輯器)
        *   Driver.js (使用者入門導覽)
        *   QRCode.js (QR 碼生成)
        *   Vue I18n (國際化)
        *   Lodash-es (工具函式)
        *   Animate.css (CSS 動畫)
        *   VueUse (Composition API 工具集合)
        *   Iconify (圖標管理)
    *   **樣式：** 使用 UnoCSS (原子 CSS)、PostCSS 和 Less。
    *   **程式碼品質：** 透過 ESLint、Prettier 和 Stylelint 強制執行。
*   **部署：** 容器化並透過 Nginx 提供服務。

### 2.3. 任務排程模組 (`task`)

*   **目的：** 獨立於主 API 服務管理和執行排程和背景任務。
*   **技術棧：**
    *   **語言：** Python 3
    *   **排程器：** APScheduler (用於靈活的任務排程：日期、cron、間隔)
    *   **訊息傳遞：** Redis (透過訊息佇列動態添加任務)
    *   **持久化：** MongoDB (用於儲存持久性任務配置和日誌)
    *   **其他庫：** `requests`, `paramiko` (暗示了外部 API 調用和 SSH 操作的能力)。
*   **主要功能：**
    *   支援各種排程類型 (日期、cron、間隔)。
    *   動態任務管理 (在運行時添加、修改、刪除任務)。
    *   任務執行日誌記錄 (開始/結束時間、持續時間、返回值、錯誤資訊)。
*   **部署：** 使用 Docker 容器化。

### 2.4. 行動應用程式模組 (`app`)

*   **目的：** 提供跨平台行動應用程式體驗。
*   **技術棧：**
    *   **框架：** uni-app (支援單一程式碼庫部署到 H5、Android、iOS 和各種小程序)
    *   **UI 框架：** Vue 2
    *   **UI 庫：** uView UI 2 (一個全面的 uni-app UI 組件庫)
    *   **路由：** uni-simple-router
    *   **工具：** uni-read-pages
*   **基礎：** 基於 RuoYi-Mobile 專案進行二次開發。
*   **部署：** 通常建置為特定平台的套件 (例如，Android 的 APK，iOS 的 IPA，或 H5 的網頁資產)。

## 3. 資料庫和訊息傳遞基礎設施

該專案利用多種資料儲存和訊息傳遞解決方案來滿足不同的需求：

*   **MySQL：** 主要的關聯式資料庫，可能用於結構化資料，例如使用者資訊、角色、權限和核心業務實體。
*   **MongoDB：** 一個 NoSQL 資料庫，由 API 和任務服務使用，用於靈活的資料儲存，例如任務日誌、系統配置或其他非結構化資料。
*   **Redis：** 一個記憶體資料結構儲存，作為高效能快取和服務間通訊的訊息代理 (例如，動態任務排程)。
*   **EMQX (MQTT)：** 一個 MQTT 代理，表示具有即時訊息傳遞能力，可能用於 IoT 整合、推播通知或應用程式內的即時更新。

## 4. 開發環境

*   **Python 版本：** Python 3.10
*   **Node.js 版本：** >= 14.0
*   **套件管理器：** `pip` 用於 Python 依賴，`pnpm` 用於 Node.js 依賴。
*   **推薦 IDE：** PyCharm (用於 Python 開發)，VSCode (用於前端開發)。

## 5. 部署策略

該專案利用 Docker Compose 實現簡化的部署流程，便於在開發和生產環境中輕鬆設定和協調所有服務及其相關資料庫。這種方法確保了一致性並簡化了依賴管理。

## 6. 主要功能和亮點

*   **單一儲存庫效率：** 集中管理多個子系統。
*   **強大後端：** 由 FastAPI 提供支援，提供高效能和豐富的功能集。
*   **現代前端：** 利用 Vue 3 和 Element-Plus 實現響應式且功能豐富的網頁介面。
*   **跨平台行動：** Uni-app 支援從單一程式碼庫高效開發各種行動平台。
*   **進階任務排程：** APScheduler 提供靈活且動態的背景任務管理。
*   **多樣化資料解決方案：** 整合 MySQL、MongoDB 和 Redis 以滿足不同的資料儲存和快取需求。
*   **即時功能：** MQTT 整合暗示支援即時通訊。
*   **開發人員生產力：** 自動化 CRUD 程式碼生成等功能提高了開發速度。

## 2.5. IT 服務請求模組 (`api/apps/bpm/it`)

API 服務中的此模組處理 IT 服務請求的管理，並與外部 BPM (業務流程管理) 系統整合。它遵循分層架構，將關注點分為模型、Schema、參數、CRUD 操作、服務和視圖。

### 2.5.1. 資料存取層 (CRUD) (`api/apps/bpm/it/crud/`)

此目錄包含 BPM IT 服務需求模組的資料存取層 (DAL)。這些檔案負責與 `BpminIt` 和 `BpminItDetail` 模型的資料庫互動。

*   **`__init__.py`**：
    *   **目的**：這是套件初始化檔案。它使 `BpminItDal` 和 `BpminItDetailDal` 類別可以直接從 `api.apps.bpm.it.crud` 套件匯入。
    *   **內容**：
        ```python
        from .bpmin_it import BpminItDal
        from .bpmin_it_detail import BpminItDetailDal
        ```
        這只是從同一目錄中的各自檔案匯入兩個 DAL 類別。

*   **`bpmin_it.py`**：
    *   **目的**：此檔案定義了 `BpminItDal` 類別，它是 `BpminIt` 模型的資料存取層。它處理與 IT 服務需求記錄相關的資料庫操作。
    *   **類別：`BpminItDal`**
        *   繼承自 `core.crud.DalBase`，提供常見的 DAL 功能。
        *   **`__init__(self, db: AsyncSession)`**：
            *   使用非同步 SQLAlchemy 會話 (`db`) 初始化 DAL 實例。
            *   將 `self.model` 設定為 `models.BpminIt`，表示此 DAL 與哪個資料庫表互動。
            *   將 `self.schema` 設定為 `schemas.BpminItSimpleOut`，用於序列化從資料庫操作返回的資料。
        *   **`async def update_data_by_serial_number(self, serial_number: str, data_dict: Dict[str, Any]) -> Any`**：
            *   **目的**：此非同步方法根據 `serial_number` 更新資料庫中現有的 `BpminIt` 記錄。
            *   **流程**：
                1.  它首先查詢資料庫以找到與提供的 `serial_number` 匹配的 `BpminIt` 物件。
                2.  如果找不到物件，則引發異常。
                3.  如果找到，它會遍歷 `data_dict` (鍵值對字典) 並更新 `BpminIt` 物件的相應屬性。
                4.  它呼叫 `await self.flush(obj)` 將更改持久化到資料庫。使用 `flush` 而不是 `commit` 是為了允許呼叫函數 (更高層) 管理事務的提交或回滾。
                5.  最後，它返回更新後的資料，如果可用則使用 `self.schema` 序列化，否則返回原始物件。

*   **`bpmin_it_detail.py`**：
    *   **目的**：此檔案定義了 `BpminItDetailDal` 類別，它是 `BpminItDetail` 模型的資料存取層。它處理與 IT 服務需求詳細記錄相關的資料庫操作。
    *   **類別：`BpminItDetailDal`**
        *   繼承自 `core.crud.DalBase`。
        *   **`__init__(self, db: AsyncSession)`**：
            *   使用 `AsyncSession` 初始化，設定模型 (`models.BpminItDetail`) 和 Schema (`schemas.BpminItDetailSimpleOut`)。
            *   目前，此類別僅提供從 `DalBase` 繼承的基本 CRUD 操作，並且在其內部沒有定義任何自訂方法，類似於 `BpminItDal` 的 `update_data_by_serial_number`。

### 2.5.2. 資料模型 (Schemas) (`api/apps/bpm/it/schemas/`)

此目錄包含 Pydantic 模型，這些模型定義了 IT 服務需求模組的資料結構。這些模型對於以下方面至關重要：

*   **資料驗證**：確保傳入資料 (例如，來自 API 請求的資料) 符合預期的類型和格式。
*   **資料序列化**：將 Python 物件 (例如 SQLAlchemy 模型實例) 轉換為適合 API 回應的格式 (例如 JSON)。
*   **資料反序列化**：將傳入資料 (例如，來自 API 請求的 JSON) 轉換為 Python 物件。

*   **`__init__.py`**：
    *   **目的**：這是套件初始化檔案。它允許您直接從 `api.apps.bpm.it.schemas` 套件匯入 Pydantic 模型，使其在整個應用程式中易於存取。
    *   **內容**：
        ```python
        from .bpmin_it import BpminIt, BpminItSimpleOut
        from .bpmin_it_detail import BpminItDetail, BpminItDetailSimpleOut
        ```
        這匯入了 `BpminIt` 和 `BpminItDetail` 的主要和簡化輸出 Schema。

*   **`bpmin_it.py`**：
    *   **目的**：定義 `BpminIt` (IT 服務需求) 實體的 Pydantic 模型。
    *   **類別：`BpminIt(BaseModel)`**
        *   這是一個 Pydantic `BaseModel`，定義了 IT 服務需求的核心欄位。這些欄位通常對應於 `BpminIt` 資料庫表中的列。
        *   每個欄位都定義了其名稱、類型提示 (例如 `str | None`) 和來自 Pydantic 的 `Field` 物件。`Field` 物件允許添加元資料，例如 `title` (欄位的人類可讀描述)。
        *   **欄位包括**：`it_manager`、`dept`、`apply_date`、`extension`、`fillman`、`main_apply_item`、`sub_apply_item`、`request_desc`、`it_undertaker`、`treatment`、`create_user`、`update_user`、`delete_user` 和 `serial_number`。所有都是可選的 (`| None`)。
    *   **類別：`BpminItSimpleOut(BpminIt)`**
        *   此模型擴展了 `BpminIt`，表示它繼承了所有欄位。
        *   **`model_config = ConfigDict(from_attributes=True)`**：這是 Pydantic V2 的功能。`from_attributes=True` 啟用「ORM 模式」，允許 Pydantic 透過屬性名稱直接從任意類別實例 (例如 SQLAlchemy 模型實例) 讀取資料，而不是要求它們是字典。這對於序列化資料庫查詢結果至關重要。
        *   **附加欄位**：它添加了通常由資料庫或 ORM 生成的欄位，例如：
            *   `id: int = Field(..., title="編號")`：主鍵，標記為必需 (`...`)。
            *   `create_datetime: DatetimeStr = Field(..., title="創建時間")`：創建時間戳，使用自訂的 `DatetimeStr` 類型 (可能是日期時間的字串表示)。
            *   `update_datetime: DatetimeStr = Field(..., title="更新時間")`：上次更新時間戳。
            *   `is_delete: bool = Field(False, title="是否軟刪除")`：用於軟刪除的布林標誌。

*   **`bpmin_it_detail.py`**：
    *   **目的**：定義 `BpminItDetail` (IT 服務需求詳細資訊) 實體的 Pydantic 模型。
    *   **類別：`BpminItDetail(BaseModel)`**
        *   此 `BaseModel` 定義了 IT 服務需求詳細方面的核心欄位。
        *   **欄位包括**：`work_desc`、`rsn` (參考序號)、`status`、`create_user`、`update_user` 和 `delete_user`。所有都是可選的。
    *   **類別：`BpminItDetailSimpleOut(BpminItDetail)`**
        *   擴展了 `BpminItDetail`，繼承其欄位。
        *   **`model_config = ConfigDict(from_attributes=True)`**：啟用 ORM 模式以從資料庫實例進行序列化。
        *   **附加欄位**：類似於 `BpminItSimpleOut`，它添加了資料庫生成的欄位：
            *   `id: int = Field(..., title="編號")`
            *   `create_datetime: DatetimeStr = Field(..., title="創建時間")`
            *   `update_datetime: DatetimeStr = Field(..., title="更新時間")`

### 2.5.3. 查詢參數 (Params) (`api/apps/bpm/it/params/`)

此目錄包含定義和處理與 IT 服務需求模組相關的 API 端點的查詢參數的類別。這些類別旨在與 FastAPI 的依賴注入系統協同工作，以解析和驗證來自傳入 HTTP 請求的參數，特別是用於過濾、搜尋和分頁。

*   **`__init__.py`**：
    *   **目的**：這是套件初始化檔案。它使 `BpminItParams` 和 `BpminItDetailParams` 類別可以直接從 `api.apps.bpm.it.params` 套件匯入。
    *   **內容**：
        ```python
        from .bpmin_it import BpminItParams
        from .bpmin_it_detail import BpminItDetailParams
        ```
        這只是從各自檔案匯入參數類別。

*   **`bpmin_it.py`**：
    *   **目的**：定義在查詢 `BpminIt` (IT 服務需求) 記錄時可以使用的查詢參數。
    *   **類別：`BpminItParams(QueryParams)`**
        *   繼承自 `core.dependencies.QueryParams`，這可能提供了處理常見查詢參數 (例如分頁和潛在的其他過濾機制) 的基本結構。
        *   **`__init__(self, serial_number: str | None = Query(None, title="表單序號"), apply_date: str | None = Query(None, title="申請日期"), it_undertaker: str | None = Query(None, title="IT承辦人"), params: Paging = Depends())`**：
            *   這是建構函數，設計為用作 FastAPI 依賴。
            *   **`serial_number`、`apply_date`、`it_undertaker`**：這些使用 `fastapi.Query` 定義為可選查詢參數。`Query(None, title="...")` 表示它們是可選的，如果 URL 中未提供，則預設值為 `None`。`title` 為 API 文件 (例如 Swagger UI) 提供描述。
            *   **`params: Paging = Depends()`**：這表示將注入 `Paging` 依賴 (來自 `core.dependencies`)。`Paging` 可能處理分頁參數，例如 `page` 和 `page_size`。
            *   **`super().__init__(params)`**：呼叫父 `QueryParams` 類別的建構函數，傳遞 `Paging` 物件，該物件可能初始化與分頁相關的屬性。
            *   **參數處理**：`__init__` 方法然後處理接收到的查詢參數並將它們儲存為 `BpminItParams` 實例的屬性。
                *   `self.serial_number = ("like", serial_number)`：將 `serial_number` 與「like」運算子提示一起儲存，表示它將用於資料庫查詢中的部分字串匹配。
                *   `self.apply_date = ("date", apply_date) if apply_date else None`：如果提供，則將 `apply_date` 與「date」運算子提示一起儲存，表示它將用於日期特定的過濾。
                *   `self.it_undertaker = ("like", it_undertaker)`：將 `it_undertaker` 與「like」運算子提示一起儲存。
            *   這些處理後的屬性通常由 DAL (資料存取層) 用於建構動態資料庫查詢。

*   **`bpmin_it_detail.py`**：
    *   **目的**：定義 `BpminItDetail` (IT 服務需求詳細資訊) 記錄的查詢參數。
    *   **類別：`BpminItDetailParams(QueryParams)`**
        *   繼承自 `core.dependencies.QueryParams`。
        *   **`__init__(self, params: Paging = Depends(), rsn: str = Query(None, description="參照序號"))`**：
            *   類似於 `BpminItParams`，它將 `Paging` 作為依賴。
            *   **`rsn: str = Query(None, description="參照序號")`**：定義一個可選的查詢參數 `rsn` (參考序號) 並附有描述。
            *   **`self.rsn = rsn`**：直接儲存 `rsn`。此參數可能用於過濾與特定主 IT 服務需求相關的詳細記錄。

### 2.5.4. 資料庫模型 (`api/apps/bpm/it/models/`)

此目錄包含 SQLAlchemy ORM (物件關係映射) 模型。這些模型定義了資料庫表的結構，將 Python 類別及其屬性映射到資料庫表和其列。它們是使用 SQLAlchemy 與資料庫互動的基礎。

*   **`__init__.py`**：
    *   **目的**：這是套件初始化檔案。它使 `BpminIt` 和 `BpminItDetail` SQLAlchemy 模型可以直接從 `api.apps.bpm.it.models` 套件匯入。這簡化了應用程式其他部分 (例如，在 CRUD 操作或 API 路由中) 的匯入。
    *   **內容**：
        ```python
        from .it import BpminIt
        from .it_detail import BpminItDetail
        ```
        這從同一目錄中的各自檔案匯入兩個主要模型類別。

*   **`it.py`**：
    *   **目的**：定義 `Bpmin_it` 資料庫表的 SQLAlchemy ORM 模型，該表儲存有關 IT 服務請求表單的資訊。
    *   **類別：`BpminIt(BaseModel)`**
        *   **`BaseModel`**：此類別繼承自 `db.db_base.BaseModel`。`BaseModel` 可能是一個自訂的基礎類別，為專案中的所有 SQLAlchemy 模型提供通用功能，例如主鍵 (`id`)、創建/更新時間戳 (`create_datetime`、`update_datetime`) 和軟刪除 (`is_delete`)。
        *   **`__tablename__ = "Bpmin_it"`**：此類別屬性明確設定此模型映射到的資料庫表的名稱。
        *   **`__table_args__ = ({'comment': 'IT service request form'})`**：這為表定義提供了額外參數。在這裡，它為資料庫表添加了註釋，描述其目的。
        *   **列定義 (使用 `Mapped` 和 `mapped_column`)**：
            *   使用 `Mapped` 和 `mapped_column` 的 SQLAlchemy 2.0 風格來定義列。
            *   `Mapped[str | None]`：這表示 Python 屬性 (`it_manager`、`dept` 等) 映射到儲存字串 (`str`) 且可以為 `None` (可為空) 的資料庫列。
            *   `mapped_column(String(100), comment="IT經理")`：這指定了資料庫列的屬性：
                *   `String(100)`：資料庫中的資料類型 (VARCHAR，最大長度為 100 個字元)。
                *   `comment="IT經理"`：資料庫 Schema 中列的註釋，提供人類可讀的描述。
            *   **關鍵欄位**：
                *   `it_manager`、`dept`、`apply_date`、`extension`、`fillman`、`main_apply_item`、`sub_apply_item`、`request_desc`、`it_undertaker`、`treatment`、`serial_number`：這些代表 IT 服務請求的核心資料欄位。
                *   `datediff: Mapped[float | None] = mapped_column(Float, comment="處理天數")`：一個儲存處理天數的列，為浮點數。
                *   `create_user`、`update_user`、`delete_user`：這些是常見的稽核欄位，儲存負責創建、更新和刪除的使用者 ID。
        *   **`column_config` 字典**：
            *   **目的**：這是一個自訂字典 (不屬於 SQLAlchemy 核心 ORM 功能)，提供前端生成的元資料。它可能由自動程式碼生成工具或網頁前端中的動態表單/列表渲染組件使用。
            *   **結構**：它是一個字典，其中鍵是模型的屬性名稱 (例如 `'id'`、`'it_manager'`)。每個值是另一個字典，包含該欄位的配置：
                *   `'label'`：UI 中欄位的顯示名稱 (例如 '編號'、'IT經理')。
                *   `'field_type'`：要渲染的輸入欄位類型 (例如 `'input'`、`'date'`、`'textarea'`)。
                *   `'show_in_list'`：一個布林值，指示此欄位是否應顯示在列表視圖中。
                *   `'show_in_search'`：一個布林值，指示此欄位是否應可用於搜尋/過濾。
                *   `'required'`：一個布林值，指示該欄位是否為必填。
            *   此配置允許前端動態建構表單、表格和搜尋介面，而無需硬編碼每個欄位的屬性。

*   **`it_detail.py`**：
    *   **目的**：定義 `Bpmin_it_detail` 資料庫表的 SQLAlchemy ORM 模型，該表儲存與 IT 服務請求相關的詳細記錄或歷史記錄。
    *   **類別：`BpminItDetail(BaseModel)`**
        *   繼承自 `db.db_base.BaseModel`，類似於 `BpminIt`。
        *   **`__tablename__ = "Bpmin_it_detail"`**：設定表名。
        *   **`__table_args__ = ({'comment': 'IT service request details'})`**：添加表註釋。
        *   **列定義**：
            *   `work_desc: Mapped[str | None] = mapped_column(String(500), comment="工作描述")`：工作執行或特定詳細資訊的描述。
            *   `rsn: Mapped[str | None] = mapped_column(String(50), comment="參照序號")`：參考序號，可能連結回主 `BpminIt` 記錄。
            *   `status: Mapped[str | None] = mapped_column(String(50), comment="狀態")`：此特定詳細資訊或工作項目的狀態。
        *   **`column_config` 字典**：
            *   類似於 `BpminIt`，此字典為 `BpminItDetail` 欄位提供前端配置，啟用這些詳細記錄的動態 UI 生成。

### 2.5.5. 業務邏輯 (Services) (`api/apps/bpm/it/services/`)

此目錄包含 IT 服務需求模組的「服務層」。此層負責實作業務邏輯，協調資料存取層 (DAL) 和外部系統 (例如 BPM WebService) 之間的互動，並準備資料以供 API 呈現。

*   **`__init__.py`**：
    *   **目的**：此檔案主要有兩個目的：
        1.  **路徑配置**：它動態地將 `../../../../utils` 目錄 (解析為 `api/utils`) 添加到 Python 的 `sys.path`。這允許 `services` 目錄 (以及 `api` 應用程式的其他部分) 中的模組匯入 `bpm_wsdl` 等工具，而無需複雜的相對匯入。
        2.  **服務類別匯入**：它從各自的檔案匯入主要服務類別 (`BpminItServices` 和 `BpminItDetailServices`)，使它們在匯入 `api.apps.bpm.it.services` 套件時易於存取。
    *   **內容**：
        ```python
        import sys
        import os
        # 添加 utils 路徑到 sys.path，讓整個 services 模塊都可以導入 utils 中的模塊
        utils_path = os.path.join(os.path.dirname(__file__), '../../../../utils')
        sys.path.insert(0, utils_path)

        from .bpmin_it import BpminItServices
        from .bpmin_it_detail import BpminItDetailServices
        ```

*   **`bpmin_it.py`**：
    *   **目的**：此檔案定義了 `BpminItServices` 類別，該類別封裝了與 IT 服務請求相關的所有業務邏輯，包括與本地資料庫和外部 BPM (業務流程管理) 系統的互動。
    *   **BPM WSDL 模組的條件性匯入**：
        ```python
        try:
            from utils.bpm_wsdl import bpm_wsl
            import zeep
            BPM_AVAILABLE = True
        except ImportError as e:
            BPM_AVAILABLE = False
            print(f"Warning: bpm_wsdl module or its dependencies not available. Error: {e}. BPM functionality will be limited.")
        ```
        此區塊嘗試匯入 `bpm_wsl` 模組 (處理 BPM WebService 通訊) 及其依賴 `zeep`。如果匯入失敗 (例如，`zeep` 未安裝或 `bpm_wsdl.py` 缺失)，則將 `BPM_AVAILABLE` 設定為 `False`，並列印警告。這允許應用程式即使在 BPM 整合未完全設定的情況下也能運行，優雅地降級功能。
    *   **映射字典**：
        *   `SUB_APPLY_ITEM_MAPPING`、`APPLY_ITEM_MAPPING`、`TREATMENT_MAPPING`、`COMPLETE_STATUS_MAPPING`：這些字典定義了內部「程式碼」值 (例如 `ad_account`) 和人類可讀的「顯示名稱」 (例如 `AD帳號申請`) 之間的映射。
        *   `_REVERSE_MAPPING` 字典：這些是自動生成的反向映射，允許從顯示名稱轉換回程式碼。
        *   **目的**：這些映射對於在前端呈現使用者友好的資訊以及將使用者輸入轉換回內部程式碼以進行資料庫儲存或 BPM 系統互動至關重要。
    *   **輔助方法 (類別方法)**：
        *   `_get_bpm_client()`：一個私有輔助方法，返回 `bpm_wsl` 客戶端的實例。如果 `BPM_AVAILABLE` 為 `False`，它會引發 `ImportError`，確保如果模組未載入，則依賴 BPM 的函數會優雅地失敗。
        *   **程式碼到顯示名稱轉換 (`_get_..._display_name`)**：
            *   `_get_apply_item_display_name`、`_get_sub_apply_item_display_name`、`_get_treatment_display_name`、`_get_complete_status_display_name`：這些方法接受內部程式碼 (或逗號/分號分隔的程式碼字串) 並使用相應的映射字典將其轉換為人類可讀的顯示名稱。它們處理單一字串中存在多個項目。
        *   **顯示名稱到程式碼轉換 (`_get_..._code`)**：
            *   `_get_sub_apply_item_code`、`_get_apply_item_code`、`_get_treatment_code`、`_get_complete_status_code`：這些方法執行反向操作，將顯示名稱轉換回其內部程式碼表示。它們也處理逗號/分號分隔的輸入。
        *   `_calculate_processing_days(db, serial_number, apply_date)`：非同步計算 `apply_date` 與與給定 `serial_number` 相關聯的 *最新* `BpminItDetail` 記錄的 `create_datetime` 之間的天數。
        *   `_get_latest_processing_status(db, serial_number)`：非同步獲取給定 `serial_number` 的最新 `BpminItDetail` 記錄的 `status`。
        *   `_calculate_elapsed_days(apply_date)`：計算從 `apply_date` 到當前系統時間經過的天數。
        *   `_process_data_for_output(data)`：這是一個用於資料轉換的關鍵方法。它接受單個字典或字典列表 (表示 `BpminIt` 記錄) 並執行深層複製。然後，它遍歷特定欄位 (`main_apply_item`、`sub_apply_item`、`treatment`、`is_delete`) 並使用適當的映射函數將其內部程式碼值轉換為人類可讀的顯示名稱。這確保了發送到前端的資料是使用者友好的。
        *   `_format_bmp_response(success, data, method, error)`：一個用於標準化 BPM WebService 呼叫返回的回應格式的工具方法，包括成功狀態、資料、呼叫的方法和任何錯誤訊息。
    *   **BPM WebService 相關方法**：
        *   這些是非同步類別方法，作為 `bpm_wsl` 客戶端函數的包裝器。它們呼叫相應的 BPM WebService 方法，然後使用 `_format_bmp_response` 格式化結果。
        *   範例包括：`accept_work_item`、`fetch_todo_work_item`、`check_work_item_state`、`complete_work_item`、`get_all_xml_form` (獲取完整表單資料)、`fetch_proc_instance_with_serial_no` (獲取簡單表單資料)、`reexecute_activity` (重新處理/返回) 和 `get_wsdl_fun_list` (列出可用的 WSDL 函數)。
    *   **IT 服務請求表單資料處理**：
        *   `_extract_it_form_data(bpm_data, serial_no)`：解析 BPM 的 `get_all_xml_form` 返回的複雜 XML 類結構，以提取與 IT 服務請求相關的特定欄位 (例如 `ItManager`、`Dept`、`ApplyDate`)。它使用正規表達式在 XML 標籤中查找值。
        *   `create_it_request_from_bpm(db, serial_no, auto_create)`：此方法協調從 BPM 資料創建本地 `BpminIt` 記錄。它首先從 BPM 獲取完整表單資料，然後提取相關欄位，如果 `auto_create` 為 true，則使用 `crud.BpminItDal` 將新記錄儲存到本地資料庫。它還處理錯誤報告。
    *   **傳統 CRUD 操作**：
        *   `create_bpmin_it(db, data)`：使用 `crud.BpminItDal` 在本地資料庫中創建新的 IT 服務請求記錄。
        *   `get_bpmin_it(db, data_id)`：透過 ID 檢索單個 IT 服務請求記錄。它使用自訂的 SQLAlchemy 查詢來確保所有記錄 (包括軟刪除的記錄，由 `is_delete=True` 指示) 都被考慮，然後使用 `_process_data_for_output` 處理輸出。
        *   `list_bpmin_it(db, params_dict)`：檢索 IT 服務請求記錄列表。它還使用自訂查詢來包含所有記錄。關鍵是，在返回之前，它會為每個項目計算 `datediff`、`elapsed_days` 和 `latest_processing_status`，然後應用 `_process_data_for_output` 將程式碼轉換為顯示名稱。
        *   `update_bpmin_it(db, data_id, data)`：透過 ID 更新現有的 IT 服務請求記錄。
        *   `update_bpmin_it_by_sn(db, serial_number, data)`：一個專門的更新方法，用於更新 IT 服務請求的 `treatment` 欄位。它首先嘗試從 BPM 系統獲取 `treatment` 值；如果在那裡找不到，則使用 `data` 參數中提供的值。
        *   `update_case_close_status(db, serial_number)`：此方法檢查 BPM 流程的狀態。它從 BPM 獲取活動列表，並特別查找「使用者測試」活動。如果找到此活動且其狀態為「closed.completed」，它會將相應本地 `BpminIt` 記錄的 `is_delete` 欄位更新為 `True`，從而有效地將其標記為已關閉。
        *   `delete_bpmin_it(db, ids, soft_delete)`：刪除 IT 服務請求記錄。它支援透過 `soft_delete` 參數進行軟刪除 (標記 `is_delete=True`) 和硬刪除 (從資料庫中實際刪除)。

*   **`bpmin_it_detail.py`**：
    *   **目的**：此檔案定義了 `BpminItDetailServices` 類別，該類別處理 IT 服務請求的詳細記錄 (歷史/步驟) 的業務邏輯。
    *   **類別：`BpminItDetailServices`**：
        *   它為 `BpminItDetail` 記錄提供標準的非同步 CRUD (創建、讀取、更新、刪除) 操作：
            *   `create_bpmin_it_detail(db, data)`：創建新的詳細記錄。
            *   `get_bpmin_it_detail(db, data_id)`：透過 ID 檢索單個詳細記錄。
            *   `list_bpmin_it_detail(db, params_dict)`：檢索詳細記錄列表。它包含按 `rsn` (參考序號) 過濾的邏輯，該邏輯將詳細資訊連結到其主 IT 請求。
            *   `update_bpmin_it_detail(db, data_id, data)`：更新現有的詳細記錄。
            *   `delete_bpmin_it_detail(db, ids, soft_delete)`：刪除詳細記錄，支援軟刪除和硬刪除。
        *   這些方法主要將實際的資料庫操作委託給 `crud.BpminItDetailDal`，並將結果包裝在標準化的成功/錯誤字典中。

### 2.5.6. API 端點 (Views) (`api/apps/bpm/it/views.py`)

此檔案使用 FastAPI 框架定義了 IT 服務需求模組的 API 端點 (路由)。此檔案在類似 MVC 的架構中充當「控制器」或「視圖層」。其主要職責是：

*   **定義 API 路由**：將 HTTP 方法 (GET、POST、PUT、DELETE) 和 URL 路徑映射到特定的 Python 函數。
*   **請求處理**：解析傳入的請求資料 (查詢參數、表單資料、JSON 主體)。
*   **依賴注入**：利用 FastAPI 的 `Depends` 系統注入必要的組件，例如資料庫會話、驗證資訊和解析後的查詢參數。
*   **委託業務邏輯**：呼叫 `services` 層中的方法來執行實際的業務操作。
*   **回應格式化**：根據服務層呼叫的結果返回標準化的 `SuccessResponse` 或 `ErrorResponse` 物件。
*   **錯誤處理**：捕獲異常並返回適當的錯誤回應。

*   **匯入和設定**：
    *   `from apps.vadmin.auth.utils.current import OpenAuth, AllUserAuth`：匯入驗證依賴。`OpenAuth` 可能表示需要驗證，而 `AllUserAuth` 可能適用於所有已驗證使用者可存取的端點。
    *   `from core.database import db_getter`：匯入提供非同步資料庫會話 (`AsyncSession`) 的依賴。
    *   `from fastapi import Depends, Query, APIRouter, Form`：用於依賴注入、查詢參數、路由和表單資料的核心 FastAPI 組件。
    *   `from sqlalchemy.ext.asyncio import AsyncSession`：非同步資料庫會話的類型提示。
    *   `from apps.vadmin.auth.utils.validation.auth import Auth`：已驗證使用者物件的類型提示。
    *   `from utils.response import ErrorResponse, SuccessResponse`：用於一致 API 輸出的自訂回應類別。
    *   `from . import schemas, models, params, crud, services`：本地模組組件的相對匯入 (Pydantic Schema、SQLAlchemy 模型、查詢參數、CRUD 操作和業務服務)。
    *   `from core.dependencies import IdList`：一個自訂依賴，可能用於從查詢參數解析 ID 列表以進行批次操作。
    *   `app = APIRouter()`：初始化 FastAPI `APIRouter` 實例。這允許對相關端點進行分組並應用通用前綴或依賴。

*   **端點中的常見模式**：
    *   **裝飾器 (`@app.<method>("/path", summary="...")`)**：每個用 `@app.get`、`@app.post` 等裝飾的函數都成為 API 端點。
        *   `summary`：為 API 文件 (例如 Swagger UI) 提供簡短描述。
    *   **依賴 (`Depends`)**：
        *   `p: params.BpminItParams = Depends()`：對於 GET 請求，查詢參數 (例如 `serial_number`、`apply_date`) 會自動解析並驗證為 `BpminItParams` 的實例。
        *   `data: schemas.BpminIt`：對於 POST/PUT 請求，傳入的 JSON 請求主體會自動根據 `BpminIt` Pydantic Schema 進行驗證。
        *   `serial_no: str = Form(...)` 或 `user_id: str = Query(...)`：對於表單資料 (POST) 或單個查詢參數 (GET)，使用 `Form` 和 `Query` 來提取和驗證值。`...` 表示必需參數。
        *   `auth: Auth = Depends(OpenAuth())` 或 `db: AsyncSession = Depends(db_getter)`：這些依賴被注入到端點函數中，提供已驗證使用者的上下文 (包括資料庫會話 `auth.db`) 或直接資料庫會話。
        *   `ids: IdList = Depends()`：用於接受 ID 列表的端點 (例如，用於批次刪除)。
    *   **請求主體 (`data: schemas.BpminIt`)**：解釋 Pydantic Schema 如何用於驗證傳入的 JSON 請求主體。
    *   **表單資料 (`Form(...)`)**：解釋 `Form` 如何用於解析來自 `application/x-www-form-urlencoded` 或 `multipart/form-data` 請求的資料。
    *   **錯誤處理 (`try-except`)**：每個端點都包裝在 `try-except` 區塊中，以捕獲處理過程中潛在的異常。如果發生錯誤，則返回帶有描述性訊息的 `ErrorResponse`。
    *   **回應處理**：
        *   視圖函數呼叫 `services` 層中的方法 (例如 `services.BpminItServices.list_bpmin_it`)。
        *   服務方法通常返回一個字典，其中包含 `success` 布林值、`data`、`message` 和 `error` 欄位。
        *   視圖函數然後檢查 `result['success']` 並返回 `SuccessResponse` (如果適用，帶有 `data`、`message`、`count`) 或 `ErrorResponse` (帶有 `message`)。

*   **區段和特定端點**：

    *   **IT 服務需求單 CRUD 操作**
        這些端點管理主要的 IT 服務請求記錄。

        *   **`GET /it` (`get_bpmin_it_list`)**：
            *   檢索 IT 服務請求列表。
            *   使用 `params.BpminItParams` 處理來自查詢參數的過濾和分頁。
            *   委託給 `services.BpminItServices.list_bpmin_it`。
        *   **`POST /it` (`create_bpmin_it`)**：
            *   創建新的 IT 服務請求。
            *   預期由 `schemas.BpminIt` 驗證的 JSON 請求主體。
            *   委託給 `services.BpminItServices.create_bpmin_it`。
        *   **`POST /it/add-from-bmp` (`create_it_from_bmp`)**：
            *   透過從外部 BPM 系統獲取資料來創建 IT 服務請求。
            *   需要 `serial_no` (BPM 流程序號) 作為表單資料。
            *   委託給 `services.BpminItServices.create_it_request_from_bpm`，並將 `auto_create` 設定為 `True`。
        *   **`POST /it/quick-add-from-bmp` (`quick_create_it_from_bmp`)**：
            *   類似於 `add-from-bmp`，但允許客戶端指定是否 `auto_create` IT 請求或僅預覽 BPM 資料。
            *   需要 `serial_no` 和 `auto_create` 作為表單資料。
        *   **`DELETE /it` (`delete_bpmin_it_list`)**：
            *   刪除一個或多個 IT 服務請求。
            *   使用 `IdList` 依賴來解析 ID 列表。
            *   透過委託給 `services.BpminItServices.delete_bpmin_it` 執行硬刪除 (`soft_delete=False`)。
        *   **`PUT /it/update-treatment-by-sn` (`put_bpmin_it_treatment_by_sn`)**：
            *   根據 `serial_no` 更新 IT 服務請求的 `treatment` 欄位。
            *   需要 `serial_no` 和可選的 `treatment` 作為表單資料。
            *   服務層 (`services.BpminItServices.update_bpmin_it_by_sn`) 優先從 BPM 獲取 `treatment` (如果可用)。
        *   **`POST /it/update-case-close-status` (`update_case_close_status`)**：
            *   檢查給定 `serial_no` 的 BPM 流程，以確定其是否已關閉，並相應地更新本地資料庫狀態。
            *   需要 `serial_no` 作為表單資料。
            *   委託給 `services.BpminItServices.update_case_close_status`。
        *   **`GET /it/{data_id}` (`get_bpmin_it`)**：
            *   透過 `data_id` (主鍵) 檢索單個 IT 服務請求的詳細資訊。
            *   委託給 `services.BpminItServices.get_bpmin_it`。

    *   **BPM WebService API**
        這些端點充當與外部 BPM WebService 直接互動的代理或包裝器，透過 FastAPI 應用程式公開其功能。

        *   **`POST /bmp/work-items/accept` (`accept_work_item`)**：接受 BPM 工作項目。
        *   **`GET /bmp/work-items/todo` (`fetch_todo_work_item`)**：檢索使用者的待處理 BPM 工作項目列表。
        *   **`GET /bmp/check-work-item-state` (`check_work_item_state`)**：檢查特定 BPM 工作項目的狀態。
        *   **`POST /bmp/work-items/complete` (`complete_work_item`)**：完成 BPM 工作項目。
        *   **`GET /bmp/get-all-xml-form` (`get_all_xml_form`)**：檢索 BPM 流程的完整 XML 表單資料。
        *   **`GET /bmo/process-instances/{serial_no}` (`fetch_proc_instance_with_serial_no`)**：檢索 BPM 流程的簡化表單資料。
        *   **`POST /bmp/activities/reexecute` (`reexecute_activity`)**：允許重新執行或返回 BPM 活動。
        *   **`GET /bmp/wsdl-functions` (`get_wsdl_fun_list`)**：檢索 BPM WSDL 中所有可用函數的列表。

    *   **IT 服務需求單歷程 CRUD 操作**
        這些端點管理與 IT 服務請求相關的詳細歷史記錄或步驟。

        *   **`GET /detail` (`get_bpmin_it_detail_list`)**：
            *   檢索 IT 服務請求詳細資訊列表。
            *   使用 `params.BpminItDetailParams` 進行過濾 (例如，按 `rsn` - 參考序號) 和分頁。
            *   委託給 `services.BpminItDetailServices.list_bpmin_it_detail`。
        *   **`POST /detail` (`create_bpmin_it_detail`)**：
            *   創建新的 IT 服務請求詳細資訊。
            *   預期由 `schemas.BpminItDetail` 驗證的 JSON 請求主體。
            *   委託給 `services.BpminItDetailServices.create_bpmin_it_detail`。
        *   **`DELETE /detail` (`delete_bpmin_it_detail_list`)**：
            *   刪除一個或多個 IT 服務請求詳細資訊 (硬刪除)。
            *   使用 `IdList` 依賴。
            *   委託給 `services.BpminItDetailServices.delete_bpmin_it_detail`。
        *   **`PUT /detail/{data_id}` (`put_bpmin_it_detail`)**：
            *   透過 `data_id` 更新現有的 IT 服務請求詳細資訊。
            *   預期由 `schemas.BpminItDetail` 驗證的 JSON 請求主體。
            *   委託給 `services.BpminItDetailServices.update_bpmin_it_detail`。
        *   **`GET /detail/{data_id}` (`get_bpmin_it_detail`)**：
            *   透過 `data_id` 檢索單個 IT 服務請求詳細資訊的詳細資訊。
            *   委託給 `services.BpminItDetailServices.get_bpmin_it_detail`。
