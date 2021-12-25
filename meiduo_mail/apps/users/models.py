from django.db import models


# Create your models here.
# 第一种方式：自己定义模型
# 密码需要加密，登录的时候还要进行密码的验证
# class User(models.Model):
#     username = models.CharField(max_length=20, unique=True)
#     password = models.CharField(max_length=20)
#     mobile = models.CharField(max_length=11, unique=True)


# ------>使用系统自带的auth_user表
from django.contrib.auth.models import AbstractUser
# from django.contrib.auth.models import User   .user继承自AbstractUser


class User(AbstractUser):   # 继承自AbstractUser类
    mobile = models.CharField(max_length=11, unique=True)
    email_active = models.BooleanField(default=False, verbose_name='邮箱验证状态')

    class Meta:
        db_table = 'tb_users'   # 设置表名字
        verbose_name = '用户管理'   # 设定名称，后台管理系统显示
        verbose_name_plural = verbose_name   # 复数形式变为单数形式














