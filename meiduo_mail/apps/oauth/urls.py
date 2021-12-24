from django.urls import path
from apps.oauth.views import QQLoginURLView

urlpatterns = [
    path('qq/authorization/', QQLoginURLView.as_view())
]