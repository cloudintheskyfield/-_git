from django.urls import path
from apps.goods.views import IndexView, ListView, SKUSearchView
urlpatterns = [
    # 商品首页
    path('index/', IndexView.as_view()),
    # 商品列表页面
    path('list/<category_id>/skus/', ListView.as_view()),
    # 搜索/索引         没有as_view()直接实例化即可
    path('search/', SKUSearchView()),


]