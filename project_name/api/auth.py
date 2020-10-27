# -*- coding:UTF-8 -*-
from datetime import timedelta, datetime

from django.core.cache import cache
from django.http import Http404
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from django.contrib.auth.models import User
from django.db.models import Model
from {{ project_name }}.models import AuthToken
from {{ project_name }}.utils import exceptions

from django.utils.translation import ugettext_lazy as _
from {{ project_name }}.utils import sdc_carrier_client

# -*- coding:UTF-8 -*-
from datetime import timedelta, datetime

from django.core.cache import cache
from django.http import Http404
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from django.contrib.auth.models import User
from django.db.models import Model
from django.db import models
from drf_cron.models import AuthToken
from drf_cron.utils import exceptions

from django.utils.translation import ugettext_lazy as _
from drf_cron.utils import sdc_carrier_client


class TokenViewSet(ViewSet):
    """
    这是一个认证的例子
    """

    @staticmethod
    def _process_user_info(user_info):
        """
        处理用户的信息
        :param user_info: 
        :return: 
        """
        if not user_info:
            return None
        _data = {
            'department': user_info.get('department'),
            'username': user_info.get('username'),
            'sex': user_info.get('sex'),
            'avatar': user_info.get('avatar'),
            'category': user_info.get('category') or False,
            'is_manager': user_info.get('is_manager') or 0,
            'is_active': user_info.get('is_active') or 0,
            'first_name': user_info.get('first_name'),
            'email': user_info.get('email'),
            'synced': datetime.now(),
            'short_name': user_info.get('short_name'),
        }
        user = None
        try:
            # 1. 遍历用户的锡尼希，增加用户没有的属性
            user = User.objects.filter(username=user_info.get("username"))
            for k, v in _data.items():
                if hasattr(k, user):
                    setattr(user, k, v)
            user.save()
        except Model.DoesNotExist:
            # 2. 没有用户信息则创建
            try:
                user = User(**_data)
                user.save()
            except Exception as e:
                print(e)
        except Exception as e:
            print(e)
            raise e
        finally:
            return user

    def list(self, request):
        """
        这是为了django能够载入ExeViewSet，没有实际用途
        :param request: 
        :return: 
        """
        return Http404

    @action(detail=False, methods=['GET'], interpretation='这是一个获取token的接口！')
    def get_token(self, request):
        """
        获取用力的token
        :param request: 
        :return: 
        """
        # 向注册中心请求用户信息
        user_data = sdc_carrier_client.verify_user_ticket(request.user.get('ticket'))
        user = self._process_user_info(user_data)

        if user and user.is_active:
            try:
                token = AuthToken.objects.filter(user=user)
                # 自定义处理相关数据
                time_now = datetime.now()
                if token.started > time_now or token.expires < time_now:
                    if cache.has_key(token.key):
                        cache.delete(token.key)
                    token.delete()
                token = AuthToken(user=user)
            except AuthToken.DoesNotExist:
                token = AuthToken(user=user)
            except:
                token = None
            if token:
                if token.user.category == '0':
                    token.expires = datetime.now() + timedelta(hours=12)
                elif token.user.category == '1':
                    token.expires = datetime.now() + timedelta(days=15)
                else:
                    token.expires = datetime.now()
                token.save()
                cache.set(token.key, user, 30 * 60)
                return token.key
        elif user and user.is_active:
            AuthToken.objects.filter(user=user).delete()
            raise exceptions.AuthenticationFailed(_('User inactive or deleted.'))
        else:
            raise exceptions.AuthenticationFailed(_('Invalid ticket.'))


class UserViewSet(ViewSet):
    """
    这是一个
    """

    @action(detail=False, methods=['GET'], interpretation='这是一个获取用户信息的接口')
    def get_user_info(self, request):
        try:
            user_info = User.objects.filter(username=request.username).values()[0]
        except User.DoesNotExist:
            raise exceptions.ParamsError('用户不存在')
        return user_info


class DomeViewSet(ViewSet):
    """
    这是一个简单的demo
    """

    @action(detail=False, methods=['GET'], interpretation='这是一个hello world的demo')
    def demo_hello_world(self, request):
        res = {
            'code': '0',
            'msg': 'success',
            'data': 'hello world!'
        }
        return Response(status=res['code'], data=res)