# 使用 Python 3.10 作為基礎鏡像
FROM python:3.10

# 設定工作目錄
WORKDIR /app

# 複製 requirements.txt 並安裝依賴
COPY ./api/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# 複製完整 api 資料夾到 /app/api
COPY ./api /app

# 如果在 requirements.txt 中沒有 uvicorn，可以手動安裝
RUN pip install uvicorn

# 讓容器能夠聽取 8000 端口
EXPOSE 8000

# 預設命令使用 Python 執行 main.py 並執行 run 參數
CMD ["python", "main.py", "run"]