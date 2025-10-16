from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from accounts.serializers import UserSerializer  # 필요시 작성
from accounts.models import User

# =========================
# JWT 로그인 관련
# =========================
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # 토큰에 사용자 정보 추가
        token['email'] = user.email
        token['nickname'] = user.nickname

        return token

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]


# =========================
# 유저 생성 (회원가입) 예제
# =========================
class UserCreateAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                "message": "User created successfully",
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User
from .serializers import UserSignUpSerializer


# 회원가입 뷰
class UserSignUpView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSignUpSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        token = default_token_generator.make_token(user)
        uid64 = urlsafe_base64_encode(force_bytes(user.pk)).decode()
        activation_link = f"http://localhost:8000/activate/{uid64}/{token}/"

        send_mail(
            subject="회원가입 인증 메일",
            message=f"링크를 클릭해 인증하세요: {activation_link}",
            from_email="noreply@myproject.com",
            recipient_list=[user.email],
        )


class UserActivateView(APIView):
    def get(self, request, uid64, token):
        try:
            uid = int(urlsafe_base64_decode(uid64).decode())
            user = get_object_or_404(User, pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"message": "유효하지 않은 링크입니다."}, status=status.HTTP_400_BAD_REQUEST)

        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return Response({"message": "계정이 활성화되었습니다."}, status=status.HTTP_200_OK)
        return Response({"message": "유효하지 않은 토큰입니다."}, status=status.HTTP_400_BAD_REQUEST)


# =========================
# 유저 정보 조회 (예제)
# =========================
from rest_framework.permissions import IsAuthenticated
class UserDetailAPIView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"