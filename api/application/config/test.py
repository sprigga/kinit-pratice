from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import urllib.parse

# 假設 MongoDB 用戶名是 'afu'，密碼是 'umcASCMVBvJjwzJr'
username = urllib.parse.quote_plus('afu')  # 編碼用戶名
password = urllib.parse.quote_plus('umcASCMVBvJjwzJr')  # 編碼密碼

# 將編碼後的用戶名和密碼插入 URI 中
uri = f"mongodb+srv://{username}:{password}@k-boss.i1bhh.mongodb.net/?retryWrites=true&w=majority&tls=true&tlsAllowInvalidCertificates=true"

# 創建客戶端並連接到 MongoDB 伺服器
client = MongoClient(uri, server_api=ServerApi('1'))

# 發送 ping 命令確認成功連接
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)


