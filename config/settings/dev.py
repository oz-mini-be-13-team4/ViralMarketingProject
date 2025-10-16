import os

DEBUG = True
ALLOWED_HOSTS = ["127.0.0.1", "localhost", "0.0.0.0"]


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME", "viral_db"),
        "USER": os.getenv("DB_USER", "postgres"),
        "PASSWORD": os.getenv("DB_PASSWORD", "password1234"),
        "HOST": os.getenv("DB_HOST", "db"),  # docker-compose의 서비스명
        "PORT": os.getenv("DB_PORT", "5432"),
    }
}
