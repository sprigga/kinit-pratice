#!/usr/bin/python
# -*- coding: utf-8 -*-
# @version        : 1.0
# @Create Time    : 2025-08-04 11:40:00
# @File           : check_mysql_table.py
# @IDE            : PyCharm
# @desc           : 檢查指定資料表是否存在於 MySQL 中

import asyncio
import sys
import os
import argparse

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import db_getter
from sqlalchemy import text


async def check_mysql_table(table_name: str):
    """檢查指定資料表是否存在"""
    
    async for db in db_getter():
        try:
            print(f"🔍 檢查資料表: {table_name}")
            print("=" * 80)
            
            # 檢查資料表是否存在 (先檢查原名，再檢查小寫)
            result = await db.execute(text(f"SHOW TABLES LIKE '{table_name}'"))
            table_exists = result.fetchone() is not None
            
            if not table_exists:
                # 嘗試小寫版本
                result = await db.execute(text(f"SHOW TABLES LIKE '{table_name.lower()}'"))
                table_exists = result.fetchone() is not None
                if table_exists:
                    table_name = table_name.lower()
            
            if not table_exists:
                # 嘗試大寫版本
                result = await db.execute(text(f"SHOW TABLES LIKE '{table_name.upper()}'"))
                table_exists = result.fetchone() is not None
                if table_exists:
                    table_name = table_name.upper()
            
            if table_exists:
                print(f"✅ {table_name} 資料表已成功創建")
                
                # 檢查資料表結構
                try:
                    result = await db.execute(text(f"DESCRIBE {table_name}"))
                    columns = result.fetchall()
                except Exception as e:
                    print(f"❌ 無法獲取表結構: {str(e)}")
                    return
                
                print(f"\n📋 {table_name} 資料表結構:")
                print("-" * 80)
                print(f"{'欄位名稱':<20} {'資料型別':<20} {'可為空':<10} {'索引':<10} {'預設值':<15} {'備註'}")
                print("-" * 80)
                
                for column in columns:
                    field = column[0]
                    type_info = column[1]
                    null = column[2]
                    key = column[3]
                    default = column[4] or ''
                    extra = column[5]
                    print(f"{field:<20} {type_info:<20} {null:<10} {key:<10} {str(default):<15} {extra}")
                
                # 檢查記錄數量
                try:
                    result = await db.execute(text(f"SELECT COUNT(*) as count FROM {table_name}"))
                    count = result.fetchone()[0]
                    print(f"\n📊 {table_name} 目前記錄數量: {count}")
                except Exception as e:
                    print(f"❌ 無法獲取記錄數量: {str(e)}")
                
            else:
                print(f"❌ {table_name} 資料表不存在")
            
            # 檢查 Alembic 遷移記錄
            try:
                result = await db.execute(text("SELECT version_num FROM alembic_version ORDER BY version_num DESC LIMIT 5"))
                versions = result.fetchall()
                
                print(f"\n🔄 最近的 Alembic 遷移版本:")
                for version in versions:
                    print(f"  - {version[0]}")
            except Exception as e:
                print(f"❌ 無法獲取 Alembic 版本信息: {str(e)}")
            
            # 列出所有資料表
            try:
                result = await db.execute(text("SHOW TABLES"))
                tables = result.fetchall()
                
                print(f"\n📋 目前資料庫中的所有資料表:")
                table_list = [table[0] for table in tables]
                table_list.sort()
                for i, table in enumerate(table_list, 1):
                    print(f"  {i:2d}. {table}")
                    
            except Exception as e:
                print(f"❌ 無法獲取資料表列表: {str(e)}")
                    
        except Exception as e:
            print(f"❌ 檢查時發生錯誤: {str(e)}")
        
        break  # 只需要一個資料庫連接


def main():
    """主程序入口"""
    parser = argparse.ArgumentParser(
        description='檢查 MySQL 資料表是否存在', 
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用範例:
  python check_mysql_table.py bpmin_it
  python check_mysql_table.py Bpmin_it
  python check_mysql_table.py vadmin_test
  python check_mysql_table.py vadmin_auth_user
        """
    )
    
    parser.add_argument(
        'table_name', 
        help='要檢查的資料表名稱'
    )
    
    parser.add_argument(
        '--version', 
        action='version', 
        version='check_mysql_table.py 1.0'
    )
    
    args = parser.parse_args()
    
    if not args.table_name:
        print("❌ 錯誤: 請提供資料表名稱")
        parser.print_help()
        sys.exit(1)
    
    # 執行檢查
    asyncio.run(check_mysql_table(args.table_name))


if __name__ == "__main__":
    main()