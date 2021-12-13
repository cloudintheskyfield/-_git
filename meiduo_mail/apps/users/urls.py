from django.urls import path
from apps.users.views import UsernameCountView

urlpatterns = [
    # 其中username可以作为 参数 传入视图---------判断用户名是否重复(可以在路由层面进行验证）
    # 此时访问用户名或者密码会出现404提示url找不到
    path('usernames/<username:username>/count/', UsernameCountView.as_view())
]