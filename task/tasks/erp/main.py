import datetime
import json
import time

import redis
import requests

from application.settings import REDIS_DB_IP, APS_API_LOCK_KEY, APS_TASK_LOCK_KEY, APS_JOB_ID, APS_RUN_TIMEOUT, \
    APS_JOB_CODE, API_URL, SCHEDULER_TASK_RECORD, T100_ENV
from core.T100_SSH import RemoteProcessMonitor
from core.mongo import get_database


class T100ApsGetStat:
    """
    這是讀取T100 的模擬APS501 讀取APS執行狀態
    """
    def __init__(self, api_endpoint):
        self.base_date = None
        self.aps_no = None
        self.redis_client = None
        self.api_endpoint = api_endpoint
        self.result = {
            "exception": '請洽IT',
            "retval": '任務失敗',
            "traceback": '請洽IT'
        }

    def main(self) -> dict:
        # 初始化返回結果

        # 連接到 Redis 資料庫，並檢索存儲的 JSON 資料
        self.redis_client = redis.StrictRedis(host=REDIS_DB_IP, port=6379, db=1)
        stored_data = json.loads(self.redis_client.get(f'{APS_JOB_ID}_params'))
        self.aps_no = stored_data.get('aps_no', None)
        self.base_date = stored_data.get('base_date', None)

        # 打印任務開始信息
        print('{}, APS進度,定時任務開始，參數為: {}, {}'.format(datetime.datetime.now(), self.aps_no, self.base_date))

        # 檢查 Redis 鎖是否存在
        lock_status = self.redis_client.exists(APS_TASK_LOCK_KEY)
        if lock_status:
            self.result['exception'] = f'{APS_TASK_LOCK_KEY}鎖定中'
            self.result['retval'] = '任務失敗'
            self.result['traceback'] = 'APS鎖定中不重複執行'
            # print('APS鎖定中')
            return self.result

        # 設置 Redis 鎖，避免任務重複執行
        lock_acquired = self.redis_client.set(APS_TASK_LOCK_KEY, "locked", nx=True, ex=APS_RUN_TIMEOUT)
        if not lock_acquired:
            self.result['exception'] = f'{APS_TASK_LOCK_KEY}無法鎖定'
            self.result['retval'] = '任務失敗'
            self.result['traceback'] = '無法鎖定APS鎖, 請洽IT'
            # print('無法獲取鎖')
            return self.result

        try:
            if self.aps_no and self.base_date:
                # 任務參數存在，開始執行任務
                # print(f"執行任務: {datetime.datetime.now()}")
                cmdline = f'fglrun /u1/{T100_ENV}/erp/aps/42r/apsp500'

                # 連接到 T100 主機
                monitor = RemoteProcessMonitor(cmdline)
                monitor.connect()

                try:
                    no_process_count = 0
                    no_process_limit = 10  # 未找到進程的最大次數
                    no_process_status = False  # APSP500 狀態
                    while not no_process_status:
                        # 查找匹配的進程
                        processes = monitor.find_process_by_cmdline()
                        if processes:
                            for process in processes:
                                # print(f"找到進程: {process}")
                                parts = process.split()
                                if len(parts) > 1:
                                    pid = parts[1]
                                    # 解析命令行參數
                                    cmd_params = monitor.parse_cmdline(process)
                                    if cmd_params:
                                        # print(f"解析命令行參數: {cmd_params}")
                                        # 如果是MES發的 才做監控
                                        # TODO ENT 跟SITE 可能要用傳的
                                        if (cmd_params['parentprog'] == APS_JOB_CODE and
                                                cmd_params['param'][0] == '1' and
                                                cmd_params['param'][1] == 'BD01' and
                                                cmd_params['param'][2] == self.aps_no and
                                                cmd_params['param'][3] == self.base_date):
                                            # print("符合MES條件，進行監控")
                                            st = self.monitor_and_update(monitor, pid)
                                            # 代表已經找到並結束所以可以直接結束
                                            if st:
                                                no_process_status = True
                                                no_process_count = 0  # 重置未找到進程計數器
                                                self.result['retval'] = '任務完成'
                                                self.result['traceback'] = f'APS版本:{self.aps_no},行動基準日:{self.base_date}'
                                            else:
                                                self.result['traceback'] = '發生異常,請洽IT'
                                                self.result['retval'] = '任務失敗'
                                        else:
                                            print("不符合MES條件，跳過")
                        else:
                            no_process_count += 1
                            print(f"未找到匹配的進程。嘗試 {no_process_count}/{no_process_limit}")
                            if no_process_count >= no_process_limit:
                                print("在指定次數內未找到匹配的進程。退出。")
                                self.result['exception'] = f'超過次數:{no_process_limit}次'
                                self.result['retval'] = '任務失敗'
                                self.result['traceback'] = '逾時找不到APS進程, 請洽IT'
                                break
                        # 暫停一段時間再進行下一次檢查
                        time.sleep(5)
                finally:
                    monitor.disconnect()
            else:
                self.result["exception"] = 'APS版本與行動基準日參數異常'
                self.result["traceback"] = '參數異常'
                self.result['retval'] = '任務失敗'
        except Exception as e:
            self.result["exception"] = str(e)
            self.result["traceback"] = '發生系統異常, 請洽IT'
            self.result['retval'] = '任務失敗'
        finally:
            # 釋放 Redis 鎖
            self.redis_client.delete(APS_TASK_LOCK_KEY)
            self.redis_client.delete(APS_API_LOCK_KEY)
            print('任務完成,鎖已釋放')
            return self.result

    def monitor_and_update(self, monitor, pid):
        try:
            try_count = 0
            try_max_count = 360
            while True:
                try_count += 1
                stdin, stdout, stderr = monitor.ssh.exec_command(f"ps -p {pid} -o %cpu,%mem")
                output = stdout.read().decode().strip().split('\n')
                start_time = datetime.datetime.now()
                if len(output) > 1:
                    cpu, mem = output[1].split()
                    print(f"CPU 使用率: {cpu}% | 記憶體使用率: {mem}%")
                    # 更新進度到任務記錄檔
                    update_status = self.update_aps_status()
                    self.result['exception'] = update_status['exception']
                    self.result['retval'] = json.dumps(update_status['retval'])
                    self.result['traceback'] = update_status['traceback'] + ',最後執行時間: ' + start_time.strftime(
                        "%Y-%m-%d %H:%M:%S")
                    print(f"更新狀態: {update_status}")
                    self.update_aps_task_status()
                else:
                    # print("進程已終止。")
                    return True

                if try_count > try_max_count:
                    self.result['exception'] = update_status['exception']
                    self.result['retval'] = json.dumps('任務失敗')
                    self.result['traceback'] = 'APS引擎執逾時30分鐘無回應' + ',最後執行時間: ' + start_time.strftime(
                        "%Y-%m-%d %H:%M:%S")
                    return False

                time.sleep(5)
        except KeyboardInterrupt:
            # print("監控已停止。")
            return False

    def update_aps_status(self):
        try:
            # 定義請求參數
            params = {
                "aps_no": self.aps_no,  # 替換為實際的 APS NO
                "base_date": self.base_date  # 替換為實際的 BASE DATE
            }
            # 發送 GET 請求
            response = requests.get(f'{API_URL}{self.api_endpoint}', params=params)
            # 處理回應
            if response.status_code == 200:
                data = response.json()
                # print(data)
                # 返回更新狀態
                if data['data']['psea003']:
                    return {"retval": "任務進行中", "exception": data['data']['psea003'], "traceback": '進行中'}
                else:
                    return {"retval": "任務進行中", "exception": "APS讀取狀態中", "traceback": 'APS501資料未更新'}
            else:
                print("更新失敗，狀態碼:", response.status_code)
                return {"retval": "任務進行中", "exception": f"無法讀取APS狀態，狀態碼: {response.status_code}", "traceback": '發生錯誤'}
        except Exception as e:
            print(f"更新 APS 狀態時發生錯誤: {e}")
            return {"retval": "任務進行中", "exception": str(e), "traceback": '發生錯誤'}

    def update_aps_task_status(self):
        """
        更新MONDB 狀態的紀錄 可能不準因為只能撈最後一筆
        """
        # 更新任務完成後的結果
        db = get_database()
        _id = None
        try:
            task = db.get_data(SCHEDULER_TASK_RECORD,
                               job_id=APS_JOB_ID,
                               end_time=('is', 'null'),
                               process_time=('is', 'null'),
                               is_object_id=True)

            _id = task.get("_id", None)
            if _id:
                # 更新返回的任務紀錄
                db.put_data(SCHEDULER_TASK_RECORD, _id=_id, data=self.result, is_object_id=True)

        except ValueError as e:
            print(f'mondb更新任務紀錄發生異常:{str(e)}')


