CREATE DATABASE IF NOT EXISTS kinit;

-- 切換到該數據庫
USE kinit;

-- 創建 odin_auction 表
CREATE TABLE odin_auction (
    id BIGINT PRIMARY KEY AUTO_INCREMENT NOT NULL COMMENT '自增主鍵',
    item_name VARCHAR(255) NOT NULL,             -- 拍賣項目名稱
    collect_price DECIMAL(10, 2),                -- 收藏價格
    bid_price DECIMAL(10, 2),                    -- 競標價格
    bid_type VARCHAR(255) NOT NULL,   -- 競標類型
    power_limit DECIMAL(10, 2),                  -- 限定戰力
    quantity INT,                                -- 商品數量
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 起標時間
    end_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '結標時間', -- 結標時間
    notes TEXT,                                  -- 備註
    guild_id VARCHAR(255),                       -- 所在公會
    winner VARCHAR(255),                         -- 得標者，逗號分隔（例如：玩家A,玩家B）
    max_winners INT DEFAULT 1,                   -- 本次拍賣可得標人數（預設為1）
    status TINYINT DEFAULT 0,                    -- 狀態：0=未開始, 1=競標中, 2=已結束
    -- 系統信息
    create_user VARCHAR(30) COMMENT '建立者',
    update_user VARCHAR(30) COMMENT '更新者',
    delete_user VARCHAR(30) COMMENT '刪除者',
    create_datetime DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '建立時間',
    update_datetime DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新時間',
    delete_datetime DATETIME COMMENT '刪除時間',
    is_delete TINYINT(1) DEFAULT 0 COMMENT '是否刪除標記'
);

-- 創建 odin_auction_details 表，設置外鍵關聯並添加 ON DELETE CASCADE
CREATE TABLE odin_auction_details (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,        -- 唯一識別碼
    auction_id BIGINT NOT NULL,                  -- 拍賣主表的 ID (外鍵)
    bid_amount DECIMAL(10, 2),                   -- 競標金額
    bid_type VARCHAR(255) NOT NULL, -- 競拍用途
    character_name VARCHAR(255) NOT NULL,        -- 角色名稱
    guild_name VARCHAR(255) NOT NULL,            -- 公會名稱
    power DECIMAL(10, 2),                        -- 角色戰力
    bid_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 投標時間
    -- 系統信息
    create_user VARCHAR(30) COMMENT '建立者',
    update_user VARCHAR(30) COMMENT '更新者',
    delete_user VARCHAR(30) COMMENT '刪除者',
    create_datetime DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '建立時間',
    update_datetime DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新時間',
    delete_datetime DATETIME COMMENT '刪除時間',
    is_delete TINYINT(1) DEFAULT 0 COMMENT '是否刪除標記',
    -- 設置外鍵約束並添加 ON DELETE CASCADE
    FOREIGN KEY (auction_id)
    REFERENCES odin_auction(id)
    ON DELETE CASCADE  -- 當刪除主表記錄時，自動刪除子表記錄
);



