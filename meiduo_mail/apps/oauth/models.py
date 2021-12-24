from django.db import models
from utils.models import BaseModel
# Create your models here.
class OAuthQQUser(BaseModel):
    """QQ用户登录数据"""
    # 外键关联的时候 注意此处关联其他app的模型类的时候，需要使用 app.模型类名称的方式
    # user字段创立的时候就是 user名称_关联的主键
    # user 为固定 User的小写 ---
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, verbose_name='用户')
    openid = models.CharField(max_length=64, verbose_name='openid', db_index=True)
    class Meta:
        # 表名字的设置
        db_table = 'tb_oauth_qq'
        # admin管理界面显示的名称
        verbose_name = 'QQ登录用户数据'
        verbose_name_plural = verbose_name





















