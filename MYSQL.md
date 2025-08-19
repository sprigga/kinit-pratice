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