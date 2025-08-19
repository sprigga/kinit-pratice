class UrlsGenerate:
    """
    自動生成路由代碼
    """
    def __init__(self, model, zh_name, en_name):
        self.model = model
        self.zh_name = zh_name
        self.en_name = en_name
        self.router_name = f"{self.en_name}_app"

    def generate_code(self) -> str:
        """
        生成 FastAPI 路由註冊代碼
        """
        route_path = self.en_name.replace("_", "-")
        return f'    {{"ApiRouter": {self.router_name}, "prefix": "/{route_path}", "tags": ["{self.zh_name}"]}},\n'