from django.urls import converters


class UsernameConverter:
    """定义一个判断用户是否重复的转换器, 定义后需要在工程的urls中注册， 再在子路由中去使用"""
    regex = '[a-zA-Z0-9_-]{5,20}'

    def to_python(self, value):
        return value
