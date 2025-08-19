#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Alembic 遷移問題修復工具
根據 SOP 文檔自動修復遷移問題
"""

import asyncio
import sys
import os
from pathlib import Path
from sqlalchemy import text
import argparse
from datetime import datetime

# 添加專案路徑到 Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.database import async_engine


class MigrationFix:
    def __init__(self, dry_run=False):
        self.dry_run = dry_run
        self.backup_info = []

    async def create_backup_info(self):
        """創建備份資訊（記錄當前狀態）"""
        try:
            async with async_engine.begin() as conn:
                # 記錄當前 Alembic 版本
                result = await conn.execute(text('SELECT version_num FROM alembic_version'))
                current_version = result.fetchone()
                
                backup_info = {
                    'timestamp': datetime.now().isoformat(),
                    'alembic_version': current_version[0] if current_version else None,
                }
                
                self.backup_info.append(backup_info)
                print(f"📝 備份資訊已記錄: Alembic 版本 {backup_info['alembic_version']}")
                return backup_info
                
        except Exception as e:
            print(f"❌ 創建備份資訊時發生錯誤: {e}")
            return None

    async def sync_alembic_version(self, target_version):
        """同步 Alembic 版本到指定版本"""
        print(f"🔄 {'[DRY RUN] ' if self.dry_run else ''}同步 Alembic 版本到 {target_version}")
        
        if self.dry_run:
            print(f"   將執行: UPDATE alembic_version SET version_num = '{target_version}'")
            return True
            
        try:
            async with async_engine.begin() as conn:
                await conn.execute(
                    text('UPDATE alembic_version SET version_num = :version'), 
                    {"version": target_version}
                )
                print(f"✅ Alembic 版本已更新到 {target_version}")
                return True
                
        except Exception as e:
            print(f"❌ 更新 Alembic 版本時發生錯誤: {e}")
            return False

    async def add_column(self, table_name, column_name, column_type, nullable=True, default=None, comment=None):
        """新增欄位到資料表"""
        # 構建 SQL 語句
        sql_parts = [f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"]
        
        if not nullable:
            sql_parts.append("NOT NULL")
        else:
            sql_parts.append("NULL")
            
        if default is not None:
            sql_parts.append(f"DEFAULT {default}")
            
        if comment:
            sql_parts.append(f"COMMENT '{comment}'")
            
        sql = " ".join(sql_parts)
        
        print(f"➕ {'[DRY RUN] ' if self.dry_run else ''}新增欄位 {column_name} 到 {table_name}")
        print(f"   SQL: {sql}")
        
        if self.dry_run:
            return True
            
        try:
            async with async_engine.begin() as conn:
                await conn.execute(text(sql))
                print(f"✅ 欄位 {column_name} 已成功新增到 {table_name}")
                return True
                
        except Exception as e:
            if 'Duplicate column name' in str(e):
                print(f"⚠️  欄位 {column_name} 已存在於 {table_name} 中")
                return True
            else:
                print(f"❌ 新增欄位時發生錯誤: {e}")
                return False

    async def check_column_exists(self, table_name, column_name):
        """檢查欄位是否存在"""
        try:
            async with async_engine.begin() as conn:
                result = await conn.execute(text('''
                    SELECT COLUMN_NAME 
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_NAME = :table_name
                    AND COLUMN_NAME = :column_name
                    AND TABLE_SCHEMA = DATABASE()
                '''), {"table_name": table_name, "column_name": column_name})
                
                return result.fetchone() is not None
                
        except Exception as e:
            print(f"❌ 檢查欄位時發生錯誤: {e}")
            return False

    def get_latest_migration_version(self):
        """獲取最新的遷移版本"""
        migration_dir = project_root / "alembic" / "versions_dev"
        migration_files = sorted(migration_dir.glob("*.py"))
        
        if not migration_files:
            return None
            
        latest_file = migration_files[-1]
        # 從檔名中提取版本 ID（假設格式為 version_id_description.py）
        version_id = latest_file.stem.split('_')[0]
        return version_id

    async def fix_missing_column(self, table_name, column_name, column_type="VARCHAR(500)", 
                                nullable=True, default=None, comment=None, sync_version=True):
        """修復缺少的欄位"""
        print(f"🔧 開始修復 {table_name}.{column_name} 欄位問題")
        print("=" * 50)
        
        # 創建備份資訊
        await self.create_backup_info()
        
        # 檢查欄位是否已存在
        exists = await self.check_column_exists(table_name, column_name)
        
        if exists:
            print(f"✅ 欄位 {column_name} 已存在於 {table_name} 中")
        else:
            # 新增欄位
            success = await self.add_column(table_name, column_name, column_type, 
                                          nullable, default, comment)
            if not success:
                return False
        
        # 同步 Alembic 版本
        if sync_version:
            latest_version = self.get_latest_migration_version()
            if latest_version:
                await self.sync_alembic_version(latest_version)
            else:
                print("⚠️  無法找到最新的遷移版本")
        
        print("✅ 修復完成！")
        return True

    async def fix_dialogue_column_issue(self):
        """專門修復 dialogue 欄位問題（基於我們的經驗）"""
        return await self.fix_missing_column(
            table_name="vadmin_test",
            column_name="dialogue", 
            column_type="VARCHAR(500)",
            nullable=True,
            comment="對話內容",
            sync_version=True
        )

    async def rollback_to_backup(self):
        """回滾到備份狀態"""
        if not self.backup_info:
            print("❌ 沒有可用的備份資訊")
            return False
            
        latest_backup = self.backup_info[-1]
        print(f"🔄 回滾到備份狀態: {latest_backup['timestamp']}")
        
        if latest_backup['alembic_version']:
            return await self.sync_alembic_version(latest_backup['alembic_version'])
        
        return True

    def show_help(self):
        """顯示使用說明"""
        help_text = """
