# MySQL 數據庫問題排除指南

本文檔記錄在設置和初始化 MySQL 數據庫時遇到的問題及解決方案。

## 目錄
1. [模組導入錯誤](#模組導入錯誤)
2. [Docker 權限問題](#docker-權限問題)
3. [MySQL InnoDB 鎖定錯誤](#mysql-innodb-鎖定錯誤)
4. [Alembic 遷移衝突](#alembic-遷移衝突)
5. [數據庫初始化成功步驟](#數據庫初始化成功步驟)

## 模組導入錯誤

### 問題描述
```
ModuleNotFoundError: No module named 'apps.bpm'
ModuleNotFoundError: No module named 'apps.vadmin.test'
```

### 解決方案
註釋掉缺失的模組導入：

**文件：`api/application/urls.py`**
```python
# 註釋掉缺失的模組導入
# from apps.bpm.it.views import app as bpmin_it_detail_app
# from apps.bpm.it.views import app as bpmin_it_app
# from apps.vadmin.test.views import app as vadmin_test_app

# 同時註釋掉對應的路由配置
urlpatterns = [
    # {"path": "/api/v1/test", "app": vadmin_test_app, "tags": ["測試模組"]},
    # {"path": "/api/v1/bpm-in", "app": bpmin_it_app, "tags": ["BPM IT"]},
    # {"path": "/api/v1/bpm-in-detail", "app": bpmin_it_detail_app, "tags": ["BPM IT Detail"]},
]
```

**文件：`api/alembic/env.py`**
```python
# 註釋掉有問題的模型導入
# from apps.vadmin.test.models import *
# from apps.bpm.it.models import *
```

## Docker 權限問題

### 問題描述
```
permission denied while trying to connect to the Docker daemon socket
```

### 解決方案
使用 sudo 權限執行 Docker 命令：
```bash
sudo docker compose --profile mysql up -d
sudo docker logs car-mysql -f
sudo docker compose down
```

## MySQL InnoDB 鎖定錯誤

### 問題描述
```
[ERROR] [MY-012574] [InnoDB] Unable to lock ./ibdata1 error: 11
```

### 原因
MySQL 數據文件被之前的進程鎖定，無法正常啟動。

### 解決方案
1. 停止 MySQL 容器
```bash
sudo docker compose down
```

2. 清理 MySQL 數據目錄
```bash
sudo rm -rf /home/ubuntu/kinit-template/docker_env/mysql/data/*
```

3. 重新啟動 MySQL 容器
```bash
sudo docker compose --profile mysql up -d
```

4. 確認 MySQL 正常啟動
```bash
sudo docker logs car-mysql -f
```

成功日誌應包含：
```
[System] [MY-010931] [Server] /usr/sbin/mysqld: ready for connections. Version: '8.0.43'
```

## Alembic 遷移衝突

### 問題描述
```
ERROR [alembic.util.messaging] Target database is not up to date.
(pymysql.err.OperationalError) (1051, "Unknown table 'oa.mes_printer'")
```

### 原因
遷移文件嘗試刪除不存在的表，導致遷移失敗。

### 解決方案
標記數據庫為最新版本，跳過有問題的遷移：
```bash
source .venv/bin/activate
cd api
alembic --name dev stamp head
```

## 數據庫配置

### 開發環境配置
**文件：`api/application/config/development.py`**
```python
# MySQL 配置
MYSQL_USER = urllib.parse.quote_plus('oa-admin')
MYSQL_SERVER_IP = urllib.parse.quote_plus('192.168.30.20')  # 外部MySQL服務器
MYSQL_PORT = '3306'
MYSQL_PASSWORD = 'Bdfrost168'
MYSQL_DB = urllib.parse.quote_plus(PROJECT_NAME)
```

**文件：`api/alembic.ini`**
```ini
# 開發環境數據庫配置
DB_USER = oa-admin
DB_PASSWORD_DEV = Bdfrost168
DB_HOST_DEV = 192.168.30.20
DB_PORT_DEV = 3306
DB_NAME_DEV = oa
```

### MySQL 用戶權限設置
連接到 MySQL 並設置用戶權限：
```sql
-- 創建數據庫
CREATE DATABASE IF NOT EXISTS oa;

-- 創建或重置用戶
ALTER USER 'oa-admin'@'%' IDENTIFIED BY 'Bdfrost168';

-- 授權
GRANT ALL PRIVILEGES ON oa.* TO 'oa-admin'@'%';

-- 刷新權限
FLUSH PRIVILEGES;
```

## 數據庫初始化成功步驟

### 完整初始化流程
1. **確保虛擬環境已激活**
```bash
cd /home/ubuntu/kinit-template
source .venv/bin/activate
```

2. **確保 MySQL 服務可用**
```bash
# 測試連接
nc -zv 192.168.30.20 3306
```

3. **執行數據庫初始化**
```bash
cd api
python main.py init --env dev
```

### 成功初始化日誌
```
環境：dev  3.10.1 數據庫表遷移完成
vadmin_auth_menu 表數據已生成
vadmin_auth_role 表數據已生成
vadmin_auth_dept 表數據已生成
vadmin_auth_user 表數據已生成
vadmin_auth_user_depts 表數據已生成
vadmin_auth_user_roles 表數據已生成
vadmin_system_settings_tab 表數據已生成
vadmin_system_dict_type 表數據已生成
vadmin_system_settings 表數據已生成
vadmin_system_dict_details 表數據已生成
vadmin_help_issue_category 表數據已生成
vadmin_help_issue 表數據已生成
環境：dev 3.10.1 數據已初始化完成
```

## 常用維護命令

### 檢查數據庫狀態
```bash
# 檢查 MySQL 容器狀態
sudo docker ps | grep mysql

# 檢查 MySQL 日誌
sudo docker logs car-mysql

# 測試數據庫連接
nc -zv 192.168.30.20 3306
```

### Alembic 常用命令
```bash
# 檢查當前遷移狀態
alembic --name dev current

# 查看遷移歷史
alembic --name dev history

# 升級到最新版本
alembic --name dev upgrade head

# 標記為最新版本（跳過遷移）
alembic --name dev stamp head
```

### 啟動 API 服務
```bash
cd /home/ubuntu/kinit-template
source .venv/bin/activate
cd api
python main.py run
```

## 預設帳號

- **管理員帳號**: `15020221010` / `kinit2022`
- **測試帳號**: `15020240125` / `test`

## MongoDB 容器設置和問題排除

### 1. MongoDB 容器掛載錯誤

#### 問題描述
```
failed to create task for container: OCI runtime create failed: unable to start container process: 
error mounting "/data/db": no such file or directory
```

#### 解決方案
1. 創建缺失的 MongoDB 目錄
```bash
mkdir -p /home/ubuntu/kinit-template/docker_env/mongo/data
mkdir -p /home/ubuntu/kinit-template/docker_env/mongo/log
```

2. 使用 sudo 權限啟動 MongoDB 容器
```bash
sudo docker-compose --profile mongo up -d
```

3. 如果仍有問題，清理並重啟
```bash
sudo docker-compose down mongo
sudo rm -rf /home/ubuntu/kinit-template/docker_env/mongo/data/*
sudo docker-compose --profile mongo up -d
```

### 2. MongoDB 用戶認證問題

#### 問題描述
```
MongoServerError[AuthenticationFailed]: Authentication failed.
```

#### 原因分析
- 配置文件與初始化腳本中的用戶信息不匹配
- 用戶創建在錯誤的數據庫中
- 環境變數與初始化腳本衝突

#### 初始化腳本配置
**文件：`docker_env/mongo/init-mongo.js`**
```javascript
db = db.getSiblingDB('car');

db.createUser({
  user: 'oa-admin',
  pwd: 'Bdfrost168',
  roles: [
    { role: "readWrite", db: "bd-oa" },
    { role: "dbAdmin", db: "bd-oa" }
  ]
});
```

#### 應用配置文件
**文件：`api/application/config/development.py`**
```python
MONGO_DB_ENABLE = True
MONGO_DB_NAME = "bd-oa"
MONGO_DB_USERNAME = "oa-admin"
MONGO_DB_PASSWORD = "Bdfrost168"
MONGO_DB_URL = f"mongodb://{MONGO_DB_USERNAME}:{MONGO_DB_PASSWORD}@192.168.30.20:27017/?authSource=car"
```

### 3. MongoDB 連接測試

#### 正確的連接命令
```bash
sudo docker exec -it car-mongo mongosh --username oa-admin --password "Bdfrost168" --authenticationDatabase car
```

#### 在 MongoDB Shell 中測試
```javascript
// 1. 檢查連接狀態和權限
db.runCommand({connectionStatus: 1})

// 2. 切換到應用數據庫
use bd-oa

// 3. 測試寫入權限
db.test.insertOne({name: "connection_test", timestamp: new Date()})

// 4. 測試讀取權限
db.test.find()

// 5. 查看集合
show collections

// 6. 查看數據庫
show dbs
```

### 4. MongoDB 用戶權限說明

#### 用戶創建位置
- **認證數據庫**: `car`
- **應用數據庫**: `bd-oa`
- **用戶**: `oa-admin`
- **密碼**: `Bdfrost168`

#### 權限設置
- `readWrite`: 對 `bd-oa` 數據庫的讀寫權限
- `dbAdmin`: 對 `bd-oa` 數據庫的管理權限（創建索引、查看統計等）

### 5. MongoDB 故障排除步驟

#### 完整重新初始化流程
```bash
# 1. 停止 MongoDB 容器
sudo docker-compose down mongo

# 2. 清理數據目錄
sudo rm -rf /home/ubuntu/kinit-template/docker_env/mongo/data/*

# 3. 確保目錄存在
mkdir -p /home/ubuntu/kinit-template/docker_env/mongo/data
mkdir -p /home/ubuntu/kinit-template/docker_env/mongo/log

# 4. 重新啟動容器
sudo docker-compose --profile mongo up -d

# 5. 檢查容器日誌
sudo docker logs car-mongo -f

# 6. 等待初始化完成後測試連接
sudo docker exec -it car-mongo mongosh --username oa-admin --password "Bdfrost168" --authenticationDatabase car
```

#### 檢查容器狀態
```bash
# 檢查容器運行狀態
sudo docker ps | grep mongo

# 檢查容器日誌
sudo docker logs car-mongo

# 檢查容器詳細信息
sudo docker inspect car-mongo
```

### 6. MongoDB 環境變數配置

#### Docker Compose 環境變數
**文件：`.env`**
```bash
MONGO_PORT=27017
MONGO_EXPOSE_PORT=27017
MONGO_USER=afu
MONGO_PASS=Y05os5352
MONGO_IP=145.10.0.6
```

**注意**: 環境變數中的 `MONGO_USER` 和 `MONGO_PASS` 用於創建 MongoDB 的 root 管理員用戶，與應用用戶不同。

## 注意事項

1. **Docker 權限**: 如果遇到權限問題，需要使用 `sudo` 執行 Docker 命令
2. **數據清理**: 清理 MySQL 或 MongoDB 數據目錄會刪除所有現有數據，請謹慎操作
3. **遷移衝突**: 如果遇到遷移衝突，可以使用 `stamp head` 標記為最新版本
4. **虛擬環境**: 確保在正確的虛擬環境中執行 Python 命令
5. **網路連接**: 確保能夠訪問外部服務器：
   - MySQL: `192.168.30.20:3306`
   - MongoDB: `192.168.30.20:27017`
6. **目錄創建**: 確保所有 Docker 掛載目錄都已創建並具有正確權限
7. **認證信息**: 
   - MySQL: 用戶 `oa-admin`，密碼 `Bdfrost168`，數據庫 `oa`
   - MongoDB: 用戶 `oa-admin`，密碼 `Bdfrost168`，認證數據庫 `car`，應用數據庫 `bd-oa`
8. **環境變數**: 區分 Docker 環境變數（root 用戶）和應用配置（應用用戶）

---

# MySQL容器數據備份與恢復完整指令摘要

## 📋 備份流程 (Backup Process)

### 1. 檢查當前MySQL容器狀態
```bash
# 檢查容器運行狀態
docker-compose ps | grep mysql

# 檢查數據目錄結構
ls -la /path/to/docker_env/mysql/data/
```

### 2. 停止MySQL服務
```bash
# 停止MySQL容器（保持其他服務運行）
docker-compose stop mysql
```

### 3. 創建數據備份
```bash
# 進入MySQL目錄
cd /path/to/docker_env/mysql

# 使用Docker臨時容器備份（推薦方法）
docker run --rm -v "$(pwd)":/backup alpine sh -c "cp -r /backup/data /backup/data_backup_$(date +%Y%m%d_%H%M%S)"

# 或者如果有sudo權限
sudo cp -r data "data_backup_$(date +%Y%m%d_%H%M%S)"
```

## 🔄 恢復流程 (Restore Process)

### 1. 檢查備份目錄
```bash
# 確認備份數據完整性
ls -la /path/to/docker_env/mysql/data_backup_YYYYMMDD_HHMMSS/

# 檢查關鍵文件是否存在
ls -la /path/to/docker_env/mysql/data_backup_YYYYMMDD_HHMMSS/ | grep -E "(ibdata1|mysql|oa)"
```

### 2. 停止MySQL服務
```bash
# 確保MySQL容器完全停止
docker-compose stop mysql

# 檢查容器狀態
docker-compose ps mysql
```

### 3. 備份當前數據（可選但建議）
```bash
# 備份當前數據作為安全措施
cd /path/to/docker_env/mysql
docker run --rm -v "$(pwd)":/backup alpine sh -c "cp -r /backup/data /backup/data_backup_current_$(date +%Y%m%d_%H%M%S)"
```

### 4. 恢復備份數據
```bash
# 使用Docker臨時容器進行恢復（推薦方法）
cd /path/to/docker_env/mysql
docker run --rm -v "$(pwd)":/backup alpine sh -c "rm -rf /backup/data && cp -r /backup/data_backup_YYYYMMDD_HHMMSS /backup/data"
```

## 🔐 權限處理方法對比

### 方法一：Docker臨時容器（推薦）
```bash
# 優點：無需sudo，自動化友好，安全可靠
docker run --rm -v "$(pwd)":/backup alpine sh -c "COMMAND_HERE"

# 實際範例
docker run --rm -v "$(pwd)":/backup alpine sh -c "rm -rf /backup/data && cp -r /backup/data_backup_20250822_104425 /backup/data"
```

### 方法二：sudo權限（需要密碼）
```bash
# 需要互動式密碼輸入
sudo rm -rf data
sudo cp -r data_backup_YYYYMMDD_HHMMSS data
```

### 方法三：權限修改（不推薦）
```bash
# 可能影響MySQL服務正常運行
sudo chown -R $USER:$USER data/
# 操作完成後需要恢復權限
sudo chown -R mysql:mysql data/
```

## ✅ 服務重啟與驗證

### 5. 重啟MySQL服務
```bash
# 方法一：重新啟動MySQL容器
docker-compose start mysql

# 方法二：如果遇到掛載問題，完全重建
docker-compose down
docker-compose up -d mysql

# 檢查容器狀態
docker-compose ps mysql
```

### 6. 驗證數據恢復
```bash
# 等待MySQL完全啟動（約10秒）
sleep 10

# 獲取MySQL密碼（從.env文件）
grep MYSQL_PASS /path/to/project/.env

# 測試數據庫連線
docker-compose exec mysql mysql -u root -p'YOUR_PASSWORD' -e "SHOW DATABASES;"

# 驗證特定數據庫的表格
docker-compose exec mysql mysql -u root -p'YOUR_PASSWORD' -e "USE oa; SHOW TABLES;" 2>/dev/null

# 檢查關鍵業務表的記錄數量
docker-compose exec mysql mysql -u root -p'YOUR_PASSWORD' -e "USE oa; SELECT COUNT(*) FROM Bpmin_it;" 2>/dev/null
```

## 📝 完整執行範例

### 實際恢復指令序列：
```bash
# 1. 檢查狀態
cd /home/ubuntu/kinit-template/docker_env/mysql
docker-compose ps | grep mysql
ls -la data_backup_before_restore_20250822_104425/

# 2. 停止服務
docker-compose stop mysql

# 3. 恢復數據
docker run --rm -v "$(pwd)":/backup alpine sh -c "rm -rf /backup/data && cp -r /backup/data_backup_before_restore_20250822_104425 /backup/data"

# 4. 重啟服務
docker-compose up -d mysql

# 5. 驗證恢復
sleep 10
docker-compose exec mysql mysql -u root -p'Y05os@5352' -e "SHOW DATABASES;"
docker-compose exec mysql mysql -u root -p'Y05os@5352' -e "USE oa; SHOW TABLES;" 2>/dev/null
```

## 🔍 技術原理說明

### Docker權限處理機制
1. **容器內外權限映射**：Docker容器內的root用戶可以操作掛載的外部文件，繞過宿主機的權限限制
2. **臨時容器模式**：使用`--rm`標記的臨時容器執行完操作後自動清理，不留下任何痕跡
3. **Volume掛載特性**：容器可以完全控制掛載的volume內容，包括特殊權限的數據庫文件

### MySQL文件權限特性
```bash
# MySQL數據文件的典型權限設置
-rw-r----- 1 dnsmasq root  196608 Aug 22 11:49 #ib_16384_0.dblwr
-rw-r----- 1 dnsmasq root 8585216 Aug 22 11:09 #ib_16384_1.dblwr
drwxr-x--- 2 dnsmasq root    4096 Aug 22 11:10 #innodb_redo
```

**問題原因**：
- 所有者是 `dnsmasq`（Docker MySQL容器內的MySQL用戶ID在宿主機上的映射）
- 權限設置 `640` (`rw-r-----`)：只有所有者可以寫入，組用戶只能讀取
- 普通用戶無法直接操作這些文件

## ⚠️ 備份恢復注意事項

1. **備份頻率**：建議在重要操作前都進行備份
2. **權限問題**：優先使用Docker容器方法處理權限問題
3. **服務依賴**：確保API服務等依賴MySQL的服務在恢復後正常重啟
4. **密碼安全**：避免在腳本中硬編碼密碼，從環境變數或配置文件讀取
5. **數據一致性**：必須先停止MySQL服務再進行數據目錄操作
6. **完整性驗證**：恢復後務必驗證數據庫連線和關鍵表格結構

## 🚨 備份恢復故障排除

### 常見問題及解決方案

#### 1. 權限拒絕錯誤
```bash
# 錯誤：rm: cannot remove 'data/xxx': Permission denied
# 解決：使用Docker臨時容器
docker run --rm -v "$(pwd)":/backup alpine sh -c "rm -rf /backup/data"
```

#### 2. MySQL啟動失敗
```bash
# 錯誤：Container startup failed
# 解決：完全重建容器
docker-compose down
docker-compose up -d mysql
```

#### 3. 掛載權限問題
```bash
# 錯誤：failed to create task for container
# 解決：重新創建容器而不是僅僅restart
docker-compose down && docker-compose up -d mysql
```

#### 4. 數據庫連線失敗
```bash
# 檢查MySQL是否完全啟動
docker-compose logs mysql

# 等待更長時間再測試連線
sleep 30
```

#### 5. 備份目錄權限問題
```bash
# 如果無法創建備份目錄
sudo mkdir -p /path/to/backup/directory
sudo chown $USER:$USER /path/to/backup/directory
```

## 📋 備份恢復最佳實踐

1. **定期備份**：建立自動化備份腳本，定期執行
2. **備份驗證**：每次備份後驗證備份文件的完整性
3. **多層備份**：保留多個時間點的備份，不要只保留最新的
4. **恢復測試**：定期在測試環境中測試恢復流程
5. **文檔記錄**：記錄每次備份和恢復的操作，包括時間和原因
6. **權限管理**：使用Docker容器方法避免直接修改文件權限

這套備份恢復流程已在實際環境中驗證有效，適用於Docker Compose管理的MySQL容器環境。