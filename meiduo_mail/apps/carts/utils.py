"""
需求：
    登录的时候，将cookie数据合并到redis中
前端：
后端：
    请求：在登录的时候，获取cookie数据
    业务逻辑：合并到redis中
抽象的问题 具体化（举个例子）
1.读取cookie数据
2.合并redis
    初始化一个字典，用于保存 sku_id:count
    初始化一个列表 用于保存选中的商品id
    初始化一个列表 用于保存未选中的商品id
3.遍历cookie数据
4.将字典数据，列表数据分别添加到redis中
5.删除cookie数据
################
redis       hash
            1:10
            3:10

            set
            1
cookie
{
    1:{count:666, selected: True}
    2:{count:999, selected:True}
}
1.获取cookie中的sku_id，看redis中是否有，有的话数量合并，选中为True？以cookie为主，将cookie中的数据覆盖到redis中
2.如果没有操作 hash，set 建立新的数据？

"""
import pickle
import base64

from django_redis import get_redis_connection


# 在登录的时候使用
def merge_cookie_to_redis(request, response):
    # 1.读取cookie的数据
    cookie_carts = request.COOKIES.get('carts')
    if cookie_carts is not None:
        carts = pickle.loads(base64.b64decode(cookie_carts))
        # 2.初始化一个字典 用于保存 sku_id, count---> {sku_id: count, sku_id:count}
        cookie_dict = {}
        # 2.1 初始化一个列表，用于保存选中的商品id
        selected_list = []
        # 2.2 初始化一个列表，用于保存未选中的商品id
        unselected_list = []
        # 3.遍历cookie数据
        for sku_id,count_selected_dict in carts.items():
            cookie_dict[sku_id] = count_selected_dict['count']
            # 看是否选中
            if count_selected_dict['selected']:
                selected_list.append(sku_id)
            else:
                unselected_list.append(sku_id)
        # 4.将字典数据，列表数据添加到redis中
        redis_cli = get_redis_connection('carts')
        pipeline = redis_cli.pipeline()
        # 4.1 hash
        pipeline.hmset('carts_%s' % request.user.id, cookie_dict)  # hmset key key value key value
        # 4.2 set
        if len(selected_list)>0:
            pipeline.sadd('selected_%s' % request.user.id, *selected_list)  # *对列表数据进行解包
        if len(unselected_list)>0:
            pipeline.srem('selected_%s' % request.user.id, *unselected_list)
        # 5.删除cookie数据
        response.delete_cookie('carts')
        # 返回respones，类似流水线
        # 6.执行管道
        pipeline.execute()
    # 不管response是不是none都要执行
    return response
