🛠️  Alembic 遷移修復工具使用說明

常用修復場景:

1. 修復缺少的欄位:
   python scripts/migration_fix.py --add-column --table vadmin_test --column dialogue --type "VARCHAR(500)" --comment "對話內容"

2. 同步 Alembic 版本:
   python scripts/migration_fix.py --sync-version --version b8b03c4e431a

3. 修復 dialogue 欄位問題（快捷方式）:
   python scripts/migration_fix.py --fix-dialogue

4. 乾跑模式（僅顯示將執行的操作）:
   python scripts/migration_fix.py --fix-dialogue --dry-run

5. 顯示這個幫助:
   python scripts/migration_fix.py --help

參數說明:
  --add-column     新增欄位模式
  --table         資料表名稱
  --column        欄位名稱  
  --type          欄位類型 (預設: VARCHAR(500))
  --comment       欄位註解
  --nullable      是否允許 NULL (預設: True)
  --sync-version  同步 Alembic 版本模式
  --version       指定版本 (留空使用最新版本)
  --fix-dialogue  修復 dialogue 欄位（快捷方式）
  --dry-run       乾跑模式，不實際執行
  --rollback      回滾到備份狀態
        """
        print(help_text)


async def main():
    parser = argparse.ArgumentParser(description='Alembic 遷移問題修復工具')
    
    # 操作模式
    parser.add_argument('--add-column', action='store_true', help='新增欄位模式')
    parser.add_argument('--sync-version', action='store_true', help='同步版本模式')
    parser.add_argument('--fix-dialogue', action='store_true', help='修復 dialogue 欄位（快捷方式）')
    parser.add_argument('--rollback', action='store_true', help='回滾到備份狀態')
    
    # 欄位相關參數
    parser.add_argument('--table', '-t', help='資料表名稱')
    parser.add_argument('--column', '-c', help='欄位名稱')
    parser.add_argument('--type', default='VARCHAR(500)', help='欄位類型')
    parser.add_argument('--comment', help='欄位註解')
    parser.add_argument('--nullable', action='store_true', default=True, help='是否允許 NULL')
    
    # 版本相關參數
    parser.add_argument('--version', '-v', help='Alembic 版本')
    
    # 其他選項
    parser.add_argument('--dry-run', action='store_true', help='乾跑模式，不實際執行')
    
    args = parser.parse_args()
    
    # 如果沒有提供任何參數，顯示幫助
    if len(sys.argv) == 1:
        MigrationFix().show_help()
        return
    
    fixer = MigrationFix(dry_run=args.dry_run)
    
    try:
        if args.fix_dialogue:
            # 修復 dialogue 欄位問題
            await fixer.fix_dialogue_column_issue()
            
        elif args.add_column:
            # 新增欄位模式
            if not args.table or not args.column:
                print("❌ 新增欄位模式需要 --table 和 --column 參數")
                return
                
            await fixer.fix_missing_column(
                table_name=args.table,
                column_name=args.column,
                column_type=args.type,
                nullable=args.nullable,
                comment=args.comment
            )
            
        elif args.sync_version:
            # 同步版本模式
            version = args.version or fixer.get_latest_migration_version()
            if not version:
                print("❌ 無法確定目標版本，請使用 --version 參數指定")
                return
                
            await fixer.sync_alembic_version(version)
            
        elif args.rollback:
            # 回滾模式
            await fixer.rollback_to_backup()
            
        else:
            fixer.show_help()
            
    except KeyboardInterrupt:
        print("\n⚠️  操作被用戶中斷")
    except Exception as e:
        print(f"❌ 執行過程中發生錯誤: {e}")


if __name__ == "__main__":
    asyncio.run(main())