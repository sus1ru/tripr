from django.urls import path

from rest_framework_simplejwt.views import TokenRefreshView

from user.viewsets import (
    LoginTokenObtainPair,
    UserRegisterVS,
    UserUpdateVS,
    activate_user,
)


urlpatterns = [
    path("signup/", UserRegisterVS.as_view(), name="registration"),
    path("login/", LoginTokenObtainPair.as_view(), name="login"),
    path("profile/", UserUpdateVS.as_view(), name="profile"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path(
        "verify/<str:uidb64>/<str:token>/",
        activate_user,
        name="email_activate",
    ),
]
