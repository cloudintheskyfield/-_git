from django.db import models
class BaseModel(models.Model):
    """为下面的模型类补充字段"""
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    class Meta:
        # 说明是抽象模型类，用于继承使用，数据库迁移的时候不会创建BaseModel的表
        abstract = True