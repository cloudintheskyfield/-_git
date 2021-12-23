import re

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

"""
图片验证码 ---------思路---------------------------
前端
    拼接一个url，然后给img，img会发起请求
    url=http://ip:port/image_codes/uuid/

后端
    请求       接收路由中的uuid
    业务逻辑    生成图片验证码和图片二进制，通过redis把图片验证码保存起来
    响应      返回图片二进制
    路由      GET     image_codes/uuid/
    步骤
        1.接收路由中的uuid
        2.生成图片验证码和图片二进制
        3.通过redis把图片验证码保存起来
        4.返回图片二进制
"""
# Create your views here.
from django.views import View


class ImageCodeView(View):

    def get(self, request, uuid):
        # 1.接收路由中的uuid

        # 2.生成图片验证码和图片二进制
        from libs.captcha.captcha import captcha
        # text 为图片验证码的内容 即验证码中的 字符， image为图片二进制文件 为验证码图片
        text, image = captcha.generate_captcha()

        # 3.通过redis把图片验证码保存起来
        # 3.1 进行redis连接  默认连接的是default get_redis_connection会读取设置中的内容
        from django_redis import get_redis_connection
        redis_cli = get_redis_connection('code')
        # 3.2 进行指令的连接
        # name time value--------->key:uuid value:text 每一个uuid在同一次只对应一个验证码，下一次会改变
        redis_cli.setex(uuid, 100, text)

        # 4.返回图片二进制
        # 因为图片为二进制，不能返回JSON数据，图片需要告诉数据类型，否则会响应一个乱码在浏览器
        # content_type=响应体数据类型---------->又称为MIME类型
        # content_type的语法形式是： 大类/小类
        # 图片：image/jpeg, image/gif, image/png
        return HttpResponse(image, content_type='image/jpeg')


"""
发送短信的思路
前端：
   当用户输入完手机号，图片验证码之后，前端发送一个axios请求
   sms_codes/手机号/?image_code= &image_code_id= 
后段：
    请求：接收请求，获取请求参数（路由有手机号，用户的图片验证码和UUID在查询字符串中）
    业务逻辑：验证参数，验证图片验证码，生成短信验证码，保存短信验证码，发送短信验证码
    响应：返回响应
        {'code': 0, 'errmsg': 'ok}
    路由： GET     sms_codes/手机号/?image_code=图形验证码&image_code_id=图形验证码id
    步骤：
        1.获取请求参数
        2.验证参数
        3.验证图片验证码
        4.生成短信验证码
        5.保存短信验证码
        6.发送短信验证码
        7.返回响应
    需求--->思路--->步骤--->代码
    -----------------------------------------------
    debug模式运行，调试模式
    debug和断电配合使用
    可以看到程序执行的过程
    
    添加断点：在函数体第一行添加断点！！！！ 只有发送请求的时候才会过来
    
"""


class SmsCodeView(View):
    def get(self, request, mobile):
        # 1.获取请求参数
        image_code = request.GET.get('image_code')  # image_code 为图片验证码内容
        uuid = request.GET.get('image_code_id')     # image_code_id 为uuid

        # 2.验证参数
        if not all([image_code, uuid]):
            return JsonResponse({'code': 400, 'errmsg': '参数不全'})

        # 3.验证图片验证码
        # 3.1 连接redis
        from django_redis import get_redis_connection
        # 该处需要从 图形验证码的库 中拿取数据
        redis_cli = get_redis_connection('code')
        # 3.2 获取redis数据---拿取数据库中的uuid
        redis_image_code = redis_cli.get(uuid)  # uuid是一个具体的值，对应redis中的key
        if redis_image_code is None:
            return JsonResponse({'code': 400, 'errmsg': '图片验证码已经过期'})
        # 3.3 对比
        #  lower()为小写模式
        if redis_image_code.decode().lower() != image_code.lower():
            return JsonResponse({'code': 400, 'errmsg': '图片验证码错误'})

        # 3.4提取发送短信的标记，看看有没有
        send_flag = redis_cli.get('send_flag_%s' % mobile)
        if send_flag is not None:
            return JsonResponse({'code': 400, 'errmsg': '不要频繁发送短信'})

        # 4.生成短信验证码
        # 确保验证码为6位---6位整数
        from random import randint
        sms_code = '%06d' % randint(0, 99999)

        # 4.5 管道--->从性能上提升redis数据库的效率，减少包的数量
        # 4.5.1新建一个管道
        pipeline = redis_cli.pipeline()

        # 5.保存短信验证码---将短信验证码存储到redis中
        pipeline.setex(mobile, 300, sms_code)
        # 5.1 添加一个发送标记 有效期60秒 内容是什么都可以
        pipeline.setex('send_flag_%s' % mobile, 60, 1)     # 注意send_flag为存入的二进制数据

        # 4.5.2管道执行指令
        pipeline.execute()

        # 6.发送短信验证码
        # from libs.yuntongxun.sms import CCP
        # # 5分钟内正确输入---对应上面的redis300s
        # CCP().send_template_sms(mobile, [sms_code, 5], 1)

        # 6.改成使用celery来进行发送
        from celery_tasks.sms.tasks import celery_send_sms_code
        # delay的参数就等同于任务（函数）的参数
        celery_send_sms_code.delay(mobile, sms_code)

        # 7.返回响应
        return JsonResponse({'code': 0, 'errmsg': 'ok'})
































