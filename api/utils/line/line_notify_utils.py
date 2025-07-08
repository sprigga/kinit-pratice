import requests
from datetime import datetime


def send_line_notify(token: str, message: str) -> bool:
    """
    發送通知到 LINE Notify.

    :param token: LINE Notify 權杖
    :param message: 要發送的訊息
    :return: 是否發送成功 (True 為成功, False 為失敗)
    """
    # LINE Notify API URL
    line_notify_api = 'https://notify-api.line.me/api/notify'

    # 設定 headers 和 payload
    headers = {
        'Authorization': f'Bearer {token}'
    }
    payload = {
        'message': message
    }

    # 發送 POST 請求
    response = requests.post(line_notify_api, headers=headers, data=payload)

    # 返回執行結果
    if response.status_code == 200:
        return True
    else:
        print(f"通知發送失敗，錯誤碼: {response.status_code}")
        return False


def format_datetime_to_chinese(dt: datetime) -> str:
    """
    將 datetime 格式化為中文顯示.

    :param dt: datetime 物件
    :return: 格式化的中文時間字串
    """
    return dt.strftime("%Y年%m月%d日 %H時%M分")