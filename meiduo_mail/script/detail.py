#! /usr/bin/env python
# 设置django的环境
import sys
# 到我们的BASE_DIR下面 --- detail的上级目录
sys.path.insert(0, '../')

# 告诉os 我们的django的配置文件在哪里
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meiduo_mail.settings')

# django setup 相当于当前的文件有了django
import django
django.setup()

# #########  上面告诉该文件在django的环境中运行的 #####################

# 商品详情页
def generic_detail_html(sku):
    from utils.goods import get_categories, get_goods_specs, get_breadcrumb
    # try:
    #     sku = SKU.objects.get(id=sku_id)
    # except SKU.DoesNotExist:
    #     pass
    # 1.分类数据
    categories = get_categories()
    # 2.面包屑
    breadcrumb = get_breadcrumb(sku.category)
    # 3.SKU信息
    # 4.规格信息
    good_specs = get_goods_specs(sku)
    context = {
        'categories': categories,
        'breadcrumb': breadcrumb,
        'sku': sku,
        'specs': good_specs,
    }
    # return render(request, 'detail.html', context)
    # 1.加载模版
    from django.template import loader
    detail_template = loader.get_template('detail.html')
    # 2.模版渲染
    detail_html_data = detail_template.render(context)
    # 3.写入指定文件
    import os
    from meiduo_mail import settings
    file_path = os.path.join(os.path.dirname(settings.BASE_DIR), 'front_end_pc/goods/%s.html' % sku.id)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(detail_html_data)
    print(sku.id)

from apps.goods.models import SKU
skus = SKU.objects.all()
for sku in skus:
    generic_detail_html(sku)

"""
详情页面与首页的不同
详情页面的变化内容比较少，一般也就是修改商品的价格

1.详情页面 应该在上线的时候 统一都生成一遍
2.应该是运营人员修改的时候生成，（定时任务）
"""










