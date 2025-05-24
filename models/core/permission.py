

class PermissionModelException(Exception):
    """权限异常类。
    
    用于表示权限相关的异常情况。
    继承自Exception类，用于自定义异常处理。"""
    def __init__(self,code:int,message:str):
        self.message=message
        self.code=code
        