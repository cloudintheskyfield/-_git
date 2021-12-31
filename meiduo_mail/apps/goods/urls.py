from django.urls import path
from apps.goods.views import IndexView, ListView
urlpatterns = [
    # 商品首页
    path('index/', IndexView.as_view()),
    # 商品列表页面
    path('list/<category_id>/skus/', ListView.as_view())

]