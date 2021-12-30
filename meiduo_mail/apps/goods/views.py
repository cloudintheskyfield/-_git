from django.shortcuts import render

# Create your views here.
"""
关于模型的分析
1.根据页面效果 尽量多的分析字段
2.去分析是保存在一个表中 还是多个表中（多举例说明）
分析表的关系的时候 最多不要超过3个表

多对多（一般是3个表）

学生和老师（多对多）
学生表
stu_id          stu_name
100             张三
200             李四

老师表
teacher_id      teacher_name
666             牛老师
999             齐老师

第三张表
stu_id          teacher_id
100             666
100             999
200             666
200             999

商品day01：
    商品模型的分析--->Fdfs（用于保存图片，视频等文件）--->为了部署Fdfs学习Docker

"""

# 上传图片的代码------------------------
from fdfs_client.client import Fdfs_client
# 1.创建客户端
# 修改加载配置文件的路径
# client = Fdfs_client(r'utils/fastdfs/client.conf')
client = Fdfs_client(r'/Users/mac/PycharmProjects/35_美多商城/-_git/meiduo_mail/utils/fastdfs/client.conf')

# 2.上传图片
# 图片的绝对路径
client.upload_by_filename('/Users/mac/Desktop/img/superwoman.jpg')

# 3.获取file_id   upload_by_filename上传成功会返回字典数据 字典数据中有file_id













