from datetime import datetime, timezone
from typing import Optional,List,Dict
from sqlalchemy import JSON
from sqlmodel import SQLModel,Field, Session, select
from core.configs import DEBUG_MODE, application_sqlmodel_engine
from models.core.department import Department
class RoleModelException(Exception):
    """角色模型异常类。
    
    用于表示角色模型相关的异常情况。
    继承自Exception类，用于自定义异常处理。"""
    def __init__(self,code:int,message:str):
        self.message=message
        self.code=code

class Role(SQLModel,table=True):
    __tablename__="roles"
    
    id:Optional[int]=Field(default=None,primary_key=True)
    name:str=Field(...,index=True)
    description:Optional[str]=Field(default='')
    permissions:List[str]=Field(default=[],sa_type=JSON)
    department_id:int=Field(...,foreign_key="departments.id",description="所属部门ID")
    created_at:datetime=Field(default_factory=lambda:datetime.now(timezone.utc))
    updated_at:datetime=Field(default_factory=lambda:datetime.now(timezone.utc))

    @classmethod
    def create(cls,name:str,department_id:int,description:Optional[str]=None,permissions:List[str]=[])->str:
        """创建角色。
        
        Args:
            name (str): 角色名称
            department_id (int): 所属部门ID
            description (Optional[str]): 角色描述
            permissions (List[str]): 角色权限列表
        
        Returns:
            str: 创建成功返回"角色创建成功"
        
        Raises:
            RoleModelException: 如果创建失败，抛出异常
        """
        with Session(application_sqlmodel_engine) as session:
            try:
                department=session.exec(select(Department).where(Department.id==department_id)).first()
                if not department:
                    raise RoleModelException(code=404,message="指定的部门不存在")
                role=cls(
                    name=name,
                    department_id=department_id,
                    description=description,
                    permissions=permissions
                )
                session.add(role)
                session.commit()                
                return "角色创建成功"
            except Exception as e:
                session.rollback()
                if DEBUG_MODE:
                    raise RoleModelException(code=500,message=f"角色创建失败: {e}")
                else:
                    raise RoleModelException(code=500,message="角色创建失败")
    @classmethod
    def update(cls,role_id:int,name:Optional[str]=None,description:Optional[str]=None,permissions:Optional[List[str]]=None)->str:
        """更新角色。
        Args:
            role_id (int): 角色ID
            name (Optional[str]): 角色名称
            description (Optional[str]): 角色描述
            permissions (List[str]): 角色权限列表
        
        Returns:
            str: 更新成功返回"角色更新成功"
        
        Raises:
            RoleModelException: 如果更新失败，抛出异常
        """ 
        with Session(application_sqlmodel_engine) as session:
            try:
                role=session.exec(select(Role).where(Role.id==role_id)).first()
                if not role:
                    raise RoleModelException(code=404,message="指定的角色不存在")
                if name:
                    role.name=name
                if description:
                    role.description=description
                if permissions:
                    role.permissions=permissions
                role.updated_at=datetime.now(timezone.utc)
                session.add(role)
                session.commit()
                return "角色更新成功"
            except Exception as e:
                session.rollback()
                if DEBUG_MODE:
                    raise RoleModelException(code=500,message=f"角色更新失败: {e}")
                else:
                    raise RoleModelException(code=500,message="角色更新失败")
    @classmethod
    def delete(cls,role_id:int)->str:
        """删除角色。
        
        Args:
            role_id (int): 角色ID
        
        Returns:
            str: 删除成功返回"角色删除成功"
        
        Raises:
            RoleModelException: 如果删除失败，抛出异常
        """
        with Session(application_sqlmodel_engine) as session:
            try:
                role=session.exec(select(Role).where(Role.id==role_id)).first()
                if not role:
                    raise RoleModelException(code=404,message="指定的角色不存在")
                session.delete(role)
                session.commit()
                return "角色删除成功"
            except Exception as e:
                session.rollback()
                if DEBUG_MODE:
                    raise RoleModelException(code=500,message=f"角色删除失败: {e}")
                else:
                    raise RoleModelException(code=500,message="角色删除失败")
    @classmethod
    def get_role(cls,role_id:int)->"Role":
        """获取角色。
        
        Args:
            role_id (int): 角色ID
        
        Returns:
            Role: 返回角色对象
        
        Raises:
            RoleModelException: 如果获取失败，抛出异常
        """
        with Session(application_sqlmodel_engine) as session:
            try:
                role=session.exec(select(Role).where(Role.id==role_id)).first()
                if not role:
                    raise RoleModelException(code=404,message="指定的角色不存在")
                return role
            except Exception as e:
                if DEBUG_MODE:
                    raise RoleModelException(code=500,message=f"获取角色失败: {e}")
                else:
                    raise RoleModelException(code=500,message="获取角色失败")
    @classmethod
    def get_roles_by_department_id(cls,department_id:int)->List["Role"]:
        """根据部门ID获取角色列表。
        
        Args:
            department_id (int): 部门ID
        
        Returns:
            List[Role]: 返回角色对象列表
        
        Raises:
            RoleModelException: 如果获取失败，抛出异常
        """
        with Session(application_sqlmodel_engine) as session:
            try:
                roles=session.exec(select(Role).where(Role.department_id==department_id)).all()
                return roles
            except Exception as e:
                if DEBUG_MODE:
                    raise RoleModelException(code=500,message=f"获取角色失败: {e}")
                else:
                    raise RoleModelException(code=500,message="获取角色失败")