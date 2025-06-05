from datetime import datetime, timezone
from typing import Dict, List, Optional
from sqlmodel import Field, SQLModel, Session, select
from core.configs import DEBUG_MODE, application_sqlmodel_engine

class PurposeModelException(Exception):
    def __init__(self,code:int,message:str):
        self.code=code
        self.message=message
        super().__init__(self.message)

class MainAccountPurpose(SQLModel,table=True):
    __tablename__="main_account_purposes"
    id:Optional[int]=Field(default=None,primary_key=True)
    name:str=Field(...,description="用途名称")
    description:Optional[str]=Field(default='',description="用途描述")
    main_account_id:int=Field(...,foreign_key="main_accounts.id",description="主账户ID")
    enabled:bool=Field(default=True,description="是否启用")
    created_at:datetime=Field(default_factory=lambda:datetime.now(timezone.utc))

    @classmethod
    def get_purposes(cls,id:Optional[int]=None,main_account_id:Optional[int]=None,enabled:Optional[bool]=True)->List["MainAccountPurpose"]:
        with Session(application_sqlmodel_engine) as session:
            try:
                if id:
                    purpose=session.exec(select(MainAccountPurpose).where(MainAccountPurpose.id==id)).first()
                    if not purpose:
                        raise PurposeModelException(code=404,message="用途不存在")
                    return [purpose]
                elif main_account_id:
                    purposes=session.exec(select(MainAccountPurpose).where(MainAccountPurpose.main_account_id==main_account_id,MainAccountPurpose.enabled==enabled)).all()
                    return purposes
                else:
                    purposes=session.exec(select(MainAccountPurpose).where(MainAccountPurpose.enabled==enabled)).all()
                    return purposes
            except PurposeModelException as e:
                raise e
            except Exception as e:
                if DEBUG_MODE:
                    raise PurposeModelException(code=500,message=f"获取用途失败: {str(e)}")
                else:
                    raise PurposeModelException(code=500,message="获取用途失败")
    @classmethod
    def create(cls,name:str,main_account_id:int,description:Optional[str]=None,enabled:Optional[bool]=True)->Dict[str,str]:
        with Session(application_sqlmodel_engine) as session:
            try:
                purpose=MainAccountPurpose(name=name,main_account_id=main_account_id,description=description,enabled=enabled)
                session.add(purpose)
                session.commit()
                return {"code":200,"message":"用途创建成功"}
            except PurposeModelException as e:
                session.rollback()
                raise e
            except Exception as e:
                session.rollback()
                if DEBUG_MODE:
                    raise PurposeModelException(code=500,message=f"用途创建失败: {str(e)}")
                else:
                    raise PurposeModelException(code=500,message="用途创建失败")
    @classmethod
    def update(cls,id:int,name:Optional[str]=None,description:Optional[str]=None,enabled:Optional[bool]=None)->Dict[str,str]:
        with Session(application_sqlmodel_engine) as session:
            try:
                purpose=session.exec(select(MainAccountPurpose).where(MainAccountPurpose.id==id)).first()
                if not purpose:
                    raise PurposeModelException(code=404,message="用途不存在")
                if name:
                    purpose.name=name
                if description:
                    purpose.description=description
                if enabled:
                    purpose.enabled=enabled
                session.add(purpose)
                session.commit()
                return {"code":200,"message":"用途更新成功"}
            except PurposeModelException as e:
                session.rollback()
                raise e
            except Exception as e:
                session.rollback()
                if DEBUG_MODE:
                    raise PurposeModelException(code=500,message=f"用途更新失败: {str(e)}")
                else:
                    raise PurposeModelException(code=500,message="用途更新失败")
class ExternalAccountPurpose(SQLModel,table=True):
    __tablename__="external_account_purposes"
    id:Optional[int]=Field(default=None,primary_key=True)
    name:str=Field(...,description="用途名称")
    description:Optional[str]=Field(default='',description="用途描述")
    external_account_id:int=Field(...,foreign_key="external_accounts.id",description="外部账户ID")
    created_at:datetime=Field(default_factory=lambda:datetime.now(timezone.utc))
    @classmethod
    def get_purposes(cls,id:Optional[int]=None,external_account_id:Optional[int]=None)->List["ExternalAccountPurpose"]:
        with Session(application_sqlmodel_engine) as session:
            try:
                if id:
                    purpose=session.exec(select(ExternalAccountPurpose).where(ExternalAccountPurpose.id==id)).first()
                    if not purpose:
                        raise PurposeModelException(code=404,message="用途不存在")
                    return [purpose]
                elif external_account_id:
                    purposes=session.exec(select(ExternalAccountPurpose).where(ExternalAccountPurpose.external_account_id==external_account_id)).all()
                    return purposes
                else:
                    purposes=session.exec(select(ExternalAccountPurpose)).all()
                    return purposes
            except PurposeModelException as e:
                raise e
            except Exception as e:
                if DEBUG_MODE:
                    raise PurposeModelException(code=500,message=f"获取用途失败: {str(e)}")
                else:
                    raise PurposeModelException(code=500,message="获取用途失败")
    @classmethod
    def create(cls,name:str,external_account_id:int,description:Optional[str]=None)->Dict[str,str]:
        with Session(application_sqlmodel_engine) as session:
            try:
                purpose=ExternalAccountPurpose(name=name,external_account_id=external_account_id,description=description)
                session.add(purpose)
                session.commit()
                return {"code":200,"message":"用途创建成功"}
            except PurposeModelException as e:
                session.rollback()
                raise e
            except Exception as e:
                session.rollback()
                if DEBUG_MODE:
                    raise PurposeModelException(code=500,message=f"用途创建失败: {str(e)}")
                else:
                    raise PurposeModelException(code=500,message="用途创建失败")
    @classmethod
    def update(cls,id:int,name:Optional[str]=None,description:Optional[str]=None)->Dict[str,str]:
        with Session(application_sqlmodel_engine) as session:
            try:
                purpose=session.exec(select(ExternalAccountPurpose).where(ExternalAccountPurpose.id==id)).first()
                if not purpose:
                    raise PurposeModelException(code=404,message="用途不存在")
                if name:
                    purpose.name=name
                if description:
                    purpose.description=description
                session.add(purpose)
                session.commit()
                return {"code":200,"message":"用途更新成功"}
            except PurposeModelException as e:
                session.rollback()
                raise e
            except Exception as e:
                session.rollback()
                if DEBUG_MODE:
                    raise PurposeModelException(code=500,message=f"用途更新失败: {str(e)}")
                else:
                    raise PurposeModelException(code=500,message="用途更新失败")