import re

from django.conf import settings
from django.contrib import admin
from django.core.exceptions import ImproperlyConfigured
from django.urls import include, path, re_path
from django.views.static import serve
from rest_framework_simplejwt.views import TokenRefreshView

from accounts.views import (
    CustomTokenObtainPairView,
    LogoutView,
    UserActivateView,
    UserDeleteAPIView,
    UserDetailAPIView,
    UserSignUpView,
    UserUpdateAPIView,
)


def static(prefix, view=serve, **kwargs):
    if not prefix:
        raise ImproperlyConfigured("Empty static prefix not permitted")
    return [
        re_path(r"^%s(?P<path>.*)$" % re.escape(prefix.lstrip("/")), view, kwargs=kwargs),
    ]


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
    path("profile/", UserDetailAPIView.as_view(), name="user-detail"),
    path("profile/update/", UserUpdateAPIView.as_view(), name="user-update"),
    path("profile/delete/", UserDeleteAPIView.as_view(), name="user-delete"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
