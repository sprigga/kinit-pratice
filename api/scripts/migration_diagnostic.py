#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Alembic 遷移問題診斷工具
根據 SOP 文檔自動診斷遷移問題
"""

import asyncio
import sys
import os
from pathlib import Path
from sqlalchemy import text
import argparse

# 添加專案路徑到 Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.database import async_engine


class MigrationDiagnostic:
    def __init__(self):
        self.issues = []
        self.recommendations = []

    async def check_alembic_version(self):
        """檢查當前 Alembic 版本"""
        try:
            async with async_engine.begin() as conn:
                result = await conn.execute(text('SELECT version_num FROM alembic_version'))
                current_version = result.fetchone()
                
                if current_version:
                    print(f"✅ 當前 Alembic 版本: {current_version[0]}")
                    return current_version[0]
                else:
                    print("❌ 未找到 Alembic 版本記錄")
                    self.issues.append("alembic_version 表中沒有版本記錄")
                    return None
        except Exception as e:
            print(f"❌ 檢查 Alembic 版本時發生錯誤: {e}")
            self.issues.append(f"無法連接資料庫或查詢 alembic_version: {e}")
            return None

    async def check_table_structure(self, table_name):
        """檢查資料表結構"""
        try:
            async with async_engine.begin() as conn:
                result = await conn.execute(text('''
                    SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT, COLUMN_COMMENT
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_NAME = :table_name
                    AND TABLE_SCHEMA = DATABASE()
                    ORDER BY ORDINAL_POSITION
                '''), {"table_name": table_name})
                
                columns = result.fetchall()
                if columns:
                    print(f"\n✅ {table_name} 表結構:")
                    for col in columns:
                        nullable = "NULL" if col[2] == "YES" else "NOT NULL"
                        default = f"DEFAULT {col[3]}" if col[3] else ""
                        comment = col[4] if col[4] else ""
                        print(f"  {col[0]}: {col[1]} {nullable} {default} | Comment: {comment}")
                    return columns
                else:
                    print(f"❌ 找不到表 {table_name}")
                    self.issues.append(f"資料庫中不存在表 {table_name}")
                    return None
        except Exception as e:
            print(f"❌ 檢查表結構時發生錯誤: {e}")
            self.issues.append(f"查詢表結構失敗: {e}")
            return None

    async def check_column_exists(self, table_name, column_name):
        """檢查特定欄位是否存在"""
        try:
            async with async_engine.begin() as conn:
                result = await conn.execute(text('''
                    SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_COMMENT
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_NAME = :table_name
                    AND COLUMN_NAME = :column_name
                    AND TABLE_SCHEMA = DATABASE()
                '''), {"table_name": table_name, "column_name": column_name})
                
                column_info = result.fetchone()
                if column_info:
                    print(f"✅ 欄位 {column_name} 存在於 {table_name} 表中")
                    print(f"  類型: {column_info[1]}")
                    print(f"  允許NULL: {column_info[2]}")
                    print(f"  註解: {column_info[3]}")
                    return True
                else:
                    print(f"❌ 欄位 {column_name} 不存在於 {table_name} 表中")
                    self.issues.append(f"缺少欄位: {table_name}.{column_name}")
                    return False
        except Exception as e:
            print(f"❌ 檢查欄位時發生錯誤: {e}")
            self.issues.append(f"查詢欄位失敗: {e}")
            return False

    def check_migration_files(self):
        """檢查遷移檔案"""
        migration_dir = project_root / "alembic" / "versions_dev"
        if not migration_dir.exists():
            print(f"❌ 遷移目錄不存在: {migration_dir}")
            self.issues.append("遷移目錄不存在")
            return []

        migration_files = sorted(migration_dir.glob("*.py"))
        if migration_files:
            print(f"\n✅ 找到 {len(migration_files)} 個遷移檔案:")
            for file in migration_files[-5:]:  # 顯示最新的5個
                print(f"  {file.name}")
            return migration_files
        else:
            print("❌ 沒有找到遷移檔案")
            self.issues.append("沒有遷移檔案")
            return []

    def check_latest_migration_content(self, search_column=None):
        """檢查最新遷移檔案內容"""
        migration_dir = project_root / "alembic" / "versions_dev"
        migration_files = sorted(migration_dir.glob("*.py"))
        
        if not migration_files:
            return None

        latest_file = migration_files[-1]
        print(f"\n🔍 檢查最新遷移檔案: {latest_file.name}")
        
        try:
            with open(latest_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if search_column:
                if search_column in content:
                    print(f"✅ 最新遷移檔案包含 {search_column} 相關內容")
                    # 找出包含該欄位的行
                    lines = content.split('\n')
                    for i, line in enumerate(lines, 1):
                        if search_column in line:
                            print(f"  第 {i} 行: {line.strip()}")
                else:
                    print(f"❌ 最新遷移檔案不包含 {search_column} 相關內容")
                    self.issues.append(f"最新遷移檔案缺少 {search_column} 變更")
                    
            return content
        except Exception as e:
            print(f"❌ 讀取遷移檔案時發生錯誤: {e}")
            return None

    def generate_recommendations(self):
        """根據發現的問題生成建議"""
        if not self.issues:
            print("\n🎉 沒有發現問題！系統狀態正常。")
            return

        print(f"\n⚠️  發現 {len(self.issues)} 個問題:")
        for i, issue in enumerate(self.issues, 1):
            print(f"{i}. {issue}")

        print("\n💡 建議的解決方案:")
        
        if any("缺少欄位" in issue for issue in self.issues):
            print("1. 執行修復指令新增缺少的欄位:")
            print("   python scripts/migration_fix.py --table <table_name> --column <column_name> --type <column_type>")
            
        if any("alembic_version" in issue for issue in self.issues):
            print("2. 修復 Alembic 版本同步問題:")
            print("   python scripts/migration_fix.py --sync-version")
            
        if any("遷移檔案" in issue for issue in self.issues):
            print("3. 重新生成遷移檔案:")
            print("   python main.py migrate --env dev")

    async def run_full_diagnostic(self, table_name=None, column_name=None):
        """執行完整診斷"""
        print("🔍 開始 Alembic 遷移診斷...")
        print("=" * 50)
        
        # 檢查 Alembic 版本
        current_version = await self.check_alembic_version()
        
        # 檢查遷移檔案
        migration_files = self.check_migration_files()
        
        # 如果指定了表名，檢查表結構
        if table_name:
            await self.check_table_structure(table_name)
            
            # 如果指定了欄位名，檢查欄位
            if column_name:
                await self.check_column_exists(table_name, column_name)
                self.check_latest_migration_content(column_name)
        
        # 生成建議
        print("\n" + "=" * 50)
        self.generate_recommendations()


async def main():
    parser = argparse.ArgumentParser(description='Alembic 遷移問題診斷工具')
    parser.add_argument('--table', '-t', help='要檢查的資料表名稱')
    parser.add_argument('--column', '-c', help='要檢查的欄位名稱')
    
    args = parser.parse_args()
    
    diagnostic = MigrationDiagnostic()
    await diagnostic.run_full_diagnostic(args.table, args.column)


if __name__ == "__main__":
    asyncio.run(main())