# Alembic 遷移問題處理工具集

這個工具集提供了一站式的 Alembic 遷移問題診斷、修復和驗證解決方案。

## 快速開始

### 一鍵修復 dialogue 欄位問題
```bash
python scripts/migration_helper.py fix-dialogue
```

### 診斷任意欄位問題
```bash
python scripts/migration_helper.py diagnose --table vadmin_test --column dialogue
```

### 自動化完整修復流程
```bash
python scripts/migration_helper.py auto-fix --table vadmin_test --column dialogue
```

## 工具說明

### 1. migration_helper.py - 主工具 🛠️
**用途**: 一站式解決方案，整合所有功能
**推薦**: ⭐⭐⭐⭐⭐ 新手首選

```bash
# 顯示幫助
python scripts/migration_helper.py help

# 互動式模式（最簡單）
python scripts/migration_helper.py interactive

# 一鍵修復 dialogue 欄位
python scripts/migration_helper.py fix-dialogue

# 新增任意欄位
python scripts/migration_helper.py add-column --table my_table --column my_field --type "TEXT"
```

### 2. migration_diagnostic.py - 診斷工具 🔍
**用途**: 診斷遷移問題，不進行修復

```bash
# 基本診斷
python scripts/migration_diagnostic.py

# 診斷特定表和欄位
python scripts/migration_diagnostic.py --table vadmin_test --column dialogue
```

### 3. migration_fix.py - 修復工具 🔧
**用途**: 執行修復操作

```bash
# 修復 dialogue 欄位（快捷方式）
python scripts/migration_fix.py --fix-dialogue

# 新增任意欄位
python scripts/migration_fix.py --add-column --table vadmin_test --column new_field --type "VARCHAR(255)"

# 同步 Alembic 版本
python scripts/migration_fix.py --sync-version --version b8b03c4e431a

# 乾跑模式（查看將執行的操作）
python scripts/migration_fix.py --fix-dialogue --dry-run
```

### 4. migration_verify.py - 驗證工具 ✅
**用途**: 驗證修復結果

```bash
# 驗證 dialogue 欄位
python scripts/migration_verify.py --dialogue

# 驗證特定表結構
python scripts/migration_verify.py --table vadmin_test

# 保存詳細報告
python scripts/migration_verify.py --dialogue --save-report
```

## 常見使用場景

### 場景 1: 新增欄位後發現欄位不存在 ❌→✅

**問題**: 執行了遷移，但資料庫中找不到新欄位

**解決方案**:
```bash
# 方法 1: 使用主工具（推薦）
python scripts/migration_helper.py auto-fix --table vadmin_test --column dialogue

# 方法 2: 分步執行
python scripts/migration_diagnostic.py --table vadmin_test --column dialogue
python scripts/migration_fix.py --add-column --table vadmin_test --column dialogue --type "VARCHAR(500)"
python scripts/migration_verify.py --table vadmin_test --column dialogue
```

### 場景 2: Alembic 版本不同步 🔄

**問題**: 遷移檔案已生成但版本記錄不正確

**解決方案**:
```bash
# 同步到最新版本
python scripts/migration_fix.py --sync-version

# 或指定特定版本
python scripts/migration_fix.py --sync-version --version your_target_version
```

### 場景 3: 批量檢查多個表 📊

**問題**: 需要檢查多個表的結構

**解決方案**:
```bash
# 使用互動式模式
python scripts/migration_helper.py interactive

# 或編寫批次腳本
for table in vadmin_test vadmin_user vadmin_role; do
    python scripts/migration_verify.py --table $table
done
```

### 場景 4: 生產環境謹慎操作 🚨

**問題**: 生產環境需要先確認操作內容

**解決方案**:
```bash
# 1. 先用乾跑模式查看操作
python scripts/migration_fix.py --fix-dialogue --dry-run

# 2. 確認無誤後執行
python scripts/migration_fix.py --fix-dialogue

# 3. 驗證結果
python scripts/migration_verify.py --dialogue --save-report
```

## 安全特性

### 🛡️ 內建安全機制
- **乾跑模式**: 所有修復工具都支援 `--dry-run` 參數
- **備份記錄**: 修復前自動記錄當前狀態
- **回滾功能**: 支援回滾到之前的狀態
- **詳細日誌**: 所有操作都有詳細日誌記錄

### 🔒 最佳實踐
1. **開發環境優先**: 先在開發環境測試
2. **備份重要資料**: 生產環境操作前備份
3. **分步驟執行**: 診斷 → 修復 → 驗證
4. **保存報告**: 使用 `--save-report` 記錄操作結果

## 故障排除

### 常見錯誤及解決方案

#### 1. 資料庫連接失敗
```
❌ 資料庫連接檢查: 連接失敗: Connection refused
```
**解決**: 檢查資料庫服務是否啟動，連接設定是否正確

#### 2. 權限不足
```
❌ 新增欄位時發生錯誤: Access denied
```
**解決**: 確認資料庫用戶有 ALTER TABLE 權限

#### 3. 欄位已存在
```
⚠️ 欄位 dialogue 已存在於 vadmin_test 中
```
**解決**: 這是正常情況，表示欄位已經存在

#### 4. 遷移檔案不存在
```
❌ 遷移目錄不存在: alembic/versions_dev
```
**解決**: 檢查專案結構，確認遷移目錄路徑正確

## 進階使用

### 自定義修復邏輯
可以修改 `migration_fix.py` 中的修復邏輯來適應特定需求。

### 擴展診斷規則
在 `migration_diagnostic.py` 中添加新的診斷規則。

### 客製化驗證項目
修改 `migration_verify.py` 來添加專案特定的驗證項目。

## 技術支援

- **SOP 文檔**: `docs/alembic-migration-troubleshooting-sop.md`
- **問題回報**: 請記錄完整的錯誤訊息和操作步驟
- **開發團隊**: 聯絡專案開發團隊

---

💡 **提示**: 建議將這些工具整合到 CI/CD 流程中，實現自動化的遷移問題檢測和修復。