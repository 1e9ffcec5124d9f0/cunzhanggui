



from datetime import datetime, timezone
from typing import List, Optional,Dict
from sqlmodel import Field, SQLModel, Session, select
from core.configs import DEBUG_MODE, application_sqlmodel_engine

class DepartmentModelException(Exception):
    """部门模型异常类。
    
    用于表示部门模型相关的异常情况。
    继承自Exception类，用于自定义异常处理。"""
    def __init__(self,code:int,message:str):
        self.message=message
        self.code=code



class Department(SQLModel,table=True):
    __tablename__="departments"
    
    id:Optional[int]=Field(default=None,primary_key=True)
    name:str=Field(...,index=True)
    level:int=Field(...,description="部门级别: 0-根部门, 1-县级, 2-镇街级, 3-村社级")
    parent_id:int=Field(default=...,foreign_key="departments.id",description="父部门ID")
    description: Optional[str] = Field(default="", description="部门描述")
    manager_name: Optional[str] = Field(default="", description="部门负责人姓名")
    manager_phone: Optional[str] = Field(default="", description="部门负责人电话")
    created_at:datetime=Field(default_factory=lambda:datetime.now(timezone.utc))
    updated_at:datetime=Field(default_factory=lambda:datetime.now(timezone.utc))

    @classmethod
    def create(cls,name:str,level:int,parent_id:int,description:Optional[str]=None,manager_name:Optional[str]=None,manager_phone:Optional[str]=None)->Dict[str,str]:
        """
        创建部门。
        
        Args:
            name (str): 部门名称
            level (int): 部门级别
            parent_id (int): 父部门ID
            description (str,optional): 部门描述
            manager_name (str,optional): 部门负责人姓名
            manager_phone (str,optional): 部门负责人电话

        Returns:
            Dict: 创建成功返回{'success':"部门创建成功"}

        Raises:
            DepartmentModelException: 如果创建失败，抛出异常
        """ 
        with Session(application_sqlmodel_engine) as session:
            try:
                department=Department(name=name,level=level,parent_id=parent_id,description=description,manager_name=manager_name,manager_phone=manager_phone)
                session.add(department)
                session.commit()
                return {'success':"部门创建成功"}
            except Exception as e:
                session.rollback()
                if DEBUG_MODE:
                    raise DepartmentModelException(code=500,message=f"部门创建失败: {e}")
                else:
                    raise DepartmentModelException(code=500,message="部门创建失败")

    @classmethod
    def update(cls,department_id:int,name:Optional[str]=None,level:Optional[int]=None,parent_id:Optional[int]=None,description:Optional[str]=None,manager_name:Optional[str]=None,manager_phone:Optional[str]=None)->Dict[str,str]:
        """
        更新部门。
        
        Args:
            department_id (int): 部门ID
            name (str,optional): 部门名称
            level (int,optional): 部门级别
            parent_id (int,optional): 父部门ID
            description (str,optional): 部门描述
            manager_name (str,optional): 部门负责人姓名
            manager_phone (str,optional): 部门负责人电话

        Returns:
            Dict: 更新成功返回{'success':"部门更新成功"}

        Raises:
            DepartmentModelException: 如果更新失败，抛出异常
        """
        with Session(application_sqlmodel_engine) as session:
            try:
                department=session.exec(select(Department).where(Department.id==department_id)).first()
                if not department:
                    raise DepartmentModelException(code=404,message="部门不存在")
                if name:
                    department.name=name
                if level:
                    department.level=level
                if parent_id:
                    department.parent_id=parent_id
                if description:
                    department.description=description
                if manager_name:
                    department.manager_name=manager_name
                if manager_phone:
                    department.manager_phone=manager_phone
                session.commit()
                return {'success':"部门更新成功"}
            except Exception as e:
                session.rollback()
                if DEBUG_MODE:
                    raise DepartmentModelException(code=500,message=f"部门更新失败: {e}")
                else:
                    raise DepartmentModelException(code=500,message="部门更新失败")
    @classmethod
    def delete(cls,department_id:int)->Dict[str,str]:
        """
        删除部门。
        
        Args:
            department_id (int): 部门ID

        Returns:
            Dict: 删除成功返回{'success':"部门删除成功"}

        Raises:
            DepartmentModelException: 如果删除失败，抛出异常
        """ 
        with Session(application_sqlmodel_engine) as session:
            try:
                department=session.exec(select(Department).where(Department.id==department_id)).first()
                if not department:
                    raise DepartmentModelException(code=404,message="部门不存在")
                session.delete(department)
                session.commit()
                return {'success':"部门删除成功"}
            except Exception as e:
                session.rollback()
                if DEBUG_MODE:
                    raise DepartmentModelException(code=500,message=f"部门删除失败: {e}")
                else:
                    raise DepartmentModelException(code=500,message="部门删除失败")
    @classmethod
    def get_department(cls,department_id:int)->Dict[str,str]:
        """
        获取部门。
        
        Args:
            department_id (int): 部门ID

        Returns:
            Dict: 返回部门信息

        Raises:
            DepartmentModelException: 如果获取失败，抛出异常
        """
        with Session(application_sqlmodel_engine) as session:
            try:
                department=session.exec(select(Department).where(Department.id==department_id)).first()
                if not department:
                    raise DepartmentModelException(code=404,message="部门不存在")
                return {
                    "id":department.id,
                    "name":department.name,
                    "level":department.level,
                    "parent_id":department.parent_id,
                    "description":department.description,
                    "manager_name":department.manager_name,
                    "manager_phone":department.manager_phone,
                    "created_at":department.created_at,
                    "updated_at":department.updated_at
                }
            except Exception as e:
                if DEBUG_MODE:
                    raise DepartmentModelException(code=500,message=f"获取部门失败: {e}")
                else:
                    raise DepartmentModelException(code=500,message="获取部门失败")

    @classmethod
    def get_department_by_parent_id(cls,parent_id:int)->List[Dict[str,str]]:
        """
        根据父部门ID获取部门列表。
        
        Args:
            parent_id (int): 父部门ID

        Returns:
            List[Dict[str,str]]: 返回部门列表

        Raises:
            DepartmentModelException: 如果获取失败，抛出异常
        """
        with Session(application_sqlmodel_engine) as session:
            try:
                departments=session.exec(select(Department).where(Department.parent_id==parent_id)).all()
                result=[]
                for department in departments:
                    result.append({
                        "id":department.id,
                        "name":department.name,
                        "level":department.level,
                        "parent_id":department.parent_id,
                        "description":department.description,
                        "manager_name":department.manager_name,
                        "manager_phone":department.manager_phone,
                        "created_at":department.created_at,
                        "updated_at":department.updated_at
                    })
                return result
            except Exception as e:
                if DEBUG_MODE:
                    raise DepartmentModelException(code=500,message=f"获取部门失败: {e}")
                else:
                    raise DepartmentModelException(code=500,message="获取部门失败")

