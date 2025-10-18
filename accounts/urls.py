from django.urls import path
from .views import AccountListCreateView, AccountRetrieveDestroyView

urlpatterns = [
    path("accounts/", AccountListCreateView.as_view(), name="account-list-create"),
    path("accounts/<int:pk>/", AccountRetrieveDestroyView.as_view(), name="account-detail"),
]