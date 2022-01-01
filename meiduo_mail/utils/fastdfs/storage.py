from django.core.files.storage import Storage
# 1.Your custom storage system must be a subclass of django.core.files.storage.Storage:

# 2.Django must be able to instantiate your storage system without any arguments.
# This means that any settings should be taken from django.conf.settings:

# 3.Your storage class must implement the _open() and _save() methods,
# along with any other methods appropriate to your storage class

# 自定义文件存储类 可以访问到渲染的templates 主页
class MyStorage(Storage):
    def open(self, name, mode='rb'):
        """Retrieve the specified file from storage."""
        pass

    # 这两个方法复制 系统_open中的
    def save(self, name, content, max_length=None):
        """
        Save new content to the file specified by name. The content should be
        a proper File object or any Python file-like object, ready to be read
        from the beginning.
        """
        pass

    def url(self, name):
        # TODO 修改域名优化访问速度
        return 'http://192.168.1.6:8888/' + name

