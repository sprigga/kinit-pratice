

# DB要記得先清空
rm -rf ./docker_env/mysql/data

-- 建立新使用者，允許從任何 IP 連線（可改 '%' 為指定 IP）
CREATE USER 'oa-admin'@'%' IDENTIFIED BY 'Bdfrost168';

-- 給予所有資料庫權限（你可調整為特定 DB）
GRANT ALL PRIVILEGES ON *.* TO 'oa-admin'@'%' WITH GRANT OPTION;

-- 套用變更
FLUSH PRIVILEGES;


# 設定alembuc.ini db資訊


### 數據初始化

```shell
# 項目根目錄下执行，需提前創建好數據庫，並且數據庫应該為空
# 會自動将模型迁移到數據庫，並生成初始化數據

# 在执行前一定要确认要操作的环境与application/settings.DEBUG 设置的环境是一致的，
# 不然會导致創建表和生成數據不在一个數據庫中！！！！！！！！！！！！！！！！！！！！！！

# 比如要初始化开发环境，那么env参數应該為 dev，並且 application/settings.DEBUG 应該 = True
# 比如要初始化生產环境，那么env参數应該為 pro，並且 application/settings.DEBUG 应該 = False

# 生產环境
python main.py init

# 开发环境
python main.py init --env dev
```

### 运行启動

```shell
# 直接运行main文件
python main.py run
```

### 建立新項目
1.先創建apps 下方新增主模組資料夾 模組資料夾盡量使用微服務概念名字不要有_
2.主模組下建立功能模組模快資料夾
3.子模組下新增models 資料夾
4.建立模型
5.almebic env.py 下引入模型路徑
6.python main.py migrate --env dev 新增資料表
7.執行項目生成 python3 main.py MesWoWo 日報管理
會自動產出 VUE 前端API 與LIST頁面 編輯頁面


PS 取名注意是 主系統/子模組/功能模組 不要有_ 會被分割路徑

















## 項目结构

使用的是仿照 Django 項目结构：

- alembic：數據庫迁移配置目錄
  - versions_dev：开发环境數據庫迁移文件目錄
  - versions_pro：生產环境數據庫迁移文件目錄
  - env.py：映射类配置文件
- application：主項目配置目錄，也存放了主路由文件
  - config：基礎环境配置文件
    - development.py：开发环境
    - production.py：生產环境
  - settings.py：主項目配置文件
  - urls.py：主路由文件
- apps：項目的app存放目錄
  - vadmin：基礎服務
    - auth：用户 - 角色 - 選單接口服務
      - models：ORM 模型目錄
      - params：查詢参數依赖項目錄
      - schemas：pydantic 模型，用于數據庫序列化操作目錄
      - utils：登錄認證功能接口服務
      - curd.py：數據庫操作
      - views.py：视圖函數
- core：核心文件目錄
  - crud.py：關係型數據庫操作核心封装
  - database.py：關係型數據庫核心配置
  - data_types.py：自定义數據類型
  - exception.py：异常处理
  - logger：日誌处理核心配置
  - middleware.py：中間件核心配置
  - dependencies.py：常用依赖項
  - event.py：全局事件
  - mongo_manage.py：mongodb 數據庫操作核心封装
  - validator.py：pydantic 模型重用驗證器
- db：ORM模型基类
- logs：日誌目錄
- static：静態资源存放目錄
- utils：封装的一些工具类目錄
- main.py：主程序入口文件
- alembic.ini：數據庫迁移配置文件

## 开发环境

开发语言：Python 3.10

开发框架：Fastapi 0.101.1

ORM 框架：SQLAlchemy 2.0.20

## 开发工具

Pycharm 2022.3.2

推荐插件：Chinese (Simplified) Language Pack / 中文语言包

代碼樣式配置：

