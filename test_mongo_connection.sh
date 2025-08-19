#!/bin/bash

echo "=== MongoDB 容器連線測試 ==="

# 檢查容器狀態
echo "1. 檢查容器狀態:"
sudo docker ps | grep mongo

# 使用 root 用戶連接
echo -e "\n2. 使用 root 用戶連接:"
sudo docker exec car-mongo mongosh --username afu --password "Y05os5352" --authenticationDatabase admin --eval "
console.log('✅ Root 用戶連接成功');
db.runCommand({connectionStatus: 1});
show dbs;
"

# 使用應用用戶連接
echo -e "\n3. 使用應用用戶連接:"
sudo docker exec car-mongo mongosh --username oa-admin --password "Bdfrost168" --authenticationDatabase bd-oa --eval "
console.log('✅ 應用用戶連接成功');
db.runCommand({connectionStatus: 1});
use('bd-oa');
show collections;
"

echo -e "\n=== 測試完成 ==="