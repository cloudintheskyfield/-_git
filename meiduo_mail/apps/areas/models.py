from django.db import models

# Create your models here.
from django.db import models
"""
省市区：

id      name        parent_id
10000   河北省       NULL
10100   保定市       10000
10200   石家庄市     10000
10300   唐山市       10000

10101   雄县         10100
10102   安新县       10100

查询省份信息：
    mysql> select * from tb_areas where parent_id is NULL;
查询市：
    mysql> select * from tb_areas where parent_id = 130000;
查询县：
    mysql> select * from tb_areas where parent_id = 130100;
    
shell中查询省:
    >>> Area.objects.filter(parent=None)
    >>> Area.objects.filter(parent_id__isnull=True)
    >>> Area.objects.filter(parent__isnull=True)
shell中查询市
    >>> Area.objects.filter(parent=130000)
    >>> Area.objects.filter(parent_id=130000)

    >>> province = Area.objects.get(id=130000)
    >>> province.subs.all()
shell中查询县
    >>> city = Area.objects.get(id=130100)
    >>> city.subs.all()


"""

class Area(models.Model):
    name = models.CharField(max_length=20, verbose_name='名称')
    # 关键关联类型为自己关联自己
    parent = models.ForeignKey('self', on_delete=models.SET_NULL,
                               related_name='subs', null=True, blank=True, verbose_name='上级行政区划')

    # related_name 关联的模型的名字---> 改变area_set为subs，之后可以通过省份获取市，通过市获取县
    # 默认是 关联模型类名小写_set      area_set
    # 我们可以通过related_name 修改默认是名字，现在就改为了subs
    class Meta:
        db_table = 'tb_areas'
        verbose_name = '省市区'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name










