# -*- coding:UTF-8 -*-

from __future__ import unicode_literals

from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.db import models

from rest_framework.authtoken.models import Token
from django.utils.translation import ugettext_lazy as _


class AuthToken(Token):
    """
    这是一个token的类
    """
    started = models.DateTimeField(_('started'), auto_now_add=True, blank=True)
    expires = models.DateTimeField(_('expires'), null=True)


class ProfileUserMetaclass(type):
    """
    用户元类
    """
    def __new__(cls, name, bases, attrs):
        if name == 'Model':
            return type.__new__(cls, name, bases, attrs)
        fields = []
        for obj_name, obj in attrs.items():
            if isinstance(obj_name, models.Field):
                fields.append(obj_name)
            User.add_to_class(obj_name, obj)
        UserAdmin.fieldsets = list(UserAdmin.fieldsets)
        UserAdmin.fieldsets.append((name, {"fields": fields}))
        return type.__new__(cls, name, bases, attrs)


class ProfileUser(object, metaclass=ProfileUserMetaclass):
    GENDER = (
        ('m', '男'),
        ('W', '女')
    )
    USER_CATEGORY = (
        ('0', '自然人'),
        ('1', '系统')
    )
    department = models.CharField(_('department'), max_length=255, blank=True, null=True)
    synced = models.DateTimeField(_('synced'), null=True)
    short_name = models.CharField(_('department'), max_length=16, blank=True, null=True)
    avatar = models.TextField(_('avatar'), null=True)
    category = models.CharField(_('category'), choices=USER_CATEGORY, max_length=16, blank=True)
    sex = models.CharField(_('sex'), choices=GENDER, max_length=2, blank=True)
    
    def display_department(self):
        pass


class Base(models.Model):
    """
    基类，后面所有的类的创建都要继承这个类
    """
    creator = models.CharField(verbose_name='创建人', max_length=50, blank=False, null=False)
    last_mender = models.CharField(verbose_name='最后修改人', max_length=50, blank=False, null=False)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True, blank=True)
    last_modified_time = models.DateTimeField(verbose_name='最后修改时间', auto_now=True, blank=True)

    class Meta:
        abstract = True
