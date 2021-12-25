import json
import re

from django.http import JsonResponse
# Create your views here.
from django.views import View
from apps.users.models import User  # abc

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
class PhoneNumberCountView(View):
    def get(self, request, mobile):
        # 1.接收手机号
        # 2.根据电话号查询
        count = User.objects.filter(mobile=mobile).count()  # 查询手机号对应的数量
        # 3.返回
        return JsonResponse({'code': 0, 'count': count, 'errmsg': 'set phone is ok'})


# 注册视图
class RegisterView(View):
    def post(self, request):
        # 1.接收请求（POST - --JSON）
        body_bytes = request.body  # 数据在request.body中
        body_str = body_bytes.decode()
        body_dict = json.loads(body_str)  # 注意该处是 loads 不是 load

        # 2.获取数据
        # body_dict['username']容易出现异常，如果数据不存在的话，下面的get后面的参数在前端页面中有显示
        username = body_dict.get('username')
        password = body_dict.get('password')
        password2 = body_dict.get('password2')
        mobile = body_dict.get('mobile')
        allow = body_dict.get('allow')
        # 接收请求中的sms_code
        sms_code = body_dict.get('sms_code')

        # 3.验证数据
        # 3.1 用户名，密码，确认密码，手机号，是否同意协议 都要有
        # all([xxx, xxx]) all中的元素只要是None或False，all就返回False，否则true
        # if username is null:      ---->需要一个一个写很麻烦，使用all的方式
        #      return JsonResponse()
        if not all([username, password, password2, mobile, sms_code]):
            return JsonResponse({'code': 400, 'errmsg': '参数不全'})  # 该处失败状态吗对应前端中的400/0 失败成功
        # 3.2  1.用户名满足规则    2.用户名不能重复（必须再验证一次）
        if not re.match('[a-zA-Z0-9_-]{5,20}', username):
            return JsonResponse({'code': 400, 'errmsg': '用户名不满足规则'})
        if User.objects.filter(username=username):
            return JsonResponse({'code': 400, 'errmsg': '用户名已存在'})
        # 3.3 密码满足规则
        if (len(password) < 8) or (len(password) > 20):
            return JsonResponse({'code': 400, 'errmsg': '密码不满足规则'})
        # 3.4 确认密码和密码要一致
        if password != password2:
            return JsonResponse({'code': 400, 'errmsg': '密码不一致，请重试'})
        # 3.5 手机号满足规则，手机号也不能重复
        if not re.match('1[345789]\d{9}', mobile):
            return JsonResponse({'code': 400, 'errmsg': '手机号不满足规则'})

        # 3.5.5 判断短信验证码是否正确

        # 获取redis中用户输入的验证码
        from django_redis import get_redis_connection
        redis_cli = get_redis_connection('code')
        sms_code_redis = redis_cli.get(mobile)  # sms_code不为字节类型
        # 判断过期
        if not sms_code_redis:
            return JsonResponse({'code': 400, 'errmsg': '短信验证码已过期'})
        # 判断用户输入短信是否正确
        if sms_code != sms_code_redis.decode():
            return JsonResponse({'code': 400, 'errmsg': '短信验证码不正确'})

        # 3.6 同意协议
        if allow is False:
            return JsonResponse({'code': 400, 'errmsg': '未勾选同意条款'})
        # 4 数据入库
        # 方案1
        # user = User(username=username, password=password, mobile=mobile)
        # user.save()
        # 方案2
        # User.objects.create(username=username, password=password, mobile=mobile)
        # 以上2中方式中，都可以入库，但是有一个问题？--->密码没有加密
        # 方案3
        user = User.objects.create_user(username=username, password=password, mobile=mobile)

        # 设置session信息
        # request.session['user_id'] = user.id
        # Django为我们提供了状态保持的方法
        from django.contrib.auth import login
        # user为已经登录的用户信息
        login(request, user)

        # 5.返回响应
        return JsonResponse({'code': 0, 'errmsg': 'register is ok'})


"""
如果需求是注册成功后表示用户认证通过，那么此时可以在注册成功后实现 状态保持（注册成功即已经登录）
如果需求是注册成功后不表示用户认证通过，那么此时不用在注册成功后实现 状态保持（注册成功，单独登录）
状态保持的两种实现方式：
    在客户端存储信息使用Cookie
    在服务器端存储信息使用Session
"""

"""
登录

前端：
    当用户把用户名和密码输入完成之后，会点击登录摁钮。这个时候前端会发送一个ajax（axios）请求
    
后端：
    请求：接收数据，验证数据
    业务逻辑：验证用户名和密码是否正确，session（状态保持）
    响应：返回json数据 0 成功 400 失败
    
    POST    /login/
    
步骤：
    1.接收数据
    2.验证数据
    3.验证用户名和密码是否正确
    4.session
    5.判断是否记住登录
    6.返回响应
"""


