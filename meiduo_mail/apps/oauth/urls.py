from django.urls import path
from apps.oauth.views import QQLoginURLView, OauthQQview

urlpatterns = [
    path('qq/authorization/', QQLoginURLView.as_view()),
    #
    path('oauth_callback/', OauthQQview.as_view())
]