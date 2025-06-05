from typing import Dict, List, Optional
from core.configs import DEBUG_MODE
from models.core.internal_organization_to_user import InternalOrganizationToUser, InternalOrganizationToUserModelException
from models.core.internal_organization import InternalOrganization
from models.core.user import User
from models.core.permission import PermissionManager
from services.core.permission_services import PermissionServiceException, require_permission


class InternalOrganizationToUserServiceException(Exception):
    """内部组织与用户关系服务异常类"""
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message


# 注册内部组织与用户关系管理相关权限
PermissionManager.register_permission(
    "internal_organization_to_user.manage.create",
    "创建内部组织与用户关系权限"
)


@require_permission("internal_organization_to_user.manage.create")
def add_user_to_internal_organization(current_user: User, internal_organization_id: int, user_id: int) -> Dict[str,str]:
    """添加用户到内部组织服务函数
    
    Args:
        current_user (User): 当前用户对象
        internal_organization_id (int): 内部组织ID
        user_id (int): 用户ID
        
    Returns:
        Dict[str,str]: 返回成功消息
        
    Raises:
        InternalOrganizationToUserServiceException: 内部组织与用户关系服务异常
        PermissionServiceException: 权限服务异常
        
    Note:
        - 只能将当前部门的用户添加到当前部门的内部组织中
    """
    try:
        current_department = current_user.get_department()
        
        # 验证内部组织权限
        internal_organization = InternalOrganization.get_internal_organization_by_id(internal_organization_id)
        if current_department.id != internal_organization.department_id:
            raise InternalOrganizationToUserServiceException(code=400, message="只能操作当前部门的内部组织")
        
        # 验证用户权限
        target_user = User.get_user(user_id=user_id)
        if current_department.id != target_user.department_id:
            raise InternalOrganizationToUserServiceException(code=400, message="只能操作当前部门的用户")
            
        result = InternalOrganizationToUser.create(
            internal_organization_id=internal_organization_id,
            user_id=user_id
        )
        return result
    except InternalOrganizationToUserModelException as e:
        raise InternalOrganizationToUserServiceException(code=e.code, message=e.message)
    except PermissionServiceException as e:
        raise e
    except InternalOrganizationToUserServiceException as e:
        raise e
    except Exception as e:
        if DEBUG_MODE:
            raise InternalOrganizationToUserServiceException(code=500, message=f"添加用户到内部组织失败: {e}")
        else:
            raise InternalOrganizationToUserServiceException(code=500, message="添加用户到内部组织失败")


PermissionManager.register_permission(
    "internal_organization_to_user.manage.delete",
    "删除内部组织与用户关系权限"
)


@require_permission("internal_organization_to_user.manage.delete")
def remove_user_from_internal_organization(current_user: User, internal_organization_id: int, user_id: int) -> Dict[str,str]:
    """从内部组织移除用户服务函数
    
    Args:
        current_user (User): 当前用户对象
        internal_organization_id (int): 内部组织ID
        user_id (int): 用户ID
        
    Returns:
        Dict[str,str]: 返回成功消息
        
    Raises:
        InternalOrganizationToUserServiceException: 内部组织与用户关系服务异常
        PermissionServiceException: 权限服务异常
        
    Note:
        - 只能从当前部门的内部组织中移除用户
    """
    try:
        current_department = current_user.get_department()
        
        # 验证内部组织权限
        internal_organization = InternalOrganization.get_internal_organization_by_id(internal_organization_id)
        if current_department.id != internal_organization.department_id:
            raise InternalOrganizationToUserServiceException(code=400, message="只能操作当前部门的内部组织")
        
        # 验证用户权限
        target_user = User.get_user(user_id=user_id)
        if current_department.id != target_user.department_id:
            raise InternalOrganizationToUserServiceException(code=400, message="只能操作当前部门的用户")
            
        result = InternalOrganizationToUser.delete(
            internal_organization_id=internal_organization_id,
            user_id=user_id
        )
        return result
    except InternalOrganizationToUserModelException as e:
        raise InternalOrganizationToUserServiceException(code=e.code, message=e.message)
    except PermissionServiceException as e:
        raise e
    except InternalOrganizationToUserServiceException as e:
        raise e
    except Exception as e:
        if DEBUG_MODE:
            raise InternalOrganizationToUserServiceException(code=500, message=f"从内部组织移除用户失败: {e}")
        else:
            raise InternalOrganizationToUserServiceException(code=500, message="从内部组织移除用户失败")


