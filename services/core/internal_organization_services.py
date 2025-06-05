from typing import Dict, List, Optional
from core.configs import DEBUG_MODE
from models.core.internal_organization import InternalOrganization, InternalOrganizationModelException
from models.core.user import User
from models.core.permission import PermissionManager
from services.core.permission_services import PermissionServiceException, require_permission


class InternalOrganizationServiceException(Exception):
    """内部组织服务异常类"""
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message


# 注册内部组织管理相关权限
PermissionManager.register_permission(
    "internal_organization.manage.create",
    "创建内部组织权限"
)


@require_permission("internal_organization.manage.create")
def create_internal_organization(current_user: User, name: str, department_id: Optional[int] = None) -> Dict[str,str]:
    """创建内部组织服务函数
    
    Args:
        current_user (User): 当前用户对象
        name (str): 内部组织名称
        department_id (Optional[int]): 部门ID，默认为当前用户所属部门
        
    Returns:
        Dict[str,str]: 返回成功消息
        
    Raises:
        InternalOrganizationServiceException: 内部组织服务异常
        PermissionServiceException: 权限服务异常
        
    Note:
        - 只能在当前用户所属部门创建内部组织
    """
    try:
        current_department = current_user.get_department()
        
        if department_id:
            if department_id != current_department.id:
                raise InternalOrganizationServiceException(code=400, message="只能在当前用户所属部门创建内部组织")
        else:
            department_id = current_department.id
            
        result = InternalOrganization.create(name=name, department_id=department_id)
        return result
    except InternalOrganizationModelException as e:
        raise InternalOrganizationServiceException(code=e.code, message=e.message)
    except PermissionServiceException as e:
        raise e
    except InternalOrganizationServiceException as e:
        raise e
    except Exception as e:
        if DEBUG_MODE:
            raise InternalOrganizationServiceException(code=500, message=f"创建内部组织失败: {e}")
        else:
            raise InternalOrganizationServiceException(code=500, message="创建内部组织失败")


PermissionManager.register_permission(
    "internal_organization.manage.update",
    "更新内部组织权限"
)


@require_permission("internal_organization.manage.update")
def update_internal_organization(current_user: User, internal_organization_id: int, 
                                name: Optional[str] = None) -> Dict[str,str]:
    """更新内部组织服务函数
    
    Args:
        current_user (User): 当前用户对象
        internal_organization_id (int): 内部组织ID
        name (Optional[str]): 内部组织名称
        
    Returns:
        Dict[str,str]: 返回成功消息
        
    Raises:
        InternalOrganizationServiceException: 内部组织服务异常
        PermissionServiceException: 权限服务异常
        
    Note:
        - 只能更新当前部门的内部组织
    """
    try:
        current_department = current_user.get_department()
        internal_organization = InternalOrganization.get_internal_organization_by_id(internal_organization_id)
        
        if current_department.id != internal_organization.department_id:
            raise InternalOrganizationServiceException(code=400, message="只能更新当前部门的内部组织")
            
        result = InternalOrganization.update(
            internal_organization_id=internal_organization_id,
            name=name
        )
        return result
    except InternalOrganizationModelException as e:
        raise InternalOrganizationServiceException(code=e.code, message=e.message)
    except PermissionServiceException as e:
        raise e
    except InternalOrganizationServiceException as e:
        raise e
    except Exception as e:
        if DEBUG_MODE:
            raise InternalOrganizationServiceException(code=500, message=f"更新内部组织失败: {e}")
        else:
            raise InternalOrganizationServiceException(code=500, message="更新内部组织失败")


PermissionManager.register_permission(
    "internal_organization.manage.delete",
    "删除内部组织权限"
)


