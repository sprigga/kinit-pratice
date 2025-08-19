#!/usr/bin/python
# -*- coding: utf-8 -*-
# @version        : 1.0
# @Create Time    : 2022/12/9 15:27
# @File           : main.py
# @IDE            : PyCharm
# @desc           : 简要说明
import importlib
import os.path
import re
import sys
from typing import Type
from application.settings import BASE_DIR
import inspect
from pathlib import Path
from core.database import Base
from scripts.crud_generate.utils.generate_base import GenerateBase
from scripts.crud_generate.utils.generate_frontend_files import FrontendFileGenerator
from scripts.crud_generate.utils.schema_generate import SchemaGenerate
from scripts.crud_generate.utils.params_generate import ParamsGenerate
from scripts.crud_generate.utils.dal_generate import DalGenerate
from scripts.crud_generate.utils.services_generate import ServicesGenerate
from scripts.crud_generate.utils.urls_generate import UrlsGenerate
from scripts.crud_generate.utils.view_generate import ViewGenerate




class CrudGenerate(GenerateBase):
    APPS_ROOT = os.path.join(BASE_DIR, "apps")
    SCRIPT_DIR = os.path.join(BASE_DIR, 'scripts', 'crud_generate')

    def __init__(self, model: Type[Base], zh_name: str, en_name: str = None):
        """
        初始化工作
        :param model: 提前定义好的 ORM 模型
        :param zh_name: 功能中文名稱，主要用于描述、注释
        :param en_name: 功能英文名稱，主要用于 schema、param 文件命名，以及它们的 class 命名，dal、url 命名，默认使用 model class
        en_name 例子：
            如果 en_name 由多个单词组成那么請使用 _ 下划线拼接
            在命名文件名稱時，會执行使用 _ 下划线名稱
            在命名 class 名稱時，會将下划线名稱转换為大驼峰命名（CamelCase）
            在命名 url 時，會将下划线转换為 /
        """
        self.model = model
        self.zh_name = zh_name
        # model 文件的地址
        self.model_file_path = Path(inspect.getfile(sys.modules[model.__module__]))
        # model 文件 app 路径
        self.app_dir_path = self.model_file_path.parent.parent
        # schemas 目錄地址
        self.schemas_dir_path = self.app_dir_path / "schemas"
        # params 目錄地址
        self.params_dir_path = self.app_dir_path / "params"
        # services 目錄地址
        self.services_dir_path = self.app_dir_path / "services"
        # dal 目錄地址
        self.dal_dir_path = self.app_dir_path / "crud"
        # view 文件地址
        self.view_file_path = self.app_dir_path / "views.py"

        # 自動生成 en_name，將類名轉為 snake_case 格式
        if en_name:
            self.en_name = en_name
        else:
            class_name = self.model.__name__  # 取得模型類名
            self.en_name = re.sub(r'(?<!^)(?=[A-Z])', '_', class_name).lower()

        self.schema_file_path = self.schemas_dir_path / f"{self.en_name}.py"
        self.param_file_path = self.params_dir_path / f"{self.en_name}.py"
        self.service_file_path = self.services_dir_path / f"{self.en_name}.py"
        self.dal_file_path = self.dal_dir_path / f"{self.en_name}.py"

        self.base_class_name = self.snake_to_camel(self.en_name)
        self.dal_class_name = f"{self.base_class_name}Dal"
        self.schema_simple_out_class_name = f"{self.base_class_name}SimpleOut"
        self.param_class_name = f"{self.base_class_name}Params"
        self.service_class_name = f"{self.base_class_name}Services"

    def generate_codes(self):
        """
        生成代碼， 不做实际操作，只是将代碼打印出来
        :return:
        """
        print(f"==========================={self.schema_file_path} 代碼内容=================================")
        schema = SchemaGenerate(
            self.model,
            self.zh_name,
            self.en_name,
            self.schema_file_path,
            self.schemas_dir_path,
            self.base_class_name,
            self.schema_simple_out_class_name
        )
        print(schema.generate_code())

        print(f"==========================={self.dal_class_name} 代碼内容=================================")
        dal = DalGenerate(
            self.model,
            self.zh_name,
            self.en_name,
            self.dal_file_path,
            self.dal_dir_path,
            self.dal_class_name,
            self.schema_simple_out_class_name
        )
        print(dal.generate_code())

        print(f"==========================={self.param_file_path} 代碼内容=================================")
        params = ParamsGenerate(
            self.model,
            self.zh_name,
            self.en_name,
            self.params_dir_path,
            self.param_file_path,
            self.param_class_name
        )
        print(params.generate_code())

        print(f"==========================={self.service_file_path} 代碼内容=================================")
        services = ServicesGenerate(
            self.model,
            self.zh_name,
            self.en_name,
            self.services_dir_path,
            self.service_file_path,
            self.service_class_name
        )
        print(services.generate_code())

        print(f"==========================={self.view_file_path} 代碼内容=================================")
        view = ViewGenerate(
            self.model,
            self.zh_name,
            self.en_name,
            self.base_class_name,
            self.schema_simple_out_class_name,
            self.dal_class_name,
            self.param_class_name
        )
        print(view.generate_code())

    def generate_urls_entry(self):
        """
        自動將路由導入語句和路由條目寫入到根目錄 /application/urls.py 文件
        """
        root_urls_path = Path(BASE_DIR) / "application" / "urls.py"

        relative_import_path = self.app_dir_path.relative_to(BASE_DIR).as_posix().replace('/', '.')
        app_import_path = f"from {relative_import_path}.views import app as {self.en_name}_app\n"

        model_name_parts = re.findall(r'[A-Z][a-z]*',
                                      self.model.__name__)  # 例如 'LotteryMembers' -> ['Lottery', 'Members']
        folder_name = model_name_parts[0].lower()  # 'lottery'

        model_name = model_name_parts[1].lower()  # 'members'

        # 提取父級和子級路徑
        prefix = f"/{folder_name}/{model_name}"

        route_entry = f'    {{"ApiRouter": {self.en_name}_app, "prefix": "{prefix}", "tags": ["{self.zh_name}"]}},\n'

        with open(root_urls_path, "r+", encoding="utf-8") as file:
            urls_content = file.readlines()
            if app_import_path not in urls_content:
                urls_content.insert(0, app_import_path)
            if route_entry not in urls_content:
                for i, line in enumerate(urls_content):
                    if "urlpatterns = [" in line:
                        urls_content.insert(i + 1, route_entry)
                        break
            file.seek(0)
            file.writelines(urls_content)

        print(f"成功添加路由至 {root_urls_path}")

    def main(self):
        """
        开始生成 crud 代碼，並直接写入到項目中，目前还未实现
        1. 生成 schemas 代碼
        2. 生成 dal 代碼
        3. 生成 params 代碼
        4. 生成 views 代碼
        4. 生成 services 代碼
        :return:
        """
        schema = SchemaGenerate(
            self.model,
            self.zh_name,
            self.en_name,
            self.schema_file_path,
            self.schemas_dir_path,
            self.base_class_name,
            self.schema_simple_out_class_name
        )
        schema.write_generate_code()

        dal = DalGenerate(
            self.model,
            self.zh_name,
            self.en_name,
            self.dal_file_path,
            self.dal_dir_path,
            self.dal_class_name,
            self.schema_simple_out_class_name
        )
        dal.write_generate_code()

        params = ParamsGenerate(
            self.model,
            self.zh_name,
            self.en_name,
            self.params_dir_path,
            self.param_file_path,
            self.param_class_name
        )
        params.write_generate_code()

        services = ServicesGenerate(
            self.model,
            self.zh_name,
            self.en_name,
            self.services_dir_path,
            self.service_file_path,
            self.service_class_name
        )
        services.write_generate_code()

        view = ViewGenerate(
            self.model,
            self.zh_name,
            self.en_name,
            self.base_class_name,
            self.schema_simple_out_class_name,
            self.dal_class_name,
            self.param_class_name
        )
        view.write_generate_code()
        # 生成前端調用模板
        # 创建 FrontendFileGenerator 类的实例
        frontend_generator = FrontendFileGenerator(self.model, self.model.__name__, self.zh_name, self.en_name)
        # 调用 generate_frontend_files 方法生成前端文件
        frontend_generator.generate_frontend_files()

        # 自動生成並寫入路由
        self.generate_urls_entry()


