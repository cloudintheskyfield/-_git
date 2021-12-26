# 第一种用户中心返回JSON数据的方法
# class LoginRequiredJSONMixin(AccessMixin):
#     """Verify that the current user is authenticated."""
#     def dispatch(self, request, *args, **kwargs):
#         if not request.user.is_authenticated:
#             # 将该处的代码改写为返回JSON数据
#             return JsonResponse({'code': 400, 'errmsg': '没有登录1'})
#         return super().dispatch(request, *args, **kwargs)

# 第二种用户中心返回JSON数据的方法
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse


class LoginRequiredJSOMixin(LoginRequiredMixin):
    def handle_no_permission(self):
        return JsonResponse({'code': 400, 'errmsg': '没有登录2'})

