-- MES 工單
CREATE TABLE IF NOT EXISTS mes_mam_mo (
    id INT PRIMARY KEY AUTO_INCREMENT NOT NULL COMMENT '自增主鍵',

    -- ERP欄位
    sfaaent INT NOT NULL COMMENT '企業編號',
    sfaasite VARCHAR(10) NOT NULL COMMENT '據點',
    sfaadocno VARCHAR(20) NOT NULL COMMENT '單號',
    sfaadocdt DATE NOT NULL COMMENT '單據日期',
    sfaastus CHAR(1) NOT NULL COMMENT '單據狀態',
    sfaaua001 CHAR(1) NOT NULL COMMENT 'MES拋轉碼 (Y=生產中, N=未生產, V=已結案)',
    sfaa001 INT COMMENT '工單版本',
    sfaa002 VARCHAR(20) COMMENT '生管人員',
    sfaa003 CHAR(1) NOT NULL COMMENT '工單類型',
    sfaa004 CHAR(1) COMMENT '發料制度',
    sfaa005 VARCHAR(30) COMMENT '工單來源',
    sfaa006 VARCHAR(30) COMMENT '來源單號',
    sfaa007 VARCHAR(30) COMMENT '來源項次',
    sfaa008 VARCHAR(30) COMMENT '來源項序',
    sfaa009 VARCHAR(30) COMMENT '參考客戶',
    sfaa010 VARCHAR(20) NOT NULL COMMENT '生產料號',
    sfaa012 INT NOT NULL COMMENT '生產數量',
    sfaa019 DATE COMMENT '預計開工日',
    sfaa020 DATE COMMENT '預計完工日',
    sfaa021 VARCHAR(30) COMMENT '母工單單號',
    sfaa034 VARCHAR(10) COMMENT '預計入庫庫位',
    sfaa035 VARCHAR(10) COMMENT '預計入庫儲位',
    sfaa039 CHAR(1) DEFAULT 'N' COMMENT '備料已產生',
    sfaa040 CHAR(1) DEFAULT 'N' COMMENT '生產途程已確認',
    sfaa041 CHAR(1) DEFAULT 'N' COMMENT '凍結',
    sfaa042 CHAR(1) DEFAULT 'N' COMMENT '重工',
    sfaa043 CHAR(1) DEFAULT 'N' COMMENT '備置',
    sfaa045 DATE COMMENT '實際開始發料日',
    sfaa046 DATE COMMENT '最後入庫日',
    sfaa047 DATE COMMENT '生管結案日',
    sfaa048 DATE COMMENT '成本結案日',
    sfaa049 INT DEFAULT 0 COMMENT '已發料套數',
    sfaa057 CHAR(1) COMMENT '委外類型',
    sfaa058 INT COMMENT '參考數量',
    sfaa062 CHAR(1) DEFAULT 'Y' COMMENT '納入AMRP計算',
    sfaa065 CHAR(1) COMMENT '生管結案狀態',
    sfaa068 VARCHAR(10) COMMENT '成本中心',
    sfaa070 DATE COMMENT '原始預計完工日期',
    sfaa074 DATE COMMENT 'AMRP執行時間',
    sfaa075 CHAR(1) DEFAULT 'Y' COMMENT '與日計劃沖銷否',
    sfaa076 VARCHAR(10) COMMENT '產線',
    sfaa077 VARCHAR(10) COMMENT '班別',
    sfaa078 CHAR(1) DEFAULT 'N' COMMENT '過期工單納入日計劃計算否',
    imaa126 VARCHAR(10) COMMENT '品牌客戶',

    -- PLM欄位
    bd_010 VARCHAR(50) COMMENT '機種',
    bd_011 VARCHAR(50) COMMENT '型號規格',
    bd_012 VARCHAR(50) COMMENT '功能',
    bd_013 VARCHAR(50) COMMENT '能力',
    bd_014 VARCHAR(50) COMMENT '電機規格',
    bd_015 VARCHAR(50) COMMENT '電源種類',
    bd_016 VARCHAR(50) COMMENT '冷媒種類',
    bd_017 VARCHAR(50) COMMENT '客戶',
    plm_state VARCHAR(50) COMMENT '狀態',
    plm_unit VARCHAR(10) COMMENT '單位',
    item_number VARCHAR(50) COMMENT '品號',
    fw_mb VARCHAR(50) COMMENT '韌體廠商',
    bd_imaa003 VARCHAR(50) COMMENT '主分群碼',
    bd_imaa009 VARCHAR(50) COMMENT '產品分群',
    bd_imaa010 VARCHAR(50) COMMENT '生命週期',
    classification VARCHAR(50) COMMENT '商品分類',
    is_current CHAR(1) DEFAULT 'N' COMMENT '是否當前',
    make_buy CHAR(1) COMMENT '製造或採購件',
        -- 機板及韌體資訊
    pcb_and_firmware JSON COMMENT '機板及韌體資訊（JSON格式）',
#     [
#     {
#         "pcb_version": "V1.0",
#         "firmwares": [
#             {"version": "00XA", "description": "主韌體"},
#             {"version": "00XB", "description": "測試韌體"}
#         ]
#     },
#     {
#         "pcb_version": "V2.0",
#         "firmwares": [
#             {"version": "00XC", "description": "升級韌體"}
#         ]
#     }
# ]

    -- MES特定欄位
    production_year INT COMMENT '生產年份',
    production_month INT COMMENT '生產月份',
    production_line VARCHAR(10) COMMENT '生產線別',
    production_model VARCHAR(50) COMMENT '生產機型',
    production_qty INT DEFAULT 0 COMMENT '生產數量',
    production_type INT DEFAULT 1 COMMENT '生產種類',
    encoding_rule JSON COMMENT '編碼規則',


    -- 列印相關資訊
    print_info_list JSON COMMENT '列印信息（標籤和值的列表）',
#     [
#     {"label": "機體", "value": ""},
#     {"label": "保證書", "value": ""},
#     {"label": "外箱", "value": ""},
#     {"label": "電控盒", "value": ""},
#     {"label": "QC測試", "value": ""}
# ]

    -- 系統信息
    create_user VARCHAR(30) COMMENT '建立者',
    update_user VARCHAR(30) COMMENT '更新者',
    delete_user VARCHAR(30) COMMENT '刪除者',
    create_datetime DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '建立時間',
    update_datetime DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新時間',
    delete_datetime DATETIME COMMENT '刪除時間',
    is_delete TINYINT(1) DEFAULT 0 COMMENT '是否刪除標記',

    UNIQUE (sfaaent, sfaasite, sfaadocno) -- 確保企業、據點和單號的唯一性
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='MES工單檔';














-- 編碼規則檔
CREATE TABLE IF NOT EXISTS  mes_mam_sn_rules (
    id INT PRIMARY KEY AUTO_INCREMENT NOT NULL COMMENT '主键，自增',
    customer_code VARCHAR(30) NOT NULL UNIQUE COMMENT '客戶名稱，不可重複',
    encoding_rule VARCHAR(255) COMMENT '編碼規則，例如：f{"型號"}{"*******"}{年份}',
    encoding_rules_json JSON COMMENT '存儲編碼規則的JSON結構，可包含多個品號和共用模版',
    last_serial_number VARCHAR(255) COMMENT '用於追蹤客戶編碼最後一次使用的流水號',
    is_customer_provided TINYINT(1) DEFAULT 0 COMMENT '是否是客戶提供的編碼，預設 0',
    remarks TEXT COMMENT '備註',
    create_user VARCHAR(30) COMMENT '建立者',
    update_user VARCHAR(30) COMMENT '更新者',
    delete_user VARCHAR(30) COMMENT '刪除者',
    create_datetime DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '建立時間',
    update_datetime DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新時間',
    delete_datetime DATETIME DEFAULT NULL COMMENT '刪除時間',
    is_delete TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否刪除標記',
    INDEX idx_cust_name (customer_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='編碼規則檔';




-- 生產線別檔
CREATE TABLE IF NOT EXISTS mes_base_prod_line (
    id INT PRIMARY KEY AUTO_INCREMENT NOT NULL COMMENT '主键，自增',
    psqient INT(5) NOT NULL COMMENT '企業編號',
    psqi001 VARCHAR(10) NOT NULL COMMENT '產線編號',
    psqi002 VARCHAR(80) COMMENT '產線說明',
    psqisite VARCHAR(10) COMMENT '營運據點',
    psqiownid VARCHAR(20) COMMENT '資料所有者',
    psqiowndp VARCHAR(10) COMMENT '資料所屬部門',
    psqicrtid VARCHAR(20) COMMENT '資料建立者',
    psqicrtdp VARCHAR(10) COMMENT '資料建立部門',
    psqicrtdt TIMESTAMP COMMENT '資料創建日',
    psqimodid VARCHAR(20) COMMENT '資料修改者',
    psqimoddt TIMESTAMP COMMENT '最近修改日',
    psqistus VARCHAR(10) COMMENT '狀態碼',
    remarks TEXT COMMENT '備註',
    create_user VARCHAR(30) COMMENT '建立者',
    update_user VARCHAR(30) COMMENT '更新者',
    delete_user VARCHAR(30) COMMENT '刪除者',
    create_datetime DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '建立時間',
    update_datetime DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新時間',
    delete_datetime DATETIME DEFAULT NULL COMMENT '刪除時間',
    is_delete TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否刪除標記',
    UNIQUE KEY `_psqient_psqisite_psqi001_uc` (psqient, psqisite, psqi001)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='生產線別';




-- T100同步紀錄檔
CREATE TABLE IF NOT EXISTS mes_base_sync_status (
    id INT PRIMARY KEY AUTO_INCREMENT,
    code_name VARCHAR(50) NOT NULL,
    table_name VARCHAR(50) NOT NULL UNIQUE,
    last_sync TIMESTAMP,
    status VARCHAR(20),
    ent VARCHAR(20),
    create_user VARCHAR(30) COMMENT '建立者',
    update_user VARCHAR(30) COMMENT '更新者',
    delete_user VARCHAR(30) COMMENT '刪除者',
    create_datetime DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '建立時間',
    update_datetime DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新時間',
    delete_datetime DATETIME DEFAULT NULL COMMENT '刪除時間',
    is_delete TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否刪除標記'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='T100同步紀錄檔';

















-- 列印規則表
CREATE TABLE IF NOT EXISTS  mes_mam_print_rules (
    id INT PRIMARY KEY AUTO_INCREMENT NOT NULL COMMENT '主鍵，自增',
    customer_code VARCHAR(50) NOT NULL UNIQUE COMMENT '客戶，不可重複',
    print_description VARCHAR(255) NOT NULL UNIQUE COMMENT '列印描述檔，不可重複',
    remarks TEXT COMMENT '備註',
    create_user VARCHAR(30) COMMENT '建立者',
    update_user VARCHAR(30) COMMENT '更新者',
    delete_user VARCHAR(30) COMMENT '刪除者',
    create_datetime DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '建立時間',
    update_datetime DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新時間',
    delete_datetime DATETIME DEFAULT NULL COMMENT '刪除時間',
    is_deleted TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否刪除標記，0: 未刪除, 1: 已刪除',
    INDEX idx_product_type (customer_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='列印規則檔';
-- 印表機管理
CREATE TABLE IF NOT EXISTS  mes_mam_printer (
    id INT PRIMARY KEY AUTO_INCREMENT NOT NULL COMMENT '主鍵，自增',
    print_name VARCHAR(50) NOT NULL,             -- 印表機名稱
    print_ip VARCHAR(15) NOT NULL,               -- 印表機名稱
    print_line VARCHAR(50) NOT NULL,             -- 列印線別: P001-P007,PH001(生管列印)
    print_position VARCHAR(50) NOT NULL,         -- 可列印種類: 1, 2 ,3
    print_remarks TEXT COMMENT '備註',
    create_user VARCHAR(30) COMMENT '建立者',
    update_user VARCHAR(30) COMMENT '更新者',
    delete_user VARCHAR(30) COMMENT '刪除者',
    create_datetime DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '建立時間',
    update_datetime DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新時間',
    delete_datetime DATETIME DEFAULT NULL COMMENT '刪除時間',
    is_deleted TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否刪除標記，0: 未刪除, 1: 已刪除',
    UNIQUE (print_ip) -- 添加唯一索引以确保 print_ip 列不重复
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='印表機設定檔';
-- 生產線別組管理
CREATE TABLE IF NOT EXISTS  mes_mam_prod_line (
    id INT PRIMARY KEY AUTO_INCREMENT NOT NULL COMMENT '主鍵，自增',
    line_name VARCHAR(50) NOT NULL,              -- 線別名稱
    line_remark TEXT COMMENT '備註',
    create_user VARCHAR(30) COMMENT '建立者',
    update_user VARCHAR(30) COMMENT '更新者',
    delete_user VARCHAR(30) COMMENT '刪除者',
    create_datetime DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '建立時間',
    update_datetime DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新時間',
    delete_datetime DATETIME DEFAULT NULL COMMENT '刪除時間',
    is_deleted TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否刪除標記，0: 未刪除, 1: 已刪除',
    UNIQUE (line_name) -- 添加唯一索引以确保 print_ip 列不重复
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='印表機設定檔';
-- 排班計畫管理
-- QC測試管理
-- 自檢站測試
-- 報工管理
-- 商品機號管理



-- 訂單管理
CREATE TABLE IF NOT EXISTS  mes_aps_order (
    id INT PRIMARY KEY AUTO_INCREMENT NOT NULL COMMENT '主键，自增',
    xmdaent INT NOT NULL,                   -- 企業編號
    xmdasite VARCHAR(10) NOT NULL,          -- 據點
    xmdadocno VARCHAR(20) NOT NULL,         -- 單號
    xmdadocdt DATE NOT NULL,                -- 單據日期
    xmdastus CHAR(1) NOT NULL,              -- 單據狀態
    xmdcua001 CHAR(1) NOT NULL,             -- MES拋轉碼 (MES Status) Y=生產中 N 未生產 V已結案
    xmda001 INT,                            -- 訂單版本
    xmda004 VARCHAR(50),                    -- 客戶
    xmdcseq INT,                            -- 訂單項次
    xmdc001 VARCHAR(100),                   -- 產品
    xmdc007 INT,                            -- 數量
    xmdc012 DATE,                           -- 需求日期
    xmdc045 CHAR(1),                        -- 狀態碼
    xmdc050 TEXT,                           -- 狀態碼
    create_user VARCHAR(30) COMMENT '建立者',
    update_user VARCHAR(30) COMMENT '更新者',
    delete_user VARCHAR(30) COMMENT '刪除者',
    create_datetime DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '建立時間',
    update_datetime DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新時間',
    delete_datetime DATETIME DEFAULT NULL COMMENT '刪除時間',
    is_delete TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否刪除標記',
    UNIQUE (xmdaent, xmdasite, xmdadocno)   -- 确保ENT、SITE和單號的组合唯一
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='訂單';

-- 獨立需求
CREATE TABLE IF NOT EXISTS  mes_aps_ir (
    id INT PRIMARY KEY AUTO_INCREMENT NOT NULL COMMENT '主键，自增',

    psabent INT NOT NULL,                   -- 企業編號
    psabsite VARCHAR(10) NOT NULL,          -- 據點
    psaadocno VARCHAR(20) NOT NULL,         -- 單號
    psaadocdt DATE NOT NULL,                -- 單據日期
    psaastus CHAR(1) NOT NULL,              -- 單據狀態

    psabua001 CHAR(1) NOT NULL,             -- MES拋轉碼 (MES Status) Y=生產中 N 未生產 V已結案

    psabseq INT,                            -- 訂單項次
    psab001 VARCHAR(50),                    -- 料件編號
    psab003 VARCHAR(50),                    -- 需求日期
    psab004 VARCHAR(50),                    -- 單位
    psab005 INT,                            -- 需求數量
    psab006 INT,                            -- 已耗需求
    psab008 CHAR(1) NOT NULL,               -- 單身結案碼

    remarks TEXT COMMENT '備註',

    create_user VARCHAR(30) COMMENT '建立者',
    update_user VARCHAR(30) COMMENT '更新者',
    delete_user VARCHAR(30) COMMENT '刪除者',
    create_datetime DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '建立時間',
    update_datetime DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新時間',
    delete_datetime DATETIME DEFAULT NULL COMMENT '刪除時間',
    is_delete TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否刪除標記',
    UNIQUE (psabent, psabsite, psaadocno)   -- 确保ENT、SITE和單號的组合唯一
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='獨立需求';

























-- 生產機號表
CREATE TABLE IF NOT EXISTS sn_d (
    uuid CHAR(36) PRIMARY KEY NOT NULL,     -- UUID
    mo_uuid CHAR(36),                       -- 外建，關聯到mo表的uuid
    sn VARCHAR(30) NOT NULL,                -- 機號
    production_status CHAR(1) DEFAULT 'N',  -- 生產狀態: Y=已完成 N=未完成
    status INT DEFAULT 0,                   -- 目前狀態: 0.正常 1.改機 2.整新 3.重工 4.拆機
    life_cycle INT DEFAULT 0,               -- 生命週期: 0 產線生產中 1產線暫存倉 2總倉倉庫 3分公司倉庫 5已出貨
    location VARCHAR(30),                   -- 目前位置
    old_sn VARCHAR(15),                     -- 舊機號
    production_start_time DATETIME DEFAULT CURRENT_TIMESTAMP,          -- 生產開始時間
    production_end_time DATETIME,            -- 生產完成時間
    print_rework_type VARCHAR(15) DEFAULT 'N',  -- 列印重工類型
    body_print_count INT DEFAULT 0,          -- 機體列印次數
    body_print_time DATETIME,                -- 機體列印時間
    external_print_count INT DEFAULT 0,      -- 外箱列印次數
    external_print_time DATETIME,            -- 外箱列印時間
    warranty_certificate_count INT DEFAULT 0, -- 保證書列印次數
    warranty_certificate_time DATETIME,       -- 保證書列印時間
    control_union_count INT DEFAULT 0,       -- 電控合列印次數
    control_union_time DATETIME,             -- 電控合列印時間
    created_user VARCHAR(30),                -- 創建者 (Created At)
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,                             -- 建立時間 (Created At)
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, -- 更新時間 (Updated At)
    CHECK (created_user IS NOT NULL AND created_user != ''),
    CHECK (sn IS NOT NULL AND sn != ''),
    FOREIGN KEY (mo_uuid) REFERENCES mes_mam_mo(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
-- 打印機設定表
CREATE TABLE IF NOT EXISTS printers_t (
    uuid CHAR(36) PRIMARY KEY NOT NULL,          -- UUID
    ip VARCHAR(50) NOT NULL,                     -- 印表機IP
    name VARCHAR(50) NOT NULL,                   -- 印表機名稱
    statuses BOOLEAN DEFAULT FALSE NOT NULL,     -- 啟用狀態: Y=啟用 N=不啟用
    sort INT DEFAULT 0 NOT NULL,                 -- 抓取列印順序
    print_line_type VARCHAR(50) NOT NULL,        -- 列印線別: P001-P007,PH001(生管列印)
    print_type VARCHAR(50) NOT NULL,             -- 列印種類: 機體, 保證書 , 外箱
    created_user VARCHAR(30) NOT NULL,           -- 創建者
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP, -- 建立時間
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP -- 更新時間
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
-- 商品列印編碼原則表格
CREATE TABLE IF NOT EXISTS product_code_policy_t (
    uuid CHAR(36) PRIMARY KEY NOT NULL,     -- UUID，例如 "550e8400-e29b-41d4-a716-446655440000"
    customer VARCHAR(50) NOT NULL,          -- 客戶代碼，例如 "A0001Y"
    product VARCHAR(50),                    -- 商品編碼，可以為空白
    product_rules_name VARCHAR(50),         -- 商品取號，可以為空白
    policy_name TEXT,                       -- 原則名稱，例如 "日期+分類+序號"
    description TEXT NOT NULL,              -- 原則描述
    product_priority BOOLEAN DEFAULT FALSE, -- 優先取商品規則的標誌，默認為假
    created_user VARCHAR(30) NOT NULL,      -- 創建者
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP, -- 建立時間
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, -- 更新時間
    UNIQUE (uuid),                        -- 確保UUID的唯一性
    UNIQUE (customer, product)            -- 確保客戶代碼和商品編碼的組合唯一
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
-- 商品取號編碼原則表格
CREATE TABLE product_numbering_rules_t (
    uuid CHAR(36) PRIMARY KEY NOT NULL COMMENT 'UUID，例如 "550e8400-e29b-41d4-a716-446655440000"',
    name NVARCHAR(255) UNIQUE COMMENT '編碼名稱',
    serial_number_length INT DEFAULT 25 COMMENT 'SN最多位數，預設 25', -- 限制 10-25
    CHECK (serial_number_length BETWEEN 10 AND 25), -- 添加 CHECK 約束

    serial_number_fun TEXT COMMENT '外掛取號計算函式，例如：DATE_FORMAT(NOW(), "%Y%m%d")',
    is_customer_provided BOOLEAN DEFAULT FALSE COMMENT '是否是客戶提供的編碼規則，預設 False',
    serial_number_site INT DEFAULT 2 COMMENT '流水號位置',-- 限制 1 2 3
    CHECK (serial_number_site IN (1, 2, 3)), -- 添加 CHECK 約束

    prefix NVARCHAR(255) COMMENT '前綴',
    serial_number NVARCHAR(255) COMMENT '流水號', -- 可能會在前面 可能會在後面 可能會在中間
    suffix NVARCHAR(255) COMMENT '後綴',

    sn_template NVARCHAR(255) COMMENT '編碼模版，例如：[PREFIX]-[SERIAL_NUMBER]-[SUFFIX]',
    last_serial_number NVARCHAR(255) COMMENT '最後一碼，用於追蹤客戶編碼最後一次使用的流水號',
    remark TEXT COMMENT '備註',

    created_user VARCHAR(30) COMMENT '創建者',
    updated_user VARCHAR(30) COMMENT '更新者',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '建立時間',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新時間'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
-- 商品機號表 //還沒好
CREATE TABLE IF NOT EXISTS product_t (
    uuid CHAR(36) NOT NULL,                        -- 產品 UUID
    mo_uuid CHAR(36) NOT NULL,                     -- 關聯到工單的 UUID
    sn VARCHAR(50) PRIMARY KEY NOT NULL,           -- 產品序號
    status INT DEFAULT 0,                          -- 產品狀態: 0=正常 1=異常
    created_user VARCHAR(30),                      -- 創建者
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP, -- 建立時間
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP-- 更新時間
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;