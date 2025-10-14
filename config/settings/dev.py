import os

DEBUG = True
ALLOWED_HOSTS = ["127.0.0.1", "localhost", "0.0.0.0"]


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv("MYSQL_DATABASE", "viral_db"),
        "USER": os.getenv("MYSQL_USER", "root"),
        "PASSWORD": os.getenv("MYSQL_PASSWORD", ""),
        "HOST": os.getenv("DB_HOST", "db"),  # docker-compose의 서비스명
        "PORT": os.getenv("DB_PORT", "3306"),
        "OPTIONS": {"init_command": "SET sql_mode='STRICT_ALL_TABLES'"},
    }
}
