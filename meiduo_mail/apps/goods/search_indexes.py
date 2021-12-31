from apps.goods.models import SKU
from haystack import indexes

"""
0.我们需要在模型对应的子应用中创建search_indexes.py文件，以方便进行检索
1.索引类必须继承自 indexes.SearchIndex, indexes.Indexable
2.必须定义一个字段，document=True
    字段的名    起什么都可以，text只是惯例（大家习惯都这么起名字）。所有的索引类（这个字段都一致就可以）
3.use_template=True
    允许我们设置一个字段那些需要进行检索
    
    这个单独的文件加创建在哪里呢？
    模版文件夹下/search/indexes/子应用目录/模型类名小写_text.txt
    
    数据<---haystack--->elasticsearch
    运作：应该让haystack将数据获取到给es来生成索引
    在虚拟环境下 python manage.py rebuild_index
"""
class SKUIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        return SKU

    def index_queryset(self, using=None):

        # return self.get_model().objects.all() 这两种方式都可以
        return SKU.objects.all()

















