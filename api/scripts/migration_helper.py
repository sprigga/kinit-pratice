#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Alembic 遷移問題處理主指令
整合診斷、修復和驗證功能的一站式解決方案
針對 bpmin_it 表創建問題的增強版本
"""

import asyncio
import sys
import argparse
from pathlib import Path
import subprocess
import os

# 添加專案路徑到 Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.migration_diagnostic import MigrationDiagnostic
from scripts.migration_fix import MigrationFix
from scripts.migration_verify import MigrationVerifier
from core.database import db_getter
from sqlalchemy import text


class MigrationHelper:
    def __init__(self):
        self.diagnostic = MigrationDiagnostic()
        self.fixer = MigrationFix()
        self.verifier = MigrationVerifier()

    def show_welcome(self):
        """顯示歡迎訊息"""
        welcome_text = """
🛠️  Alembic 遷移問題處理工具 v2.0 (增強版)
========================================

這個工具可以幫助您：
✅ 診斷遷移問題
🔧 自動修復常見問題  
✅ 驗證修復結果
🆕 處理版本不同步問題
🆕 檢查表創建狀態
🆕 強制同步 Alembic 版本

基於 SOP 文檔開發，特別針對 bpmin_it 表創建問題優化。
        """
        print(welcome_text)

    def show_quick_commands(self):
        """顯示快速指令參考"""
        commands = """
🚀 快速指令參考：

=== 基本診斷 ===
1. 檢查遷移狀態：
   python scripts/migration_helper.py check-migration-status

2. 檢查特定表是否存在：
   python scripts/migration_helper.py check-table --table bpmin_it

3. 診斷版本不同步問題：
   python scripts/migration_helper.py diagnose-version-sync

=== 修復操作 ===
4. 同步 Alembic 版本到最新：
   python scripts/migration_helper.py sync-version

5. 強制重新創建遷移：
   python scripts/migration_helper.py force-migrate --table bpmin_it

6. 手動創建表（當遷移失敗時）：
   python scripts/migration_helper.py create-table --table bpmin_it

=== 完整工作流 ===
7. 一鍵解決表創建問題：
   python scripts/migration_helper.py fix-table-creation --table bpmin_it

8. 完整的遷移健康檢查：
   python scripts/migration_helper.py health-check

=== 傳統功能 ===
9. 修復 dialogue 欄位：
   python scripts/migration_helper.py fix-dialogue

