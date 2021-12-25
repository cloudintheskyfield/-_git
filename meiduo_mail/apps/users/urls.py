from django.urls import path
from apps.users.views import UsernameCountView, RegisterView, LoginView, LogoutView, CenterView
from apps.users.views import PhoneNumberCountView

"""使用POSTman进行测试的时候需要根据下面的路由进行测试"""
urlpatterns = [
    # 其中username可以作为 参数 传入视图---------判断用户名是否重复(可以在路由层面进行验证）
    # 此时访问用户名或者密码会出现404提示url找不到
    # 这里的路由是根据js文件中的路由来的
    # 第一个username为上面定义的名字，第二个username为需要传递给视图的参数
    # http://127.0.0.1/usernames/<username>/count/
    path('usernames/<username:username>/count/', UsernameCountView.as_view()),   # 后面为 类名.as_view()固定写法
    # # http://127.0.0.1/mobiles/<mobile>/count/
    path('mobiles/<mobile:mobile>/count/', PhoneNumberCountView.as_view()),
    # http://127.0.0.1:8000/register
    path('register/', RegisterView.as_view()),
    # http://127.0.0.1:8000/login/
    path('login/', LoginView.as_view()),
    # http://127.0.0.1:8000/logout/
    path('logout/', LogoutView.as_view()),
    # http://127.0.0.1:8000/info/       根据前端的路由来的
    path('info/', CenterView.as_view())

]















