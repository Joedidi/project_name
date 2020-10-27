# -*- coding:UTF-8 -*-

from django.urls import path
from django.conf.urls import include
from rest_framework.routers import DefaultRouter

from {{ project_name }}.api.status import StatusViewSet


router = DefaultRouter()

router.register(r'status', StatusViewSet, base_name='status')

urlpatterns = [
    path('api/', include(router.urls)),
]



