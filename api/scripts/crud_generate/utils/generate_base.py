import datetime
import re
from pathlib import Path


class GenerateBase:

    @staticmethod
    def camel_to_snake(name: str) -> str:
        """
        將大駝峰命名（CamelCase）轉換為下劃線命名（snake_case）
        在大寫字母前添加一個空格，然後將字串分割並用下劃線拼接
        :param name: 大駝峰命名（CamelCase）
        :return:
        """
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    @staticmethod
    def snake_to_camel(name: str) -> str:
        """
        將下劃線命名（snake_case）轉換為大駝峰命名（CamelCase）
        根據下劃線分割，然後將字串轉為第一個字母大寫後拼接
        :param name: 下劃線命名（snake_case）
        :return:
        """
        # 按下劃線分割字串
        words = name.split('_')
        # 將每個單詞的首字母大寫，然後拼接
        return ''.join(word.capitalize() for word in words)

    @staticmethod
    def generate_file_desc(filename: str, version: str = '1.0', desc: str = '') -> str:
        """
        生成檔案註釋
        :param filename:
        :param version:
        :param desc:
        :return:
        """
        code = '#!/usr/bin/python\n# -*- coding: utf-8 -*-'
        code += f"\n# @version        : {version}"
        code += f"\n# @Create Time    : {datetime.datetime.now().strftime('%Y/%m/%d %H:%M')}"
        code += f"\n# @File           : {filename}"
        code += f"\n# @IDE            : PyCharm"
        code += f"\n# @desc           : {desc}"
        code += f"\n"
        return code

    @staticmethod
    def generate_modules_code(modules: dict[str, list]) -> str:
        """
        生成模組導入程式碼
        :param modules: 導入得模組
        :return:
        """
        code = "\n"
        args = modules.pop("args", [])
        for k, v in modules.items():
            code += f"from {k} import {', '.join(v)}\n"
        if args:
            code += f"import {', '.join(args)}\n"
        return code

    @staticmethod
    def update_init_file(init_file: Path, code: str):
        """
        __init__ 檔案添加導入內容
        :param init_file:
        :param code:
        :return:
        """
        content = init_file.read_text()
        if content and code in content:
            return
        if content:
            if content.endswith("\n"):
                with init_file.open("a+", encoding="utf-8") as f:
                    f.write(f"{code}\n")
            else:
                with init_file.open("a+", encoding="utf-8") as f:
                    f.write(f"\n{code}\n")
        else:
            init_file.write_text(f"{code}\n", encoding="utf-8")

    @staticmethod
    def module_code_to_dict(code: str) -> dict:
        """
        將 from import 語句程式碼轉為 dict 格式
        :param code:
        :return:
        """
        # 分解程式碼為單行
        lines = code.strip().split('\n')

        # 初始化字典
        modules = {}

        # 遍歷每行程式碼
        for line in lines:
            # 處理 'from ... import ...' 型別的導入
            if line.startswith('from'):
                parts = line.split(' import ')
                module = parts[0][5:]  # 移除 'from ' 並獲取模組路徑
                imports = parts[1].split(',')  # 使用逗號分割導入項
                imports = [item.strip() for item in imports]  # 移除多餘空格
                if module in modules:
                    modules[module].extend(imports)
                else:
                    modules[module] = imports

            # 處理 'import ...' 型別的導入
            elif line.startswith('import'):
                imports = line.split('import ')[1]
                # 分割多個導入項
                imports = imports.split(', ')
                for imp in imports:
                    # 處理直接導入的模組
                    modules.setdefault('args', []).append(imp)
        return modules

    @classmethod
    def file_code_split_module(cls, file: Path) -> list:
        """
        檔案程式碼內容拆分，分為以下三部分
        1. 檔案開頭的註釋。
        2. 全局層面的 from import 語句。該程式碼格式會被轉換為 dict 格式
        3. 其他程式碼內容。
        :param file:
        :return:
        """
        content = file.read_text(encoding="utf-8")
        if not content:
            return []
        lines = content.split('\n')
        part1 = []  # 檔案開頭註釋
        part2 = []  # from import 語句
        part3 = []  # 其他程式碼內容

        # 標記是否已超過註釋部分
        past_comments = False

        for line in lines:
            # 檢查是否為註釋行
            if line.startswith("#") and not past_comments:
                part1.append(line)
            else:
                # 標記已超過註釋部分
                past_comments = True
                # 檢查是否為 from import 語句
                if line.startswith("from ") or line.startswith("import "):
                    part2.append(line)
                else:
                    part3.append(line)

        part2 = cls.module_code_to_dict('\n'.join(part2))

        return ['\n'.join(part1), part2, '\n'.join(part3)]

    @staticmethod
    def merge_dictionaries(dict1, dict2):
        """
        合併兩個鍵為字串、值為列表的字典
        :param dict1:
        :param dict2:
        :return:
        """
        # 初始化結果字典
        merged_dict = {}

        # 合併兩個字典中的鍵值對
        for key in set(dict1) | set(dict2):  # 獲取兩個字典的鍵的併集
            merged_dict[key] = list(set(dict1.get(key, []) + dict2.get(key, [])))

        return merged_dict


if __name__ == '__main__':
    _modules = {
        "sqlalchemy.ext.asyncio": ['AsyncSession'],
        "core.crud": ["DalBase"],
        ".": ["models", "schemas"],
        "args": ["test", "test1"]
    }
    print(GenerateBase.generate_modules_code(_modules))
