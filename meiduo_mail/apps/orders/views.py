import json

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
        result = pipeline.execute()  # 在这里接收结果！！！
        sku_id_counts = result[0]
        selected_ids = result[1]

        # 3.4 重新组织一个 选中的信息
        # selected_carts = {sku_id:count}
        selected_carts = {}
        for sku_id in selected_ids:
            selected_carts[int(sku_id)] = int(sku_id_counts[sku_id])

        # 3.5 根据商品的id 查询商品的具体信息[SKU, SKU..]
        sku_list = []
        for sku_id, count in selected_carts.items():  # .item()为固定写法
            sku = SKU.objects.get(pk=sku_id)  # 根据主键查询
            # 3.6 需要将对象数据转换为字典数据
            sku_list.append({
                'id': sku.id,
                'name': sku.name,
                'count': count,
                'default_image_url': sku.default_image.url,
                'price': sku.price,
            })
        # 4.组织前端需要的数据
        from decimal import Decimal
        freight = Decimal('10')
        """
        decimal：货币类型--->很特殊--->字符串的形式保存数据--->钱方面的一般都是decimal类型
        
        01010101
        整数比较方便保存
        小数的保存比较 特殊，小数分开存储
        12.5
        12 0.5
        1100 1
        
        12.33
        12 0.33
        0.33不断乘以2知道得到1，无限循环，会有部分缺失（会省略一部分）
        """

        context = {
            'skus': sku_list,
            'addresses': addresses_list,
            'freight': freight,  # 运费 单独返回

        }
        # 4.返回响应
        return JsonResponse({'code': 0, 'errmsg': 'ok', 'context': context})
        pass


"""
需求：点击提交订单，生成订单
前端：发送axios请求，POST 携带数据给后端
后端：
    请求：接收请求，验证数据
    业务逻辑：数据入库
    响应：返回响应
    路由：POST
    步骤：
        1.接收数据  前端需要传user,address_id, pay_method 
        2.验证数据
        order_id为主键自己生成
        拿取总数量/总金额的时候，需要遍历redis拿取数据。在后面遍历的时候改变这两个值！先赋值0
        total_count,total_amount,freight
        支付状态由支付方式来决定的
        
        3.数据入库  生成订单（订单基本信息表和订单商品信息表）
            订单基本信息表
            订单商品信息表
            3.1 先订单基本信息，再商品信息---有基本信息的外键（先基本信息）
            
            3.2 订单商品信息
            3.3 连接redis
            3.4 获取hash
            3.5 获取set
            3.6 最好重新组织一个数据，这个数据为选中的商品信息
            3.7 根据选中商品的id进行查询
            4.8 判断库存是否充足
            4.9 如果充足，库存减少，销量增加
            5.0 如果不充足，下单失败
            
            5.1 累加总数量和总金额
            
            5.2 保存订单商品信息
            5.3 更新订单的总金额和总数量
            
            5.4 将redis中选中的商品信息移除
        6.返回响应
    
"""
from apps.orders.models import OrderInfo, OrderGoods
from django.db import transaction

