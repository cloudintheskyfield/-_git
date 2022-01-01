import time

from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
"""
关于模型的分析
1.根据页面效果 尽量多的分析字段
2.去分析是保存在一个表中 还是多个表中（多举例说明）
分析表的关系的时候 最多不要超过3个表

多对多（一般是3个表）

学生和老师（多对多）
学生表
stu_id          stu_name
100             张三
200             李四

老师表
teacher_id      teacher_name
666             牛老师
999             齐老师

第三张表
stu_id          teacher_id
100             666
100             999
200             666
200             999

商品day01：
    商品模型的分析--->Fdfs（用于保存图片，视频等文件）--->为了部署Fdfs学习Docker

"""

# 上传图片的代码------------------------
# from fdfs_client.client import Fdfs_client
# 1.创建客户端
# 修改加载配置文件的路径
# client = Fdfs_client(r'utils/fastdfs/client.conf')
# client = Fdfs_client(r'/Users/mac/PycharmProjects/35_美多商城/-_git/meiduo_mail/utils/fastdfs/client.conf')

# 2.上传图片
# 图片的绝对路径
# client.upload_by_filename('/Users/mac/Desktop/img/superwoman.jpg')

# 3.获取file_id   upload_by_filename上传成功会返回字典数据 字典数据中有file_id


# 首页商品展示的实现
from django.views import View
from utils.goods import get_categories
from apps.contents.models import ContentCategory


class IndexView(View):
    def get(self, request):
        """
        首页的数据分为2部分：
        1部分是商品分类数据
        2部分是广告数据
        """
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
        # 模版使用比较少，以后到公司自然就会了
        return render(request, 'index.html', context)


"""
需求：
    根据点击的分类来获取分类数据（有排序有分页）
前端：
    前端会发送一个axios中，分类id在路由中
    分页的页码（第几页数据），每页多少条数据，排序也会传递过来
后端：
    请求：接收参数
    业务逻辑：根据需求查询数据，将对象数据转换为字典数据，返回响应
    响应：JSON
    
    路由：GET      /list/category_id/skus/
    步骤：
        1.接收参数
        2.获取分类id
        3.根据分类id进行分类数据的查询验证
        4.获取面包屑数据
        5.查询分类对应的sku数据，然后排序，然后分页
        6.返回响应
"""
from apps.goods.models import GoodsCategory, SKU
from utils.goods import get_breadcrumb


# 显示手机页面的数据
class ListView(View):
    def get(self, request, category_id):
        # 1.接收参数
        # 排序字段
        ordering = request.GET.get('ordering')
        # 每页多少条数据
        page_size = request.GET.get('page_size')
        # 第几页数据
        page = request.GET.get('page')
        # 2.获取分类id---在路由中
        # 3.根据分类id进行数据的查询验证
        try:
            category = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return JsonResponse({'code': 400, 'errmsg': '参数缺失'})
        # 4.获取面包屑数据---面包屑数据需要传入一个商品对象（面包屑会进行判断是否存在父级对象）
        breadcrumb = get_breadcrumb(category)
        # 5.根据 分类 查询对应的sku数据，然后排序，然后分页
        # 该处为三级分类中查询到的对应的手机页面
        skus = SKU.objects.filter(category_id=category.id, is_launched=True).order_by(ordering)
        # 分页
        from django.core.paginator import Paginator
        # paginator对象的建立
        paginator = Paginator(skus, per_page=page_size)  # skus为数据，page_size为每页数据多少条
        # 第几页---返回当前页的信息---一个page对象建立
        page_skus = paginator.page(page)
        # 将对象转换为字典数据
        sku_list = []
        # page_skus.object_list 为当前页上所有数据的列表
        for sku in page_skus.object_list:
            # sku列表中的这几个元素可以在前端的html中看到
            sku_list.append({
                'id': sku.id,
                'name': sku.name,
                'price': sku.price,
                # 该处的sku.default_image.url访问默认存储类的url方法
                'default_image_url': sku.default_image.url
            })
        # 获取总页码  分页后的页面总数 ---有几页 paginator.num+pages固定写法
        total_num = paginator.num_pages
        # 6.返回响应
        return JsonResponse({
            'code': 0,
            'errmsg': 'ok',
            'list': sku_list,
            'count': total_num,
            'breadcrumb': breadcrumb,

        })


# TODO 热销排行

# ##############################搜索功能的实现#################
"""
搜索：
1.不实用like
2.使用全文检索
3.全文检索需要配合搜索引擎来实现
4.搜索引擎

原理：对数据进行拆分
我爱北京天安门                 我爱，北京，天安门
王红姑娘，我内里挂念你             王红姑娘，我爱你，睡不着觉，挂念你
我夜里睡不着觉                 我，睡不着觉，夜里

5.Elasticsearch
进行分词操作，将一句话拆分为多个单词或字
6.数据  <--------Haystack---------> elasticsearch

"""

"""
数据《---haystack---》elasticsearch
借助于haystack帮助我们查询数据
"""
from haystack.views import SearchView


# 该搜索类继承自SearchView没有as_view()方法
class SKUSearchView(SearchView):
    # 该方法取自SearchView中的源码
    def create_response(self):
        # 获取搜索的结果---抄写SearchView中的源代码，产生响应返回给服务器
        # 理解为context为 haystack 对接 elasticSearch后查询到的 响应结果
        context = self.get_context()
        # 该如何知道context中有那些数据呢
        # 添加断点来进行分析---调试问题，解决问题
        sku_list = []
        # 利用断点查到 获取商品列表为 context['page'].object_list
        for sku in context['page'].object_list:
            sku_list.append({
                # 前4个为context下page中的内容
                'id': sku.object.id,
                'name': sku.object.name,
                'price': sku.object.price,
                # 该处的url为访问fastfds中storage的方法
                'default_image_url': sku.object.default_image.url,
                # 下面三个为context下的内容---------------------------
                'searchkey': context.get('query'),
                'page_size': context['page'].paginator.num_pages,  # 当前页面页码
                'count': context['page'].paginator.count  # 查询到的结果数量
            })
        # 这里后端需求的数据中，只需求了相关数据，并没有要求code和errmsg
        return JsonResponse(sku_list, safe=False)


"""
需求：详情页面
    1.分类数据
    2.面包屑
    3.SKU信息
    4.规格信息
    
    我们的详情也是静态化实现的，但是我们在讲解静态话之前，应该可以先把详情页面的数据展示出来
"""
# 最后一个为规格信息
from utils.goods import get_categories, get_breadcrumb, get_goods_specs


class DetailView(View):
    def get(self, request, sku_id):
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            pass
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
        return render(request, 'detail.html', context)



"""
需求：
    统计每一天的分类商品访问量
前端：
    当访问具体的页面的时候，会发送一个axios请求，携带分类id
后端：
    请求：接收请求，获取参数
    业务逻辑：查询有没有，有的话更新数据，没有的话新建数据
    响应：返回JSON响应
    
    路由：POST 新增数据  detail/visit/<category_id>/
    步骤：
        1.接收分类id
        2.验证参数（验证分类id）
        3.查询当天 这个分类的记录有没有
        4.没有 新建数据
        5.有的话更新数据
        6.返回响应
        
"""
























