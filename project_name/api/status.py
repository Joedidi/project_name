# -*- coding:UTF-8 -*-

from django.http import Http404
from rest_framework import viewsets

from {{ project_name }}.utils.decorators import api_action as action


class StatusViewSet(viewsets.ViewSet):
    """
    这是一个系统保活的接口类
    """
    permission_classes = ()
    authentication_classes = ()
        
    def list(self, request):
        """
        这是为了django能够载入ExeViewSet，没有实际用途
        :param request: 
        :return: 
        """
        return Http404

    @action(detail=False, methods=['GET'], interpretation='这是一个保活接口！')
    def keeplive(self, request):
        """
        这是一个保活接口
        :param request: 
        :return: 
        """
        return 'I.m alive!'
