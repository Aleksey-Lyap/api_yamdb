from django.urls import path

from users.views import APIToken, APISignUp


urlpatterns = [
    path('signup/', APISignUp.as_view(), name='signup'),
    path('token/', APIToken.as_view(), name='token'),
]
