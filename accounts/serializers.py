from rest_framework import serializers

from .models import User


class UserSignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "password", "nickname", "name", "phone_number"]

    def create(self, validated_data):
        password = validated_data.pop("password")

        user = User(
            email=validated_data.get("email"),
            nickname=validated_data.get("nickname"),
            name=validated_data.get("name"),
            phone_number=validated_data.get("phone_number", ""),
        )
        user.set_password(password)
        user.save()
        return user
from rest_framework import serializers
from accounts.models import User

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'nickname', 'name', 'phone_number')

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)  # 비밀번호 해시 처리
        user.save()
        return user