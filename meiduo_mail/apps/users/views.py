import json
import re

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
1.判断用户名是否重复的功能：
    前端（了解）：当用户输入用户名之后，失去焦点，发送一个axios（ajax）请求
    后端：
        1.接收请求：接收用户输入的用户名
        2.业务逻辑：根据用户名查询数据库，如果查询结果等于0，说明没有注册
                如果查询数量等于1，说明有注册
        3.响应：返回Json数据
                {code:0, count:0/1, errmsg:ok}      code为0说明没有问题
                code：状态码为0表示没有问题  ---  errmsg：错误信息 ---  count：记录该用户名的个数
        4.路由：GET方式  usernames/ (?<username>[a-zA-Z0-9_-]{5, 20}/count/
                        usernames/<username>/count/
        5.步骤：
            1.接收用户名
            2.根据用户名查询数据
            3.返回响应
"""


# 固定写法必须继承view 判断用户名是否重复
class UsernameCountView(View):
    """需要继承自View类"""

    # 固定写法get方法
    def get(self, request, username):
        """处理所有的get请求"""
        # 1.接收用户名 对用户名的输入进行一下判断 判断是否在5-20之间，不符合就没有必要进行数据库的查询
        #       虽然前端会进行查询判断，但是每一次的数据后段都会进行数据库查询
        #       在这里写的正则可以验证，但是，每次用的话都要重新复制代码
        # if not re.match('[a-zA-Z0-9_-]{5,20}', username):
        #     return JsonResponse({'code': 200, 'errmsg': '用户名不满足需求'})

        # 2.根据用户名查询数据
        count = User.objects.filter(username=username).count()  # count()为查询该用户名对应的数量

        # 3.返回响应--->返回json数据--->根据前端js代码来确定使用什么数据进行交互。 其中count必须返回的，code和errmsg返回与否都可
        return JsonResponse({'code': 0, 'count': count, 'errmsg': 'ok'})  # 返回的Json数据一般为字典


"""
2.判断 是否注册 的实现功能
    我们不相信前端提交的任何数据！！！ 必须验证
    前端：当用户输入 用户名，密码，确认密码，手机号，是否同意协议之后，会点击注册摁钮。前端发送axios（ajax）请求
    后段：
        1.接收请求：接收请求（JSON），获取数据
        2.业务逻辑：接收数据，数据入库
        3.响应：返回Json数据（字典）  0 表示成功， 400 表示失败
                {code:0, count:0/1, errmsg:ok} code为0说明没有问题,code为200说明有问题
        4.路由：GET方式 http://127.0.0.1:8000/mobiles/^1[3,4,5,7,8,9]\d{9}$/count
               POST方式 http://127.0.0.1:8000/register/
                        将手机号传递参数进来： mobiles/<phone_number>/count/
        5.步骤：
            1.接收请求（POST---JSON）
            2.获取数据
            3.验证数据
                3.1 用户名，密码，确认密码，手机号，是否同意协议 都要有
                3.2 用户名满足规则，用户名不能重复（必须再验证一次）
                3.3 密码满足规则
                3.4 确认密码和密码要一致
                3.5 手机号满足规则，手机号也不能重复
                3.6 同意协议
            4.数据入库
            5.返回响应


"""


# 判断手机号是否注册
# class PhoneNumberCountView(View):
#     def get(self, request, mobile):
#         # 1.接收手机号
#         # 2.根据电话号查询
#         count = User.objects.filter(mobile=mobile).count()  # 查询手机号对应的数量
#         # 3.返回
#         return JsonResponse({'code': 0, 'count': count, 'errmsg': 'set phone is ok'})

# 注册视图
class RegisterView(View):
    def post(self, request):
        # 1.接收请求（POST - --JSON）
        body_bytes = request.body   # 数据在request.body中
        body_str = body_bytes.decode()
        body_dict = json.loads(body_str)    # 注意该处是 loads 不是 load

        # 2.获取数据
        # body_dict['username']容易出现异常，如果数据不存在的话，下面的get后面的参数在前端页面中有显示
        username = body_dict.get('username')
        password = body_dict.get('password')
        password2 = body_dict.get('password2')
        mobile = body_dict.get('mobile')
        allow = body_dict.get('allow')

        # 3.验证数据
        # 3.1 用户名，密码，确认密码，手机号，是否同意协议 都要有
        # all([xxx, xxx]) all中的元素只要是None或False，all就返回False，否则true
        # if username is null:      ---->需要一个一个写很麻烦，使用all的方式
        #      return JsonResponse()
        if not all([username, password, password2, mobile, allow]):
            return JsonResponse({'code': 400, 'errmsg': '参数不全'})    # 该处失败状态吗对应前端中的400/0 失败成功
        # 3.2  1.用户名满足规则    2.用户名不能重复（必须再验证一次）
        if not re.match('[a-zA-Z_-]{5,20}', username):
            return JsonResponse({'code': 400, 'errmsg': '用户名不满足规则'})
        # 3.3 密码满足规则

        # 3.4 确认密码和密码要一致
        # 3.5 手机号满足规则，手机号也不能重复
        # 3.6 同意协议

        # 4 数据入库
        # 方案1
        # user = User(username=username, password=password, mobile=mobile)
        # user.save()
        # 方案2
        # User.objects.create(username=username, password=password, mobile=mobile)
        # 以上2中方式中，都可以入库，但是有一个问题？--->密码没有加密
        # 方案3
        User.objects.create_user(username=username, password=password, mobile=mobile)
        # 5.返回响应
        return JsonResponse({'code': 0, 'errmsg': 'ok'})

























