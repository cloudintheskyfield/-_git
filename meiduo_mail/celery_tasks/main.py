"""
生产者(任务，函数，单独放一个文件，单独指定一个包） --- sms/task.py
消费者（worker）
    celery -A proj worker -l info
    在虚拟环境下执行下列命令
    celery -A celery实例的脚本路径 worker -l info
队列（中间人，经纪人，broker）
    设置broker
    1.
    2. 通过加载配置文件来设置broker
        app.config_from_object('celery_tasks.config')

    配置信息 key = value
    指定redis为我们的broker
    broker_url = 'redis://127.0.0.1:6379/15'

Celery---将这3者实现了

"""
# 0.为celery的运行设置Django的环境---配置环境变量，如果想使用设置中的变量就要这样配置
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meiduo_mail.settings')  # 再打错字吃屎去吧
django.setup()
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meiduo_mail.settings') 上面配置为manage.py中的配置 为设置环境
# meiduo_mail 为工程的名称--->随工程名称而改变

# --------------------------------------------------------->broker
# 1.创建celery实例
from celery import Celery
# 参数1：main设置脚本路径就可以了，脚本路径是唯一的--->创建实例app，celery_tasks的脚本路径是celery_tasks
app = Celery(main='celery_tasks')

# 2.设置broker
# 通过加载配置文件设置broker  加载中间人 配置文件为目录中的config.py
app.config_from_object('celery_tasks.config')
# app.config_from_object('django.conf:settings', namespace='CELERY')


# --------------------------------------------------------> tasks

# 3.需要celery自动检测指定包的任务
# autodiscover_tasks参数是列表
# 列表中的元素的是tasks的路径，自动检测app中的任务，自动检测该包下的任务
app.autodiscover_tasks(['celery_tasks.sms', 'celery_tasks.email'])
# app.autodiscover_tasks(['celery_tasks.email'])






# #  <------------------------------------发送邮箱的配置-------------------------------------------------->
# # 0.为celery的运行设置Django环境
# import os
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meiduo_mail.settings')
# # 1.创建celery的实例
# from celery import Celery
# app = Celery('celery_tasks')    # 后面的celery_tasks为设置的脚本路径
# # 2.设置broker
# app.config_from_object('celery_tasks.config')   # 通过加载配置文件来设置broker
# # 3.自动检测任务
# app.autodiscover_tasks(['celery_tasks.sms', 'celery_tasks.email'])  # 列表中的元素为tasks的路径 自动检测sms和email包下面的任务












