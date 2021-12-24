from django.shortcuts import render

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
















