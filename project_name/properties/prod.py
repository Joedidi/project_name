#!/usr/bin/python
# -*- coding: UTF-8 -*-


# 调试模式开关
DEBUG = False

# 相关需要对接的服务器信息

# 数据库配置
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',  # 引擎，选mysql
        'NAME': '******',  # 要连接的数据库，连接前需要创建好
        'USER': '******',  # 连接数据库的用户名
        'PASSWORD': '******',  # 连接数据库的密码
        'HOST': '127.0.0.1',  # 连接主机，默认本本机
        'PORT': 3306,  # 端口 默认3306
        # Django中设置数据库的严格模式
        'OPTIONS': {
            'init_command': "set sql_mode='STRICT_TRANS_TABLES' ",
        }
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
