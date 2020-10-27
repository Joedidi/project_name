#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
from {{ project_name }}.settings import BASE_DIR



# 数据库配置
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

AUTO_SERVER_ENDPOINT = '127.0.0.1:10101'
AUTO_SERVER_CLIENT_ID = '*************************************'
AUTO_SERVER_CLIENT_SECRET = '*************************************'

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {"max_connections": 100}
            # "PASSWORD": "密码",
        }
    }
}
