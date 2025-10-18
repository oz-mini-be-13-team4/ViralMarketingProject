from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters as drf_filters
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated

from .filters import TransactionFilter
from .models import Transaction
from .serializers import TransactionSerializer


class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    # DjangoFilterBackend를 통해 FilterSet을 사용
    filter_backends = [DjangoFilterBackend, drf_filters.OrderingFilter, drf_filters.SearchFilter]
    filterset_class = TransactionFilter

    # 검색/정렬 가능 필드
    search_fields = ["transaction_type", "deposit_and_withdrawal_type"]
    ordering_fields = ["transaction_amount", "transaction_timestamp"]
    ordering = ["-transaction_timestamp"]

    def get_queryset(self):
        # 로그인 사용자와 연결된 계좌의 거래만 보여줌
        user = self.request.user
        return Transaction.objects.filter(account__user=user).order_by("-transaction_timestamp")

    def perform_create(self, serializer):
        # 생성 시: 계좌 소유자 확인 및 잔액 반영
        account = serializer.validated_data["account"]
        amount = serializer.validated_data["transaction_amount"]
        deposit_or_withdrawal = serializer.validated_data["deposit_and_withdrawal_type"]

        if account.user != self.request.user:
            raise PermissionDenied("본인 계좌에 대해서만 거래내역을 생성할 수 있습니다.")

        # 입금/출금에 따른 잔액 처리
        if deposit_or_withdrawal == "DEPOSIT":
            account.balance += amount
        else:  # 출금
            if account.balance < amount:
                raise PermissionDenied("잔액이 부족합니다.")
            account.balance -= amount

        account.save()
        # 실제로 저장될 때 거래 후 잔액을 넣어줌
        serializer.save(amount_after_transaction=account.balance)
