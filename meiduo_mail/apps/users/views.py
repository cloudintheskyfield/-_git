import json
import re

from django.http import JsonResponse
# Create your views here.
from django.views import View
from apps.users.models import User  # abc
from django.core.cache import cache

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

        # 6.5 必须是登录后 还得有response
        from apps.carts.utils import merge_cookie_to_redis
        response = merge_cookie_to_redis(request, response)
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


# 退出登录 的类视图
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


# 用户中心信息展示
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

# 为用户发送激活邮件
class EmailView(LoginRequiredJSOMixin, View):

    def put(self, request):
        # 1.接收请求
        data = json.loads(request.body.decode())
        # 2.获取数据
        email = data.get('email')
        # 3.验证数据--->正则（自己完善）TODO 2
        # 4. 更新数据
        user = request.user
        user.email = email
        # 5.保存
        user.save()

        # 6.发送一封激活邮件（一会单独讲发送邮件）
        from django.core.mail import send_mail
        # def send_mail(subject, message, from_email, recipient_list,
        subject = '美多商城激活邮件'
        # 邮件的内容如果向使用html这个时候使用html_message
        message = ''

        # 6.5对a标签的链接数据进行加密处理 generic未注册的
        from apps.users.utils import generic_email_verify_token
        # 将用户id作为token
        token = generic_email_verify_token(request.user.id)

        # 6.5.5组织激活邮件
        # html_message = '点击摁钮进行激活<a href=\'http://itcast.cn/?token=%s\'>激活</a>' % token
        verify_url = 'http://www.meiduo.site:8080/success_verify_email.html?token=%s' % token
        html_message = '<p>尊敬的用户您好！</p>' \
                       '<p>感谢您使用美多商城</p>' \
                       '<p>您的邮箱为：%s 点击此处链接激活您的邮箱：</p>' \
                       '<p><a href="%s">%s<a>' % (email, verify_url, verify_url)
        # 采用下面这种 名称<邮件> 的形式可以使邮件看起来更正规
        from_email = '美多商城<1747709835@qq.com>'
        # send_mail(subject=subject,
        #           message=message,
        #           html_message=html_message,
        #           from_email=from_email,
        #           recipient_list=['1747709835@qq.com']
        #           )
        # 使用celery发送email 注意一定要启动了celery
        from celery_tasks.email.tasks import celery_send_email
        # 注意该delay不能少 如果少了delay就不走 异步了
        celery_send_email.delay(
            subject=subject,
            message=message,
            html_message=html_message,
            from_email=from_email,
            recipient_list=['1747709835@qq.com']
        )

        # 7.返回响应
        return JsonResponse({'code': 0, 'errmsg': 'set email is ok'})


"""
django项目
1.django的基础 夯实 例如：data = json.loads(request.body.decode())
2.需求分析
3.学习新知识
4.掌握分析问题，解决问题的能力（debug）

"""

"""
1.设置QQ/163邮箱服务器
2.设置邮件发送的配置信息
    # 1.django的那个类发送邮件
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    # 2.邮箱服务器
    EMAIL_HOST = 'smtp.qq.com'
    # 3.邮箱端口
    EMAIL_PORT = 25
    # 4.邮箱使用者
    EMAIL_HOST_USER = '1747709835@qq.com'
    # 5.下面的密码为授权码
    EMAIL_HOST_PASSWORD = 'tkvskmcpteqreceg'
3.调用 send_mail方法
"""

"""
需求（知道我们要干什么？？？）：
前端（用户干了什么，传递了什么参数）：
    用户会点击激活链接，那个激活链接携带了token
后端：
    请求：接收请求，获取参数，验证参数
    业务逻辑：user_id ,根据用户的id查询数据，修改数据
    响应：返回响应JSON
    路由：PUT emails/verification/ 说明token并没有在body里
    步骤：
        1.接收请求
        2.获取参数
        3.验证参数
        4.获取user_id
        5.根据用户id查询数据
        6.修改数据
        7.返回响应JSON
"""


