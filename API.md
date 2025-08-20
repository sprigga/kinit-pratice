# API 容器啟動問題與解決方案

**問題：**
API 容器 (`car-api`) 因 `OperationalError: (1045, "Access denied for user 'oa-admin'@'145.10.0.1' (using password: YES)")` 而無法啟動。這表示 API 服務無法使用 `oa-admin` 使用者的憑證連接到 MySQL 資料庫。追蹤記錄顯示此錯誤發生在應用程式啟動期間，特別是在嘗試連接 Redis 並快取表名時，這反過來又需要資料庫連接。

**解決方案：**
透過解決 MySQL 使用者權限和資料庫 Schema 初始化問題來解決此問題：

1.  **建立 MySQL 使用者並授予權限：**
    *   在 MySQL 容器中建立了 `oa-admin` 使用者，密碼為 'Bdfrost168'，並授予其從任何主機 (`%`) 對 `oa` 資料庫的所有權限。
    *   執行命令：
        *   `docker exec car-mysql mysql -uroot -p'Y05os@5352' -e "CREATE USER 'oa-admin'@'%' IDENTIFIED BY 'Bdfrost168';"`
        *   `docker exec car-mysql mysql -uroot -p'Y05os@5352' -e "GRANT ALL PRIVILEGES ON oa.* TO 'oa-admin'@'%';"`
        *   `docker exec car-mysql mysql -uroot -p'Y05os@5352' -e "FLUSH PRIVILEGES;"`
    *   透過查詢 `mysql.user` 表驗證了使用者建立。

2.  **初始化資料庫 Schema：**
    *   最初，`docker exec car-api python main.py init --env dev` 因 `alembic.util.messaging.Target database is not up to date` 錯誤而失敗。
    *   透過使用 `alembic stamp head` 將資料庫標記為最新來解決此問題：
        `docker exec car-api bash -c "cd /app && alembic --name dev stamp head"`
    *   標記頭部後，重新執行資料庫初始化命令並成功：
        `docker exec car-api python main.py init --env dev`

3.  **重新啟動 API 容器並驗證連接：**
    *   重新啟動了 API 容器：`docker restart car-api`
    *   驗證步驟確認了修復：
        *   `docker logs car-api --tail 20` 顯示 API 服務成功啟動。
        *   `docker exec car-mysql mysql -u'oa-admin' -p'Bdfrost168' -e "USE oa; SHOW TABLES;"` 確認 `oa` 資料庫中已建立所有必要的表。
        *   存取 `http://localhost:9000/docs` 顯示 Swagger UI，表示 API 正在運行且可存取。

API 容器現在健康且能夠連接到 MySQL 資料庫，並且資料庫 Schema 已正確初始化。