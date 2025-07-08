import inspect
import sys
from pathlib import Path
from typing import Type
from core.database import Base
from .generate_base import GenerateBase


class ServicesGenerate(GenerateBase):

    def __init__(
            self,
            model: Type[Base],
            zh_name: str,
            en_name: str,
            services_dir_path: Path,
            service_file_path: Path,
            service_class_name: str
    ):
        """
        初始化工作
        :service model: 提前定義好的 ORM 模型
        :service zh_name: 功能中文名稱，主要用於描述、註釋
        :service service_class_name:
        :service service_file_path:
        :service services_dir_path:
        :service en_name: 功能英文名稱，主要用於 service、service 文件命名，以及它們的 class 命名，dal、url 命名，默認使用 model class
        en_name 例子：
            如果 en_name 由多個單詞組成那麼請使用 _ 下劃線拼接
            在命名文件名稱時，會執行使用 _ 下劃線名稱
            在命名 class 名稱時，會將下劃線名稱轉換為大駝峰命名（CamelCase）
            在命名 url 時，會將下劃線轉換為 /
        """

        self.model = model
        self.service_class_name = service_class_name
        self.zh_name = zh_name
        self.en_name = en_name
        # model 文件的地址
        self.model_file_path = Path(inspect.getfile(sys.modules[model.__module__]))
        # model 文件 app 路徑
        self.app_dir_path = self.model_file_path.parent.parent
        # services 目錄地址
        self.services_dir_path = services_dir_path
        self.service_file_path = service_file_path

    def write_generate_code(self):
        """
        生成 services 文件，以及程式碼內容
        :return:
        """
        service_init_file_path = self.services_dir_path / "__init__.py"
        self.service_file_path.parent.mkdir(parents=True, exist_ok=True)
        if self.service_file_path.exists():
            self.service_file_path.unlink()
        self.service_file_path.touch()
        service_init_file_path.touch()

        # 把檔案寫入
        code = self.generate_code()
        self.service_file_path.write_text(code, "utf-8")

        init_code = f"from .{self.en_name} import {self.service_class_name}"
        self.update_init_file(service_init_file_path, init_code)
        print(f"===========================service 程式碼創建完成=================================")

    def generate_code(self) -> str:
        """
        生成 schema 程式碼內容
        :return:
        """
        code = self.generate_file_desc(self.service_file_path.name, "1.0", self.zh_name)

        modules = {
            "..": ["models", "schemas", "crud", "params"],
            "core.dependencies": ['Paging', "QueryParams"],
        }
        code += self.generate_modules_code(modules)

        base_code = f"\n\nclass {self.service_class_name}:"
        base_code += "\n\t@classmethod"
        base_code += f"\n\tasync def create_{self.en_name}(cls, data):"
        base_code += "\n\t\tpass"

        base_code += "\n\t@classmethod"
        base_code += f"\n\tasync def get_{self.en_name}(cls, data):"
        base_code += "\n\t\tpass"

        base_code += "\n\t@classmethod"
        base_code += f"\n\tasync def list_{self.en_name}(cls, data):"
        base_code += "\n\t\tpass"
        base_code += "\n"

        base_code += "\n\t@classmethod"
        base_code += f"\n\tasync def update_{self.en_name}(cls, data):"
        base_code += "\n\t\tpass"
        base_code += "\n"

        base_code += "\n\t@classmethod"
        base_code += f"\n\tasync def delete_{self.en_name}(cls, data):"
        base_code += "\n\t\tpass"
        base_code += "\n"




        base_code += "\n"
        code += base_code
        return code.replace("\t", "    ")
