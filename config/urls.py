from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import TokenRefreshView

from accounts.views import CustomTokenObtainPairView, UserActivateView, UserSignUpView, LogoutView, UserDetailAPIView, UserUpdateAPIView, UserDeleteAPIView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("signup/", UserSignUpView.as_view(), name="signup"),
    path("activate/<str:uid64>/<str:token>/", UserActivateView.as_view(), name="activate"),
    path("login/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("accounts/<str:uid64>/<str:token>/", UserActivateView.as_view()),
    path("api/", include("accounts.urls")),
    # 테스트때문에 넣은거
    path("api-auth/", include("rest_framework.urls")),
    path("logout/", LogoutView.as_view(), name="logout"),
    path('profile/', UserDetailAPIView.as_view(), name='user-detail'),
    path('profile/update/', UserUpdateAPIView.as_view(), name='user-update'),
    path('profile/delete/', UserDeleteAPIView.as_view(), name='user-delete'),
]
