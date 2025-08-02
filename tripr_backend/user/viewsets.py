from django.contrib.auth import get_user_model

from rest_framework.views import Response
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView

from user.serializers import (
    LoginTokenObtainPairSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
)

User = get_user_model()

class UserRegisterVS(CreateAPIView):
    serializer_class = UserCreateSerializer

    def create(self, request, *args, **kwargs):
        try:
            email = request.data.get("email")
            username = email.rsplit("@")[0]

            if User.objects.filter(email=email).exists():
                return Response(
                    {"message": "Email is already registered"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                user = serializer.save(username=username)
                user.set_password(serializer.validated_data["password"])
                user.save()
                return Response(
                    {
                        "message": "User successfully registered. Please check your mail and verify your account"
                    },
                    status=status.HTTP_201_CREATED,
                )
            else:
                return Response(
                    {"message": str(serializer.errors)},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as error:
            return Response({"message": str(error)}, status=status.HTTP_400_BAD_REQUEST)


class UserUpdateVS(RetrieveUpdateAPIView):
    serializer_class = UserUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class LoginTokenObtainPair(TokenObtainPairView):
    serializer_class = LoginTokenObtainPairSerializer

