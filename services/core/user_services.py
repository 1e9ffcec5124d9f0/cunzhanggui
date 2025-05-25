from typing import List, Optional, Dict

from flask_jwt_extended import create_access_token
from core.configs import DEBUG_MODE
from models.core.user import User, UserModelException
from models.core.department import Department
from models.core.role import Role
from models.core.permission import PermissionManager
from services.core.permission_services import PermissionServiceException, require_permission


class UserServiceException(Exception):
    """用户服务异常类"""
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message


PermissionManager.register_permission(
    "user.manage.create",
    "创建用户权限"
)
@require_permission("user.manage.create")
def create_user(current_user: User, username: str, password: str, id_card_number: str, 
                phone_number: str, real_name: str, department_id: int) -> str:
    """创建用户服务函数
    
    Args:
        current_user (User): 当前用户对象
        username (str): 用户名
        password (str): 密码
        id_card_number (str): 身份证号码
        phone_number (str): 手机号码
        real_name (str): 真实姓名
        department_id (int): 所属部门ID
        
    Returns:
        str: 返回成功消息
        
    Raises:
        UserServiceException: 用户模型异常
        PermissionServiceException: 权限服务异常
        
    Note:
        - 只能在当前部门或直接子部门中创建用户
    """
    try:
        current_department = current_user.get_department()
        
        if department_id != current_department.id and not current_department.check_is_direct_child(department_id):
            raise UserServiceException(code=400, message="只能在当前部门或直接子部门中创建用户")
        
        return User.create(
            username=username,
            password=password,
            id_card_number=id_card_number,
            phone_number=phone_number,
            real_name=real_name,
            department_id=department_id
        )
    except UserModelException as e:
        raise UserServiceException(code=e.code, message=e.message)
    except PermissionServiceException as e:
        raise e
    except Exception as e:
        if DEBUG_MODE:
            raise UserServiceException(code=500, message=f"创建用户失败: {e}")
        else:
            raise UserServiceException(code=500, message="创建用户失败")


PermissionManager.register_permission(
    "user.manage.update",
    "更新用户权限"
)
@require_permission("user.manage.update")
def update_user(current_user: User, user_id: int, username: Optional[str] = None,
                id_card_number: Optional[str] = None, phone_number: Optional[str] = None,
                real_name: Optional[str] = None, department_id: Optional[int] = None,
                role_ids: Optional[List[int]] = None) -> str:
    """更新用户服务函数
    
    Args:
        current_user (User): 当前用户对象
        user_id (int): 用户ID
        username (Optional[str]): 用户名
        id_card_number (Optional[str]): 身份证号码
        phone_number (Optional[str]): 手机号码
        real_name (Optional[str]): 真实姓名
        department_id (Optional[int]): 所属部门ID
        role_ids (Optional[List[int]]): 角色ID列表
        
    Returns:
        str: 返回成功消息
        
    Raises:
        UserServiceException: 用户模型异常
        PermissionServiceException: 权限服务异常
        
    Note:
        - 只能更新当前部门或直接子部门的用户
        - 如果指定新部门，新部门也必须是当前部门或直接子部门
    """
    try:
        current_department = current_user.get_department()
        
        # 获取目标用户
        target_user = User.get_user(user_id=user_id)
        
        # 检查目标用户是否在当前部门或子部门中
        if (target_user.department_id != current_department.id and 
            not current_department.check_is_direct_child(target_user.department_id)):
            raise UserServiceException(code=400, message="只能更新当前部门或直接子部门的用户")
        
        # 如果要更改部门，检查新部门是否合法
        if department_id and department_id != target_user.department_id:
            if (department_id != current_department.id and 
                not current_department.check_is_direct_child(department_id)):
                raise UserServiceException(code=400, message="只能将用户分配到当前部门或直接子部门")
        
        return User.update(
            user_id=user_id,
            username=username,
            id_card_number=id_card_number,
            phone_number=phone_number,
            real_name=real_name,
            department_id=department_id,
            role_ids=role_ids
        )
    except UserModelException as e:
        raise UserServiceException(code=e.code, message=e.message)
    except PermissionServiceException as e:
        raise e
    except Exception as e:
        if DEBUG_MODE:
            raise UserServiceException(code=500, message=f"更新用户失败: {e}")
        else:
            raise UserServiceException(code=500, message="更新用户失败")


PermissionManager.register_permission(
    "user.manage.delete",
    "删除用户权限"
)
@require_permission("user.manage.delete")
def delete_user(current_user: User, user_id: int) -> str:
    """删除用户服务函数
    
    Args:
        current_user (User): 当前用户对象
        user_id (int): 用户ID
        
    Returns:
        str: 返回成功消息
        
    Raises:
        UserServiceException: 用户模型异常
        PermissionServiceException: 权限服务异常
        
    Note:
        - 只能删除当前部门的用户
        - 不能删除自己
    """
    try:
        current_department = current_user.get_department()
        
        # 不能删除自己
        if user_id == current_user.id:
            raise UserServiceException(code=400, message="不能删除自己")
        
        # 获取目标用户
        target_user = User.get_user(user_id=user_id)
        
        if current_department.id!=target_user.department_id:
            raise UserServiceException(code=400, message="只能删除当前部门用户")
        
        return User.delete(user_id=user_id)
    except UserModelException as e:
        raise UserServiceException(code=e.code, message=e.message)
    except PermissionServiceException as e:
        raise e
    except Exception as e:
        if DEBUG_MODE:
            raise UserServiceException(code=500, message=f"删除用户失败: {e}")
        else:
            raise UserServiceException(code=500, message="删除用户失败")


