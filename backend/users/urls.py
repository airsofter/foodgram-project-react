from django.urls import path, include
from djoser.views import TokenCreateView, TokenDestroyView

from api.views import SubscribtionsView, SubscribtionsCreateDeleteView


app_name = 'users'

urlpatterns = [
    path('users/<int:pk>/subscribe/', SubscribtionsCreateDeleteView.as_view()),
    path('users/subscriptions/', SubscribtionsView.as_view()),
    path('', include('djoser.urls')),
    path('auth/token/login/', TokenCreateView.as_view()),
    path('auth/token/logout/', TokenDestroyView.as_view())
]
