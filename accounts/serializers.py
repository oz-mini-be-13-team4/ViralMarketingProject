from rest_framework import serializers

from accounts.models import Transaction, User

from .models import Account

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

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


class TransactionSerializer(serializers.ModelSerializer):
    account_number = serializers.CharField(source="account.account_number", read_only=True)
    user_email = serializers.CharField(source="account.user.email", read_only=True)

    class Meta:
        model = Transaction
        fields = [
            "id",
            "user_email",  # 거래된 사용자(계좌 소유자) 식별용
            "account_number",  # 계좌 번호 (조회 시 필수)
            "deposit_and_withdrawal_type",  # 입금/출금 (조회 시 필수)
            "transaction_amount",  # 거래 금액 (조회/생성/수정)
            "amount_after_transaction",  # 거래 후 잔액 (조회 전용)
            "transaction_type",  # 거래 방식(이체, ATM 등)
            "transaction_timestamp",  # 거래 일시 (조회 시 필수)
            "account",  # account (생성/수정 시 계좌 PK로 전달)
        ]
        read_only_fields = [
            "id",
            "user_email",
            "account_number",
            "amount_after_transaction",
            "transaction_timestamp",
        ]

        def validate_transaction_amount(self, value):
            if value <= 0:
                raise serializers.ValidationError("거래 금액은 0보다 커야 합니다.")
            return value




class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ("id", "email", "password", "nickname", "name", "phone_number")

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)  # 비밀번호 해시 처리
        user.save()
        return user


class AccountSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = Account
        fields = [
            "id",
            "account_number",
            "bank_code",
            "account_type",
            "balance",
            "user_email",
        ]
        read_only_fields = ["id", "user_email"]

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # 토큰에 사용자 정보 추가
        token["email"] = user.email
        token["nickname"] = user.nickname
        return token