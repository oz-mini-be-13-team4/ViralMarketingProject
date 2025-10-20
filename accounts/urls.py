from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AccountListCreateView, AccountRetrieveDestroyView, TransactionViewSet

router = DefaultRouter()
router.register(r"transactions", TransactionViewSet, basename="transaction")

urlpatterns = [
    path("accounts/", AccountListCreateView.as_view(), name="account-list-create"),
    path("accounts/<int:pk>/", AccountRetrieveDestroyView.as_view(), name="account-detail"),
    path("", include(router.urls)),
]