class OrderCommitView(LoginRequiredJSOMixin, View):
    def post(self, request):
        user = request.user
        # 1.接收数据
        data = json.loads(request.body.decode())
        # 前端需要传user, address_id, pay_method
        address_id = data.get('address_id')
        pay_method = data.get('pay_method')

        # 2.验证数据
        if not all([address_id, pay_method]):
            return JsonResponse({'code': 400, 'errmsg': '参数不全'})
        try:
            address = Address.objects.get(id=address_id)
        except Address.DoesNotExist:
            return JsonResponse({'code': 400, 'errmsg': '地址不正确'})
        # 这样写没有问题，就是代码的可读性差
        # if pay_method not in [1,2]:
        if pay_method not in [OrderInfo.PAY_METHODS_ENUM['CASH'], OrderInfo.PAY_METHODS_ENUM['ALIPAY']]:
            return JsonResponse({'code': 400, 'errmsg': '参数不正确'})

        # order_id为主键自己生成
        from django.utils import timezone
        from datetime import datetime
        # datetime.strftime() 与下面的效果一样
        # Year month day Hour Minutes Second %f为微秒  订单id根据现在的时间来生成+用户id，避免秒杀重复
        order_id = timezone.localtime().strftime('%Y%m%d%H%M%S%f') + '%09d' % user.id

        #     拿取总数量 / 总金额的时候，需要遍历redis拿取数据。在后面遍历的时候改变这两个值！先赋值0
        #     total_count, total_amount, freight
        #     支付状态由支付方式来决定的
        # if pay_method == 1:    # 货到付款
        #     pay_status = 2
        if pay_method == OrderInfo.PAY_METHODS_ENUM['CASH']:
            status = OrderInfo.ORDER_STATUS_ENUM['UNSEND']
        else:
            status = OrderInfo.ORDER_STATUS_ENUM['UNPAID']
        # 总数量，总金额，运费
        from decimal import Decimal
        total_count = 0
        total_amount = Decimal('0')  # 总金额
        freight = Decimal('10.00')

        # 使用事务
        with transaction.atomic():
            point = transaction.savepoint()  # 事务的开始点/回滚点
            # 3.数据入库
            # 1.订单基本信息表 生成订单（订单基本信息表和订单商品信息表）
            order_info = OrderInfo.objects.create(
                order_id=order_id,
                user=user,
                address=address,
                total_count=total_count,
                total_amount=total_amount,
                freight=freight,
                pay_method=pay_method,
                status=status,
            )

            # 订单商品信息
            # 3.1 先订单基本信息，再商品信息 - --有基本信息的外键（先基本信息）
            # 3.2 订单商品信息
            # 3.3 连接redis
            redis_cli = get_redis_connection('carts')
            # 3.4 获取hash   {cart_%s{sku_id:count}} ===》{sku_id:count}
            sku_id_counts = redis_cli.hgetall('carts_%s' % user.id)
            # 3.5 获取set [1, 2]
            selected_ids = redis_cli.smembers('selected_%s' % user.id)
            # 3.6 最好重新组织一个数据，这个数据为选中的商品信息 {sku_id:count}
            carts = {}
            for sku_id in selected_ids:
                carts[int(sku_id)] = int(sku_id_counts[sku_id])

            # 3.7 根据选中商品的id进行查询
            for sku_id, count in carts.items():
                sku = SKU.objects.get(id=sku_id)
                # 3.8 判断库存是否充足,如果不充足，下单失败
                if sku.stock < count:

                    # 回滚点
                    transaction.savepoint_rollback(point)

                    return JsonResponse({'code': 400, 'errmsg': '库存不足'})

                # 3.9 否则库存充足
                ########### 睡眠---并发的模拟 #########
                from time import sleep
                sleep(10)
                ############ 乐观锁 ##############
                # 1.先记录一个数据 什么数据都可以 参照这个记录
                old_stock = sku.stock
                # 2.更新的时候，对比一下记录对不对
                new_stock = sku.stock - count
                new_sales = sku.sales + count
                # 3.如果 库存等于之前的库存
                result = SKU.objects.filter(id=sku_id, stock=old_stock).update(stock=new_stock, sales=new_sales)
                # result = 1 表示有1条记录修改成功  result = 0 表示没有更新
                if result == 0:
                    # 回滚事务 下单失败
                    transaction.savepoint_rollback(point)
                    return JsonResponse({'code': 400, 'errmsg': '下单失败----------'})


                # 3.9 如果充足，库存减少，销量增加
                # sku.stock -= count
                # sku.sales += count
                # sku.save()
                # 5.1 累加总数量和总金额
                order_info.total_count += count
                order_info.total_amount += (count * sku.price + freight)
                # 5.2 保存订单商品信息
                OrderGoods.objects.create(
                    order=order_info,
                    sku=sku,
                    count=count,
                    price=sku.price
                )
            order_info.save()

            # 事务的提交点 可以不用写 with语句可以自动提交
            transaction.savepoint_commit(point)

        # 5.4 将redis中选中的商品信息移除(暂缓）
        # 6.返回响应
        return JsonResponse({'code': 0, 'errmsg': 'ok', 'order_id': order_id})


"""
解决并发的超卖问题：
1.队列
2.锁
    悲观锁：当查询某条记录的时候，即让数据库为改记录加锁，锁住记录后别人无法操作
            悲观锁类似于我们在多线程资源竞争时添加的互斥锁，容易出现死锁现象
    
    乐观锁：并不是真的锁，更新数据的时候判断此时的库存是否是之前查询处的库存，如果相同，表示没人修
            改，可以更新库存，否则表示别人抢夺过资源，不再执行库存更新。
   
    乐观锁步骤：
        1.记录某一个数据 10
        2.更新的时候，比对一下这个记录对不对 10-->可以操作 9-->不能操作

MySql数据库隔离的级别：
    Serializable：串行化，一个事务一个事务的执行
    
    Repeatable read：可重复读，无论其他事务是否修改并提交了数据，在这个事务中看到的数据值始终不受其他事务影响
    
    Read committed：读取已提交，其他事务提交了队数据的修改后，本事务就能读取到修改后的数据值（采用这种方式）
        a 事务完全操作之后，b事务操作的数据才为a
    
    Read uncommitted：读取未提交，其他事务只要修改了数据，即使未提交，本事务也能看到修改后的数据值
        举例：5，7库存都是8
            甲 5，7    5 --- 5：3 --- 
            乙 7，5    5 --- 7：3 --- （都失败）

MySql数据库默认使用了可重复读（Repeatable read）

"""