def find_model_class(model_name: str):
    """
    自動遍歷 apps 目錄下的所有 .py 文件，查找符合名稱的 SQLAlchemy 模型類
    :param model_name: 模型類名，例如 'LotteryMembers'
    :return: 返回 SQLAlchemy 模型類本身
    """
    found_classes = []
    
    for root, _, files in os.walk(os.path.join(BASE_DIR, "apps")):
        for file in files:
            if file.endswith(".py") and not file.startswith("__init__"):
                # 計算相對路徑，轉換成模組導入路徑
                module_path = os.path.relpath(os.path.join(root, file), BASE_DIR).replace(os.path.sep, ".")
                if module_path.endswith(".py"):
                    module_path = module_path[:-3]  # 只刪除 `.py`
                try:
                    # 動態導入模組
                    module = importlib.import_module(module_path)
                    # 檢查模組內是否有指定的類
                    if hasattr(module, model_name):
                        model_class = getattr(module, model_name)
                        
                        # 檢查是否為 SQLAlchemy 模型類
                        if _is_sqlalchemy_model(model_class):
                            print(f"找到 SQLAlchemy 模型類 '{model_name}' 於模組: {module_path}")
                            found_classes.append((model_class, module_path))
                        else:
                            print(f"跳過非 SQLAlchemy 模型類 '{model_name}' 於模組: {module_path} (類型: {type(model_class)})")
                            
                except Exception as e:
                    # 靜默處理導入錯誤，避免過多輸出
                    pass
    
    if not found_classes:
        raise ImportError(f"未找到 SQLAlchemy 模型類 '{model_name}'，請確認類名是否正確且該類繼承自 Base。")
    
    if len(found_classes) > 1:
        print(f"警告: 找到多個同名的 SQLAlchemy 模型類:")
        for cls, path in found_classes:
            print(f"  - {path}")
        print(f"使用第一個找到的: {found_classes[0][1]}")
    
    return found_classes[0][0]


