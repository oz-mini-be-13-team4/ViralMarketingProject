from django_filters import rest_framework as filters

from .models import Transaction


class TransactionFilter(filters.FilterSet):
    # 금액 범위: ?min_amount=1000&max_amount=5000
    min_amount = filters.NumberFilter(field_name="transaction_amount", lookup_expr="gte")
    max_amount = filters.NumberFilter(field_name="transaction_amount", lookup_expr="lte")

    # 거래 방식 / 입출금 타입: ?transaction_type=ATM
    transaction_type = filters.CharFilter(field_name="transaction_type", lookup_expr="exact")
    deposit_and_withdrawal_type = filters.CharFilter(field_name="deposit_and_withdrawal_type", lookup_expr="exact")

    # 날짜 범위: DateFromToRangeFilter를 쓰면
    # ?transaction_timestamp_after=2025-01-01&transaction_timestamp_before=2025-02-01 처럼 사용 가능
    transaction_timestamp = filters.DateFromToRangeFilter(field_name="transaction_timestamp")

    class Meta:
        model = Transaction
        # 외부에 드러날 필드 이름은 여기서 관리(자동 생성도 가능)
        fields = [
            "transaction_type",
            "deposit_and_withdrawal_type",
            "min_amount",
            "max_amount",
            "transaction_timestamp",
        ]
