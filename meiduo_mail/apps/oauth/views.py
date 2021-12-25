import json

from django.shortcuts import render
from django.views import View
from QQLoginTool.QQtool import OAuthQQ
from meiduo_mail import settings
from django.http import JsonResponse
from apps.oauth.models import OAuthQQUser
from django.contrib.auth import login
from apps.users.models import User

# Create your views here.

"""
第三方登录的步骤
1.QQ互联开放平台申请成为开发者（不用做）
2.QQ互联创建应用（不用做）
3.按照文档开发（看文档的）

3.1准备工作：
    QQ登录参数 申请的客户端id：
        QQ_CLIENT_ID = '101474184'  appid
    申请的客户端密钥：
        QQ_CLIENT_SECRET = 'c6ce949e04e12ecc909ae6a8b09b637c'   aookey
    申请时添加的，登录成功后回调的路径
        QQ_REDIRECT_URL = 'http://www.meiduo.site:8080/oauth_callback.html'

3.2 放置QQ登录的图标（目的：点击QQ图标来实现第三方登录）----------------------------------前端做好了
3.3 根据oath2.0来获取Code和Access_token---------------------------------------------后端任务
    3.3.1 获取Authorization Code：
        最终的效果是获取code，表面的效果是一个链接页面，这个页面就是用户点击QQ图片的跳转链接
        https://graph.qq.com/oauth2.0/authorize?response_type=code&client_id=101474184&redirect_url=www.meiduo.site:8080/oauth_callback.html&state=xxx
    3.3.2 通过Authorization Code获取Access Token
        访问上述地址成功后得到Access Token
3.4 通过token获取openid-----------------------------------------------------------后端任务
    openid是此网站上唯一对应用户身份的表示，网站可将此ID进行存储便于用户下次登录时辨识其身份，或将其与用户在网站上的原有账号进行绑定

生成用户绑定链接------->获取code--------->获取token---------->获取openid--------->保存openid
"""
"""
生成用户绑定链接：
    前端：当用户点击QQ登录图标的时候，前端应该发送一个axios（Ajax）请求
    
    后段：
        请求
        业务逻辑    调用QQLoginTool 生成跳转链接
        响应      返回跳转链接{'code':0, 'qq_login_url': 'http://xxx'}
        路由      this.host + '/qq/authorization/?next='
        步骤
            1.生成QQLoginTool实例对象
            2.调用对象的方法生成跳转链接
            3.返回响应
"""

class QQLoginURLView(View):
    """生成点击QQ图标后QQ的跳转链接"""
    def get(self, request):
        # 1.生成QQ实例化对象
        # client_id         appid
        # client_secret     appsecret
        # redirect_url = None   用户登录之后跳转的页面
        # state = None      不知道什么意思，随便写，等出了问题再分析
        #     def __init__(self, client_id=None, client_secret=None, redirect_uri=None, state=None): 4个参数
        qq = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                     client_secret=settings.QQ_CLIENT_SECRET,
                     redirect_uri=settings.QQ_REDIRECT_URL,
                     state='xxx')
        # 2.调用对象的方法生成跳转链接   该跳转链接需要传递给前端进行跳转操作
        qq_login_url = qq.get_qq_url()
        # 3.返回响应
        return JsonResponse({'code': 0, 'errmsg': 'set qq_url is ok', 'login_url': qq_login_url})

"""注意：该步骤出现404（路由问题） 或者405（类视图中方法定义为GET或者POST错误问题）"""

