import inspect
import sys
from pathlib import Path
from typing import Type
from core.database import Base
from .generate_base import GenerateBase


class DalGenerate(GenerateBase):

    def __init__(
            self,
            model: Type[Base],
            zh_name: str,
            en_name: str,
            dal_file_path: Path,
            dal_dir_path: Path,
            dal_class_name: str,
            schema_simple_out_class_name: str
    ):
        """
        初始化工作
        :param model: 提前定義好的 ORM 模型
        :param zh_name: 功能中文名稱，主要用於描述、註釋
        :param en_name: 功能英文名稱，主要用於 schema、param 文件命名，以及它們的 class 命名，dal、url 命名，默認使用 model class
        en_name 例子：
            如果 en_name 由多個單詞組成那麼請使用 _ 下劃線拼接
            在命名文件名稱時，會執行使用 _ 下劃線名稱
            在命名 class 名稱時，會將下劃線名稱轉換為大駝峰命名（CamelCase）
            在命名 url 時，會將下劃線轉換為 /
        :param dal_class_name:
        :param schema_simple_out_class_name:
        """
        self.model = model
        self.dal_class_name = dal_class_name
        self.schema_simple_out_class_name = schema_simple_out_class_name
        self.zh_name = zh_name
        self.en_name = en_name
        # model 文件的地址
        self.model_file_path = Path(inspect.getfile(sys.modules[model.__module__]))
        # model 文件 app 路徑
        self.app_dir_path = self.model_file_path.parent.parent
        # dal 目錄
        self.dal_file_path = dal_file_path
        self.dal_dir_path = dal_dir_path
        self.dal_init_file_path = self.dal_dir_path / "__init__.py"

    def write_generate_code(self):
        """
        生成 dal 文件，以及代碼內容
        :return:
        """
        self.dal_file_path.parent.mkdir(parents=True, exist_ok=True)
        if self.dal_file_path.exists():
            # 存在則直接刪除，重新創建寫入
            self.dal_file_path.unlink()
        self.dal_file_path.touch()
        self.dal_init_file_path.touch()
        code = self.generate_code()
        self.dal_file_path.write_text(code, "utf-8")

        init_code = self.generate_init_code()
        self.update_init_file(self.dal_init_file_path, init_code)

        print(f"===========================dal 代碼創建完成=================================")

    def generate_init_code(self):
        """
        生成 __init__ 文件導入程式碼
        :return:
        """
        init_code = f"from .{self.en_name} import {self.dal_class_name}"
        return init_code

    def generate_code(self):
        """
        代碼生成
        :return:
        """
        code = self.generate_file_desc(self.dal_file_path.name, "1.0", "資料存取層")
        code += self.generate_modules_code(self.get_base_module_config())
        code += self.get_base_code_content()
        return code

    @staticmethod
    def get_base_module_config():
        """
        獲取基礎模組導入配置
        :return:
        """
        modules = {
            "sqlalchemy.ext.asyncio": ['AsyncSession'],
            "core.crud": ["DalBase"],
            "..": ["models", "schemas"],
        }
        return modules

    def get_base_code_content(self):
        """
        獲取基礎代碼內容
        :return:
        """
        base_code = f"\n\nclass {self.dal_class_name}(DalBase):\n"
        base_code += "\n\tdef __init__(self, db: AsyncSession):"
        base_code += f"\n\t\tsuper({self.dal_class_name}, self).__init__()"
        base_code += f"\n\t\tself.db = db"
        base_code += f"\n\t\tself.model = models.{self.model.__name__}"
        base_code += f"\n\t\tself.schema = schemas.{self.schema_simple_out_class_name}"
        base_code += "\n"
        return base_code.replace("\t", "    ")
