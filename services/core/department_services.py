from typing import List, Optional,Dict
from core.configs import DEBUG_MODE
from models.core.department import Department, DepartmentModelException
from models.core.user import User
from models.core.role import Role
from models.core.permission import PermissionManager
from services.core.permission_services import PermissionServiceException, require_permission




class DepartmentServiceException(Exception):
    """部门服务异常类"""
    def __init__(self,code:int,message:str):
        self.code=code
        self.message=message

PermissionManager.register_permission(
    "department.manage.create",
    "创建部门权限"
)
@require_permission("department.manage.create")
def create_department(current_user:User,name:str,description:Optional[str]=None,manager_name:Optional[str]=None,manager_phone:Optional[str]=None)->str:
    """创建子部门服务函数
    Args:
        current_user (User): 当前用户对象
        name (str): 部门名称
        description (Optional[str]): 部门描述
        manager_name (Optional[str]): 部门负责人姓名
        manager_phone (Optional[str]): 部门负责人电话

    Returns:
        str: 返回成功消息
    Raises:
        DepartmentServiceException: 部门模型异常
        PermissionServiceException: 权限服务异常
    Note:
        - 只能创建直接子部门
        - 村社级部门不能再创建子部门
    """
    try:
        current_department=current_user.get_department()
        if current_department.level+1 not in [1,2,3]:
            if current_department.level+1>3:
                raise DepartmentServiceException(code=400,message="村社级部门不能再创建子部门")
            raise DepartmentServiceException(code=400,message="只能创建县级、镇街级、村社级部门")
        
        return Department.create(
            name=name,
            level=current_department.level+1,
            parent_id=current_department.id,
            description=description,
            manager_name=manager_name,
            manager_phone=manager_phone
        )
    except DepartmentModelException as e:
        raise DepartmentServiceException(code=e.code,message=e.message)
    except PermissionServiceException as e:
        raise e
    except DepartmentServiceException as e:
        raise e
    except Exception as e:
        if DEBUG_MODE:
            raise DepartmentServiceException(code=500,message=f"创建部门失败: {e}")
        else:
            raise DepartmentServiceException(code=500,message="创建部门失败")
PermissionManager.register_permission(
    "department.manage.update",
    "更新部门权限"
)
@require_permission("department.manage.update")
def update_department(current_user:User,department_id:int,name:Optional[str]=None,description:Optional[str]=None,manager_name:Optional[str]=None,manager_phone:Optional[str]=None)->str:
    """更新部门服务函数
    Args:
        current_user (User): 当前用户对象
        department_id (int): 子部门ID
        name (Optional[str]): 部门名称
        description (Optional[str]): 部门描述
        manager_name (Optional[str]): 部门负责人姓名
        manager_phone (Optional[str]): 部门负责人电话
    Returns:
        str: 返回成功消息
    Raises:
        DepartmentServiceException: 部门模型异常
        PermissionServiceException: 权限服务异常
    Note:
        - 只能更新直接子部门
    """
    try:
        current_department=current_user.get_department()
        if not current_department.check_is_direct_child(department_id):
            raise DepartmentServiceException(code=400,message="只能更新直接子部门")
        return Department.update(
            department_id=department_id,
            name=name,
            description=description,
            manager_name=manager_name,
            manager_phone=manager_phone
        )
    except DepartmentModelException as e:
        raise DepartmentServiceException(code=e.code,message=e.message)
    except PermissionServiceException as e:
        raise e
    except DepartmentServiceException as e:
        raise e
    except Exception as e:
        if DEBUG_MODE:
            raise DepartmentServiceException(code=500,message=f"更新部门失败: {e}")
        else:
            raise DepartmentServiceException(code=500,message="更新部门失败")
PermissionManager.register_permission(
    "department.manage.delete",
    "删除部门权限"
)
@require_permission('department.manage.delete')
def delete_department(current_user:User,department_id:int)->str:
    """删除部门服务函数
    Args:
        current_user (User): 当前用户对象
        department_id (int): 子部门ID
    Returns:
        str: 返回成功消息
    Raises:
        DepartmentServiceException: 部门模型异常
        PermissionServiceException: 权限服务异常
    Note:
        - 只能删除直接子部门
    """
    try:
        current_department=current_user.get_department()
        if not current_department.check_is_direct_child(department_id):
            raise DepartmentServiceException(code=400,message="只能删除直接子部门")
        return Department.delete(department_id=department_id)
    except DepartmentModelException as e:
        raise DepartmentServiceException(code=e.code,message=e.message)
    except PermissionServiceException as e:
        raise e
    except DepartmentServiceException as e:
        raise e
    except Exception as e:
        if DEBUG_MODE:
            raise DepartmentServiceException(code=500,message=f"删除部门失败: {e}")
        else:
            raise DepartmentServiceException(code=500,message="删除部门失败")
PermissionManager.register_permission(
    "department.view.get",
    "获取部门权限"
)
@require_permission('department.view.get')
def get_department(current_user:User,department_id:Optional[int]=None)->Department:
    """
    获取部门服务函数
    Args:
        current_user (User): 当前用户对象
        department_id (int,optional): 子部门ID
    Returns:
        Department: 返回部门对象
    Raises:
        DepartmentServiceException: 部门模型异常
        PermissionServiceException: 权限服务异常
    Note:
        - 只能获取当前部门或子部门(包括子部门的子部门)
    """
    try:
        current_department=current_user.get_department()
        if department_id:
            if not current_department.check_is_child(department_id) and department_id!=current_department.id:
                raise DepartmentServiceException(code=400,message="只能获取当前部门或子部门(包括子部门的子部门)")
            return Department.get_department(department_id=department_id)
        else:
            return current_department
    except DepartmentModelException as e:
        raise DepartmentServiceException(code=e.code,message=e.message)
    except PermissionServiceException as e:
        raise e
    except DepartmentServiceException as e:
        raise e
    except Exception as e:
        if DEBUG_MODE:
            raise DepartmentServiceException(code=500,message=f"获取部门失败: {e}")
        else:
            raise DepartmentServiceException(code=500,message="获取部门失败")

PermissionManager.register_permission(
    "department.view.tree",
    "获取部门树权限"
)
@require_permission('department.view.tree')
def get_department_tree(current_user:User)->List[Dict[str,str]]:
    """获取当前部门树服务函数
    Args:
        current_user (User): 当前用户对象
    Returns:
        List[Dict[str,str]]: 返回部门树
    Raises:
        DepartmentServiceException: 部门模型异常
        PermissionServiceException: 权限服务异常
    """
    try:
        current_department=current_user.get_department()
        return Department.get_department_tree_by_parent_id_fast(current_department.id)
    except DepartmentModelException as e:
        raise DepartmentServiceException(code=e.code,message=e.message)
    except PermissionServiceException as e:
        raise e
    except DepartmentServiceException as e:
        raise e
    except Exception as e:
        if DEBUG_MODE:
            raise DepartmentServiceException(code=500,message=f"获取部门树失败: {e}")
        else:
            raise DepartmentServiceException(code=500,message="获取部门树失败")