class LoginView(View):
    def post(self, request):
        # 1.接收数据 接收用户输入的数据
        data = json.loads(request.body.decode())
        username = data.get('username')
        password = data.get('password')
        remembered = data.get('remembered')

        # 2.验证数据
        if not all([username, password]):
            return JsonResponse({'code': 400, 'errmsg': '参数不全'})

        # 2.5 验证用户名和密码
        # 2.5.验证是根据手机号查询还是根据用户名查询   可以根据修改User.USERNAME_FIELD字段来确定是用户名/手机号来进行判断是什么登录
        if re.match('1[3-9]\d{9}', username):
            User.USERNAME_FIELD = 'mobile'
        else:
            User.USERNAME_FIELD = 'username'

        # 3.验证用户名和密码是否正确
        # 方式1
        # user = User.objects.filter(username=username, password=password)
        # if not user:
        #     return JsonResponse({'code': 400, 'errmsg': '用户名或者密码错误'})
        # 方式2
        # 系统自带的认证系统
        from django.contrib.auth import authenticate, login
        user = authenticate(username=username, password=password)
        if user is None:
            return JsonResponse({'code': 400, 'errmsg': '账号或者密码错误'})

        # 4.session 登录状态保持
        login(request, user)

        # 5.判断是否记住登录
        if remembered is True:
            # 记住登录---记住后直接自动登录，不需要用户再去自行手动设置
            request.session.set_expiry(None)
            response = JsonResponse({'code': 0, 'errmsg': 'set session is ok'})
        else:
            # 不记住登录 浏览器关闭session过期
            request.session.set_expiry(0)
            response = JsonResponse({'code': 0, 'errmsg': 'ok'})
        # 6.设置cookie 并返回响应
        # 为了首页显示用户信息-----------------
        response.set_cookie('username', username)  # 不设置max_age= 默认会话结束之后
        return response


"""
退出登录----------------------------------------------------------------->
前端：
    当用户点击退出摁钮的时候，前端发送一个axios delete的请求
后段：
    请求
    业务逻辑    退出
    响应 发挥JSON数据
    
"""


class LogoutView(View):
    # 该处定义名称的时候定义get/ post/ put等等 按照规则
    # 此处对应前端js中的axios.get 中的get
    def get(self, request):
        from django.contrib.auth import logout
        # 删除session信息
        logout(request)
        # 删除cookie信息
        response = JsonResponse({'code': 0, 'errmsg': 'log out is ok'})
        response.delete_cookie('username')
        return response


# 用户中心也必须是登录用户
"""
用户中心--------------------------------------------------------------------->
LoginRequiredMixin  未登录的用户会返回重定向，重定向并不是JSON数据
需要的是返回JSON数据 和亲端是通过JSON进行交互的

"""
# 调用utils中方法
# 直接继承自上面的函数  LoginRequiredJSONMixin 应为类的第一个参数
from utils.views import LoginRequiredJSOMixin


class CenterView(LoginRequiredJSOMixin, View):
    def get(self, request):
        info_data = {
            # request.user 来源于中间件，系统会进行判断，如果确实是登录用户，可以获取登录用户对用的模型实例数据
            # 如果不是登录用户request.user 返回一个 AnonymousUser
            'username': request.user.username,
            'email': request.user.email,
            'mobile': request.user.mobile,
            'email_active': request.user.email_active
        }
        return JsonResponse({'code': 0, 'errmsg': 'set center is ok', 'info_data': info_data})


"""
邮箱验证------------------------------->
我的思路：
    用户POST提交保存后，接收前端用户传入的Email数据，将该Email保存到数据库，并返回响应
    
需求：1.保存邮箱地址 2.发送一封激活邮件 3.用户激活邮件

前端：
    用户输入邮箱后发送ajax（axios）请求
后端：
当用户输入邮箱，点击保存后，会发送ajax请求
    请求      就收请求，获取数据
    业务逻辑    保存邮箱地址 发送一封激活邮件
    响应  JSON code=0
    路由  PUT---> 用来更新数据       var url = this.host + '/emails/'
    步骤
        1.接收请求
        2.获取数据
        3.保存邮箱地址
        4.发送一封激活邮件
        5.返回响应

需求（实现什么功能）---> 请求 --业务逻辑--->响应 ---> 步骤 ---> 代码实现

"""

# 养成一个习惯，在每个函数的第一行添加断点
# 添加一个LoginRequiredJSONMixin
class EmailView(LoginRequiredJSOMixin, View):

    def put(self, request):
        # 1.接收请求
        data = json.loads(request.body.decode())
        # 2.获取数据
        email = data.get('email')
        # 3.验证数据--->正则（自己完善）
        # 4. 更新数据
        user = request.user
        user.email = email
        # 5.保存
        user.save()
        # 6.发送一封激活邮件（一会单独讲发送邮件）
        # 7.返回响应
        return JsonResponse({'code': 0, 'errmsg': 'set email is ok'})


"""
django项目
1.django的基础 夯实 例如：data = json.loads(request.body.decode())
2.需求分析
3.学习新知识
4.掌握分析问题，解决问题的能力（debug）


"""






























