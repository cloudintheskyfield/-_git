"""中间人的配置文件"""
# 使用 Amazon SQS 作为作为中间人的URL为：
# broker_url = 'sqs://ABCDEFGHIJKLMNOPQRST:ZYXK7NiynGlTogH8Nj+P9nlE73sq3@'

# 我们指定redis为我们的中间人（队列）  0 - 16号库
broker_url = 'redis://127.0.0.1:6379/15'