from rest_framework import serializers
from .models import Account

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