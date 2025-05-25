from typing import List, Optional
from core.configs import DEBUG_MODE
from models.core.role import Role, RoleModelException
from models.core.user import User
from models.core.permission import PermissionManager
from services.core.permission_services import PermissionServiceException, require_permission


class RoleServiceException(Exception):
    """角色服务异常类"""
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message


# 注册角色管理相关权限
PermissionManager.register_permission(
    "role.manage.create",
    "创建角色权限"
)


@require_permission("role.manage.create")
def create_role(current_user: User, name: str, description: Optional[str] = None, permissions: List[str] = []) -> str:
    """创建角色服务函数
    
    Args:
        current_user (User): 当前用户对象
        name (str): 角色名称
        description (Optional[str]): 角色描述
        permissions (List[str]): 角色权限列表
        
    Returns:
        str: 返回成功消息
        
    Raises:
        RoleServiceException: 角色服务异常
        PermissionServiceException: 权限服务异常
        
    Note:
        - 只能在当前用户所属部门创建角色
    """
    try:
        current_department = current_user.get_department()
        return Role.create(
            name=name,
            department_id=current_department.id,
            description=description,
            permissions=permissions
        )
    except RoleModelException as e:
        raise RoleServiceException(code=e.code, message=e.message)
    except PermissionServiceException as e:
        raise e
    except Exception as e:
        if DEBUG_MODE:
            raise RoleServiceException(code=500, message=f"创建角色失败: {e}")
        else:
            raise RoleServiceException(code=500, message="创建角色失败")


PermissionManager.register_permission(
    "role.manage.update",
    "更新角色权限"
)


@require_permission("role.manage.update")
def update_role(current_user: User, role_id: int, name: Optional[str] = None, 
                description: Optional[str] = None, permissions: Optional[List[str]] = None) -> str:
    """更新角色服务函数
    
    Args:
        current_user (User): 当前用户对象
        role_id (int): 角色ID
        name (Optional[str]): 角色名称
        description (Optional[str]): 角色描述
        permissions (Optional[List[str]]): 角色权限列表
        
    Returns:
        str: 返回成功消息
        
    Raises:
        RoleServiceException: 角色服务异常
        PermissionServiceException: 权限服务异常
        
    Note:
        - 只能更新当前部门的角色
    """
    try:
        current_department = current_user.get_department()
        role = Role.get_role(role_id)
        
        if current_department.id!=role.department_id:
            raise RoleServiceException(code=400, message="只能更新当前部门角色")
            
        return Role.update(
            role_id=role_id,
            name=name,
            description=description,
            permissions=permissions
        )
    except RoleModelException as e:
        raise RoleServiceException(code=e.code, message=e.message)
    except PermissionServiceException as e:
        raise e
    except Exception as e:
        if DEBUG_MODE:
            raise RoleServiceException(code=500, message=f"更新角色失败: {e}")
        else:
            raise RoleServiceException(code=500, message="更新角色失败")


PermissionManager.register_permission(
    "role.manage.delete",
    "删除角色权限"
)


@require_permission("role.manage.delete")
def delete_role(current_user: User, role_id: int) -> str:
    """删除角色服务函数
    
    Args:
        current_user (User): 当前用户对象
        role_id (int): 角色ID
        
    Returns:
        str: 返回成功消息
        
    Raises:
        RoleServiceException: 角色服务异常
        PermissionServiceException: 权限服务异常
        
    Note:
        - 只能删除当前部门的角色
    """
    try:
        current_department = current_user.get_department()
        role = Role.get_role(role_id)
        
        if current_department.id!=role.department_id:
            raise RoleServiceException(code=400, message="只能删除当前部门角色")
            
        return Role.delete(role_id=role_id)
    except RoleModelException as e:
        raise RoleServiceException(code=e.code, message=e.message)
    except PermissionServiceException as e:
        raise e
    except Exception as e:
        if DEBUG_MODE:
            raise RoleServiceException(code=500, message=f"删除角色失败: {e}")
        else:
            raise RoleServiceException(code=500, message="删除角色失败")


PermissionManager.register_permission(
    "role.view.get",
    "获取角色权限"
)


@require_permission("role.view.get")
def get_role(current_user: User, role_id: int) -> Role:
    """获取角色服务函数
    
    Args:
        current_user (User): 当前用户对象
        role_id (int): 角色ID
        
    Returns:
        Role: 返回角色对象
        
    Raises:
        RoleServiceException: 角色服务异常
        PermissionServiceException: 权限服务异常
        
    Note:
        - 只能获取当前部门的角色
    """
    try:
        current_department = current_user.get_department()
        role = Role.get_role(role_id)
        
        if current_department.id!=role.department_id:
            raise RoleServiceException(code=400, message="只能获取当前部门角色")
            
        return role
    except RoleModelException as e:
        raise RoleServiceException(code=e.code, message=e.message)
    except PermissionServiceException as e:
        raise e
    except Exception as e:
        if DEBUG_MODE:
            raise RoleServiceException(code=500, message=f"获取角色失败: {e}")
        else:
            raise RoleServiceException(code=500, message="获取角色失败")


PermissionManager.register_permission(
    "role.view.list",
    "获取角色列表权限"
)


@require_permission("role.view.list")
def get_roles_by_department(current_user: User, department_id: Optional[int] = None) -> List[Role]:
    """获取部门角色列表服务函数
    
    Args:
        current_user (User): 当前用户对象
        department_id (Optional[int]): 部门ID，如果不提供则获取当前部门的角色
        
    Returns:
        List[Role]: 返回角色对象列表
        
    Raises:
        RoleServiceException: 角色服务异常
        PermissionServiceException: 权限服务异常
        
    Note:
        - 只能获取当前部门的角色列表
    """
    try:
        current_department = current_user.get_department()
        
        if department_id is None:
            target_department_id = current_department.id
        else:
            if current_department.id!=department_id:
                raise RoleServiceException(code=400, message="只能获取当前部门的角色列表")
            target_department_id = department_id
            
        return Role.get_roles_by_department_id(target_department_id)
    except RoleModelException as e:
        raise RoleServiceException(code=e.code, message=e.message)
    except PermissionServiceException as e:
        raise e
    except Exception as e:
        if DEBUG_MODE:
            raise RoleServiceException(code=500, message=f"获取角色列表失败: {e}")
        else:
            raise RoleServiceException(code=500, message="获取角色列表失败")
