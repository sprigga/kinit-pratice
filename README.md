
## 🔗 子系統倉庫

- [📦 API 服務](https://github.com/saafu/bd-sales-oa-api)
- [🌐 前端 Web 系統](https://github.com/saafu/bd-sales-oa-web)
- [📋 任務排程模組](https://github.com/saafu/bd-sales-oa-task)
- [📱 手機 App 模組](https://github.com/saafu/bd-sales-oa-app)

---

> 此主倉庫僅作為子系統的總覽與開發文件導引，實際開發請至對應子倉庫操作。





GIT 改模組名稱
Git 子模組重命名 SOP

前提條件

將子模組名稱從：
	•	改成 api
	•	改成 web
	•	改成 task
	•	改成 uni
    
✅ 查詢目前追蹤中的 Git 子模組
cat .gitmodules

步驟 1：解除舊子模組的追蹤
git rm --cached tw_lottery-api
git rm --cached tw_lottery-web
git rm --cached tw_lottery-task
git rm --cached tw_lottery-uni


步驟 2：修改 .gitmodules 文件
[submodule "mes-api"]
    path = mes-api
    url = https://github.com/saafu/mes-api.git

[submodule "mes-web"]
    path = mes-web
    url = https://github.com/saafu/mes-web.git

[submodule "mes-task"]
    path = mes-task
    url = https://github.com/saafu/mes-task.git

[submodule "mes-uni"]
    path = mes-uni
    url = https://github.com/saafu/mes-uni.git



步驟 3：修改 .git/config 文件
[submodule "mes-api"]
    url = https://github.com/saafu/mes-api.git
    active = true
[submodule "mes-web"]
    url = https://github.com/saafu/mes-web.git
    active = true
[submodule "mes-task"]
    url = https://github.com/saafu/mes-task.git
    active = true
[submodule "mes-uni"]
    url = https://github.com/saafu/mes-uni.git
    active = true

步驟 4：重命名本地子模組資料夾
mv tw_lottery-api mes-api
mv tw_lottery-web mes-web
mv tw_lottery-task mes-task
mv tw_lottery-uni mes-uni


步驟 5：同步並初始化子模組
# 同步子模組設定
git submodule sync

# 重新初始化所有子模組
git submodule update --init --recursive


步驟 6：提交變更
git add .gitmodules .git/config mes-api mes-web mes-task mes-uni
git commit -m "Rename submodules to mes-api, mes-web, mes-task, and mes-uni"

步驟 7：確認結果
git submodule status









然後改GIT
步驟 1：更新主倉庫的遠端 URL
# 檢查當前遠端 URL
git remote -v

# 更新主倉庫的遠端 URL
git remote set-url origin https://github.com/saafu/mes.git

# 確認遠端 URL 是否已更新
git remote -v


步驟 3：更新 .gitmodules 文件
[submodule "mes-api"]
    path = mes-api
    url = https://github.com/saafu/mes-api.git

[submodule "mes-web"]
    path = mes-web
    url = https://github.com/saafu/mes-web.git

[submodule "mes-task"]
    path = mes-task
    url = https://github.com/saafu/mes-task.git

[submodule "mes-uni"]
    path = mes-uni
    url = https://github.com/saafu/mes-uni.git


步驟 4：同步子模組 URL 和目錄名稱
# 先清理舊的子模組
git submodule deinit -f .

# 同步子模組 URL
git submodule sync

# 重新初始化並更新子模組
git submodule update --init --recursive

# 確認子模組狀態
git submodule status

步驟 5：重新提交並推送變更
# 將修改後的 .gitmodules 和其他變更加入
git add .gitmodules

# 提交更新
git commit -m "Update submodule URLs and rename directories"

# 推送到遠端主倉庫
git push origin main



























管理员账户：

- 账号：15020221010
- 密码：kinit2022

测试账户：

- 账号：15020240125
- 密码：test

## 接口 CURD 代码自動生成

1. 目前只支持生成接口代码
2. 目前只支持使用脚本方式运行，后续会更新到頁面操作
3. 代码是根据手動配置的 ORM 模型来生成的，支持参数同步，比如默认值，是否为空...

脚本文件地址：`scripts/crud_generate/main.py`



該功能首先需要手動创建出 ORM 模型，然后会根据 ORM 模型依次创建代码，包括如下代码：

1. schema 序列化代码

   schema 文件名称会使用设置的 en_name 名称，如果文件已经存在会先执行删除，再创建。

   schema 代码内容生成完成后，同时会将新创建的 class 在 `__init__.py` 文件中导入。

2. dal 数据操作代码

   dal 文件名称会使用默认的 `crud.py` 文件名称，目前不支持自定义。

   如果 dal 文件已经存在，并且已经有代码内容，那么会将新的模型 dal class 追加到文件最后，并会合并文件内导入的 module。

3. param 请求参数代码

   param 文件名取名方式与 schema 一致。

   会创建出默认最简的 param class。

4. view 视图代码

   view 文件名称同样会使用默认的 `view.py` 文件名称，目前不支持自定义。

   如果 view 文件已经存在，与 dal 执行操作一致。



脚本中目前有两个方法：

```python
if __name__ == '__main__':
    from apps.vadmin.auth.models import VadminUser

    crud = CrudGenerate(VadminUser, "用户", "user")
    # 只打印代码，不执行创建写入
    crud.generate_codes()
    # 创建并写入代码
    crud.main()
```

目前不会去检测已有的代码，比如 `UserDal` 已经存在，还是会继续添加的。

B站 视频演示：https://www.bilibili.com/video/BV19e411a7zP/

## 源码地址

gitee地址(主推)：https://gitee.com/ktianc/kinit

github地址：https://github.com/vvandk/kinit

## PC端内置功能

- [x] 菜单管理：配置系统菜单，操作權限，按钮權限标识、后端接口權限等。

- [x] 部门管理：支持无限层级部门配置。

- [x] 角色管理：角色菜单權限，角色部门權限分配。

- [x] 用户管理：用户是系统操作者，該功能主要完成系统用户配置。

- [x] 个人主頁：配置用户个人信息，密码修改等。

- [x] 字典管理：对系统中经常使用的一些较为固定的数据進行维护。

- [x] 文件上传：对接阿里云OSS与本地存储。

- [x] 登录认证：目前支持用户使用手机号+密码登录方式，手机验证码登录方式。

  说明：新建用户密码默认为手机号后六位；

  说明：用户在第一次登录时，必须修改当前用户密码。

- [x] 系统配置：对本系统环境信息進行動態配置

  网站标题，LOGO，描述，ICO，备案号，底部内容，微信小程序信息，等等

- [x] 用户分布：接入高德地图显示各地区用户分布情况

- [x] 数据概览：提供两种数据统计展示模板，更直观的查看数据统计情况

- [x] 智慧大屏：大屏展示`办公室空气质量实时检测`数据分析

- [x] 登录日志：用户登录日志记录和查询。

- [x] 操作日志：系统用户每次操作功能时的详细记录。

- [x] 接口文檔：提供自動生成的交互式 API 文檔，与 ReDoc 文檔

- [x] 导入导出：灵活支持数据导入导出功能

- [x] 已加入常见的`Redis`、`MySQL`、`MongoDB`数据库异步操作。

- [x] 命令行操作：新加入 `Typer` 命令行应用，简单化数据初始化，数据表模型迁移。

- [x] 定时任务：在线操作（添加、修改、删除)任务调度包含查看任务执行结果日志。

## 移動端内置功能

- [x] 登录认证：支持用户使用手机号+密码方式登录，微信手机号一键登录方式。

  说明：新建用户密码默认为手机号后六位；

  说明：用户在第一次登录时，必须修改当前用户密码。

- [x] 导航栏：首頁、我的、工作台

- [x] 我的基础功能：编辑资料、头像修改、密码修改、常见问题、关于我们等

##  前序准备

### 后端技术

- [Python3](https://www.python.org/downloads/windows/)：熟悉 python3 基础语法
- [FastAPI](https://fastapi.tiangolo.com/zh/) - 熟悉后台接口 Web 框架
- [SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/index.html) - 数据数据库操作
- [Typer](https://typer.tiangolo.com/) - 熟悉命令行工具的使用
- [MySQL](https://www.mysql.com/) 和 [MongoDB](https://www.mongodb.com/) 和 [Redis](https://redis.io/)  - 熟悉数据存储数据库
- [iP查询接口文檔](https://user.ip138.com/ip/doc)：IP查询第三方服务，有1000次的免费次数

### PC端

- [node](https://gitee.com/link?target=http%3A%2F%2Fnodejs.org%2F) 和 [git](https://gitee.com/link?target=https%3A%2F%2Fgit-scm.com%2F) - 项目开发环境
- [Vite](https://gitee.com/link?target=https%3A%2F%2Fvitejs.dev%2F) - 熟悉 vite 特性
- [Vue3](https://gitee.com/link?target=https%3A%2F%2Fv3.vuejs.org%2F) - 熟悉 Vue 基础语法
- [TypeScript](https://gitee.com/link?target=https%3A%2F%2Fwww.typescriptlang.org%2F) - 熟悉 `TypeScript` 基本语法
- [Es6+](https://gitee.com/link?target=http%3A%2F%2Fes6.ruanyifeng.com%2F) - 熟悉 es6 基本语法
- [Vue-Router-Next](https://gitee.com/link?target=https%3A%2F%2Fnext.router.vuejs.org%2F) - 熟悉 vue-router 基本使用
- [Element-Plus](https://gitee.com/link?target=https%3A%2F%2Felement-plus.org%2F) - element-plus 基本使用
- [vue3-json-viewer](https://gitee.com/isfive/vue3-json-viewer)：简单易用的json内容展示组件,适配vue3和vite。
- [高德地图API (amap.com)](https://lbs.amap.com/api/jsapi-v2/guide/webcli/map-vue1)：地图 JSAPI 2.0 是高德开放平台免费提供的第四代 Web 地图渲染引擎。

### 移動端

- [uni-app](https://uniapp.dcloud.net.cn/component/) - 熟悉 uni-app 基本语法
- [Vue2](https://v2.cn.vuejs.org/v2/guide/) - 熟悉 Vue 基础语法
- [uView UI 2](https://www.uviewui.com/components/intro.html)：uView UI 组件的基本使用
- [uni-read-pages](https://github.com/SilurianYang/uni-read-pages) ：自動读取 `pages.json` 所有配置。
- [uni-simple-router](https://hhyang.cn/v2/start/quickstart.html) ：在uni-app中使用vue-router的方式進行跳转路由，路由拦截。

### 定时任务

- [Python3](https://www.python.org/downloads/windows/) -熟悉 python3 基础语法
- [APScheduler](https://github.com/agronholm/apscheduler) - 熟悉定时任务框架
- [MongoDB](https://www.mongodb.com/) 和 [Redis](https://redis.io/)  - 熟悉数据存储数据库

## 安装和使用

获取代码

```
git clone https://gitee.com/ktianc/kinit.git
```

### 准备工作

```
Python == 3.10 (其他版本均未测试)
nodejs >= 14.0 (推荐使用最新稳定版)
Mysql >= 8.0
MongoDB (推荐使用最新稳定版)
Redis (推荐使用最新稳定版)
```

### 后端

1. 安装依赖

   ```
   cd kinit-api
   
   pip3 install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
   ```

2. 修改项目环境配置

   修改 `application/settings.py` 文件

   ```python
   # 安全警告: 不要在生产中打开调试运行!
   DEBUG = True # 如果当前为开发环境则改为 True，如果为生产环境则改为 False
   ```

3. 修改项目数据库配置信息

   在 `application/config` 目录中

   - development.py：开发环境

   - production.py：生产环境

   ```python
   # Mysql 数据库配置项
   # 连接引擎官方文檔：https://www.osgeo.cn/sqlalchemy/core/engines.html
   # 数据库链接配置说明：mysql+asyncmy://数据库用户名:数据库密码@数据库地址:数据库端口/数据库名称
   
   SQLALCHEMY_DATABASE_URL = "mysql+asyncmy://数据库用户名:数据库密码@数据库地址:数据库端口/数据库名称"
   SQLALCHEMY_DATABASE_TYPE = "mysql"
   
   
   # Redis 数据库配置
   REDIS_DB_ENABLE = True
   REDIS_DB_URL = "redis://:密码@地址:端口/数据库"
   
   # MongoDB 数据库配置
   MONGO_DB_ENABLE = True
   MONGO_DB_NAME = "数据库名称"
   MONGO_DB_URL = f"mongodb://用户名:密码@地址:端口/?authSource={MONGO_DB_NAME}"
   
   # 阿里云对象存储OSS配置
   # 阿里云账号AccessKey拥有所有API的访问權限，风险很高。强烈建议您创建并使用RAM用户進行API访问或日常运维，请登录RAM控制台创建RAM用户。
   # yourEndpoint填写Bucket所在地域对应的Endpoint。以华东1（杭州）为例，
   # Endpoint填写为https://oss-cn-hangzhou.aliyuncs.com。
   #  *  [accessKeyId] {String}：通过阿里云控制台创建的AccessKey。
   #  *  [accessKeySecret] {String}：通过阿里云控制台创建的AccessSecret。
   #  *  [bucket] {String}：通过控制台或PutBucket创建的bucket。
   #  *  [endpoint] {String}：bucket所在的区域， 默认oss-cn-hangzhou。
   ALIYUN_OSS = {
       "accessKeyId": "accessKeyId",
       "accessKeySecret": "accessKeySecret",
       "endpoint": "endpoint",
       "bucket": "bucket",
       "baseUrl": "baseUrl"
   }
   
   # 获取IP地址归属地
   # 文檔：https://user.ip138.com/ip/doc
   IP_PARSE_ENABLE = True
   IP_PARSE_TOKEN = "IP_PARSE_TOKEN"
   ```

4. 并在`alembic.ini`文件中配置数据库信息，用于数据库映射

   ```python
   # mysql+pymysql://数据库用户名:数据库密码@数据库地址:数据库端口/数据库名称
   
   [dev]
   # 开发环境
   version_locations = %(here)s/alembic/versions_dev
   sqlalchemy.url = mysql+pymysql://root:123456@127.0.0.1/kinit
   
   
   [pro]
   # 生产环境
   version_locations = %(here)s/alembic/versions_pro
   sqlalchemy.url = mysql+pymysql://root:123456@127.0.0.1/kinit
   ```

5. 创建数据库

   ```
   mysql> create database kinit;             # 创建数据库
   mysql> use kinit;                         # 使用已创建的数据库 
   mysql> set names utf8;                    # 设置编码
   ```

6. 初始化数据库数据

   ```python
   # 项目根目录下执行，需提前创建好数据库
   # 会自動将模型迁移到数据库，并生成初始化数据
   # 执行前请确认执行的环境与settings.py文件中配置的DEBUG一致
   
   # （生产环境）
   python3 main.py init
   
   # （开发环境）
   python3 main.py init --env dev
   ```

7. 修改项目基本配置信息

   修改数据库表 - vadmin_system_settings 中的关键信息

   ```
   # 阿里云短信配置
   sms_access_key
   sms_access_key_secret
   sms_sign_name_1
   sms_template_code_1
   sms_sign_name_2
   sms_template_code_2
   
   # 高德地图配置
   map_key
   
   # 微信小程序配置
   wx_server_app_id
   wx_server_app_secret
   
   # 邮箱配置
   email_access
   email_password
   email_server
   email_port
   ```

8. 启動

   ```
   # 進入项目根目录下执行
   python3 main.py run
   ```

### PC端

1. 安装依赖

```
cd kinit-admin

pnpm install
```

2. 运行

```
pnpm run dev
```

3. 打包

```
pnpm run build:pro
```

### 定时任务

1. 安装依赖

   ```
   # 安装依赖库
   pip3 install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
   
   # 第三方源：
   1. 阿里源： https://mirrors.aliyun.com/pypi/simple/
   ```

2. 修改项目数据库配置信息

   在 `application/config` 目录中

   - development.py：开发环境

   - production.py：生产环境

   ```python
   # MongoDB 数据库配置
   # 与接口是同一个数据库
   MONGO_DB_NAME = "数据库名称"
   MONGO_DB_URL = f"mongodb://用户名:密码@地址:端口/?authSource={MONGO_DB_NAME}"
   
   
   # Redis 数据库配置
   # 与接口是同一个数据库
   REDIS_DB_URL = "redis://:密码@地址:端口/数据库名称"
   ```
   
3. 启動

   ```
   python3 main.py
   ```


### 访问项目

- 访问地址：http://localhost:5000 (默认为此地址，如有修改请按照配置文件)
- 账号：`15020221010` 密码：`kinit2022`
- 接口地址：http://localhost:9000/docs (默认为此地址，如有修改请按照配置文件)

## Docker Compose 生产环境部署

### 准备工作

1. 获取代码

   ```
   git clone https://gitee.com/ktianc/kinit.git
   ```

2. 修改项目环境配置：

   1. 修改 API 端：

      文件路径为：`kinit-api/application/settings.py`

      ```python
      # 安全警告: 不要在生产中打开调试运行!
      DEBUG = False # 生产环境应該改为 False
      ```

   2. 修改定时任务端：

      文件路径为：`kinit-task/application/settings.py`

      ```python
      # 安全警告: 不要在生产中打开调试运行!
      DEBUG = False # 生产环境应該改为 False
      ```

3. （**如果没有安装数据库则不需要这一操作**）如果已有 Mysql 或者 Redis 或者 MongoDB 数据库，请执行以下操作：

   请先在对应数据库中创建用户名以及数据库，并修改以下数据库连接改为已有的数据库连接

   1. 修改 API 端配置文件：

      文件路径为：`kinit-api/application/config/production.py`

      ```python
      # Mysql 数据库配置项
      # 连接引擎官方文檔：https://www.osgeo.cn/sqlalchemy/core/engines.html
      # 数据库连接配置说明：mysql+asyncmy://数据库用户名:数据库密码@数据库地址:数据库端口/数据库名称
      SQLALCHEMY_DATABASE_URL = "mysql+asyncmy://root:123456@157.8.0.7:3306/kinit"
      
      # Redis 数据库配置
      # 格式："redis://:密码@地址:端口/数据库名称"
      REDIS_DB_ENABLE = True
      REDIS_DB_URL = "redis://:123456@157.8.0.5:6379/1"
      
      # MongoDB 数据库配置
      # 格式：mongodb://用户名:密码@地址:端口/?authSource=数据库名称
      MONGO_DB_ENABLE = True
      MONGO_DB_NAME = "kinit"
      MONGO_DB_URL = f"mongodb://kinit:123456@157.8.0.6:27017/?authSource={MONGO_DB_NAME}"
      ```
      
   2. 修改定时任务配置文件

      文件路径为：`kinit-task/application/config/production.py`

      ```python
      # Redis 数据库配置
      # 与接口是同一个数据库
      # 格式："redis://:密码@地址:端口/数据库名称"
      REDIS_DB_ENABLE = True
      REDIS_DB_URL = "redis://:123456@157.8.0.5:6379/1"
      
      # MongoDB 数据库配置
      # 与接口是同一个数据库
      # 格式：mongodb://用户名:密码@地址:端口/?authSource=数据库名称
      MONGO_DB_ENABLE = True
      MONGO_DB_NAME = "kinit"
      MONGO_DB_URL = f"mongodb://kinit:123456@157.8.0.6:27017/?authSource={MONGO_DB_NAME}"
      ```
      
   3. 将已有的数据库在 `docker-compose.yml` 文件中注释

4. 配置阿里云 OSS 与 IP 解析接口地址（可选）

   文件路径：`kinit-api/application/config/production.py`

   ```python
   # 阿里云对象存储OSS配置
   # 阿里云账号AccessKey拥有所有API的访问權限，风险很高。强烈建议您创建并使用RAM用户進行API访问或日常运维，请登录RAM控制台创建RAM用户。
   # yourEndpoint填写Bucket所在地域对应的Endpoint。以华东1（杭州）为例，
   # Endpoint填写为https://oss-cn-hangzhou.aliyuncs.com。
   #  *  [accessKeyId] {String}：通过阿里云控制台创建的AccessKey。
   #  *  [accessKeySecret] {String}：通过阿里云控制台创建的AccessSecret。
   #  *  [bucket] {String}：通过控制台或PutBucket创建的bucket。
   #  *  [endpoint] {String}：bucket所在的区域， 默认oss-cn-hangzhou。
   ALIYUN_OSS = {
       "accessKeyId": "accessKeyId",
       "accessKeySecret": "accessKeySecret",
       "endpoint": "endpoint",
       "bucket": "bucket",
       "baseUrl": "baseUrl"
   }
   
   # 获取IP地址归属地
   # 文檔：https://user.ip138.com/ip/doc
   IP_PARSE_ENABLE = False
   IP_PARSE_TOKEN = "IP_PARSE_TOKEN"
   ```

5. 前端项目打包：

   ```shell
   cd kinit-admin
   
   # 安装依赖包
   pnpm install
   
   # 打包
   pnpm run build:pro
   ```

### 启動并初始化项目

```shell
# 启動并创建所有容器
docker-compose up -d

# 初始化数据
docker-compose exec kinit-api python3 main.py init

# 重启所有容器
docker-compose restart


# 其他命令：

# 停止所有容器
docker-compose down

# 查看所有容器状態
docker-compose ps -a
```

### 访问项目

- 访问地址：http://localhost (默认为此地址，如有修改请按照配置文件)
- 账号：`15020221010` 密码：`kinit2022`
- 接口地址：http://localhost:9000/docs (默认为此地址，如有修改请按照配置文件)

## 如何贡献

你可以[提一个 issue](https://gitee.com/link?target=https%3A%2F%2Fgithub.com%2Fkailong321200875%2Fvue-element-plus-admin%2Fissues%2Fnew) 或者提交一个 Pull Request。

**Pull Request:**

1. Fork 代码
2. 创建自己的分支: `git checkout -b feat/xxxx`
3. 提交你的修改: `git commit -am 'feat(function): add xxxxx'`
4. 推送您的分支: `git push origin feat/xxxx`
5. 提交 `pull request`

## 浏览器支持

本地开发推荐使用 `Chrome 80+` 浏览器

支持现代浏览器, 不支持 IE

| IE          | Edge            | Firefox         | Chrome          | Safari          |
| ----------- | --------------- | --------------- | --------------- | --------------- |
| not support | last 2 versions | last 2 versions | last 2 versions | last 2 versions |

## 许可证

[MIT](https://gitee.com/kailong110120130/vue-element-plus-admin/blob/master/LICENSE)

## PC端演示图

![image-20221010214526082](https://k-typora.oss-cn-beijing.aliyuncs.com/kinit/1687232679892.jpg)

![image-20221010214526082](https://ktianc.oss-cn-beijing.aliyuncs.com/resource/images/1695373476/1695373476b028a6f9.jpg)

![image-20221010214526082](https://ktianc.oss-cn-beijing.aliyuncs.com/resource/images/1695373476/16953734768af98563.jpg)

![image-20221010214526082](https://ktianc.oss-cn-beijing.aliyuncs.com/resource/images/1695373476/169537347630c0e225.jpg)

![image-20221010214526082](https://ktianc.oss-cn-beijing.aliyuncs.com/resource/images/1695373476/1695373476da1a414f.jpg)

![1688392266702](https://ktianc.oss-cn-beijing.aliyuncs.com/resource/images/1695373475/1695373475fca1d7b8.jpg)

![image-20221010214526082](https://ktianc.oss-cn-beijing.aliyuncs.com/resource/images/1695373475/16953734756617d25d.jpg)

![image-20221010214526082](https://ktianc.oss-cn-beijing.aliyuncs.com/resource/images/1695373477/169537347735257fe5.jpg)

![image-20221010214526082](https://ktianc.oss-cn-beijing.aliyuncs.com/resource/images/1695373478/1695373478511f21e3.jpg)

![image-20221010214526082](https://ktianc.oss-cn-beijing.aliyuncs.com/resource/images/1695373477/16953734770decc360.jpg)

![image-20221010214526082](https://ktianc.oss-cn-beijing.aliyuncs.com/resource/images/1695373477/169537347735257fe5.jpg)

![image-20221010214526082](https://k-typora.oss-cn-beijing.aliyuncs.com/kinit/1687233000595-10.jpg)

## 另一种布局演示图

图1

![image-20221010214526082](https://ktianc.oss-cn-beijing.aliyuncs.com/resource/images/1695375057/1695375057ebef7bd9.jpg)





图2

![image-20221010214526082](https://ktianc.oss-cn-beijing.aliyuncs.com/resource/images/1695375057/1695375057abf3dcf6.jpg)





图3

![image-20221010214526082](https://ktianc.oss-cn-beijing.aliyuncs.com/resource/images/1695375057/16953750571f2f9f7e.jpg)





图4

![image-20221010214526082](https://ktianc.oss-cn-beijing.aliyuncs.com/resource/images/1695375058/1695375058542fcf76.jpg)



## 微信小程序端演示图

<table>
    <tr>
        <td><img src="https://k-typora.oss-cn-beijing.aliyuncs.com/kinit/1670077811740.jpg"/></td>
        <td><img src="https://k-typora.oss-cn-beijing.aliyuncs.com/kinit/1670077826257.jpg"/></td>
		<td><img src="https://k-typora.oss-cn-beijing.aliyuncs.com/kinit/1670077835024.jpg"/></td>
    </tr>
	<tr>
        <td><img src="https://k-typora.oss-cn-beijing.aliyuncs.com/kinit/1670077849753.jpg"/></td>
        <td><img src="https://k-typora.oss-cn-beijing.aliyuncs.com/kinit/1670077860987.jpg"/></td>
		<td><img src="https://k-typora.oss-cn-beijing.aliyuncs.com/kinit/1670077870240.jpg"/></td>
    </tr>
</table>
