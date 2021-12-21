from django.http import HttpResponse
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
        # text 为图片验证码的内容， image为图片二进制文件
        text, image = captcha.generate_captcha()

        # 3.通过redis把图片验证码保存起来
        # 3.1 进行redis连接  默认连接的是default get_redis_connection会读取设置中的内容
        from django_redis import get_redis_connection
        redis_cli = get_redis_connection('code')
        # 3.2 进行指令的连接
        # name time value
        redis_cli.setex(uuid, 100, text)
        # 4.返回图片二进制
        # 因为图片为二进制，不能返回JSON数据，图片需要告诉数据类型，否则会响应一个乱码在浏览器
        # content_type=响应体数据类型---------->又称为MIME类型
        # content_type的语法形式是： 大类/小类
        # 图片：image/jpeg, image/gif, image/png
        return HttpResponse(image, content_type='image/jpeg')


















