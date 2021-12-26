import json

from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views import View
from apps.areas.models import Area
from django.core.cache import cache

"""
需求：
    获取省份信息
前端：
    当页面加载的时候，会发送axios请求来获取省份信息
后端：
    请求：     不需要请求参数
    业务逻辑：   查询省份信息
    响应：     JSON
    
    路由：     areas/
    步骤：      
            1.查询省份信息
            2.返回响应
"""
"""访问用户中心界面的时候加载 市"""
class AreaView(View):
    def get(self, request):
        # 0.5 获取缓存数据
        if cache.get('province'):
            return JsonResponse({'code': 0, 'errmsg': 'set areas is ok', 'province_list': cache.get('province')})
        # 1.查询省份信息
        provinces = Area.objects.filter(parent_id=None)
        # 2.将对象转换为字典数据
        province_list = []
        for province in provinces:
            province_list.append({
                'id': province.id,
                'name': province.name
            })
        # 2.5缓存数据
        cache.set('province', province_list, 3600*24)
        # 3.返回响应
        # JsonResponse 不能返回对象数据，例如QuerySet， JsonResponse可以转换字典数据
        return JsonResponse({'code': 0, 'errmsg': 'set areas is ok', 'province_list': province_list})


"""
需求：
    获取市，区/县信息
前端：
    当页面加载的时候，会发送axios请求来获取 下一级信息
后端：
    请求：     需要传递省份id，市的id
    业务逻辑：   根据id查询信息，将查询的结果转化为字典列表
    响应：     JSON

    路由：     areas/
    步骤：      
            1.查询省份id，市的id，查询信息
            2.将数据转化为字典数据
            3.返回响应
"""
""" 根据市的id查询下一级的信息"""
class SubAreaView(View):
    def get(self, request, id):
        # 0.5查询缓存数据
        # 该处的key根据id来改变
        if cache.get('city:%s' % id):
            return JsonResponse({'code': 0, 'errmsg': 'set cities is ok', 'sub_data': {'subs': cache.get('city:%s' % id)}})
        # 1.获取市的id
        up_level = Area.objects.get(id=id)      # 注意此处一定为get，不能为filter否则没有subs方法/属性
        down_level = up_level.subs.all()
        # 2.将对象转换为字典数据
        data_list = []
        for item in down_level:
            data_list.append({
                'id': item.id,
                'name': item.name
            })

        # 2.5保存缓存数据---过期时间为 秒
        # 该处的key需要变化的
        cache.set('city:%s' % id, data_list, 24*3600)

        # 3.返回响应
        return JsonResponse({'code': 0, 'errmsg': 'set cities is ok', 'sub_data': {'subs': data_list}})


"""
举例：美多商城
注册用户：1个亿
日活用户：10%  100万
下单比例 1%     1w  10000
新增地址的概率  1%  100  300次
查询不经常变化的数据--->存入到 redis/缓存 中--->对省 市 区数据进行 缓存
5/1 分钟 为期间对 新闻做一个缓存
第一种方法：
    直接调用redis进行缓存
第二种方法：
    使用django进行缓存

"""




















