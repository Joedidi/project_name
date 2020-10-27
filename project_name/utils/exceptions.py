# -*- coding:UTF-8 -*-
from __future__ import unicode_literals

import math

from django.db import transaction, connection
from django.http import JsonResponse, Http404
from django.utils import six
from django.utils.encoding import force_str
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext
from django.conf import settings

from rest_framework import status
from rest_framework.response import Response

from rest_framework import exceptions as rest_framework_exceptions


from django.core.exceptions import PermissionDenied as RestFrameWorkPermissionDenied
# from rest_framework.views import exception_handler


def _get_error_details(msg, code, data):
    return ErrorDetail(msg, code, data)


def _get_codes(detail):
    return detail.code


def _get_full_details(detail):
    return {
        'msg': detail.msg,
        'code': detail.code,
        'data': detail.data
    }


class ErrorDetail(six.text_type):
    """
    这是一个封装响应异常的类
    """
    msg = None
    code = None
    data = None

    def __init__(self, msg=None, code=None, data=None):
        self.msg = msg
        self.code = code
        self.data = data

    def __new__(cls, msg, code=None, data=None):
        self = super(ErrorDetail, cls).__new__(cls, msg)
        self.code = code
        self.data = data
        return self

    def __eq__(self, other):
        r = super().__eq__(other)
        try:
            return r and self.code == other.code
        except AttributeError:
            return r

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return 'ErrorDetail(msg=%r, code=%r)' % (
            self.msg,
            self.code,
        )


class APIException(Exception):
    """
    Base class for REST framework exceptions.
    Subclasses should provide `.status_code` and `.default_detail` properties.
    """
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_msg = _('A server error occurred.')
    default_code = 'error'
    default_data = None

    def __init__(self, msg=None, code=None, data=None):
        if msg is None:
            msg = self.default_msg
        if code is None:
            code = self.default_code
        if data is None:
            data = self.default_data
        self.detail = _get_error_details(msg, code, data)

    def __str__(self):
        return six.text_type(self.detail)

    def get_codes(self):
        """
        Return only the code part of the error details.

        Eg. {"name": ["required"]}
        """
        return _get_codes(self.detail)

    def get_full_details(self):
        """
        Return both the message & code parts of the error details.

        Eg. {"name": [{"message": "This field is required.", "code": "required"}]}
        """
        return _get_full_details(self.detail)


# The recommended style for using `ValidationError` is to keep it namespaced
# under `serializers`, in order to minimize potential confusion with Django's
# built in `ValidationError`. For example:
#
# from rest_framework import serializers
# raise serializers.ValidationError('Value was invalid')

class ValidationError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_msg = _('Invalid input.')
    default_code = 'invalid'
    default_data = None

    def __init__(self, msg=None, code=None, data=None):
        if msg is None:
            detail = self.default_msg
        if code is None:
            code = self.default_code
        if data is None:
            data = self.default_data

        # For validation failures, we may collect many errors together,
        # so the details should always be coerced to a list if not already.
        if not isinstance(msg, dict) and not isinstance(msg, list):
            msg = [msg]

        self.detail = _get_error_details(msg, code, data)


class ParseError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Malformed request.')
    default_code = 'parse_error'


