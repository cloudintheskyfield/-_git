from django.urls import path
from apps.areas.views import AreaView, SubAreaView
urlpatterns = [
    # 省信息的路由
    path('areas/', AreaView.as_view()),
    # axios.get(this.host + '/areas/' + this.form_address.province_id + '/', {
    # 市/县信息路由 将省的id传入进来
    path('areas/<id>/', SubAreaView.as_view())

]