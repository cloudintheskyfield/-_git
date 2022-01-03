from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection

"""
需求：提交订单页面的显示
前端：发送一个axios请求来获取，地址信息和购物车中选中商品的信息
后端：
    请求：必须是登录用户才可以访问
    业务逻辑：地址信息，购物车中商品的信息
    响应：JSON
    路由：GET  orders/settlement/
    步骤：
        1.获取用户信息
        
        2.地址信息
        2.1 查询用户的地址信息 [address,address...]
        2.2 将对象数据转换为字典数据
        
        3.购物车中选中商品的信息
        3.1 连接redis
        3.2 hash    {sku_id:count, sku_id:count}
        3.3 set     [1,2]
        3.4 重新组织一个 选中的信息
        3.5 根据商品的id 查询商品的具体信息 [SKU,SKU..]
        3.6 需要将对象数据转换为字典数据
        
        4.返回响应
        
    
"""
from django.views import View
from utils.views import LoginRequiredJSOMixin
from apps.users.models import Address
from apps.goods.models import SKU
class OrderSettlementView(LoginRequiredJSOMixin, View):
    def get(self, request):
        # 1.获取用户信息
        user = request.user
        # 2.地址信息
        # 2.1 查询用户的地址信息[address, address...]
        addresses = Address.objects.filter(is_deleted=False)
        # 2.2 将对象数据转换为字典数据
        addresses_list = []
        for address in addresses:
            addresses_list.append({
                'id': address.id,
                'province': address.province.name,
                'city': address.city.name,
                'district': address.district.name,
                'place': address.place,
                'receiver': address.receiver,
                'mobile': address.mobile,

            })
        # 3.购物车中选中商品的信息
        # 3.1 连接redis
        redis_cli = get_redis_connection('carts')
        pipeline = redis_cli.pipeline()
        # 3.2 hash
        pipeline.hgetall('carts_%s' % user.id)  # 接收管道，统一执行后返回结果 result = pipeline.execute() result: []
        # {sku_id: count, sku_id: count}
        # 3.3 set[1, 2]
        pipeline.smembers('selected_%s' % user.id)
        result = pipeline.execute()     # 在这里接收结果！！！
        sku_id_counts = result[0]
        selected_ids = result[1]

        # 3.4 重新组织一个 选中的信息
        # selected_carts = {sku_id:count}
        selected_carts = {}
        for sku_id in selected_ids:
            selected_carts[int(sku_id)] = int(sku_id_counts[sku_id])

        # 3.5 根据商品的id 查询商品的具体信息[SKU, SKU..]
        sku_list = []
        for sku_id,count in selected_carts.items(): # .item()为固定写法
            sku = SKU.objects.get(pk=sku_id)  # 根据主键查询
            # 3.6 需要将对象数据转换为字典数据
            sku_list.append({
                'id':sku.id,
                'name': sku.name,
                'count': count,
                'default_image_url': sku.default_image.url,
                'price': sku.price,
            })
        # 4.组织前端需要的数据
        context = {
            'skus': sku_list,
            'addresses': addresses_list,
            'freight': 10,      # 运费 单独返回

        }
        # 4.返回响应
        return JsonResponse({'code': 0, 'errmsg': 'ok', 'context': context})
        pass















