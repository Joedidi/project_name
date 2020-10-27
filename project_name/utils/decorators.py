# -*- coding:UTF-8 -*-

from rest_framework.response import Response
from functools import wraps
# from rest_framework import decorators

from {{ project_name }}.utils.exceptions import ErrorDetail


def api_response(interpretation=None):
    """
    这是对请求同意封装的方法
    :param interpretation: 
    :return: 
    """
    
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            res = func(request, *args, **kwargs)
            msg = interpretation
            code = '0'
            if isinstance(res, Response):
                return res
            if isinstance(res, tuple):
                res_length = len(list(res))
                assert 1 <= res_length <= 3, (
                    "tuple length not right!"
                )
                if res_length == 2:
                    data, msg = res
                elif res_length == 3:
                    data, msg, code = res
                else:
                    data = res
            else:
                data = res
            return Response({
                'msg': msg,
                'code': code,
                'data': data
            })
        wrapper.bind_to_methods = func.bind_to_methods
        wrapper.url_path = func.url_path
        wrapper.url_name = func.url_name
        wrapper.detail = func.detail
        wrapper.kwargs = func.kwargs
        return wrapper
    return decorator


def api_action(detail=None, methods=None, url_name=None, url_path=None, interpretation=None, **kwargs):
    methods = ['get'] if (methods is None) else methods
    methods = [method.lower() for method in methods]

    assert detail is not None, (
        "@action() missing required argument: 'detail'"
    )

    def decorator(func):
        func.bind_to_methods = methods
        func.detail = detail
        func.url_path = url_path if url_path else func.__name__
        func.url_name = url_name if url_name else func.__name__.replace('_', '-')
        func.kwargs = kwargs
        return api_response(interpretation=interpretation)(func)
    return decorator
