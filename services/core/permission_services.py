from functools import wraps
from typing import List, Optional, Union, Callable, Any
from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlmodel import Session, select
from models.core.user import User, UserModelException
from models.core.role import Role, RoleModelException
from models.core.permission import PermissionModelException
from core.configs import DEBUG_MODE, application_sqlmodel_engine


class PermissionServiceException(Exception):
    """权限服务异常类
    
    用于表示权限服务相关的异常情况。
    继承自Exception类，用于自定义异常处理。
    """
    def __init__(self, code: int, message: str):
        self.message = message
        self.code = code


def require_permission(permission_key: str):
    """权限检查装饰器
    
    检查当前用户是否具有指定的权限。
    使用此装饰器的函数必须有一个名为 current_user 的 User 对象参数。
    
    Args:
        permission_key (str): 需要检查的权限键
        
    Returns:
        Callable: 装饰器函数
        
    Raises:
        PermissionServiceException: 当用户没有权限时抛出异常
        
    Example:
        @require_permission('user.create')
        def create_user_endpoint(current_user: User):
            # 函数实现
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 从参数中查找 current_user
            current_user = None
            
            # 首先检查关键字参数
            if 'current_user' in kwargs:
                current_user = kwargs['current_user']
            else:
                # 检查位置参数（通过函数签名推断）
                import inspect
                sig = inspect.signature(func)
                param_names = list(sig.parameters.keys())
                
                if 'current_user' in param_names:
                    param_index = param_names.index('current_user')
                    if param_index < len(args):
                        current_user = args[param_index]
            
            # 如果没有找到 current_user 参数，抛出异常
            if current_user is None:
                raise PermissionServiceException(
                    code=500, 
                    message="使用 require_permission 装饰器的函数必须包含 current_user 参数"
                )
            
            # 检查 current_user 是否为 User 类型
            if not isinstance(current_user, User):
                raise PermissionServiceException(
                    code=500, 
                    message="current_user 参数必须是 User 类型的对象"
                )
            
            # 检查用户是否具有指定权限
            if not _check_user_permission(current_user, permission_key):
                raise PermissionServiceException(
                    code=403, 
                    message=f"用户没有 '{permission_key}' 权限"
                )
            
            # 权限检查通过，执行原函数
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def _check_user_permission(user: User, permission_key: str) -> bool:
    """检查用户是否具有指定权限
    
    Args:
        user (User): 用户对象
        permission_key (str): 权限键
        
    Returns:
        bool: 如果用户具有权限返回 True，否则返回 False
    """
    try:
        # 获取用户的所有角色
        user_roles = user.get_roles()
        
        # 检查每个角色的权限
        for role in user_roles:
            if permission_key in role.permissions:
                return True
        
        return False
        
    except Exception as e:
        if DEBUG_MODE:
            raise PermissionServiceException(
                code=500, 
                message=f"检查用户权限时发生错误: {e}"
            )
        else:
            raise PermissionServiceException(
                code=500, 
                message="检查用户权限时发生错误"
            )


def get_user_permissions(user: User) -> List[str]:
    """获取用户的所有权限列表
    
    Args:
        user (User): 用户对象
        
    Returns:
        List[str]: 用户拥有的所有权限键列表
        
    Raises:
        PermissionServiceException: 当获取权限失败时抛出异常
    """
    try:
        permissions = set()  # 使用集合避免重复权限
        
        # 获取用户的所有角色
        user_roles = user.get_roles()
        
        # 收集所有角色的权限
        for role in user_roles:
            permissions.update(role.permissions)
        
        return list(permissions)
        
    except Exception as e:
        if DEBUG_MODE:
            raise PermissionServiceException(
                code=500, 
                message=f"获取用户权限列表时发生错误: {e}"
            )
        else:
            raise PermissionServiceException(
                code=500, 
                message="获取用户权限列表时发生错误"
            )


def require_any_permission(*permission_keys: str):
    """检查用户是否具有任意一个指定权限的装饰器
    
    用户只需要具有其中任意一个权限即可通过检查。
    
    Args:
        *permission_keys (str): 需要检查的权限键列表
        
    Returns:
        Callable: 装饰器函数
        
    Example:
        @require_any_permission('user.create', 'user.update')
        def manage_user_endpoint(current_user: User):
            # 函数实现
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 从参数中查找 current_user（与 require_permission 相同的逻辑）
            current_user = None
            
            if 'current_user' in kwargs:
                current_user = kwargs['current_user']
            else:
                import inspect
                sig = inspect.signature(func)
                param_names = list(sig.parameters.keys())
                
                if 'current_user' in param_names:
                    param_index = param_names.index('current_user')
                    if param_index < len(args):
                        current_user = args[param_index]
            
            if current_user is None:
                raise PermissionServiceException(
                    code=500, 
                    message="使用 require_any_permission 装饰器的函数必须包含 current_user 参数"
                )
            
            if not isinstance(current_user, User):
                raise PermissionServiceException(
                    code=500, 
                    message="current_user 参数必须是 User 类型的对象"
                )
            
            # 检查用户是否具有任意一个指定权限
            for permission_key in permission_keys:
                if _check_user_permission(current_user, permission_key):
                    return func(*args, **kwargs)
            
            # 如果没有任何权限，抛出异常
            permissions_str = "', '".join(permission_keys)
            raise PermissionServiceException(
                code=403, 
                message=f"用户没有以下任意权限: '{permissions_str}'"
            )
        
        return wrapper
    return decorator


def require_all_permissions(*permission_keys: str):
    """检查用户是否具有所有指定权限的装饰器
    
    用户必须具有所有指定的权限才能通过检查。
    
    Args:
        *permission_keys (str): 需要检查的权限键列表
        
    Returns:
        Callable: 装饰器函数
        
    Example:
        @require_all_permissions('user.create', 'department.view')
        def create_user_in_department_endpoint(current_user: User):
            # 函数实现
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 从参数中查找 current_user（与 require_permission 相同的逻辑）
            current_user = None
            
            if 'current_user' in kwargs:
                current_user = kwargs['current_user']
            else:
                import inspect
                sig = inspect.signature(func)
                param_names = list(sig.parameters.keys())
                
                if 'current_user' in param_names:
                    param_index = param_names.index('current_user')
                    if param_index < len(args):
                        current_user = args[param_index]
            
            if current_user is None:
                raise PermissionServiceException(
                    code=500, 
                    message="使用 require_all_permissions 装饰器的函数必须包含 current_user 参数"
                )
            
            if not isinstance(current_user, User):
                raise PermissionServiceException(
                    code=500, 
                    message="current_user 参数必须是 User 类型的对象"
                )
            
            # 检查用户是否具有所有指定权限
            missing_permissions = []
            for permission_key in permission_keys:
                if not _check_user_permission(current_user, permission_key):
                    missing_permissions.append(permission_key)
            
            if missing_permissions:
                permissions_str = "', '".join(missing_permissions)
                raise PermissionServiceException(
                    code=403, 
                    message=f"用户缺少以下权限: '{permissions_str}'"
                )
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator
