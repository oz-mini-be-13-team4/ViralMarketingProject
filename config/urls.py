
from django.contrib import admin
from accounts.views import CustomTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView
from django.urls import path, include
from django.urls import path
from accounts.views import CustomTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView

from accounts.views import UserActivateView, UserSignUpView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("signup/", UserSignUpView.as_view(), name="signup"),
    path("activate/<str:uid64>/<str:token>/", UserActivateView.as_view(), name="activate"),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("api/", include("accounts.urls")),

    # 테스트때문에 넣은거
    path("api-auth/", include("rest_framework.urls")),
]
