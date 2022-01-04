from django.urls import path
from apps.pay.views import PayUrlView
urlpatterns = [
    # 支付宝跳转的连接 订单id需要为32位的整数
    path('payment/<order_id>/', PayUrlView.as_view()),

]