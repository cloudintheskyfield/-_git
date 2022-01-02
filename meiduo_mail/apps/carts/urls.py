from django.urls import path
from apps.carts.views import CartsView
urlpatterns = [
    path('carts/', CartsView.as_view()),

]