PermissionManager.register_permission(
    "user.view.get",
    "获取用户权限"
)
@require_permission("user.view.get")
def get_user(current_user: User, user_id: Optional[int] = None, username: Optional[str] = None) -> User:
    """获取用户服务函数
    
    Args:
        current_user (User): 当前用户对象
        user_id (Optional[int]): 用户ID
        username (Optional[str]): 用户名
        
    Returns:
        User: 返回用户对象
        
    Raises:
        UserServiceException: 用户模型异常
        PermissionServiceException: 权限服务异常
        
    Note:
        - 只能获取当前部门或子部门的用户
        - 如果不指定参数，返回当前用户信息
    """
    try:
        # 如果没有指定参数，返回当前用户
        if not user_id and not username:
            return current_user
        
        current_department = current_user.get_department()
        
        # 获取目标用户
        target_user = User.get_user(user_id=user_id, username=username)
        
        # 检查目标用户是否在当前部门或子部门中
        if (target_user.department_id != current_department.id and 
            not current_department.check_is_child(target_user.department_id)):
            raise UserServiceException(code=400, message="只能获取当前部门或子部门的用户")
        
        return target_user
    except UserModelException as e:
        raise UserServiceException(code=e.code, message=e.message)
    except PermissionServiceException as e:
        raise e
    except Exception as e:
        if DEBUG_MODE:
            raise UserServiceException(code=500, message=f"获取用户失败: {e}")
        else:
            raise UserServiceException(code=500, message="获取用户失败")


PermissionManager.register_permission(
    "user.view.list",
    "获取用户列表权限"
)
@require_permission("user.view.list")
def get_users_by_department(current_user: User, department_id: Optional[int] = None) -> List[User]:
    """根据部门获取用户列表服务函数
    
    Args:
        current_user (User): 当前用户对象
        department_id (Optional[int]): 部门ID，如果不指定则获取当前部门用户
        
    Returns:
        List[User]: 返回用户列表
        
    Raises:
        UserServiceException: 用户模型异常
        PermissionServiceException: 权限服务异常
        
    Note:
        - 只能获取当前部门或子部门的用户列表
    """
    try:
        current_department = current_user.get_department()
        
        # 如果没有指定部门ID，使用当前用户的部门
        if department_id is None:
            department_id = current_department.id
        else:
            # 检查指定部门是否为当前部门或子部门
            if (department_id != current_department.id and 
                not current_department.check_is_child(department_id)):
                raise UserServiceException(code=400, message="只能获取当前部门或子部门的用户列表")
        
        return User.get_users_by_department_id(department_id=department_id)
    except UserModelException as e:
        raise UserServiceException(code=e.code, message=e.message)
    except PermissionServiceException as e:
        raise e
    except Exception as e:
        if DEBUG_MODE:
            raise UserServiceException(code=500, message=f"获取用户列表失败: {e}")
        else:
            raise UserServiceException(code=500, message="获取用户列表失败")


PermissionManager.register_permission(
    "user.manage.password",
    "修改用户密码权限"
)
@require_permission("user.manage.password")
def change_user_password(current_user: User, user_id: int, new_password: str) -> str:
    """修改用户密码服务函数
    
    Args:
        current_user (User): 当前用户对象
        user_id (int): 用户ID
        new_password (str): 新密码
        
    Returns:
        str: 返回成功消息
        
    Raises:
        UserServiceException: 用户模型异常
        PermissionServiceException: 权限服务异常
        
    Note:
        - 只能修改当前部门或直接子部门用户的密码
        - 可以修改自己的密码
    """
    try:
        current_department = current_user.get_department()
        
        # 如果是修改自己的密码，直接允许
        if user_id != current_user.id:
            # 获取目标用户
            target_user = User.get_user(user_id=user_id)
            
            # 检查目标用户是否在当前部门或子部门中
            if (target_user.department_id != current_department.id and 
                not current_department.check_is_direct_child(target_user.department_id)):
                raise UserServiceException(code=400, message="只能修改当前部门或直接子部门用户的密码")
        
        return User.change_password(user_id=user_id, new_password=new_password)
    except UserModelException as e:
        raise UserServiceException(code=e.code, message=e.message)
    except PermissionServiceException as e:
        raise e
    except Exception as e:
        if DEBUG_MODE:
            raise UserServiceException(code=500, message=f"修改密码失败: {e}")
        else:
            raise UserServiceException(code=500, message="修改密码失败")

PermissionManager.register_permission(
    "user.login",
    "用户登录权限"
)
@require_permission("user.login")
def login(current_user: User, username: str, password: str) -> str:
    """用户登录服务函数
    
    Args:
        current_user (User): 当前用户对象
        username (str): 用户名
        password (str): 密码
        
    Returns:
        str: Access Token
    
    Raises:
        UserServiceException: 用户模型异常
        PermissionServiceException: 权限服务异常
    """
    try:
        from core.crypto.sm2_crypto import SM2Crypto
        password=SM2Crypto.decrypt(password)
        if User.verify_password(username=username, password=password) and current_user.login_attempts<=5:
            current_user.login_attempts=0
            User.update(user_id=current_user.id, login_attempts=current_user.login_attempts)
            return create_access_token(identity=current_user.id)
        else:
            current_user.login_attempts+=1
            User.update(user_id=current_user.id, login_attempts=current_user.login_attempts)
            raise UserServiceException(code=403, message="用户名或密码错误")
    except UserModelException as e:
        raise UserServiceException(code=e.code, message=e.message)
    except PermissionServiceException as e:
        raise e
    except Exception as e:
        if DEBUG_MODE:
            raise UserServiceException(code=500, message=f"登录失败: {e}")
        else:
            raise UserServiceException(code=500, message="登录失败")

