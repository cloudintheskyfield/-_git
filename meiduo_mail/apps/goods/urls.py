from django.urls import path
from apps.goods.views import IndexView
urlpatterns = [
    # 商品首页
    path('index/', IndexView.as_view()),

]