@require_permission("internal_organization.manage.delete")
def delete_internal_organization(current_user: User, internal_organization_id: int) -> Dict[str,str]:
    """删除内部组织服务函数
    
    Args:
        current_user (User): 当前用户对象
        internal_organization_id (int): 内部组织ID
        
    Returns:
        Dict[str,str]: 返回成功消息
        
    Raises:
        InternalOrganizationServiceException: 内部组织服务异常
        PermissionServiceException: 权限服务异常
        
    Note:
        - 只能删除当前部门的内部组织
    """
    try:
        current_department = current_user.get_department()
        internal_organization = InternalOrganization.get_internal_organization_by_id(internal_organization_id)
        
        if current_department.id != internal_organization.department_id:
            raise InternalOrganizationServiceException(code=400, message="只能删除当前部门的内部组织")
            
        result = InternalOrganization.delete(internal_organization_id=internal_organization_id)
        return result
    except InternalOrganizationModelException as e:
        raise InternalOrganizationServiceException(code=e.code, message=e.message)
    except PermissionServiceException as e:
        raise e
    except InternalOrganizationServiceException as e:
        raise e
    except Exception as e:
        if DEBUG_MODE:
            raise InternalOrganizationServiceException(code=500, message=f"删除内部组织失败: {e}")
        else:
            raise InternalOrganizationServiceException(code=500, message="删除内部组织失败")


PermissionManager.register_permission(
    "internal_organization.view.get",
    "获取内部组织权限"
)


@require_permission("internal_organization.view.get")
def get_internal_organization(current_user: User, internal_organization_id: int) -> InternalOrganization:
    """获取内部组织服务函数
    
    Args:
        current_user (User): 当前用户对象
        internal_organization_id (int): 内部组织ID
        
    Returns:
        InternalOrganization: 返回内部组织对象
        
    Raises:
        InternalOrganizationServiceException: 内部组织服务异常
        PermissionServiceException: 权限服务异常
        
    Note:
        - 只能获取当前部门或父部门的内部组织
    """
    try:
        current_department = current_user.get_department()
        internal_organization = InternalOrganization.get_internal_organization_by_id(internal_organization_id)
        
        if current_department.id != internal_organization.department_id and current_department.parent_id != internal_organization.department_id:
            raise InternalOrganizationServiceException(code=400, message="只能获取当前部门的内部组织")
            
        return internal_organization
    except InternalOrganizationModelException as e:
        raise InternalOrganizationServiceException(code=e.code, message=e.message)
    except PermissionServiceException as e:
        raise e
    except InternalOrganizationServiceException as e:
        raise e
    except Exception as e:
        if DEBUG_MODE:
            raise InternalOrganizationServiceException(code=500, message=f"获取内部组织失败: {e}")
        else:
            raise InternalOrganizationServiceException(code=500, message="获取内部组织失败")


PermissionManager.register_permission(
    "internal_organization.view.list",
    "获取内部组织列表权限"
)


@require_permission("internal_organization.view.list")
def get_internal_organizations_by_department(current_user: User, department_id: Optional[int] = None) -> List[InternalOrganization]:
    """获取部门内部组织列表服务函数
    
    Args:
        current_user (User): 当前用户对象
        department_id (Optional[int]): 部门ID，默认为当前用户所属部门
        
    Returns:
        List[InternalOrganization]: 返回内部组织列表
        
    Raises:
        InternalOrganizationServiceException: 内部组织服务异常
        PermissionServiceException: 权限服务异常
        
    Note:
        - 只能获取当前部门或父部门的内部组织列表
    """
    try:
        current_department = current_user.get_department()
        
        if department_id:
            if current_department.id != department_id and current_department.parent_id != department_id:
                raise InternalOrganizationServiceException(code=400, message="只能获取当前部门或父部门的内部组织列表")
        else:
            department_id = current_department.id
            
        return InternalOrganization.get_internal_organization_by_department_id(department_id)
    except InternalOrganizationModelException as e:
        raise InternalOrganizationServiceException(code=e.code, message=e.message)
    except PermissionServiceException as e:
        raise e
    except InternalOrganizationServiceException as e:
        raise e
    except Exception as e:
        if DEBUG_MODE:
            raise InternalOrganizationServiceException(code=500, message=f"获取内部组织列表失败: {e}")
        else:
            raise InternalOrganizationServiceException(code=500, message="获取内部组织列表失败") 