PermissionManager.register_permission(
    "internal_organization_to_user.view.get_by_organization",
    "获取内部组织用户关系权限"
)


@require_permission("internal_organization_to_user.view.get_by_organization")
def get_users_by_internal_organization(current_user: User, internal_organization_id: int) -> List[InternalOrganizationToUser]:
    """获取内部组织中的用户关系列表服务函数
    
    Args:
        current_user (User): 当前用户对象
        internal_organization_id (int): 内部组织ID
        
    Returns:
        List[InternalOrganizationToUser]: 返回内部组织与用户关系列表
        
    Raises:
        InternalOrganizationToUserServiceException: 内部组织与用户关系服务异常
        PermissionServiceException: 权限服务异常
        
    Note:
        - 只能获取当前部门或直接父部门的内部组织中的用户关系
    """
    try:
        current_department = current_user.get_department()
        
        # 验证内部组织权限
        internal_organization = InternalOrganization.get_internal_organization_by_id(internal_organization_id)
        if current_department.id != internal_organization.department_id and current_department.parent_id != internal_organization.department_id:
            raise InternalOrganizationToUserServiceException(code=400, message="只能获取当前部门或直接父部门的内部组织用户关系")
            
        return InternalOrganizationToUser.get_internal_organization_to_user_by_internal_organization_id(
            internal_organization_id
        )
    except InternalOrganizationToUserModelException as e:
        raise InternalOrganizationToUserServiceException(code=e.code, message=e.message)
    except PermissionServiceException as e:
        raise e
    except InternalOrganizationToUserServiceException as e:
        raise e
    except Exception as e:
        if DEBUG_MODE:
            raise InternalOrganizationToUserServiceException(code=500, message=f"获取内部组织用户关系失败: {e}")
        else:
            raise InternalOrganizationToUserServiceException(code=500, message="获取内部组织用户关系失败")


PermissionManager.register_permission(
    "internal_organization_to_user.view.get_by_user",
    "获取用户内部组织关系权限"
)


@require_permission("internal_organization_to_user.view.get_by_user")
def get_internal_organizations_by_user(current_user: User, user_id: Optional[int] = None) -> List[InternalOrganizationToUser]:
    """获取用户所属内部组织关系列表服务函数
    
    Args:
        current_user (User): 当前用户对象
        user_id (Optional[int]): 用户ID，默认为当前用户
        
    Returns:
        List[InternalOrganizationToUser]: 返回内部组织与用户关系列表
        
    Raises:
        InternalOrganizationToUserServiceException: 内部组织与用户关系服务异常
        PermissionServiceException: 权限服务异常
        
    Note:
        - 只能获取当前部门或直接父部门的用户的内部组织关系
        - 如果不指定用户ID，则获取当前用户的内部组织关系
    """
    try:
        current_department = current_user.get_department()
        
        if user_id is None:
            user_id = current_user.id
        else:
            # 验证用户权限
            target_user = User.get_user(user_id=user_id)
            if current_department.id != target_user.department_id and current_department.parent_id != target_user.department_id:
                raise InternalOrganizationToUserServiceException(code=400, message="只能获取当前部门或直接父部门的用户的内部组织关系")
            
        return InternalOrganizationToUser.get_internal_organization_to_user_by_user_id(user_id)
    except InternalOrganizationToUserModelException as e:
        raise InternalOrganizationToUserServiceException(code=e.code, message=e.message)
    except PermissionServiceException as e:
        raise e
    except InternalOrganizationToUserServiceException as e:
        raise e
    except Exception as e:
        if DEBUG_MODE:
            raise InternalOrganizationToUserServiceException(code=500, message=f"获取用户内部组织关系失败: {e}")
        else:
            raise InternalOrganizationToUserServiceException(code=500, message="获取用户内部组织关系失败")

