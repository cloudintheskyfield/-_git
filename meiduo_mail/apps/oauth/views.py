from django.shortcuts import render
from django.views import View
from QQLoginTool.QQtool import OAuthQQ
from meiduo_mail import settings
from django.http import JsonResponse

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

























