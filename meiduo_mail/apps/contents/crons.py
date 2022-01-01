"""
首页，详情页面
都是先查询数据库的数据---将数据库的数据放入redis中进行缓存---通过ajax动态发送请求去获取数据（一部分数据）
然后再进行HTML页面的渲染

不管是数据库的数据缓存还是HTML页面的渲染（特别是分类渲染，比较慢） 多少都会影响用户的体验

最好的体验是：用户直接就可以访问到经过数据库查询，已经渲染的HTML页面--------》称之为静态化---》

我们经过数据库查询，已经渲染的HTML页面，写入到指定的目录
"""

# 这个函数能够帮助我们查询数据库，渲染HTML页面，然后将渲染的HTML写入到指定文件
def generic_meiduo_index():
    # 注意在python manage.py shell 里调用的时候一定要将导入的包放在函数内部
    import time
    import os
    from pathlib import Path
    from meiduo_mail import settings
    from django.template import loader
    from utils.goods import get_categories
    from apps.contents.models import ContentCategory

    # 该处需要加一个print否则不会打印日志中的时间
    print('----------------%s-----------------' % time.ctime())
    # 1.商品数据
    categories = get_categories()
    # 2.广告数据
    contents = {}
    content_categories = ContentCategory.objects.all()
    for cat in content_categories:
        contents[cat.key] = cat.content_set.filter(status=True).order_by('sequence')

    # 我们的首页后面会讲解 页面静态化
    # 我们将数据 传递给模版---这里是首页渲染去实现的
    context = {
        'categories': categories,
        'contents': contents,
    }
    # 未渲染之前的方式
    # return render(request, 'index.html', context)

    # render就是渲染
    # 1.加载渲染的模版
    index_template = loader.get_template('index.html')  # 拿到templates下的模版
    # 2.把数据给模版
    index_html_data = index_template.render(context)
    # 3.把渲染好的HTML写入到指定文件
    # BASE_DIR的上一级----页面渲染到指定位置
    # file_path = os.path.join(Path(__file__).resolve().parent.parent.parent, 'front_end_pc/index.html')
    file_path = os.path.join(os.path.dirname(settings.BASE_DIR), 'front_end_pc/index.html')
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(index_html_data)
















