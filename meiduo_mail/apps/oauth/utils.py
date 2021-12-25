from meiduo_mail.settings import SECRET_KEY
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from itsdangerous import BadData, BadSignature, BadTimeSignature


# 加密openid的函数
def generic_openid(openid):
    # 2.创建实例对象
    s = Serializer(secret_key=SECRET_KEY, expires_in=3600)
    access_token = s.dumps({'openid': openid})
    # access_token为二进制类型的数据 最好将byte类型的数据转换为str 该数据仍然是加密状态
    access_token = access_token.decode()
    return access_token


# 解密openid的函数
def check_access_token(openid):
    # 2.创建实例对象
    s = Serializer(secret_key=SECRET_KEY, expires_in=3600)
    # 3.解密
    try:
        # 解密的时候很可能会报错，所以最好异常捕捉一下
        result = s.loads(openid)
    except Exception as e:
        return None
    else:
        # 字典中含有 字典.get(key) 方法
        return result.get('openid')
