10. 互動式模式：
    python scripts/migration_helper.py interactive
        """
        print(commands)

    async def check_migration_status(self):
        """檢查遷移狀態"""
        print("🔍 檢查 Alembic 遷移狀態...")
        print("=" * 60)
        
        try:
            # 檢查資料庫中的版本
            async for db in db_getter():
                result = await db.execute(text("SELECT version_num FROM alembic_version"))
                db_version = result.fetchone()
                db_version = db_version[0] if db_version else "None"
                print(f"📊 資料庫版本: {db_version}")
                break
                
            # 檢查文件系統中的最新版本
            versions_dir = project_root / "alembic" / "versions_dev"
            if versions_dir.exists():
                version_files = list(versions_dir.glob("*.py"))
                if version_files:
                    latest_file = max(version_files, key=lambda f: f.stat().st_mtime)
                    latest_version = latest_file.stem.split('_')[0]
                    print(f"📁 最新遷移文件: {latest_version} ({latest_file.name})")
                    
                    # 比較版本
                    if db_version != latest_version:
                        print("⚠️  版本不同步！")
                        print(f"   資料庫版本: {db_version}")
                        print(f"   文件版本:   {latest_version}")
                        return False
                    else:
                        print("✅ 版本同步正常")
                        return True
            
            # 使用 alembic current 命令檢查
            try:
                result = subprocess.run(
                    ["alembic", "--name", "dev", "current"],
                    capture_output=True,
                    text=True,
                    cwd=project_root
                )
                if result.returncode == 0:
                    print(f"🔄 Alembic current: {result.stdout.strip()}")
                else:
                    print(f"❌ Alembic current 命令失敗: {result.stderr}")
            except Exception as e:
                print(f"❌ 無法執行 alembic current: {e}")
                
        except Exception as e:
            print(f"❌ 檢查遷移狀態時發生錯誤: {e}")
            return False

    async def check_table_exists(self, table_name):
        """檢查指定表是否存在"""
        print(f"🔍 檢查表 '{table_name}' 是否存在...")
        print("=" * 60)
        
        try:
            async for db in db_getter():
                # 檢查原名
                result = await db.execute(text(f"SHOW TABLES LIKE '{table_name}'"))
                exists = result.fetchone() is not None
                
                if not exists:
                    # 嘗試大小寫變體
                    variants = [table_name.lower(), table_name.upper(), table_name.capitalize()]
                    for variant in variants:
                        if variant != table_name:
                            result = await db.execute(text(f"SHOW TABLES LIKE '{variant}'"))
                            if result.fetchone() is not None:
                                print(f"✅ 找到表: {variant} (不同大小寫)")
                                return True, variant
                
                if exists:
                    print(f"✅ 表 '{table_name}' 存在")
                    return True, table_name
                else:
                    print(f"❌ 表 '{table_name}' 不存在")
                    
                    # 顯示所有表
                    result = await db.execute(text("SHOW TABLES"))
                    tables = [row[0] for row in result.fetchall()]
                    print(f"\n📋 資料庫中現有的表 ({len(tables)} 個):")
                    for i, table in enumerate(sorted(tables), 1):
                        print(f"  {i:2d}. {table}")
                    
                    return False, None
                break
        except Exception as e:
            print(f"❌ 檢查表時發生錯誤: {e}")
            return False, None

    async def sync_alembic_version(self):
        """同步 Alembic 版本到最新"""
        print("🔄 同步 Alembic 版本到最新...")
        print("=" * 60)
        
        try:
            # 獲取最新版本
            versions_dir = project_root / "alembic" / "versions_dev"
            if not versions_dir.exists():
                print("❌ 找不到遷移文件目錄")
                return False
                
            version_files = list(versions_dir.glob("*.py"))
            if not version_files:
                print("❌ 沒有找到遷移文件")
                return False
                
            latest_file = max(version_files, key=lambda f: f.stat().st_mtime)
            latest_version = latest_file.stem.split('_')[0]
            
            print(f"📁 最新版本: {latest_version}")
            
            # 使用 alembic stamp 命令
            result = subprocess.run(
                ["alembic", "--name", "dev", "stamp", latest_version],
                capture_output=True,
                text=True,
                cwd=project_root
            )
            
            if result.returncode == 0:
                print("✅ Alembic 版本同步成功")
                return True
            else:
                print(f"❌ 同步失敗: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ 同步版本時發生錯誤: {e}")
            return False

    async def force_migrate(self, table_name=None):
        """強制重新執行遷移"""
        print("🚀 強制重新執行遷移...")
        print("=" * 60)
        
        try:
            # 先同步版本
            print("步驟 1: 同步版本")
            await self.sync_alembic_version()
            
            # 執行遷移
            print("\n步驟 2: 執行遷移")
            result = subprocess.run(
                ["python", "main.py", "migrate", "--env", "dev"],
                capture_output=True,
                text=True,
                cwd=project_root
            )
            
            if result.returncode == 0:
                print("✅ 遷移執行成功")
                print(result.stdout)
                
                # 如果指定了表名，檢查表是否創建成功
                if table_name:
                    print(f"\n步驟 3: 檢查表 '{table_name}' 是否創建成功")
                    exists, actual_name = await self.check_table_exists(table_name)
                    if exists:
                        print(f"✅ 表創建成功: {actual_name}")
                    else:
                        print(f"❌ 表創建失敗: {table_name}")
                        return False
                
                return True
            else:
                print(f"❌ 遷移執行失敗: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ 強制遷移時發生錯誤: {e}")
            return False

    async def create_table_manually(self, table_name):
        """手動創建表（當遷移失敗時的備用方案）"""
        print(f"🔧 手動創建表 '{table_name}'...")
        print("=" * 60)
        
        # 預定義的表結構
        table_schemas = {
            "bpmin_it": """
                CREATE TABLE {table_name} (
                    id INTEGER NOT NULL AUTO_INCREMENT COMMENT '主鍵ID',
                    it_manager VARCHAR(100) COMMENT 'IT經理',
                    dept VARCHAR(50) COMMENT '部門',
                    apply_date VARCHAR(20) COMMENT '申請日期',
                    extension VARCHAR(20) COMMENT '分機號碼',
                    fillman VARCHAR(100) COMMENT '填表人',
                    apply_item VARCHAR(200) COMMENT '申請項目',
                    request_desc VARCHAR(500) COMMENT '需求描述',
                    it_undertaker VARCHAR(100) COMMENT 'IT承辦人',
                    treatment VARCHAR(500) COMMENT '處理方式',
                    create_user VARCHAR(30) COMMENT '建立者工號',
                    update_user VARCHAR(30) COMMENT '更新者',
                    delete_user VARCHAR(30) COMMENT '刪除者',
                    create_datetime DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL COMMENT '創建時間',
                    update_datetime DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL COMMENT '更新時間',
                    delete_datetime DATETIME COMMENT '刪除時間',
                    is_delete BOOLEAN DEFAULT FALSE NOT NULL COMMENT '是否軟刪除',
                    PRIMARY KEY (id)
                ) COMMENT='IT service request form';
            """,
            "Bpmin_it": """
                CREATE TABLE {table_name} (
                    id INTEGER NOT NULL AUTO_INCREMENT COMMENT '主鍵ID',
                    it_manager VARCHAR(100) COMMENT 'IT經理',
                    dept VARCHAR(50) COMMENT '部門',
                    apply_date VARCHAR(20) COMMENT '申請日期',
                    extension VARCHAR(20) COMMENT '分機號碼',
                    fillman VARCHAR(100) COMMENT '填表人',
                    apply_item VARCHAR(200) COMMENT '申請項目',
                    request_desc VARCHAR(500) COMMENT '需求描述',
                    it_undertaker VARCHAR(100) COMMENT 'IT承辦人',
                    treatment VARCHAR(500) COMMENT '處理方式',
                    create_user VARCHAR(30) COMMENT '建立者工號',
                    update_user VARCHAR(30) COMMENT '更新者',
                    delete_user VARCHAR(30) COMMENT '刪除者',
                    create_datetime DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL COMMENT '創建時間',
                    update_datetime DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL COMMENT '更新時間',
                    delete_datetime DATETIME COMMENT '刪除時間',
                    is_delete BOOLEAN DEFAULT FALSE NOT NULL COMMENT '是否軟刪除',
                    PRIMARY KEY (id)
                ) COMMENT='IT service request form';
            """
        }
        
        # 嘗試不同的表名變體
        table_variants = [table_name, table_name.lower(), table_name.upper(), table_name.capitalize()]
        
        for variant in table_variants:
            if variant in table_schemas:
                try:
                    sql = table_schemas[variant].format(table_name=variant)
                    
                    async for db in db_getter():
                        await db.execute(text(sql))
                        await db.commit()
                        print(f"✅ 表 '{variant}' 創建成功")
                        
                        # 驗證創建結果
                        exists, _ = await self.check_table_exists(variant)
                        if exists:
                            print(f"✅ 驗證通過: 表 '{variant}' 已存在")
                            return True
                        break
                        
                except Exception as e:
                    print(f"❌ 創建表 '{variant}' 失敗: {e}")
                    continue
        
        print(f"❌ 無法創建表 '{table_name}' (嘗試了所有變體)")
        return False

    async def fix_table_creation_workflow(self, table_name):
        """一鍵解決表創建問題的完整工作流"""
        print(f"🎯 開始表創建問題修復工作流: {table_name}")
        print("=" * 80)
        
        # 步驟 1: 檢查表是否已存在
        print("步驟 1/5: 檢查表是否已存在")
        exists, actual_name = await self.check_table_exists(table_name)
        if exists:
            print(f"✅ 表已存在: {actual_name}，無需修復")
            return True
        
        # 步驟 2: 檢查遷移狀態
        print("\n步驟 2/5: 檢查遷移狀態")
        migration_ok = await self.check_migration_status()
        
        # 步驟 3: 修復遷移狀態（如果需要）
        if not migration_ok:
            print("\n步驟 3/5: 修復遷移狀態")
            sync_ok = await self.sync_alembic_version()
            if not sync_ok:
                print("❌ 無法修復遷移狀態")
                return False
        else:
            print("\n步驟 3/5: 遷移狀態正常，跳過修復")
        
        # 步驟 4: 嘗試重新執行遷移
        print("\n步驟 4/5: 嘗試重新執行遷移")
        migrate_ok = await self.force_migrate(table_name)
        
        if migrate_ok:
            print("✅ 遷移執行成功，表創建完成")
            return True
        
        # 步驟 5: 備用方案 - 手動創建表
        print("\n步驟 5/5: 備用方案 - 手動創建表")
        manual_ok = await self.create_table_manually(table_name)
        
        if manual_ok:
            print("✅ 手動創建表成功")
            # 同步 Alembic 版本以避免下次遷移衝突
            await self.sync_alembic_version()
            return True
        else:
            print("❌ 所有修復方案都失敗了")
            return False

    async def health_check(self):
        """完整的遷移健康檢查"""
        print("🏥 開始遷移健康檢查...")
        print("=" * 80)
        
        issues = []
        
        # 檢查 1: 資料庫連接
        print("檢查 1/5: 資料庫連接")
        try:
            async for db in db_getter():
                await db.execute(text("SELECT 1"))
                print("✅ 資料庫連接正常")
                break
        except Exception as e:
            issues.append(f"資料庫連接失敗: {e}")
            print(f"❌ 資料庫連接失敗: {e}")
        
        # 檢查 2: Alembic 版本
        print("\n檢查 2/5: Alembic 版本同步")
        migration_ok = await self.check_migration_status()
        if not migration_ok:
            issues.append("Alembic 版本不同步")
        
        # 檢查 3: 重要表存在性
        print("\n檢查 3/5: 重要表存在性")
        important_tables = ["bpmin_it", "Bpmin_it", "vadmin_test", "vadmin_auth_user"]
        for table in important_tables:
            exists, actual_name = await self.check_table_exists(table)
            if not exists:
                issues.append(f"表 '{table}' 不存在")
        
        # 檢查 4: 遷移文件完整性
        print("\n檢查 4/5: 遷移文件完整性")
        versions_dir = project_root / "alembic" / "versions_dev"
        if not versions_dir.exists():
            issues.append("遷移文件目錄不存在")
        else:
            migration_files = list(versions_dir.glob("*.py"))
            print(f"📁 找到 {len(migration_files)} 個遷移文件")
        
        # 檢查 5: Alembic 配置
        print("\n檢查 5/5: Alembic 配置")
        alembic_ini = project_root / "alembic.ini"
        if not alembic_ini.exists():
            issues.append("alembic.ini 配置文件不存在")
        else:
            print("✅ alembic.ini 配置文件存在")
        
        # 生成報告
        print("\n" + "=" * 80)
        print("🎯 健康檢查報告")
        print("=" * 80)
        
        if not issues:
            print("✅ 所有檢查都通過！遷移系統健康。")
        else:
            print(f"❌ 發現 {len(issues)} 個問題:")
            for i, issue in enumerate(issues, 1):
                print(f"  {i}. {issue}")
            
            print("\n🔧 建議的修復步驟:")
            print("1. 執行: python scripts/migration_helper.py sync-version")
            print("2. 執行: python scripts/migration_helper.py force-migrate")
            print("3. 如果仍有問題，執行: python scripts/migration_helper.py fix-table-creation --table <table_name>")
        
        return len(issues) == 0

    # 保留原有的方法...
    async def auto_fix_workflow(self, table_name, column_name, column_type="VARCHAR(500)", comment=None):
        """自動化修復工作流：診斷 → 修復 → 驗證"""
        print("🤖 開始自動化修復工作流...")
        print("=" * 60)
        
        # 步驟 1: 診斷
        print("📋 步驟 1/3: 診斷問題")
        print("-" * 30)
        await self.diagnostic.run_full_diagnostic(table_name, column_name)
        
        if not self.diagnostic.issues:
            print("✅ 沒有發現問題，無需修復")
            return True
            
        # 步驟 2: 修復
        print(f"\n🔧 步驟 2/3: 修復問題 ({len(self.diagnostic.issues)} 個)")
        print("-" * 30)
        
        # 根據診斷結果決定修復策略
        needs_column_fix = any("缺少欄位" in issue for issue in self.diagnostic.issues)
        needs_version_sync = any("alembic_version" in issue for issue in self.diagnostic.issues)
        
        success = True
        if needs_column_fix:
            success = await self.fixer.fix_missing_column(
                table_name=table_name,
                column_name=column_name,
                column_type=column_type,
                comment=comment,
                sync_version=needs_version_sync
            )
        elif needs_version_sync:
            latest_version = self.fixer.get_latest_migration_version()
            if latest_version:
                success = await self.fixer.sync_alembic_version(latest_version)
        
        if not success:
            print("❌ 修復失敗，停止工作流")
            return False
            
        # 步驟 3: 驗證
        print("\n✅ 步驟 3/3: 驗證修復結果")
        print("-" * 30)
        
        await self.verifier.verify_database_connection()
        await self.verifier.verify_alembic_version()
        await self.verifier.verify_column_exists(table_name, column_name)
        
        # 生成最終報告
        print("\n🎯 自動化修復工作流完成")
        print("=" * 60)
        self.verifier.generate_report()
        
        return self.verifier.failed_tests == 0

    async def dialogue_fix_workflow(self, dry_run=False):
        """專門的 dialogue 欄位修復工作流"""
        print("💬 開始 dialogue 欄位修復工作流...")
        
        if dry_run:
            print("🔍 [乾跑模式] 僅顯示將執行的操作，不實際修改")
            
        return await self.auto_fix_workflow(
            table_name="vadmin_test",
            column_name="dialogue", 
            column_type="VARCHAR(500)",
            comment="對話內容"
        )

    async def interactive_mode(self):
        """互動式模式"""
        print("🎮 進入互動式模式")
        print("=" * 40)
        
        while True:
            print("\n請選擇操作:")
            print("1. 診斷問題")
            print("2. 修復 dialogue 欄位")
            print("3. 新增自定義欄位") 
            print("4. 驗證結果")
            print("5. 檢查遷移狀態")
            print("6. 修復表創建問題")
            print("7. 完整健康檢查")
            print("8. 查看幫助")
            print("0. 退出")
            
            try:
                choice = input("\n請輸入選項 (0-8): ").strip()
                
                if choice == "0":
                    print("👋 再見！")
                    break
                elif choice == "1":
                    table = input("請輸入表名 (預設: vadmin_test): ").strip() or "vadmin_test"
                    column = input("請輸入欄位名 (選填): ").strip() or None
                    await self.diagnostic.run_full_diagnostic(table, column)
                    
                elif choice == "2":
                    confirm = input("確定要修復 dialogue 欄位嗎? (y/N): ").strip().lower()
                    if confirm == 'y':
                        await self.dialogue_fix_workflow()
                    else:
                        print("已取消操作")
                        
                elif choice == "3":
                    table = input("請輸入表名: ").strip()
                    column = input("請輸入欄位名: ").strip() 
                    column_type = input("請輸入欄位類型 (預設: VARCHAR(500)): ").strip() or "VARCHAR(500)"
                    comment = input("請輸入欄位註解 (選填): ").strip() or None
                    
                    if table and column:
                        await self.auto_fix_workflow(table, column, column_type, comment)
                    else:
                        print("❌ 表名和欄位名不能為空")
                        
                elif choice == "4":
                    await self.verifier.verify_database_connection()
                    await self.verifier.run_dialogue_column_verification()
                    
                elif choice == "5":
                    await self.check_migration_status()
                    
                elif choice == "6":
                    table = input("請輸入要修復的表名 (預設: bpmin_it): ").strip() or "bpmin_it"
                    await self.fix_table_creation_workflow(table)
                    
                elif choice == "7":
                    await self.health_check()
                    
                elif choice == "8":
                    self.show_quick_commands()
                    
                else:
                    print("❌ 無效選項，請重新選擇")
                    
            except KeyboardInterrupt:
                print("\n\n👋 再見！")
                break
            except Exception as e:
                print(f"❌ 操作失敗: {e}")

    def show_usage(self):
        """顯示使用說明"""
        usage_text = """