"""
需求：获取code，通过code换取token，再通过token换取openid
前端：
    应该获取用户同意登录的code，把这个code发送给后段
后端：
    请求  获取code
    业务逻辑 
        通过code换取token，再通过token换取openid
        根据openid进行判断
        如果没有绑定过，则需要绑定
        如果绑定过，则直接登录
    响应：
    路由  GET     this.host + '/oauth_callback/?code='
    步骤
        1.获取code
        2.通过code换取token
        3.再通过token换取openid
        4.根据openid进行判断--->是否绑定手机号
        5.如果没有绑定过，则需要绑定
        6.如果绑定过，则直接登录
"""
class OauthQQview(View):
    def get(self, request):
        # 1.获取code
        code = request.GET.get('code')
        if code is None:
            # 实际错误码应该又一个严格的规定
            return JsonResponse({'code': 400, 'errmsg': '参数不全'})

        # 2.通过code换取token--->需要一个QQ对象来进行操作，类似cursor游标
        # token--->E537ED5F128AD5F2820CA84A5C458C04--->一个人不会变
        qq = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                     client_secret=settings.QQ_CLIENT_SECRET,
                     redirect_uri=settings.QQ_REDIRECT_URL,
                     state='xxx')
        token = qq.get_access_token(code)
        # 3.通过token换取openid
        # openid---> 0F7272E90769D38757AF1E35611B8D1C--->同一个QQ号码不会变
        openid = qq.get_open_id(token)

        # 4.根据openid进行查询
        try:
            qquser = OAuthQQUser.objects.get(openid=openid)     # 使用get对 索引/唯一索引取值的时候，需要try
        # 当用户不存在时候跳转到绑定界面
        except OAuthQQUser.DoesNotExist:
            # 5.如果没有绑定过，则需要绑定       前端需要将access_token返回给前端--->即openid

            # 5.5对该处返回前端的openid进行加密，即access_token
            """封装的思想其实就是把一些实现了特定功能的代码封装称一个函数（方法） 
                封装的目的：解耦--->当需求发生改变的时候，对代码的需求影响比较小
                封装的步骤：
                    1.将要封装的代码放到一个函数中
                    2.优化封装的代码
                    3.验证封装的代码
            """
            from apps.oauth.utils import generic_openid
            access_token = generic_openid(openid)

            response = JsonResponse({'code': 400, 'access_token': access_token})
            return response
        else:
            # 6.存在
            # 6.1设置session  1对多正向查询 含有外键类创建的对象.外键字段查询到对应的 用户
            #       该查询到的用户即为主表中的用户对象
            login(request, qquser.user)
            # 6.2设置cookie
            response = JsonResponse({'code': 0, 'errmsg': 'set cookie is ok'})
            response.set_cookie('username', qquser.user.username)
            return response

    def post(self, request):
        # 1.接收请求
        data = json.loads(request.body.decode())
        # 2.获取请求参数 openid
        mobile = data.get('mobile')
        password = data.get('password')
        sms_code = data.get('sms_code')
        openid = data.get('access_token')

        # 需要对数据进行验证(省略）
        # 2.5.在redis中存储 短信验证码

        # 对前端传给后端的access_token进行解密
        from apps.oauth.utils import check_access_token
        openid = check_access_token(openid)
        if openid is None:
            return JsonResponse({'code': 400, 'errmsg': '参数缺失'})

        # 3.根据手机号进行用户信息的查询
        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            # 手机号不存在 用户没有注册 需要创建数据库中的用户
            user = User.objects.create_user(username=mobile, mobile=mobile, password=password)
        else:
            # 手机号存在 用户已经注册--->检查密码
            if not user.check_password(password):
                return JsonResponse({'code': 400, 'errmsg': '账号或者密码错误'})
        # 4.创建QQ用户表中的信息--->对openid进行加密， 否则前端可以拿到， 在上面的get中进行加密
        OAuthQQUser.objects.create(user=user, openid=openid)
        # 5.状态保持
        login(request, user)
        # 6.返回响应
        response = JsonResponse({'code': 0, 'errmsg': 'set cookie is ok'})
        response.set_cookie('username', user.username)
        return response


"""
需求：QQ绑定账号信息
前端：
    当用户输入手机号，密码，短信验证码之后就发送axios请求，请求需要携带mobile,password,sms_code,access_token(openid)
后端：
    请求：接收请求，获取请求参数
    业务逻辑：绑定，完成状态保持
    响应：返回code=0跳转到首页
    路由：POST
    步骤：
        1.接收请求
        2.获取请求参数
        3.绑定（根据手机号进行查询）
            3.1 查询到手机号已经注册，就可以直接保持（绑定）用户和openid信息
            3.2 查询到手机号没有注册，就创建一个user信息，然后再进行绑定
        4.完成状态保持
        5.返回响应
    
"""

"""
<----------------------------------------itsdangerous 的基本使用-------------------------------------------->
itsdangerous就是为了数据加密的
数据加密
1.导入itsdangerous的类
2.创建类的实例对象
3.加密数据

数据解密
1.导入itsdangerous的类
2.创建类的实例对象
3.加密数据
"""
# 加密
# 1.导入itsdangerous的类--->导入最长的--->不仅可以对数据进行加密，还可以对数据设置一个时效
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
# 2.创建类的实例对象
# secret_key  ，密钥
# expires_in = None   , 数据的过期时间 秒
from meiduo_mail import settings
s = Serializer(secret_key=settings.SECRET_KEY, expires_in=3600)
# 3.加密数据--->加密openid--->dump转存计算机数据
token = s.dumps({'openid': '1234567890'})
# 上述字典数据加密后的结果
# b'eyJhbGciOiJIUzUxMiIsImlhdCI6MTY0MDQ0MjM1NSwiZXhwIjoxNjQwNDQ1OTU1fQ.eyJvcGVuaWQiOiIxMjM0NTY3ODkwIn0._MLbG7IaLHACvveEOyNH4LUl2EyKBYH2dFEvx9DsbnwNPzrBHlkZpM25rx2iBBRPbbqt16jTTPc21GXducFn4A'

# 解密
# 1.导入itsdangerous的类
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
# 2.创建类的实例对象
from meiduo_mail import settings
s = Serializer(secret_key=settings.SECRET_KEY, expires_in=3600)
# 3.解密数据--->load加载
s.loads(token)























