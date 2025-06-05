

from typing import Dict, List, Optional
from sqlmodel import Field, SQLModel, Session, select
from core.configs import DEBUG_MODE, application_sqlmodel_engine


class InternalOrganizationToUserModelException(Exception):
    """内部组织与用户关系模型异常类。"""
    def __init__(self,code:int,message:str):
        self.message=message
        self.code=code


class InternalOrganizationToUser(SQLModel,table=True):
    __tablename__="internal_organization_to_users"
    id:Optional[int]=Field(default=None,primary_key=True)
    internal_organization_id:int=Field(...,foreign_key="internal_organizations.id")
    user_id:int=Field(...,foreign_key="users.id")

    @classmethod
    def create(cls,internal_organization_id:int,user_id:int)->Dict[str,str]:
        """
        创建内部组织与用户关系。
        
        Args:
            internal_organization_id (int): 内部组织ID
            user_id (int): 用户ID
        """
        with Session(application_sqlmodel_engine) as session:
            try:
                internal_organization_to_user=InternalOrganizationToUser(internal_organization_id=internal_organization_id,user_id=user_id)
                session.add(internal_organization_to_user)
                session.commit()
                return {"code":200,"message":"内部组织与用户关系创建成功"}
            except Exception as e:
                session.rollback()
                if DEBUG_MODE:
                    raise InternalOrganizationToUserModelException(code=500,message=f"内部组织与用户关系创建失败: {e}")
                else:
                    raise InternalOrganizationToUserModelException(code=500,message="内部组织与用户关系创建失败")

    @classmethod
    def delete(cls,internal_organization_id:int,user_id:int)->Dict[str,str]:
        """
        删除内部组织与用户关系。
        
        Args:
            internal_organization_id (int): 内部组织ID
            user_id (int): 用户ID
        """
        with Session(application_sqlmodel_engine) as session:
            try:
                internal_organization_to_user=session.get(InternalOrganizationToUser,internal_organization_id,user_id)
                if not internal_organization_to_user:
                    raise InternalOrganizationToUserModelException(code=404,message="内部组织与用户关系不存在")
                session.delete(internal_organization_to_user)
                session.commit()
                return {"code":200,"message":"内部组织与用户关系删除成功"}
            except Exception as e:
                session.rollback()
                if DEBUG_MODE:
                    raise InternalOrganizationToUserModelException(code=500,message=f"内部组织与用户关系删除失败: {e}")
                else:
                    raise InternalOrganizationToUserModelException(code=500,message="内部组织与用户关系删除失败")
    @classmethod
    def get_internal_organization_to_user_by_internal_organization_id(cls,internal_organization_id:int)->List["InternalOrganizationToUser"]:
        """
        获取内部组织与用户关系。
        
        Args:
            internal_organization_id (int): 内部组织ID

        Returns:
            List[InternalOrganizationToUser]: 内部组织与用户关系列表

        Raises:
            InternalOrganizationToUserModelException: 如果获取失败，抛出异常
        """
        with Session(application_sqlmodel_engine) as session:
            try:
                internal_organization_to_users=session.exec(select(InternalOrganizationToUser).where(InternalOrganizationToUser.internal_organization_id==internal_organization_id)).all()
                if not internal_organization_to_users:
                    return []
                return internal_organization_to_users
            except Exception as e:
                session.rollback()
                if DEBUG_MODE:
                    raise InternalOrganizationToUserModelException(code=500,message=f"内部组织与用户关系获取失败: {e}")
                else:
                    raise InternalOrganizationToUserModelException(code=500,message="内部组织与用户关系获取失败")
    @classmethod
    def get_internal_organization_to_user_by_user_id(cls,user_id:int)->List["InternalOrganizationToUser"]:
        """
        获取内部组织与用户关系。
        
        Args:
            user_id (int): 用户ID

        Returns:
            List[InternalOrganizationToUser]: 内部组织与用户关系列表

        Raises:
            InternalOrganizationToUserModelException: 如果获取失败，抛出异常
        """
        with Session(application_sqlmodel_engine) as session:
            try:
                internal_organization_to_users=session.exec(select(InternalOrganizationToUser).where(InternalOrganizationToUser.user_id==user_id)).all()
                if not internal_organization_to_users:
                    return []
                return internal_organization_to_users
            except Exception as e:
                session.rollback()
                if DEBUG_MODE:
                    raise InternalOrganizationToUserModelException(code=500,message=f"内部组织与用户关系获取失败: {e}")
                else:
                    raise InternalOrganizationToUserModelException(code=500,message="内部组织与用户关系获取失败")