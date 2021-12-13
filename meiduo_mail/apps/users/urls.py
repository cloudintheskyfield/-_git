from django.urls import path
from apps.users.views import UsernameCountView

urlpatterns = [
    # 其中username可以作为 参数 传入视图---------判断用户名是否重复
    path('usernames/<username>/count/', UsernameCountView.as_view())
]