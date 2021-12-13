from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views import View
from apps.users.models import User
"""
需求分析：根据页面的功能（从上倒下，从左到右面），那些功能需要和后段配合完成
如何确定 那些功能需要和后段进行交互？？？
    1.经验
    2.关注类似网站的相似功能
"""

"""
判断用户名是否重复的功能：
    前端（了解）：当用户输入用户名之后，失去焦点，发送一个axiox（ajax）请求
    后段：
        1.接收请求：接收用户名
        2.业务逻辑：根据用户名查询数据库，如果查询结果等于0，说明没有注册
                如果查询数量等于1，说明有注册
        3.响应：返回Json数据
                {code:0, count:0/1, errmsg:ok}      code为0说明没有问题
                code：状态码  ---  errmsg：错误信息 ---  count：记录该用户名的个数
        4.路由：GET方式  usernames/ (?<username>[a-zA-Z0-9_-]{5, 20}/count/
                        usernames/<username>/count/
        5.步骤：
            1.接收用户名
            2.根据用户名查询数据
            3.返回响应
        
"""


class UsernameCountView(View):
    def get(self, request, username):
        # 1.接收用户名
        # 2.根据用户名查询数据
        count = User.objects.filter(username=username).count()  # count()为查询该用户名对应的数量
        # 3.返回响应
        return JsonResponse({'code': 0, 'count': count, 'errmsg': 'ok'})    # 返回的Json数据一般为字典











