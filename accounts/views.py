from rest_framework.generics import ListCreateAPIView, RetrieveDestroyAPIView
from rest_framework.permissions import IsAuthenticated

from .models import Account
from .serializers import AccountSerializer

# 계좌 목록/생성
class AccountListCreateView(ListCreateAPIView):
    serializer_class = AccountSerializer    # 요청 검증, 응답에 쓸 시리얼라이저 지정
    permission_classes = [IsAuthenticated]  # 로그인 된 사용자만 접근 가능하게
    http_method_names = ["get", "post"] # 허용할 메서드 : get, post만

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
    http_method_names = ["get", "delete"]   # 허용할 메서드 : get, delete만

    # 조회/삭제 대상도 내 계좌만 가능하게
    def get_queryset(self):
        return Account.objects.filter(user=self.request.user)