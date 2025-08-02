from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


User = get_user_model()

class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "password")
        extra_kwargs = {
            "email": {"write_only": True, "required": True},
            "password": {"write_only": True, "required": True},
        }


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name")
        extra_kwargs = {"email": {"read_only": True}}


class LoginTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        if not self.user.is_active:
            raise serializers.ValidationError(
                "Unverified account, please check your email and verify your account."
            )
        data["username"] = self.user.username
        data["email"] = self.user.email
        return data
