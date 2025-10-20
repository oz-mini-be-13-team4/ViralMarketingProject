from decimal import Decimal

from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import transaction  # DB 트랜잭션 보장을 위해
from django.shortcuts import get_object_or_404
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters as drf_filters
from rest_framework import generics, status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import ListCreateAPIView, RetrieveDestroyAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import Account, User
from accounts.serializers import AccountSerializer, UserSerializer, UserSignUpSerializer, CustomTokenObtainPairSerializer

from .filters import TransactionFilter
from .models import Transaction
from .serializers import TransactionSerializer


# =========================
# JWT 로그인 관련
# =========================
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        token = response.data["access"]
        refresh_token = response.data.get("refresh")
        response.set_cookie(key="access_token", value=token, httponly=True, secure=False, samesite="Lax")
        response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, secure=False, samesite="Lax")
        return response

# =========================
# JWT 로그아웃
# =========================
class LogoutView(APIView):
    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")
        if refresh_token is None:
            return Response({"detail": "refresh token 없음"}, status=status.HTTP_400_BAD_REQUEST)
        token = RefreshToken(refresh_token)
        token.blacklist()

        response = Response({"detail": "로그아웃 완료"}, status=status.HTTP_200_OK)
        response.delete_cookie("refresh_token")
        response.delete_cookie("access_token")
        return response

# =========================
# 회원 정보 조회 (본인만)
# =========================
class UserDetailAPIView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # 로그인한 본인의 정보만 조회 가능
        return self.request.user

# =========================
# 회원 정보 수정 (본인만)
# =========================
class UserUpdateAPIView(generics.UpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def patch(self, request, *args, **kwargs):
        # 일부 필드만 수정 (PATCH)
        return self.partial_update(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        # 전체 필드 수정 (PUT)
        return self.update(request, *args, **kwargs)

# =========================
# 회원 삭제 (본인만)
# =========================
class UserDeleteAPIView(generics.DestroyAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        user.delete()
        return Response({"message": "Deleted successfully"}, status=status.HTTP_200_OK)

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

    def perform_update(self, serializer):
        instance = serializer.instance
        account = instance.account

        # 소유자 확인
        if account.user != self.request.user:
            raise PermissionDenied("본인 계좌의 거래만 수정할 수 있습니다.")

        # 계좌 변경 금지
        if "account" in serializer.validated_data and serializer.validated_data["account"] != account:
            raise PermissionDenied("거래의 계좌 변경은 허용되지 않습니다.")

        old_amount = instance.transaction_amount
        old_type = instance.deposit_and_withdrawal_type

        new_amount = serializer.validated_data.get("transaction_amount", old_amount)
        new_type = serializer.validated_data.get("deposit_and_withdrawal_type", old_type)

        # 효과 계산 함수
        def effect(t, amt):
            return amt if t == "DEPOSIT" else -amt

        # 잔액에 적용될 변화량(delta)
        delta = effect(new_type, new_amount) - effect(old_type, old_amount)
        if not isinstance(delta, Decimal):
            delta = Decimal(delta)

        with transaction.atomic():
            # 잔액이 음수가 되면 차단
            if delta < Decimal("0") and (account.balance + delta) < Decimal("0"):
                raise PermissionDenied("수정 결과 잔액이 부족합니다.")

            account.balance += delta
            account.save()

            # amount_after_transaction 최신화
            serializer.save(amount_after_transaction=account.balance)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        account = instance.account

        # 소유자 확인
        if account.user != request.user:
            raise PermissionDenied("본인 계좌의 거래만 삭제할 수 있습니다.")

        with transaction.atomic():
            # 거래 영향 롤백
            if instance.deposit_and_withdrawal_type == "DEPOSIT":
                # 입금 거래였으므로 삭제 시 잔액에서 빼야 함
                if account.balance < instance.transaction_amount:
                    raise PermissionDenied("해당 거래를 삭제하면 잔액이 음수가 되어 삭제 불가.")
                account.balance -= instance.transaction_amount
            else:
                # 출금 거래였으므로 삭제 시 잔액에 다시 더해야 함
                account.balance += instance.transaction_amount

            account.save()
            instance.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)



# =========================
# 회원가입 (이메일 인증)
# =========================
class UserSignUpView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSignUpSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        # 처음엔 비활성화 상태로 저장
        user = serializer.save(is_active=False)
        token = default_token_generator.make_token(user)
        uid64 = urlsafe_base64_encode(force_bytes(user.pk))

        activation_link = f"http://localhost:8000/accounts/{uid64}/{token}/"

        send_mail(
            subject="[ViralMarketingProject] 회원가입 인증 메일",
            message=f"아래 링크를 클릭해 계정을 활성화하세요:\n{activation_link}",
            from_email="noreply@myproject.com",
            recipient_list=[user.email],
        )


# =========================
# 이메일 인증 활성화
# =========================
class UserActivateView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, uid64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uid64))
            user = get_object_or_404(User, pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"message": "유효하지 않은 링크입니다."}, status=status.HTTP_400_BAD_REQUEST)

        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return Response({"message": "계정이 활성화되었습니다."}, status=status.HTTP_200_OK)

        return Response({"message": "유효하지 않은 토큰입니다."}, status=status.HTTP_400_BAD_REQUEST)

# 계좌 목록/생성
class AccountListCreateView(ListCreateAPIView):
    serializer_class = AccountSerializer  # 요청 검증, 응답에 쓸 시리얼라이저 지정
    permission_classes = [IsAuthenticated]  # 로그인 된 사용자만 접근 가능하게
    http_method_names = ["get", "post"]  # 허용할 메서드 : get, post만

    # 본인의 계좌만 조회되도록
    def get_queryset(self):
        return Account.objects.filter(user=self.request.user).order_by("-id")

    # 생성 시 로그인 사용자를 소유자로 지정
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# 계좌 조회/삭제
class AccountRetrieveDestroyView(RetrieveDestroyAPIView):
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "delete"]  # 허용할 메서드 : get, delete만

    # 조회/삭제 대상도 내 계좌만 가능하게
    def get_queryset(self):
        return Account.objects.filter(user=self.request.user)
