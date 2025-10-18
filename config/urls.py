
from django.contrib import admin
from django.urls import path, include

from accounts.views import UserActivateView, UserSignUpView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("signup/", UserSignUpView.as_view(), name="signup"),
    path("activate/<str:uid64>/<str:token>/", UserActivateView.as_view(), name="activate"),
    path("api/", include("accounts.urls")),

    # 테스트때문에 넣은거
    path("api-auth/", include("rest_framework.urls")),
]
