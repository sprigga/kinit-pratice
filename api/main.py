# -*- coding: utf-8 -*-
# @version        : 1.0
# @Create Time    : 2021/10/19 15:47
# @File           : main.py
# @IDE            : PyCharm
# @desc           : 主程序入口

"""
FastApi 更新文檔：https://github.com/tiangolo/fastapi/releases
FastApi Github：https://github.com/tiangolo/fastapi
Typer 官方文檔：https://typer.tiangolo.com/
"""
import os

from fastapi import FastAPI
import uvicorn
from starlette.middleware.cors import CORSMiddleware
from application import settings
from application import urls
from application.settings import SERVER_PORT, SERVER_TITLE, SERVER_DESCRIPTION
from starlette.staticfiles import StaticFiles  # 依赖安装：pip install aiofiles
from core.docs import custom_api_docs
from core.exception import register_exception
import typer
from scripts.initialize.initialize import InitializeData, Environment
import asyncio
from scripts.create_app.main import CreateApp
from core.event import lifespan
from utils.tools import import_modules

shell_app = typer.Typer()


def create_app():
    """
    启動項目

    docs_url：配置交互文檔的路由地址，如果禁用则為None，默认為 /docs
    redoc_url： 配置 Redoc 文檔的路由地址，如果禁用则為None，默认為 /redoc
    openapi_url：配置接口文件json數據文件路由地址，如果禁用则為None，默认為/openapi.json
    """
    app = FastAPI(
        title=SERVER_TITLE,
        description=SERVER_DESCRIPTION,
        version=settings.VERSION,
        lifespan=lifespan,
        docs_url=None,
        redoc_url=None
    )

    # 健康檢查端點
    @app.get("/")
    def health_check():
        return {"status": "ok", "message": "is running"}

    import_modules(settings.MIDDLEWARES, "中間件", app=app)
    # 全局异常捕捉处理
    register_exception(app)
    # 跨域解决
    if settings.CORS_ORIGIN_ENABLE:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.ALLOW_ORIGINS,
            allow_credentials=settings.ALLOW_CREDENTIALS,
            allow_methods=settings.ALLOW_METHODS,
            allow_headers=settings.ALLOW_HEADERS
        )
    # 挂在静態目錄
    if settings.STATIC_ENABLE:
        app.mount(settings.STATIC_URL, app=StaticFiles(directory=settings.STATIC_ROOT))
    # 引入应用中的路由
    for url in urls.urlpatterns:
        app.include_router(url["ApiRouter"], prefix=url["prefix"], tags=url["tags"])
    # 配置接口文檔静態资源
    custom_api_docs(app)
    return app

@shell_app.command()
def run(
        host: str = typer.Option(default='0.0.0.0', help='監聽主機IP，默認開放给本網路所有主機'),
        port: int = typer.Option(os.environ.get("PORT", SERVER_PORT), help='監聽端口')
):
    """
    启動項目

    factory: 在使用 uvicorn.run() 启動 ASGI 应用程序時，可以通過设置 factory 参數来指定应用程序工厂。
    应用程序工厂是一个返回 ASGI 应用程序实例的可調用對象，它可以在启動時動態創建应用程序实例。
    """
    uvicorn.run(app='main:create_app', host=host, port=port, lifespan="on", factory=True)


@shell_app.command()
def init(env: Environment = Environment.pro):
    """
    初始化數據

    在执行前一定要确认要操作的环境与application/settings.DEBUG 设置的环境是一致的，
    不然會导致創建表和生成數據不在一个數據庫中！！！！！！！！！！！！！！！！！！！！！！

    比如要初始化开发环境，那么env参數应該為 dev，並且 application/settings.DEBUG 应該 = True
    比如要初始化生產环境，那么env参數应該為 pro，並且 application/settings.DEBUG 应該 = False

    :param env: 數據庫环境
    """
    print("開始初始化數據")
    data = InitializeData()
    asyncio.run(data.run(env))


@shell_app.command()
def migrate(env: Environment = Environment.pro):
    """
    将模型迁移到數據庫，更新數據庫表结构

    :param env: 數據庫环境
    """
    print("開始更新數據庫表")
    InitializeData.migrate_model(env)


@shell_app.command()
def init_app(path: str):
    """
    自動創建初始化 APP 结构

    命令例子：python main.py init-app vadmin/test

    :param path: app 路径，根目錄為apps，填写apps后面路径即可，例子：vadmin/auth
    """
    print(f"開始創建並初始化 {path} APP")
    app = CreateApp(path)
    app.run()


if __name__ == '__main__':
    shell_app()
