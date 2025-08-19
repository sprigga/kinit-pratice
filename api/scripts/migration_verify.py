#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Alembic 遷移結果驗證工具
驗證修復操作是否成功完成
"""

import asyncio
import sys
import os
from pathlib import Path
from sqlalchemy import text
import argparse
from datetime import datetime
import json

# 添加專案路徑到 Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.database import async_engine


class MigrationVerifier:
    def __init__(self):
        self.test_results = []
        self.passed_tests = 0
        self.failed_tests = 0

    def add_test_result(self, test_name, passed, message="", details=None):
        """添加測試結果"""
        result = {
            'test_name': test_name,
            'passed': passed,
            'message': message,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        if passed:
            self.passed_tests += 1
            print(f"✅ {test_name}: {message}")
        else:
            self.failed_tests += 1
            print(f"❌ {test_name}: {message}")
            
        if details:
            print(f"   詳細: {details}")

    async def verify_alembic_version(self, expected_version=None):
        """驗證 Alembic 版本"""
        try:
            async with async_engine.begin() as conn:
                result = await conn.execute(text('SELECT version_num FROM alembic_version'))
                current_version = result.fetchone()
                
                if current_version:
                    version = current_version[0]
                    if expected_version:
                        if version == expected_version:
                            self.add_test_result(
                                "Alembic 版本檢查", 
                                True, 
                                f"版本正確: {version}"
                            )
                        else:
                            self.add_test_result(
                                "Alembic 版本檢查", 
                                False, 
                                f"版本不符: 期望 {expected_version}, 實際 {version}"
                            )
                    else:
                        self.add_test_result(
                            "Alembic 版本檢查", 
                            True, 
                            f"當前版本: {version}"
                        )
                    return version
                else:
                    self.add_test_result(
                        "Alembic 版本檢查", 
                        False, 
                        "alembic_version 表中沒有版本記錄"
                    )
                    return None
                    
        except Exception as e:
            self.add_test_result(
                "Alembic 版本檢查", 
                False, 
                f"查詢失敗: {str(e)}"
            )
            return None

    async def verify_column_exists(self, table_name, column_name, expected_type=None, expected_comment=None):
        """驗證欄位存在且配置正確"""
        try:
            async with async_engine.begin() as conn:
                result = await conn.execute(text('''
                    SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT, COLUMN_COMMENT
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_NAME = :table_name
                    AND COLUMN_NAME = :column_name
                    AND TABLE_SCHEMA = DATABASE()
                '''), {"table_name": table_name, "column_name": column_name})
                
                column_info = result.fetchone()
                
                if column_info:
                    details = {
                        'name': column_info[0],
                        'type': column_info[1],
                        'nullable': column_info[2] == 'YES',
                        'default': column_info[3],
                        'comment': column_info[4]
                    }
                    
                    # 檢查類型
                    type_ok = True
                    if expected_type and expected_type.lower() not in column_info[1].lower():
                        type_ok = False
                        
                    # 檢查註解
                    comment_ok = True
                    if expected_comment and column_info[4] != expected_comment:
                        comment_ok = False
                    
                    if type_ok and comment_ok:
                        self.add_test_result(
                            f"欄位 {table_name}.{column_name} 檢查",
                            True,
                            "欄位存在且配置正確",
                            details
                        )
                    else:
                        issues = []
                        if not type_ok:
                            issues.append(f"類型不符 (期望包含: {expected_type}, 實際: {column_info[1]})")
                        if not comment_ok:
                            issues.append(f"註解不符 (期望: {expected_comment}, 實際: {column_info[4]})")
                            
                        self.add_test_result(
                            f"欄位 {table_name}.{column_name} 檢查",
                            False,
                            f"欄位存在但配置有問題: {'; '.join(issues)}",
                            details
                        )
                    
                    return details
                else:
                    self.add_test_result(
                        f"欄位 {table_name}.{column_name} 檢查",
                        False,
                        f"欄位不存在於 {table_name} 表中"
                    )
                    return None
                    
        except Exception as e:
            self.add_test_result(
                f"欄位 {table_name}.{column_name} 檢查",
                False,
                f"查詢失敗: {str(e)}"
            )
            return None

    async def verify_table_structure(self, table_name, expected_columns=None):
        """驗證整個表結構"""
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
                    column_names = [col[0] for col in columns]
                    details = {
                        'total_columns': len(columns),
                        'columns': [
                            {
                                'name': col[0],
                                'type': col[1], 
                                'nullable': col[2] == 'YES',
                                'default': col[3],
                                'comment': col[4]
                            } for col in columns
                        ]
                    }
                    
                    if expected_columns:
                        missing_columns = set(expected_columns) - set(column_names)
                        if missing_columns:
                            self.add_test_result(
                                f"表 {table_name} 結構檢查",
                                False,
                                f"缺少欄位: {', '.join(missing_columns)}",
                                details
                            )
                        else:
                            self.add_test_result(
                                f"表 {table_name} 結構檢查",
                                True,
                                f"所有期望欄位都存在 ({len(columns)} 個欄位)",
                                details
                            )
                    else:
                        self.add_test_result(
                            f"表 {table_name} 結構檢查",
                            True,
                            f"表存在且包含 {len(columns)} 個欄位",
                            details
                        )
                    
                    return details
                else:
                    self.add_test_result(
                        f"表 {table_name} 結構檢查",
                        False,
                        f"表 {table_name} 不存在"
                    )
                    return None
                    
        except Exception as e:
            self.add_test_result(
                f"表 {table_name} 結構檢查",
                False,
                f"查詢失敗: {str(e)}"
            )
            return None

    async def verify_database_connection(self):
        """驗證資料庫連接"""
        try:
            async with async_engine.begin() as conn:
                result = await conn.execute(text('SELECT 1 as test'))
                test_result = result.fetchone()
                
                if test_result and test_result[0] == 1:
                    self.add_test_result(
                        "資料庫連接檢查",
                        True,
                        "資料庫連接正常"
                    )
                    return True
                else:
                    self.add_test_result(
                        "資料庫連接檢查",
                        False,
                        "資料庫連接異常"
                    )
                    return False
                    
        except Exception as e:
            self.add_test_result(
                "資料庫連接檢查",
                False,
                f"連接失敗: {str(e)}"
            )
            return False

    def verify_migration_files(self):
        """驗證遷移檔案完整性"""
        migration_dir = project_root / "alembic" / "versions_dev"
        
        if not migration_dir.exists():
            self.add_test_result(
                "遷移檔案檢查",
                False,
                f"遷移目錄不存在: {migration_dir}"
            )
            return False
            
        migration_files = list(migration_dir.glob("*.py"))
        
        if migration_files:
            details = {
                'migration_count': len(migration_files),
                'latest_migration': migration_files[-1].name if migration_files else None
            }
            
            self.add_test_result(
                "遷移檔案檢查",
                True,
                f"找到 {len(migration_files)} 個遷移檔案",
                details
            )
            return True
        else:
            self.add_test_result(
                "遷移檔案檢查",
                False,
                "沒有找到遷移檔案"
            )
            return False

    async def run_dialogue_column_verification(self):
        """專門驗證 dialogue 欄位的修復結果"""
        print("🔍 開始驗證 dialogue 欄位修復結果...")
        print("=" * 50)
        
        # 基本檢查
        await self.verify_database_connection()
        await self.verify_alembic_version()
        self.verify_migration_files()
        
        # 驗證 vadmin_test 表結構
        expected_columns = ['id', 'name_test', 'desc_test', 'status', 'dialogue', 
                           'create_datetime', 'update_datetime', 'delete_datetime', 
                           'is_delete', 'create_user', 'update_user', 'delete_user']
        
        await self.verify_table_structure('vadmin_test', expected_columns)
        
        # 詳細驗證 dialogue 欄位
        await self.verify_column_exists(
            'vadmin_test', 
            'dialogue', 
            expected_type='varchar',
            expected_comment='對話內容'
        )

    def generate_report(self, save_to_file=False):
        """生成驗證報告"""
        total_tests = self.passed_tests + self.failed_tests
        success_rate = (self.passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        report = {
            'summary': {
                'total_tests': total_tests,
                'passed_tests': self.passed_tests,
                'failed_tests': self.failed_tests,
                'success_rate': round(success_rate, 2),
                'timestamp': datetime.now().isoformat()
            },
            'test_results': self.test_results
        }
        
        print("\n" + "=" * 50)
        print("📊 驗證報告")
        print("=" * 50)
        print(f"總測試數: {total_tests}")
        print(f"通過測試: {self.passed_tests}")
        print(f"失敗測試: {self.failed_tests}")
        print(f"成功率: {success_rate:.1f}%")
        
        if self.failed_tests > 0:
            print("\n⚠️  失敗的測試:")
            for result in self.test_results:
                if not result['passed']:
                    print(f"  - {result['test_name']}: {result['message']}")
        else:
            print("\n🎉 所有測試都通過了！")
        
        if save_to_file:
            report_file = project_root / "logs" / f"migration_verification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            report_file.parent.mkdir(exist_ok=True)
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            print(f"\n📄 詳細報告已保存到: {report_file}")
        
        return report


async def main():
    parser = argparse.ArgumentParser(description='Alembic 遷移結果驗證工具')
    
    # 驗證模式  
    parser.add_argument('--dialogue', action='store_true', help='驗證 dialogue 欄位修復結果')
    parser.add_argument('--table', '-t', help='驗證指定表結構')
    parser.add_argument('--column', '-c', help='驗證指定欄位')
    parser.add_argument('--version', '-v', help='期望的 Alembic 版本')
    
    # 輸出選項
    parser.add_argument('--save-report', action='store_true', help='保存詳細報告到檔案')
    parser.add_argument('--quiet', '-q', action='store_true', help='只顯示摘要結果')
    
    args = parser.parse_args()
    
    verifier = MigrationVerifier()
    
    try:
        if args.dialogue:
            # 驗證 dialogue 欄位修復
            await verifier.run_dialogue_column_verification()
            
        elif args.table:
            # 驗證指定表
            await verifier.verify_database_connection()
            
            if args.column:
                await verifier.verify_column_exists(args.table, args.column)
            else:
                await verifier.verify_table_structure(args.table)
                
        elif args.version:
            # 驗證 Alembic 版本
            await verifier.verify_database_connection()
            await verifier.verify_alembic_version(args.version)
            
        else:
            # 基本驗證
            await verifier.verify_database_connection()
            await verifier.verify_alembic_version()
            verifier.verify_migration_files()
        
        # 生成報告
        verifier.generate_report(save_to_file=args.save_report)
        
        # 返回適當的退出碼
        exit_code = 0 if verifier.failed_tests == 0 else 1
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print("\n⚠️  驗證被用戶中斷")
        sys.exit(130)
    except Exception as e:
        print(f"❌ 驗證過程中發生錯誤: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())