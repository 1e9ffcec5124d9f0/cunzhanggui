

from typing import Dict


class PermissionModelException(Exception):
    """权限异常类。
    
    用于表示权限相关的异常情况。
    继承自Exception类，用于自定义异常处理。"""
    def __init__(self,code:int,message:str):
        self.message=message
        self.code=code



class PermissionManager():
    __permissions={}

    @classmethod
    def register_permission(cls,permission_key:str,permission_name:str)->None:
        """ 
        注册权限。

        Args:
            permission_key (str): 权限键|权限代码
            permission_name (str): 权限名称

        Returns:
            None
        """
        cls.__permissions[permission_key]=permission_name

    @classmethod
    def get_all_permissions(cls)->Dict[str,str]:
        """
        获取所有注册的权限。

        Returns:
            Dict[str,str]: 所有注册的权限
        """
        return cls.__permissions