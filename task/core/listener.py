import datetime
import json

import pytz
from apscheduler.events import JobExecutionEvent

from application.settings import SCHEDULER_TASK_RECORD, SCHEDULER_TASK
from core.logger import logger
from core.mongo import get_database

Taipei_tz = pytz.timezone("Asia/Taipei")
# 全局变量，用于存储记录ID
record_ids = {}


# 定義事件處理函數，在作業提交或執行前被調用
def before_job_execution(event: JobExecutionEvent):
    print(f'任務: {event.job_id} 準備開始執行。')
    # 获取当前时间
    start_time = datetime.datetime.now()

    job_id = event.job_id
    if "-temp-" in job_id:
        job_id = job_id.split("-")[0]

    result = {
        "job_id": job_id,
        "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
        "end_time": '',
        "process_time": '',
        "retval": json.dumps('任務開始'),
        "exception": '',
        "traceback": ''
    }

    db = get_database()
    try:
        task = db.get_data(SCHEDULER_TASK, job_id, is_object_id=True)
        result["job_class"] = task.get("job_class", None)
        result["name"] = task.get("name", None)
        result["group"] = task.get("group", None)
        result["exec_strategy"] = task.get("exec_strategy", None)
        result["expression"] = task.get("expression", None)
    except ValueError as e:
        result["exception"] = str(e)
        logger.error(f"任務編號：{event.job_id}，抱錯：{e}")

    # 新增任務紀錄
    new_id = db.create_data(SCHEDULER_TASK_RECORD, result)

    # 新增ID 到全局 讓執行完後 可以更新紀錄
    record_ids[event.job_id] = str(new_id.inserted_id)


# 定义事件处理函数，在作业执行完成后被调用
def after_job_execution(event: JobExecutionEvent):
    print(f'任務 {event.job_id} 執行完成。')
    # 計算時間
    start_time = event.scheduled_run_time.astimezone(Taipei_tz)
    end_time = datetime.datetime.now(Taipei_tz)
    process_time = (end_time - start_time).total_seconds()

    # 获取任务的 new_id
    record_id = record_ids.get(event.job_id, None)

    # 更新任務完成後的結果
    db = get_database()

    result = {
        "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S"),
        "process_time": process_time,
        "retval": json.dumps(event.retval.get('retval', '任務失敗')),
        "exception": event.retval.get('exception', None),
        "traceback": event.retval.get('traceback', None),
    }

    # 更新返回的任務紀錄
    db.put_data(SCHEDULER_TASK_RECORD, _id=record_id, data=result, is_object_id=True)
