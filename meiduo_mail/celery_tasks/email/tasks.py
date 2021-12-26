from django.core.mail import send_mail
from celery_tasks.main import app

"""
生产者--- 任务 函数
1.函数必须要让celery的实例的task装饰器装饰
2.需要celery自动检测指定包的任务
"""
@app.task
def celery_send_email(subject, message, html_message, from_email, recipient_list):
    send_mail(subject=subject,
              message=message,
              html_message=html_message,
              from_email=from_email,
              recipient_list=recipient_list
              )





















