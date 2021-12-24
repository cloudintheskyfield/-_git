# 生产者 -- 任务 函数
# 1. 这个函数 必须要让celery的实例task装饰器装饰
# 2. 需要celery自动检测指定包的任务

from libs.yuntongxun.sms import CCP
from celery_tasks.main import app
from celery import shared_task


@app.task
# @shared_task
def celery_send_sms_code(mobile, code):
    CCP().send_template_sms(mobile, [code, 5], 1)  # 有效期5min，模版为1
