# 用户点击验证邮件中的验证内容后面的操作
class EmailVerifyView(View):
    def put(self, request):
        # 1.接收请求
        params = request.GET
        # 2.获取参数
        token = params.get('token')
        # 3.验证参数
        if token is None:
            return JsonResponse({'code': 400, 'errmsg': '参数缺失'})
        # 4.获取user_id
        from apps.users.utils import check_verify_token
        user_id = check_verify_token(token)
        if user_id is None:
            return JsonResponse({'code': 400, 'errmsg': '参数错误'})
        # 5.根据用户id进行查询数据--------自己尝试使用request.user获取数据
        user = User.objects.get(id=user_id)
        # 6.修改数据
        user.email_active = True
        user.save()
        # 7.返回JSON响应
        return JsonResponse({'code': 0, 'errmsg': 'verify email is ok'})
        pass


"""
请求
业务逻辑 （数据库的增删改查）
响应

增：（注册的时候）
    1.接收数据
    2.验证数据
    3.数据入库
    4.返回响应
删：
    1.查询到指定记录
    2.删除数据（物理删除，逻辑删除）
    3.返回响应
改：（个人的邮箱信息）
    1.查询到指定的记录
    2.接收数据
    3.验证数据
    4.数据更新
    5.返回响应
查：（个人中心的数据展示, 省市区）
    1.查询指定的数据
    2.将对象数据转换为字典数据
    3.返回响应
"""

"""
需求：
    新增地址
前端：
    当用户填写完成地址信息后，前端应该发送一个axios请求,会携带相关信息（POST---body)
后端：
    请求：接收请求，获取参数
    业务逻辑：数据入库
    响应：返回响应
    路由：     POST    /addresses/create/
    步骤：
        1.接收请求
        2.获取参数，验证参数
        3.数据入库
        4.返回响应
    
"""
from apps.users.models import Address
from apps.areas.models import Area


# 新增地址的实现   修改地址    删除地址
class AddressCreateView(LoginRequiredJSOMixin, View):
    # 新增地址
    def post(self, request):
        # 1.接收参数
        data = json.loads(request.body.decode())
        # 2.获取参数
        receiver = data.get('receiver')
        province_id = data.get('province_id')
        city_id = data.get('city_id')
        district_id = data.get('district_id')
        place = data.get('place')
        mobile = data.get('mobile')
        tel = data.get('tel')
        email = data.get('email')

        user = request.user
        # 3.验证参数(省略）
        # 3.1验证必传参数
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return JsonResponse({'code': 400, 'errmsg': '参数不全'})
        # 3.2省市区的id是否正确（如果能在区表中查到市，根据市查到区/县说明id正确）
        province = Area.objects.get(id=province_id)
        city = Area.objects.get(id=city_id)
        district = Area.objects.get(id=district_id)
        if not all([province, city, district]):
            return JsonResponse({'code': 400, 'errmsg': '请输入正确的地区信息'})
        # 3.3详细地址的长度
        if len(place) > 50:
            return JsonResponse({'code': 400, 'errmsg': '地址过长'})
        # 3.4手机号
        if not re.match('1[345789]\d{9}', mobile):
            return JsonResponse({'code': 400, 'errmsg': '手机号不正确，请重新输入'})
        # 3.5固定电话
        if len(tel) > 0:
            if not re.match('(\d{4}-)?\d{6,8}', tel):
                return JsonResponse({'code': 400, 'errmsg': '电话格式不正确'})
        # 3.6邮箱
        if len(email) > 0:
            if not re.match('^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$', email):
                return JsonResponse({'code': 400, 'errmsg': '邮箱格式不正确'})
        # 4.数据入库
        address = Address.objects.create(
            user=user,
            title=receiver,
            receiver=receiver,
            province_id=province_id,
            city_id=city_id,
            district_id=district_id,
            place=place,
            mobile=mobile,
            tel=tel,
            email=email,
        )
        # 4.5转化一个字典 返回给前端
        address_dict = {
            'user': address.user.username,

            'id': address.id,
            'title': address.title,
            'receiver': address.receiver,
            # 该处为正向查询，通过地址查询到外键关联对应的市信息
            'province_id': address.province.name,
            'city_id': address.city.name,
            'district_id': address.district.name,
            'place': address.place,
            'mobile': address.mobile,
            'tel': address.tel,
            'email': address.email,
        }

        # 5.返回响应
        return JsonResponse({'code': 0, 'errmsg': 'set address is ok', 'address': address_dict})

    # 修改地址
    def put(self, request, address_id):

        # 1.接收数据
        data = json.loads(request.body.decode())
        receiver = data.get('receiver')

        # 1.5 查询到的为未改变的数据 需求：拿到用户输入的数据 TODO
        province = data.get('province')
        city = data.get('city')
        district = data.get('district')

        place = data.get('place')
        mobile = data.get('mobile')
        tel = data.get('tel')
        email = data.get('email')
        # 2. 修改数据
        address = Address.objects.get(id=address_id)
        address.receiver = receiver

        address.province_id = province
        address.city_id = city
        address.district_id = district

        address.place = place
        address.mobile = mobile
        address.tel = tel
        address.email = email

        address.save()
        # 3.封装字典
        address_dict = {
            'receiver': receiver,
            'province': province,
            'city': city,
            'district': district,
            'place': place,
            'mobile': mobile,
            'tel': tel,
            'email': email
        }
        address.save()
        # 4.返回响应
        return JsonResponse({'code': 0, 'message': 'modify address is ok', 'address': address_dict})

    def delete(self, request, address_id):
        # 1.获取数据
        # 2.查询数据
        address = Address.objects.get(id=address_id)
        # 3.删除数据
        try:
            address.delete()
        except Exception as e:
            print(e)
            return JsonResponse({'code': 400, 'errmsg': 'delete is ok'})
        # 4.返回响应
        return JsonResponse({'code': 0, 'errmsg': 'delete is ok'})


