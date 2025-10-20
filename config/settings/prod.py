import os

from config.settings.base import *  # noqa  # noqa

DEBUG = False
ALLOWED_HOSTS = ["*"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME", "viral_db"),
        "USER": os.getenv("DB_USER", "postgres"),
        "PASSWORD": os.getenv("DB_PASSWORD", "password1234"),
        "HOST": os.getenv("DB_HOST", "127.0.0.1"),  # docker-compose의 서비스명
        "PORT": os.getenv("DB_PORT", "5432"),
    }
}

# # 이메일 발송에 사용할 백엔드
# EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
#
# # SMTP 서버 주소 및 포트
# EMAIL_HOST = "smtp.gmail.com"
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True  # TLS 보안 연결 사용
#
# # Gmail 계정 정보 (앱 비밀번호 사용!)
# EMAIL_HOST_USER = "your_gmail_account@gmail.com"
# EMAIL_HOST_PASSWORD = "your_app_password"
#
# # 발신자 주소 (표시되는 이름)
# DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# Gmail은 보안 강화로 인해 일반 비밀번호로는 SMTP 접근이 막혀 있음.
# “앱 비밀번호”를 발급받아서 EMAIL_HOST_PASSWORD에 넣어야 함.
# Gmail 앱 비밀번호 발급 절차 (중요)
#
# Google 계정 설정
#  접속
#
# 좌측 메뉴에서 보안 → “Google에 로그인” 섹션 확인
#
# 2단계 인증을 활성화
#
# 앱 비밀번호 메뉴에 들어감
#
# 앱 종류 “메일”, 기기 “기타(예: Django)” 선택 후 생성
#
# 생성된 16자리 앱 비밀번호를 EMAIL_HOST_PASSWORD에 복사
#
# 보안상 주의점
#
# 절대 settings.py에 이메일 계정 비밀번호를 직접 하드코딩하면 안 돼.
# 보통 .env 파일을 만들어서 환경 변수로 관리해👇
#
# .env 파일
# EMAIL_HOST_USER=your_gmail_account@gmail.com
# EMAIL_HOST_PASSWORD=your_app_password
#
# settings.py (dotenv 사용)
# import os
# from dotenv import load_dotenv
# load_dotenv()
#
# EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
# EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
