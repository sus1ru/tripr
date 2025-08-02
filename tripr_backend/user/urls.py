from django.urls import path

from rest_framework_simplejwt.views import TokenRefreshView

from user.viewsets import (
    LoginTokenObtainPair,
    UserRegisterVS,
    UserUpdateVS,
)


urlpatterns = [
    path("signup/", UserRegisterVS.as_view(), name="registration"),
    path("login/", LoginTokenObtainPair.as_view(), name="login"),
    path("profile/", UserUpdateVS.as_view(), name="profile"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
