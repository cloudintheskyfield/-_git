from django.urls import path
from apps.orders.views import OrderSettlementView,OrderCommitView

urlpatterns = [
    path('orders/settlement/', OrderSettlementView.as_view()),
    # 订单提交
    path('orders/commit/', OrderCommitView.as_view()),

]