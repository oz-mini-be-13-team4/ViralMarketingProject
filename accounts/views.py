from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
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
                return Response({"detail":"refresh token 없음"},status=status.HTTP_400_BAD_REQUEST)
            token = RefreshToken(refresh_token)
            token.blacklist()

            response = Response({"detail":"로그아웃 완료"},status=status.HTTP_200_OK)
            response.delete_cookie("refresh_token")
            return response

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


# =========================
# 유저 정보 조회 (로그인 필요)
# =========================
class UserDetailAPIView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"


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