class T100TableRsync:
    """
    同步T100
    """
    def __init__(self, api_code, endpoint):
        self.api_code = api_code
        self.endpoint = endpoint
        self.result = {
            "exception": '請洽IT',
            "retval": '任務失敗',
            "traceback": '請洽IT'
        }

    def main(self) -> dict:
        # 打印任務開始信息
        print(f'{datetime.datetime.now()}, 同步ERP進度,定時任務開始, 參數{self.api_code}')
        time.sleep(1)

        try:
            # 定義請求參數
            parameter = {
                'api_code': [self.api_code],
                'start_date': ['20230618102000'],
                'sync_type': [1],
                'page_size': [1000],

            }

            # 發送 GET 請求
            response = requests.get(f'{API_URL}/{self.endpoint}', params=parameter)
            # 處理回應
            if response.status_code == 200:
                data = response.json()
                if data['code'] == 200:
                    self.result['exception'] = f''
                    self.result['retval'] = '任務成功'
                    self.result['traceback'] = ''
                else:
                    self.result['exception'] = f'錯誤訊息: {data["message"]}'
                    self.result['retval'] = '任務失敗'
                    self.result['traceback'] = 'API讀取失敗'
            else:
                self.result['exception'] = f''
                self.result['retval'] = '任務失敗'
                self.result['traceback'] = 'API讀取失敗'

        except Exception as e:
            print(f"更新 {self.endpoint} 時發生系統錯誤: {e}")
            self.result['exception'] = f'{str(e)}'
            self.result['retval'] = '任務失敗'
            self.result['traceback'] = 'API讀取發生系統異常'
        finally:
            return self.result