📚 使用說明：

基本用法:
  python scripts/migration_helper.py <command> [options]

=== 新增命令 ===
  check-migration-status    檢查遷移狀態
  check-table              檢查指定表是否存在
  diagnose-version-sync    診斷版本不同步問題
  sync-version             同步 Alembic 版本到最新
  force-migrate            強制重新執行遷移
  create-table             手動創建表
  fix-table-creation       一鍵解決表創建問題
  health-check             完整的遷移健康檢查

=== 傳統命令 ===
  help                     顯示幫助資訊
  diagnose                 診斷遷移問題
  fix-dialogue             修復 dialogue 欄位
  add-column               新增自定義欄位
  auto-fix                 自動化修復工作流
  verify                   驗證修復結果
  interactive              進入互動式模式

常用選項:
  --table, -t              指定資料表名稱
  --column, -c             指定欄位名稱
  --type                   指定欄位類型 (預設: VARCHAR(500))
  --comment                指定欄位註解
  --dry-run                乾跑模式，僅顯示操作不執行

=== 針對 bpmin_it 表問題的範例 ===
  # 檢查 bpmin_it 表是否存在
  python scripts/migration_helper.py check-table -t bpmin_it
  
  # 一鍵修復 bpmin_it 表創建問題
  python scripts/migration_helper.py fix-table-creation -t bpmin_it
  
  # 完整健康檢查
  python scripts/migration_helper.py health-check
  
  # 強制重新遷移
  python scripts/migration_helper.py force-migrate -t bpmin_it

