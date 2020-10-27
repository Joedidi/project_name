# -*- coding:UTF-8 -*-

import logging

from django.http import Http404
from rest_framework.viewsets import ViewSet
from {{ project_name }}.utils.exceptions import ParamsError


class MainViewSet(ViewSet):
    """
    这是一个系统测试的接口类
    """
    permission_classes = ()
    authentication_classes = ()

    def list(self, request):
        """
        这是为了djangp能够载入ExeViewSet，没有实际用途
        :param request: 
        :return: 
        """
        return Http404

    def hello_world(self, request):
        """
        这是一个保活接口
        :param request: 
        :return: 
        """
        return 'hello world!'

    def exception_demo(self, request):
        """
        这是一个异常调用的例子
        :param request: 
        :return: 
        """
        return ParamsError("这是一个异常调用的例子")

    def log_demo(self, request):
        """
        这是一个日志调用的例子
        :param request: 
        :return: 
        """
        logging.info("这是一个日志调用的例子")
        return '这是一个日志调用的例子'
