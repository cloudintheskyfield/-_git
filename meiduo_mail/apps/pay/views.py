from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
"""
1.到相应的开放平台，注册成为开发者

2.创建应用

3.按照文档开发

我们不需要创建应用（测试学习）支付宝为我们提供了沙箱环境（测试环境）

在整个支付流程中，我们需要做的就两件事
1.生成跳转到支付宝的连接
2.保存交易完成后，支付宝返回的交易流水号

一：设置公钥和私钥
    美多商城一对（自己弄）
    支付宝一对（它自己弄）
    
在整个支付流程中，我们（美多商城）需要做的就是2件事
1.生成跳转到支付宝的连接
2.保存交易完成后，支付宝返回的交易流水号

"""
"""
需求：
    当用户点击去支付摁钮的时候，要后端生成一个跳转的连接
前端：
    axios请求，携带订单id
后端：
    请求：获取订单id
    业务逻辑：生成支付宝连接（读取文档）
            读取应用私钥和支付宝公钥
            创建支付宝的实例，调用支付宝的方法
            拼接连接
    响应：
    路由： GET payment/order_id/
    步骤：
        1.获取订单id
        2.验证订单id（根据订单id查询订单信息）
        3.读取应用私钥和支付宝公钥
        4.创建支付宝实例
        5.调用支付宝的支付方法
        6.拼接连接
        7.返回响应
"""
from django.views import View
from apps.orders.models import OrderInfo
from utils.views import LoginRequiredJSOMixin
from meiduo_mail import settings
from alipay import AliPay, AliPayConfig


class PayUrlView(LoginRequiredJSOMixin, View):
    def get(self, request, order_id):
        user = request.user
        # 1.获取订单id
        # 2.验证订单id（根据订单id查询订单信息）
        try:
            order = OrderInfo.objects.get(order_id=order_id,
                                          status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'],
                                          user=user)
        except OrderInfo.DoesNotExist:
            return JsonResponse({'code': 400, 'errmsg': '没有此订单'})
        # 3.读取应用私钥和支付宝公钥

        app_private_key_string = open(settings.APP_PRIVATE_KEY_PATH).read()
        alipay_public_key_string = open(settings.APP_PUBLIC_KEY_PATH).read()

        # 4.创建支付宝实例
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,  # 默认回调 url
            app_private_key_string=app_private_key_string,
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_string=alipay_public_key_string,
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=settings.ALIPAY_DEBUG,  # 默认 False
            verbose=False,  # 输出调试数据
            config=AliPayConfig(timeout=15)  # 可选，请求超时时间
        )
        # 5.调用支付宝的支付方法
        subject = '美多商城测试订单'
        # 电脑网站支付，需要跳转到：https://openapi.alipay.com/gateway.do? + order_string  ----》这个是线上的
        # 设置中的支付是沙箱的
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,
            total_amount=str(order.total_amount),  # 一定要进行类型转，转换为字符型
            subject=subject,
            return_url=settings.ALIPAY_RETURN_URL,  # 支付成功之后跳转的页面
            notify_url="https://example.com/notify"  # 可选，不填则使用默认 notify url
        )
        # 6.拼接连接
        pay_url = settings.ALIPAY_URL + '?' + order_string
        # 7.返回响应
        return JsonResponse({'code': 0, 'errmsg':'ok', 'alipay_url': pay_url})


"""
前端：当用户支付完成之后，会跳转到指定商家页面
    页面中的请求 查询字符串中有支付相关信息
    前端把这些数据提交给后端就可以了
    
后端：
    请求： 接收数据
    业务逻辑：查询字符串转换为字典，验证数据，验证没有问题获取支付宝交易流水号,改变订单状态
    响应：
    路由：PUT payment/status/
    步骤：
        1.接收数据
        2.查询字符串转换为字典，验证数据，
        3.验证没有问题获取支付宝交易流水号
        4.改变订单状态
        5.返回响应
"""
from apps.pay.models import Payment
class PaymentStatusView(View):
    def put(self, request):
        # 1.接收数据
        data = request.GET
        # 2.查询字符串转换为字典，验证数据，
        data = data.dict()
        # 3.验证没有问题获取支付宝交易流水号
        signature = data.pop('sign')

        app_private_key_string = open(settings.APP_PRIVATE_KEY_PATH).read()
        alipay_public_key_string = open(settings.APP_PUBLIC_KEY_PATH).read()
        # 创建支付宝实例
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,  # 默认回调 url
            app_private_key_string=app_private_key_string,
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_string=alipay_public_key_string,
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=settings.ALIPAY_DEBUG,  # 默认 False
            verbose=False,  # 输出调试数据
            config=AliPayConfig(timeout=15)  # 可选，请求超时时间
        )
        success = alipay.verify(data, signature)
        # 获取支付宝id
        if success:
            # 支付宝的交易流水号
            trade_no = data.get('trade_no')
            # 我们的订单号
            order_id = data.get('out_trade_no')
            try:
                Payment.objects.create(
                    trade_id = trade_no,
                    order_id= order_id,
                )
            except Exception as e:
                return JsonResponse({'code': 400, 'errmsg': '订单已经存在'})
            # 4.改变订单状态
            try:
                OrderInfo.objects.filter(order_id=order_id).update(status=OrderInfo.ORDER_STATUS_ENUM['UNSEND'])
            except Exception as e:
                print(e)
                return JsonResponse({'code': 400, 'errmsg': '请到个人中心的订单中查询订单状态'})
            # 5.返回响应
            return JsonResponse({'code': 0, 'errmsg': 'ok', 'trade_id': trade_no})
        else:
            return JsonResponse({'code': 400, 'errmsg': '请到个人中心的订单中查询订单状态'})































