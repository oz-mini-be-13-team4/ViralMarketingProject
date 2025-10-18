from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework.views import APIView

from accounts.models import User
from accounts.serializers import UserSerializer, UserSignUpSerializer


# =========================
# JWT 로그인 관련
# =========================
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # 토큰에 사용자 정보 추가
        token["email"] = user.email
        token["nickname"] = user.nickname
        return token


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]


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

        activation_link = f"http://localhost:8000/accounts/activate/{uid64}/{token}/"

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