def _is_sqlalchemy_model(cls):
    """
    檢查類是否為 SQLAlchemy 模型類
    :param cls: 要檢查的類
    :return: 如果是 SQLAlchemy 模型類則返回 True
    """
    try:
        # 檢查是否為類
        if not inspect.isclass(cls):
            return False
            
        # 檢查是否繼承自 Base
        if not issubclass(cls, Base):
            return False
            
        # 檢查是否有 __tablename__ 屬性
        if not hasattr(cls, '__tablename__'):
            return False
            
        # 排除 Base 類本身
        if cls is Base:
            return False
            
        return True
    except (TypeError, AttributeError):
        return False

if __name__ == '__main__':
    # 檢查命令行參數
    if len(sys.argv) < 3:
        print("用法: python main.py <模型類名> <功能中文名稱>")
        print("示例: python main.py LotteryMembers 會員管理")
        sys.exit(1)

    model_name = sys.argv[1]  # 模型類名，例如 LotteryMembers
    zh_name = sys.argv[2]     # 功能中文名稱，例如 會員管理

    try:
        # 自動查找模型類
        ModelClass = find_model_class(model_name)
        print(f"成功找到模型類 '{model_name}'，開始生成代碼...")
        crud = CrudGenerate(ModelClass, zh_name)
        crud.main()

        # # 使用模型类
        # from apps.lottery.members.models import LotteryMembers  # 根据您的实际模型类路径导入
        #
        # model = LotteryMembers  # 模型类
        # base_class_name = "LotteryMember"  # 基类名称
        # zh_name = "会员"  # 中文名称
        # en_name = "lottery_member"  # 英文名称
        #
        # # 创建 FrontendFileGenerator 类的实例
        # frontend_generator = FrontendFileGenerator(model, base_class_name, zh_name, en_name)
        #
        # # 调用 generate_frontend_files 方法生成前端文件
        # frontend_generator.generate_frontend_files()


    except ImportError as e:
        print(e)