# 地址展示的实现
class AddressView(LoginRequiredJSOMixin, View):
    def get(self, request):
        # 1.查询指定数据
        user = request.user
        # 1.1 addresses = user.addresses
        addresses = Address.objects.filter(user_id=user.id, is_deleted=0)

        # 2.转化为字典数据
        address_list = []
        for address in addresses:
            address_list.append({
                'id': address.id,
                'title': address.title,
                'receiver': address.receiver,
                'province': address.province.name,
                'city': address.city.name,
                'district': address.district.name,
                'place': address.place,
                'mobile': address.mobile,
                'tel': address.tel,
                'email': address.email
            })
        # 返回响应
        return JsonResponse({'code': 0, 'errmsg': 'display address info is ok',
                             'addresses': address_list, 'default_address_id': user.default_address_id})


# 修改地址标题的实现
class AddressTitleView(LoginRequiredJSOMixin, View):
    def put(self, request, addresses_id):
        # 1.获取请求参数
        data = json.loads(request.body.decode())
        title = data.get('title')
        user = request.user
        # 2.修改指定数据
        addresses = Address.objects.get(user_id=user.id, id=addresses_id)
        addresses.title = title
        addresses.save()
        # 3.返回响应
        return JsonResponse({'code': 0, 'errmsg': 'set address title is ok'})


# 设置默认地址的实现
class AddressDefaultView(LoginRequiredJSOMixin, View):
    def put(self, request, address_id):
        # 1.修改数据
        user = request.user
        user.default_address_id = address_id
        user.save()
        # 2.返回响应
        # default_address_id        addresses
        return JsonResponse({'code': 0, 'errmsg': 'set default address is ok'})


# 修改密码的实现
class PasswordChangeView(LoginRequiredJSOMixin, View):
    def put(self, request):
        # 1.查询信息
        user = request.user

        # 2.接收数据
        data = json.loads(request.body.decode())
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        new_password2 = data.get('new_password2')
        # 3.验证数据
        from django.contrib.auth import authenticate
        user = authenticate(username=user.username, password=old_password)

        if not user:
            return JsonResponse({'code': 400, 'errmsg': '密码输入不正确，请重新尝试'})
        if new_password != new_password2:
            return JsonResponse({'code': 400, 'errmsg': '密码不一致'})

        # 4.数据更新
        user.set_password(new_password)
        user.save()
        #           password: pbkdf2_sha256$150000$uIwuwgLSRRmU$P7tLdTHEP7SSpmts1TeMs8+9u01172g6ahCIle1/i6Q=
        # 5.返回响应
        return JsonResponse({'code': 0, 'errmsg': 'set password is ok'})


