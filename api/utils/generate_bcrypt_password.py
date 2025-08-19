from passlib.hash import bcrypt

# 替換 'new_password' 為你想要的新密碼
new_password = '16231623'
hashed_password = bcrypt.hash(new_password)

# 印出生成的哈希密碼
print(f"新密碼的哈希值: {hashed_password}")