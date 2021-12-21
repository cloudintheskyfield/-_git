from django.urls import path
from apps.verifications.views import ImageCodeView

urlpatterns = [
    # 该路径根据前端路径代码来写的，该uuid为前端生成的
    path('image_codes/<uuid>/', ImageCodeView.as_view())
]