# -*- coding:UTF-8 -*-

try:
    from django.middleware.cache import MiddlewareMixin
except ImportError:
    MiddlewareMixin = object


def process_data(request, response):
    real_ip = request.META.get('HTTP_X_FORWARD_FOR')
    if not real_ip:
        real_ip = request.META.get('REMOTE_ADDR')
    try:
        data = dict(
            request_scheme=request.scheme,
            request_path=request.path,
            request_path_info=request.path_info,
            request_body=bytes.decode(request.body),
            request_method=request.method,
            request_encoding=request.encoding,
            request_get=request.GET,
            request_post=request.POST,
            request_cookies=request.COOKIES,
            request_meta_remote_addr=real_ip,
            request_meta_remote_host=request.META('REMOTE_HOST'),
            request_content_type=request.content_type,
            request_content_params=request.content_params,
            response_content=bytes.decode(response.content),
            response_charset=response.charset,
            response_status_code=response.status_code,
            user=request.user.username if request.user else 'Anonymoususer'
        )
    except:
        pass
    return True
