from django.urls import path
from apps.verifications.views import ImageCodeView, SmsCodeView

"""下面的路由都是根据前端写死的路径来的"""
urlpatterns = [
    # 该路径根据前端路径代码来写的，该uuid为前端生成的 图形验证码
    path('image_codes/<uuid>/', ImageCodeView.as_view()),

    # 根据图形验证码来发送的短信验证码  ------------------该路由是根据前端写死的路径来的---转换器已经在meiduo_mail工程下注册直接使用即可
    path('sms_codes/<mobile:mobile>/', SmsCodeView.as_view())

]