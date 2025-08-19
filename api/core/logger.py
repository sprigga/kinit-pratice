import os
import sys
import time
from loguru import logger
from application.settings import BASE_DIR

"""
# 日誌設定
# 具體其他配置可參考 https://github.com/Delgan/loguru
"""

# 確保日誌目錄存在
log_path = os.path.join(BASE_DIR, 'logs')
os.makedirs(log_path, exist_ok=True)

# 設定日誌文件名稱
log_path_info = os.path.join(log_path, f'info_{time.strftime("%Y-%m-%d")}.log')
log_path_warning = os.path.join(log_path, f'warning_{time.strftime("%Y-%m-%d")}.log')
log_path_error = os.path.join(log_path, f'error_{time.strftime("%Y-%m-%d")}.log')

# 先移除預設的控制台日誌
logger.remove()

# 設定不同級別的日誌文件
logger.add(log_path_info, rotation="00:00", retention="3 days", enqueue=True, encoding="UTF-8", level="INFO")
logger.add(log_path_warning, rotation="00:00", retention="3 days", enqueue=True, encoding="UTF-8", level="WARNING")
logger.add(log_path_error, rotation="00:00", retention="3 days", enqueue=True, encoding="UTF-8", level="ERROR")

# 允許 INFO 以上的日誌輸出到控制台
logger.add(sys.stdout, level="INFO", format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}")