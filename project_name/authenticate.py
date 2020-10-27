# -*- coding:UTF-8 -*-

from datetime import datetime, timedelta

from django.core.cache import cache
from rest_framework.authentication import TokenAuthentication, get_authorization_header
from {{ project_name }}.models import AuthToken
from {{ project_name }}.utils import exceptions


class TokenAuthenticationHandler(TokenAuthentication):
    """
    Simple token based authentication.

    Clients should authenticate by passing the token key in the "Authorization"
    HTTP header, prepended with the string "Token ".  For example:

        Authorization: Token 401f7ac837da42b97f613d789819ff93537bee6a
    """

    model = AuthToken

    def authenticate(self, request):
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None

        if len(auth) == 1:
            msg = _('Invalid token header. No credentials provided.')
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = _('Invalid token header. Token string should not contain spaces.')
            raise exceptions.AuthenticationFailed(msg)

        try:
            token = auth[1].decode()
        except UnicodeError:
            msg = _('Invalid token header. Token string should not contain invalid characters.')
            raise exceptions.AuthenticationFailed(msg)

        return self.authenticate_credentials(token)

    def authenticate_credentials(self, key):
        cache_user =  cache.get(key)
        if cache_user:
            return key, cache_user
        model = self.get_model()
        try:
            token = model.objects.select_related('user').get(key=key)
            # 自定义处理相关数据
            time_now = datetime.now()
            if token:
                if token.started <= time_now <= token.expires:
                    if token.user.category == '0':
                        token.expires = time_now + timedelta(hours=12)
                    elif token.user.category == '1':
                        token.expires = time_now + timedelta(days=15)
                    else:
                        raise exceptions.AuthenticationFailed(_('user type invalid.'))
                    token.save()
                else:
                    raise exceptions.AuthenticationFailed(_('token expired.'))
                if token:
                    cache.set(key, token.user, 30 * 60)
                return token, token.user
            else:
                raise exceptions.AuthenticationFailed(_('Invalid token.'))
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed(_('Invalid token.'))


