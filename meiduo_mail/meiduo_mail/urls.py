"""meiduo_mail URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include


def log(request):
    # 日志器的使用
    # 1.导入
    import logging
    # 2.创建日志器
    logger = logging.getLogger('django')
    # 3.调动日志器的方法保存日志
    logger.info('用户登录了')
    logger.warning('redis缓存不足')
    logger.error('该记录不存在')
    logger.debug('~~~~~~~~~~~')

    return HttpResponse('log')

# 注册转换器
    # 1.判断用户名是否重复转换器
from utils.converters import UsernameConverter  # 1.将UsernameConverter转换器导入
from django.urls import register_converter  # 2. 再从django.urls中的resister_converter中导入转换器--->每个自定义转换器的需要
# 注册的方式类似源码中标记的 参数1：转换器类，参数2：以及转换器的名字 ----->其中转换器的名字为自定义的，需要在app的对应子应用路由中使用
register_converter(UsernameConverter, 'username')
    # 2.判断手机号是否注册转换器
from utils.converters import MobileConverter
register_converter(MobileConverter, 'mobile')



urlpatterns = [
    path('admin/', admin.site.urls),
    # 检测到变化git，使用pycharm自带的工具 ctrl+k 来进行git add 操作和 git commit操作
    # 进行push ： ctrl + shift + k 进行git push操作
    path('log/', log),

    #   导入users子应用的路由
    path('', include('apps.users.urls')),
    #   导入verifications应用的路由
    path('', include('apps.verifications.urls')),
    # 导入oauth的路由
    path('', include('apps.oauth.urls')),
    # 导入area的路由
    path('', include('apps.areas.urls')),
    # goods的url
    path('', include('apps.goods.urls')),
    # carts
    path('', include('apps.carts.urls')),
    # orders
    path('', include('apps.orders.urls')),
    # alipay
    path('', include('apps.pay.urls')),



]


















