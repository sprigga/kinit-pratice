# 使用 Python 3.10 作為基礎鏡像
FROM python:3.10

# 設定工作目錄
WORKDIR /app

# 複製 requirements.txt 並安裝依賴
COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

# 複製應用的源碼到容器內
COPY . /app

# 如果在 requirements.txt 中沒有 uvicorn，可以手動安裝
RUN pip install uvicorn

# 讓容器能夠聽取 8080 端口
EXPOSE 8080

# 預設命令使用 Python 執行 main.py 並執行 run 參數
CMD ["python", "main.py", "run"]