class AuthenticationFailed(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = _('Incorrect authentication credentials.')
    default_code = 'authentication_failed'


class NotAuthenticated(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = _('Authentication credentials were not provided.')
    default_code = 'not_authenticated'


class PermissionDenied(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = _('You do not have permission to perform this action.')
    default_code = 'permission_denied'


class NotFound(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = _('Not found.')
    default_code = 'not_found'


class MethodNotAllowed(APIException):
    status_code = status.HTTP_405_METHOD_NOT_ALLOWED
    default_msg = _('Method "{method}" not allowed.')
    default_code = 'method_not_allowed'

    def __init__(self, method, msg=None, code=None):
        if msg is None:
            msg = force_str(self.default_msg).format(method=method)
        super().__init__(msg, code)


class NotAcceptable(APIException):
    status_code = status.HTTP_406_NOT_ACCEPTABLE
    default_msg = _('Could not satisfy the request Accept header.')
    default_code = 'not_acceptable'

    def __init__(self, msg=None, code=None, available_renderers=None):
        self.available_renderers = available_renderers
        super().__init__(msg, code)


class UnsupportedMediaType(APIException):
    status_code = status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
    default_msg = _('Unsupported media type "{media_type}" in request.')
    default_code = 'unsupported_media_type'

    def __init__(self, media_type, msg=None, code=None):
        if msg is None:
            msg = force_str(self.default_msg).format(media_type=media_type)
        super().__init__(msg, code)


class Throttled(APIException):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_msg = _('Request was throttled.')
    extra_detail_singular = _('Expected available in {wait} second.')
    extra_detail_plural = _('Expected available in {wait} seconds.')
    default_code = 'throttled'

    def __init__(self, wait=None, msg=None, code=None):
        if msg is None:
            msg = force_str(self.default_msg)
        if wait is not None:
            wait = math.ceil(wait)
            detail = ' '.join((
                msg,
                force_str(ngettext(self.extra_detail_singular.format(wait=wait),
                                   self.extra_detail_plural.format(wait=wait),
                                   wait))))
        self.wait = wait
        super().__init__(msg, code)


def server_error(request, *args, **kwargs):
    """
    Generic 500 error handler.
    """
    data = {
        'error': 'Server Error (500)'
    }
    return JsonResponse(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def bad_request(request, exception, *args, **kwargs):
    """
    Generic 400 error handler.
    """
    data = {
        'error': 'Bad Request (400)'
    }
    return JsonResponse(data, status=status.HTTP_400_BAD_REQUEST)


def set_rollback():
    atomic_requests = connection.settings_dict.get('ATOMIC_REQUESTS', False)
    if atomic_requests and connection.in_atomic_block:
        transaction.set_rollback(True)


def exception_handler(exc, context):
    """
    Returns the response that should be used for any given exception.

    By default we handle the REST framework `APIException`, and also
    Django's built-in `Http404` and `PermissionDenied` exceptions.

    Any unhandled exceptions may return `None`, which will cause a 500 error
    to be raised.
    """
    if isinstance(exc, Http404):
        exc = NotFound()
    elif isinstance(exc, RestFrameWorkPermissionDenied):
        exc = rest_framework_exceptions.PermissionDenied()

    if isinstance(exc, rest_framework_exceptions.APIException):
        headers = {}
        if getattr(exc, 'auth_header', None):
            headers['WWW-Authenticate'] = exc.auth_header
        if getattr(exc, 'wait', None):
            headers['Retry-After'] = '%d' % exc.wait

        if isinstance(exc.detail, (list, dict)):
            data = exc.detail
        else:
            data = {'detail': exc.detail}

        set_rollback()
        return Response(data, status=exc.status_code, headers=headers)
    if isinstance(exc, APIException):
        headers = {}
        if getattr(exc, 'auth_header', None):
            headers['WWW-Authenticate'] = exc.auth_header
        if getattr(exc, 'wait', None):
            headers['Retry-After'] = '%d' % exc.wait

        data = exc.get_full_details()
        return Response(data, status=exc.status_code, headers=headers)
    return None
    


class ErrorCodeException(APIException):
    status_code = status.HTTP_200_OK
    default_msg = _('调用成功')
    default_code = '0'


class TokenAuthcationError(ErrorCodeException):
    default_msg = _('Token认证失败')
    default_code = f'0x{settings.APP_ERROR_CODE}70003'


class UnknownError(ErrorCodeException):
    status_code = status.HTTP_200_OK
    default_msg = _('未知错误')
    default_code = f'0x{settings.APP_ERROR_CODE}30000'
    

class ParamsError(ErrorCodeException):
    default_msg = _('参数错误')
    default_code = f'0x{settings.APP_ERROR_CODE}30001'


class ApiPermissionError(ErrorCodeException):
    default_msg = _('api权限错误')
    default_code = f'0x{settings.APP_ERROR_CODE}30002'


class TicketNotValid(ErrorCodeException):
    default_msg = _('无效的 ticket')
    default_code = f'0x{settings.APP_ERROR_CODE}30003'


class UserNotActive(ErrorCodeException):
    default_msg = _('用户未激活或已删除')
    default_code = f'0x{settings.APP_ERROR_CODE}30004'