=== 其他範例 ===
  # 診斷版本同步問題
  python scripts/migration_helper.py diagnose-version-sync
  
  # 同步版本到最新
  python scripts/migration_helper.py sync-version
  
  # 手動創建表（備用方案）
  python scripts/migration_helper.py create-table -t bpmin_it
        """
        print(usage_text)


async def main():
    parser = argparse.ArgumentParser(
        description='Alembic 遷移問題處理主工具 v2.0',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # 子命令
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # === 新增的命令 ===
    
    # check-migration-status 命令
    subparsers.add_parser('check-migration-status', help='檢查遷移狀態')
    
    # check-table 命令
    check_table_parser = subparsers.add_parser('check-table', help='檢查指定表是否存在')
    check_table_parser.add_argument('--table', '-t', required=True, help='要檢查的表名')
    
    # diagnose-version-sync 命令
    subparsers.add_parser('diagnose-version-sync', help='診斷版本不同步問題')
    
    # sync-version 命令
    subparsers.add_parser('sync-version', help='同步 Alembic 版本到最新')
    
    # force-migrate 命令
    force_migrate_parser = subparsers.add_parser('force-migrate', help='強制重新執行遷移')
    force_migrate_parser.add_argument('--table', '-t', help='要檢查的表名')
    
    # create-table 命令
    create_table_parser = subparsers.add_parser('create-table', help='手動創建表')
    create_table_parser.add_argument('--table', '-t', required=True, help='要創建的表名')
    
    # fix-table-creation 命令
    fix_table_parser = subparsers.add_parser('fix-table-creation', help='一鍵解決表創建問題')
    fix_table_parser.add_argument('--table', '-t', required=True, help='要修復的表名')
    
    # health-check 命令
    subparsers.add_parser('health-check', help='完整的遷移健康檢查')
    
    # === 原有命令 ===
    
    # help 命令
    help_parser = subparsers.add_parser('help', help='顯示幫助資訊')
    
    # diagnose 命令
    diagnose_parser = subparsers.add_parser('diagnose', help='診斷遷移問題')
    diagnose_parser.add_argument('--table', '-t', help='資料表名稱')
    diagnose_parser.add_argument('--column', '-c', help='欄位名稱')
    
    # fix-dialogue 命令
    dialogue_parser = subparsers.add_parser('fix-dialogue', help='修復 dialogue 欄位')
    dialogue_parser.add_argument('--dry-run', action='store_true', help='乾跑模式')
    
    # add-column 命令
    add_column_parser = subparsers.add_parser('add-column', help='新增欄位')
    add_column_parser.add_argument('--table', '-t', required=True, help='資料表名稱')
    add_column_parser.add_argument('--column', '-c', required=True, help='欄位名稱')
    add_column_parser.add_argument('--type', default='VARCHAR(500)', help='欄位類型')
    add_column_parser.add_argument('--comment', help='欄位註解')
    add_column_parser.add_argument('--dry-run', action='store_true', help='乾跑模式')
    
    # auto-fix 命令
    auto_fix_parser = subparsers.add_parser('auto-fix', help='自動化修復工作流')
    auto_fix_parser.add_argument('--table', '-t', required=True, help='資料表名稱')
    auto_fix_parser.add_argument('--column', '-c', required=True, help='欄位名稱')
    auto_fix_parser.add_argument('--type', default='VARCHAR(500)', help='欄位類型')
    auto_fix_parser.add_argument('--comment', help='欄位註解')
    
    # verify 命令
    verify_parser = subparsers.add_parser('verify', help='驗證修復結果')
    verify_parser.add_argument('--dialogue', action='store_true', help='驗證 dialogue 欄位')
    verify_parser.add_argument('--table', '-t', help='驗證指定表')
    verify_parser.add_argument('--column', '-c', help='驗證指定欄位')
    
    # interactive 命令
    interactive_parser = subparsers.add_parser('interactive', help='互動式模式')
    
    args = parser.parse_args()
    
    helper = MigrationHelper()
    
    # 如果沒有提供命令，顯示歡迎訊息和快速指令
    if not args.command:
        helper.show_welcome()
        helper.show_quick_commands()
        return
    
    try:
        # === 新增命令的處理 ===
        if args.command == 'check-migration-status':
            await helper.check_migration_status()
            
        elif args.command == 'check-table':
            await helper.check_table_exists(args.table)
            
        elif args.command == 'diagnose-version-sync':
            await helper.check_migration_status()
            
        elif args.command == 'sync-version':
            await helper.sync_alembic_version()
            
        elif args.command == 'force-migrate':
            await helper.force_migrate(args.table)
            
        elif args.command == 'create-table':
            await helper.create_table_manually(args.table)
            
        elif args.command == 'fix-table-creation':
            await helper.fix_table_creation_workflow(args.table)
            
        elif args.command == 'health-check':
            await helper.health_check()
            
        # === 原有命令的處理 ===
        elif args.command == 'help':
            helper.show_usage()
            
        elif args.command == 'diagnose':
            await helper.diagnostic.run_full_diagnostic(args.table, args.column)
            
        elif args.command == 'fix-dialogue':
            helper.fixer.dry_run = args.dry_run
            await helper.dialogue_fix_workflow(args.dry_run)
            
        elif args.command == 'add-column':
            helper.fixer.dry_run = args.dry_run
            await helper.auto_fix_workflow(args.table, args.column, args.type, args.comment)
            
        elif args.command == 'auto-fix':
            await helper.auto_fix_workflow(args.table, args.column, args.type, args.comment)
            
        elif args.command == 'verify':
            if args.dialogue:
                await helper.verifier.run_dialogue_column_verification()
            elif args.table:
                await helper.verifier.verify_database_connection()
                if args.column:
                    await helper.verifier.verify_column_exists(args.table, args.column)
                else:
                    await helper.verifier.verify_table_structure(args.table)
            else:
                await helper.verifier.verify_database_connection()
                await helper.verifier.verify_alembic_version()
                
        elif args.command == 'interactive':
            await helper.interactive_mode()
            
    except KeyboardInterrupt:
        print("\n⚠️  操作被用戶中斷")
    except Exception as e:
        print(f"❌ 執行過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())