########################## 最近浏览记录 #################
"""
一 根据页面效果，分析需求
    1.最近浏览记录 只有登录用户才可以访问 只记录登录用户的浏览信息
    2.浏览记录应该有顺序
    3.没有分页

二 功能
    功能：
        1：在用户访问商品详情的时候，添加浏览记录
        2：在个人中心，展示浏览记录

三 具体分析
    问题1：保存那些数据？用户id，商品id，顺序（访问时间）---根据商品id来进行查询
    问题2：保存在哪里？一般要保存在数据库（缺点：慢，会频繁操作数据库）
                    最好保存在redis中
        保存在两个库中都可以，看公司具体的安排，服务器内存比较大，mysql + redis
    
    user_id,sku_id,顺序
        
    redis： 5中数据类型
    key：value
    
    string：x
    hash：x
    list：v（去重，不能重复）
    set：x
    zset：权重：值
"""
"""
添加浏览记录：
    前端：当登录用户，访问某一个具体SKU页面的时候，发送一个axios请求，请求携带sku_id
    后端：
        请求：接收请求，获取请求参数，验证参数
        业务逻辑：连接redis，先去重，再保存到redis中，redis中只保存5条记录
        响应：返回JSON
        路由： POST browse_histories
        步骤：
            1：接收请求
            2：获取请求参数
            3：验证参数
            4：连接redis       list
            5：去重
            6：保存到redis中
            7：只保存5条记录
            8：返回响应
"""
# 添加 用户浏览商品记录
from apps.goods.models import SKU
from django_redis import get_redis_connection

class UserHistoryView(LoginRequiredJSOMixin, View):
    def post(self, request):
        user = request.user
        # 1：接收请求
        data = json.loads(request.body.decode())
        # 2：获取请求参数
        sku_id = data.get('sku_id')
        # 3：验证参数
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return JsonResponse({'code': 400, 'errmsg': '没有此商品'})

        # 4：连接redis
        redis_cli = get_redis_connection('history')
        # list
        # 5：去重(先删除再保存）
        try:
            redis_cli.lrem('history_%s' % user.id, 0, sku_id)
        finally:
            # 6：保存到redis中
            redis_cli.lpush('history_%s' % user.id, sku_id)
            # 7：只保存5条记录
            redis_cli.ltrim('history_%s' % user.id, 0, 4)
            # 8：返回响应
            return JsonResponse({'code': 0, 'errmsg': 'ok'})

    def get(self, request):
        # 1.连接redis
        redis_cli = get_redis_connection('history')
        # 2.获取redis数据
        ids = redis_cli.lrange('history_%s' % request.user.id, 0,4)
        # 3.根据商品id进行数据查询
        history_list = []
        for sku_id in ids:
            sku = SKU.objects.get(id=sku_id)
            # 4.将对象转化为字典
            history_list.append({
                'id':sku.id,
                'name':sku.name,
                'default_image_url':sku.default_image.url,
                'price':sku.price,
            })
        # 5.返回JSON
        return JsonResponse({'code':0, 'errmsg': 'set display history is ok', 'skus':history_list})

"""
展示用户浏览记录
    前端：
        用户在访问浏览记录的时候，会发送axios请求，请求会携带session信息
    后端：
        请求：
        业务逻辑：连接redis，获取redis数据（获取商品id），根据商品id进行查询，将对象转化为字典
                根据商品id进行数据查询
        响应：JSON
        路由：GET 与添加 浏览记录的路由相同
        步骤：
            1.连接redis
            2.获取redis数据
            3.根据商品id进行数据查询
            4.将对象转化为字典
            5.返回JSON
"""