![image-20230315194534959](https://ktianc.oss-cn-beijing.aliyuncs.com/kinit/public/images/image-20230315194534959.png)

## 使用

```
source /opt/env/kinit-pro/bin/activate

# 安装依赖庫
pip3 install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# 第三方源：

1. 阿里源： https://mirrors.aliyun.com/pypi/simple/

# 线上安装更新依赖庫
/opt/env/kinit-pro-310/bin/pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
```


## 其他操作

在线文檔地址(在配置文件里面设置路径或者关闭)

```
http://127.0.0.1:9000/docs
```

Git更新ignore文件直接修改gitignore是不會生效的，需要先去掉已經托管的文件，修改完成之后再重新添加並提交。
```
第一步：
git rm -r --cached .
去掉已經托管的文件

第二步：
修改自己的igonre文件内容

第三步：
git add .
git commit -m "clear cached"
```

执行數據庫迁移命令（终端执行）

```shell
# 执行命令（生產环境）：
python main.py migrate

# 执行命令（开发环境）
# 需要手動把要新增遷移的表加入env.py文件中的target_metadata中
# 
#：
python main.py migrate --env dev

# 开发环境的原命令
alembic --name dev revision --autogenerate -m 2.0
alembic --name dev upgrade head
```

生成迁移文件后，會在alembic迁移目錄中的version目錄中多个迁移文件

## 查詢數據

### 自定义的一些查詢過滤

```python
# 日期查詢
# 值的類型：str
# 值得格式：%Y-%m-%d：2023-05-14
字段名稱=("date", 值)

# 模糊查詢
# 值的類型: str
字段名稱=("like", 值)

# in 查詢
# 值的類型：list
字段名稱=("in", 值)

# 時間区間查詢
# 值的類型：tuple 或者 list
字段名稱=("between", 值)

# 月份查詢
# 值的類型：str
# 值的格式：%Y-%m：2023-05
字段名稱=("month", 值)

# 不等于查詢
字段名稱=("!=", 值)

# 大于查詢
字段名稱=(">", 值)

# 等于 None
字段名稱=("None")

# 不等于 None
字段名稱=("not None")
```

代碼部分：

```python
def __dict_filter(self, **kwargs) -> list[BinaryExpression]:
    """
    字典過滤
    :param model:
    :param kwargs:
    """
    conditions = []
    for field, value in kwargs.items():
        if value is not None and value != "":
            attr = getattr(self.model, field)
            if isinstance(value, tuple):
                if len(value) == 1:
                    if value[0] == "None":
                        conditions.append(attr.is_(None))
                    elif value[0] == "not None":
                        conditions.append(attr.isnot(None))
                    else:
                        raise CustomException("SQL查詢语法錯误")
                elif len(value) == 2 and value[1] not in [None, [], ""]:
                    if value[0] == "date":
                        # 根據日期查詢， 关键函數是：func.time_format和func.date_format
                        conditions.append(func.date_format(attr, "%Y-%m-%d") == value[1])
                    elif value[0] == "like":
                        conditions.append(attr.like(f"%{value[1]}%"))
                    elif value[0] == "in":
                        conditions.append(attr.in_(value[1]))
                    elif value[0] == "between" and len(value[1]) == 2:
                        conditions.append(attr.between(value[1][0], value[1][1]))
                    elif value[0] == "month":
                        conditions.append(func.date_format(attr, "%Y-%m") == value[1])
                    elif value[0] == "!=":
                        conditions.append(attr != value[1])
                    elif value[0] == ">":
                        conditions.append(attr > value[1])
                    elif value[0] == "<=":
                        conditions.append(attr <= value[1])
                    else:
                        raise CustomException("SQL查詢语法錯误")
            else:
                conditions.append(attr == value)
    return conditions
```

示例：

查詢所有用户id為1或2或 4或6，並且email不為空，並且名稱包括李：

```python
users = UserDal(db).get_datas(limit=0, id=("in", [1,2,4,6]), email=("not None", ), name=("like", "李"))

# limit=0：表示返回所有结果數據
# 这里的 get_datas 默认返回的是 pydantic 模型數據
# 如果需要返回用户對象列表，使用如下语句：
users = UserDal(db).get_datas(
    limit=0,
    id=("in", [1,2,4,6]),
    email=("not None", ),
    name=("like", "李"),
    v_return_objs=True
)
```

查詢所有用户id為1或2或 4或6，並且email不為空，並且名稱包括李：

查詢第一頁，每頁两條數據，並返回总數，同樣可以通過 `get_datas` 实现原始查詢方式：

```python
v_where = [VadminUser.id.in_([1,2,4,6]), VadminUser.email.isnot(None), VadminUser.name.like(f"%李%")]
users, count = UserDal(db).get_datas(limit=2, v_where=v_where, v_return_count=True)

# 这里的 get_datas 默认返回的是 pydantic 模型數據
# 如果需要返回用户對象列表，使用如下语句：
users, count = UserDal(db).get_datas(
    limit=2,
    v_where=v_where,
    v_return_count=True
    v_return_objs=True
)
```

### 外键查詢示例

以常见問题表為主表，查詢出創建用户名稱為kinit的用户，創建了哪些常见問题，並加載出用户信息：

```python
v_options = [joinedload(VadminIssue.create_user)]
v_join = [["create_user"]]
v_where = [VadminUser.name == "kinit"]
datas = await crud.IssueCategoryDal(auth.db).get_datas(
    limit=0,
    v_options=options,
    v_join=v_join,
    v_where=v_where,
    v_return_objs=True
)
```

### GCP指令
查看GCP LOG
gcloud logging read 'resource.type="cloud_run_revision" AND resource.labels.service_name="k-boss-api" AND resource.labels.location="asia-east1"' --limit=20 --format="table(timestamp, textPayload)"

查看GCP 所有專案
gcloud run services list --region=asia-east1


