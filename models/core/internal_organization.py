

from datetime import datetime, timezone
from typing import Dict, List, Optional
from sqlmodel import Field, SQLModel, Session, select
from core.configs import DEBUG_MODE, application_sqlmodel_engine

class InternalOrganizationModelException(Exception):
    """内部组织模型异常类。
    
    用于表示内部组织模型相关的异常情况。
    继承自Exception类，用于自定义异常处理。"""
    def __init__(self,code:int,message:str):
        self.message=message
        self.code=code



class InternalOrganization(SQLModel,table=True):
    __tablename__="internal_organizations"
    id:Optional[int]=Field(default=None,primary_key=True)
    name:str=Field(...,index=True)
    department_id:int=Field(...,foreign_key="departments.id")
    created_at:datetime=Field(default_factory=lambda:datetime.now(timezone.utc))
    updated_at:datetime=Field(default_factory=lambda:datetime.now(timezone.utc))


    @classmethod
    def get_internal_organization_by_id(cls,internal_organization_id:int)->"InternalOrganization":
        """
        获取内部组织。
        
        Args:
            internal_organization_id (int): 内部组织ID

        Returns:
            InternalOrganization: 内部组织

        Raises:
            InternalOrganizationModelException: 如果获取失败，抛出异常
        """
        with Session(application_sqlmodel_engine) as session:
            try:
                internal_organization=session.get(InternalOrganization,internal_organization_id)
                if not internal_organization:
                    raise InternalOrganizationModelException(code=404,message="内部组织不存在")
                return internal_organization
            except Exception as e:
                if DEBUG_MODE:
                    raise InternalOrganizationModelException(code=500,message=f"内部组织获取失败: {e}")
                else:
                    raise InternalOrganizationModelException(code=500,message="内部组织获取失败")

    @classmethod
    def get_internal_organization_by_department_id(cls,department_id:int)->List["InternalOrganization"]:
        """
        获取内部组织。
        
        Args:
            department_id (int): 部门ID

        Returns:
            List[InternalOrganization]: 内部组织列表

        Raises:
            InternalOrganizationModelException: 如果获取失败，抛出异常
        """
        with Session(application_sqlmodel_engine) as session:
            try:
                internal_organizations=session.exec(select(InternalOrganization).where(InternalOrganization.department_id==department_id)).all()
                if not internal_organizations:
                    return []
                return internal_organizations
            except Exception as e:
                if DEBUG_MODE:
                    raise InternalOrganizationModelException(code=500,message=f"内部组织获取失败: {e}")
                else:
                    raise InternalOrganizationModelException(code=500,message="内部组织获取失败")

    @classmethod
    def create(cls,name:str,department_id:int)->Dict[str,str]:
        """
        创建内部组织。
        
        Args:
            name (str): 内部组织名称
            department_id (int): 部门ID
        """
        with Session(application_sqlmodel_engine) as session:   
            try:
                internal_organization=InternalOrganization(name=name,department_id=department_id)
                session.add(internal_organization)
                session.commit()
                return {"code":200,"message":"内部组织创建成功"}
            except Exception as e:
                session.rollback()
                if DEBUG_MODE:
                    raise InternalOrganizationModelException(code=500,message=f"内部组织创建失败: {e}")
                else:
                    raise InternalOrganizationModelException(code=500,message="内部组织创建失败")

    @classmethod
    def update(cls,internal_organization_id:int,name:Optional[str]=None)->Dict[str,str]:
        """
        更新内部组织。
        
        Args:
            internal_organization_id (int): 内部组织ID
            name (str,optional): 内部组织名称
        
        Returns:
            Dict[str,str]: 返回更新结果
        
        Raises:
            InternalOrganizationModelException: 如果更新失败，抛出异常
        """
        with Session(application_sqlmodel_engine) as session:
            try:
                internal_organization=session.get(InternalOrganization,internal_organization_id)
                if not internal_organization:
                    raise InternalOrganizationModelException(code=404,message="内部组织不存在")
                if name:
                    internal_organization.name=name
                session.commit()
                return {"code":200,"message":"内部组织更新成功"}
            except Exception as e:
                session.rollback()
                if DEBUG_MODE:
                    raise InternalOrganizationModelException(code=500,message=f"内部组织更新失败: {e}")
                else:
                    raise InternalOrganizationModelException(code=500,message="内部组织更新失败")

    @classmethod
    def delete(cls,internal_organization_id:int)->Dict[str,str]:
        """
        删除内部组织。
        
        Args:
            internal_organization_id (int): 内部组织ID
        
        Returns:
            Dict[str,str]: 返回删除结果
        
        Raises:
            InternalOrganizationModelException: 如果删除失败，抛出异常
        """
        with Session(application_sqlmodel_engine) as session:
            try:
                internal_organization=session.get(InternalOrganization,internal_organization_id)
                if not internal_organization:
                    raise InternalOrganizationModelException(code=404,message="内部组织不存在")
                session.delete(internal_organization)
                session.commit()
                return {"code":200,"message":"内部组织删除成功"}
            except Exception as e:
                session.rollback()
                if DEBUG_MODE:
                    raise InternalOrganizationModelException(code=500,message=f"内部组织删除失败: {e}")
                else:
                    raise InternalOrganizationModelException(code=500,message="内部组织删除失败")