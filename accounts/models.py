from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from .constants import BANK_CODES, ACCOUNT_TYPE


# 유저 매니저
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        return self.create_user(email, password, **extra_fields)


# 유저 모델
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True, verbose_name="이메일")
    password = models.CharField(max_length=255, verbose_name="비밀번호")
    nickname = models.CharField(max_length=50, verbose_name="닉네임")
    name = models.CharField(max_length=50, verbose_name="이름")
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="전화번호")
    last_login = models.DateTimeField(auto_now=True, verbose_name="마지막 로그인")
    is_staff = models.BooleanField(default=False, verbose_name="관리자 권한")
    is_active = models.BooleanField(default=True, verbose_name="활성화 상태")

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nickname", "name"]

    def __str__(self):
        return self.email


class Account(models.Model):
    account_id = models.AutoField("계좌ID", primary_key=True)
    account_number = models.CharField("계좌번호", max_length=20, unique=True)
    bank_code = models.CharField("은행코드", max_length=10, choices=BANK_CODES)
    account_type = models.CharField("계좌종류", max_length=20, choices=ACCOUNT_TYPE)
    balance = models.DecimalField("잔액", decimal_places=2, max_digits=18)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = '계좌'
        verbose_name_plural = '계좌 목록'
        db_table = 'accounts'
        ordering = ['-account_id']

    def __str__(self):
        return self.account_number