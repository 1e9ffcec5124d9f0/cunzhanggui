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
    def create(cls,name:str,level:int,parent_id:int,description:Optional[str]=None,manager_name:Optional[str]=None,manager_phone:Optional[str]=None)->str:
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
            str: 创建成功返回"部门创建成功"

        Raises:
            DepartmentModelException: 如果创建失败，抛出异常
        """ 
        with Session(application_sqlmodel_engine) as session:
            try:
                department=Department(name=name,level=level,parent_id=parent_id,description=description,manager_name=manager_name,manager_phone=manager_phone)
                session.add(department)
                session.commit()
                return "部门创建成功"
            except Exception as e:
                session.rollback()
                if DEBUG_MODE:
                    raise DepartmentModelException(code=500,message=f"部门创建失败: {e}")
                else:
                    raise DepartmentModelException(code=500,message="部门创建失败")

    @classmethod
    def update(cls,department_id:int,name:Optional[str]=None,level:Optional[int]=None,parent_id:Optional[int]=None,description:Optional[str]=None,manager_name:Optional[str]=None,manager_phone:Optional[str]=None)->str:
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
            str: 更新成功返回"部门更新成功"

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
                return "部门更新成功"
            except Exception as e:
                session.rollback()
                if DEBUG_MODE:
                    raise DepartmentModelException(code=500,message=f"部门更新失败: {e}")
                else:
                    raise DepartmentModelException(code=500,message="部门更新失败")
    @classmethod
    def delete(cls,department_id:int)->str:
        """
        删除部门。
        
        Args:
            department_id (int): 部门ID

        Returns:
            str: 删除成功返回"部门删除成功"

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
                return "部门删除成功"
            except Exception as e:
                session.rollback()
                if DEBUG_MODE:
                    raise DepartmentModelException(code=500,message=f"部门删除失败: {e}")
                else:
                    raise DepartmentModelException(code=500,message="部门删除失败")
    @classmethod
    def get_department(cls,department_id:int)->"Department":
        """
        获取部门。
        
        Args:
            department_id (int): 部门ID

        Returns:
            Department: 返回部门对象

        Raises:
            DepartmentModelException: 如果获取失败，抛出异常
        """
        with Session(application_sqlmodel_engine) as session:
            try:
                department=session.exec(select(Department).where(Department.id==department_id)).first()
                if not department:
                    raise DepartmentModelException(code=404,message="部门不存在")
                return department
            except Exception as e:
                if DEBUG_MODE:
                    raise DepartmentModelException(code=500,message=f"获取部门失败: {e}")
                else:
                    raise DepartmentModelException(code=500,message="获取部门失败")

    @classmethod
    def get_departments_by_parent_id(cls,parent_id:int)->List["Department"]:
        """
        根据父部门ID获取部门列表。
        
        Args:
            parent_id (int): 父部门ID

        Returns:
            List[Department]: 返回部门对象列表

        Raises:
            DepartmentModelException: 如果获取失败，抛出异常
        """
        with Session(application_sqlmodel_engine) as session:
            try:
                departments=session.exec(select(Department).where(Department.parent_id==parent_id)).all()
                return departments
            except Exception as e:
                if DEBUG_MODE:
                    raise DepartmentModelException(code=500,message=f"获取部门失败: {e}")
                else:
                    raise DepartmentModelException(code=500,message="获取部门失败")
    @classmethod
    def get_department_tree_by_parent_id(cls, parent_id: int) -> List[Dict[str,str]]:
        """
        根据父部门ID构建完整的部门树。
        
        Args:
            parent_id (int): 父部门ID

        Returns:
            List[Dict[str:str]]: 返回包含子部门的树形结构列表

        Raises:
            DepartmentModelException: 如果获取失败，抛出异常
        """
        with Session(application_sqlmodel_engine) as session:
            try:
                # 递归构建部门树的内部函数
                def build_department_tree(dept_parent_id: int) -> List[Dict]:
                    """
                    递归构建部门树结构
                    
                    Args:
                        dept_parent_id (int): 当前层级的父部门ID
                        
                    Returns:
                        List[Dict[str:str]]: 当前层级的部门列表，包含子部门
                    """
                    departments = session.exec(
                        select(Department).where(Department.parent_id == dept_parent_id)
                    ).all()
                    
                    result = []
                    for department in departments:
                        dept_dict = {
                            "id": department.id,
                            "name": department.name,
                            "level": department.level,
                            "parent_id": department.parent_id,
                            "description": department.description,
                            "manager_name": department.manager_name,
                            "manager_phone": department.manager_phone,
                            "created_at": department.created_at,
                            "updated_at": department.updated_at,
                            "children": []  # 初始化子部门列表
                        }
                        
                        # 递归获取子部门
                        children = build_department_tree(department.id)
                        if children:
                            dept_dict["children"] = children
                            
                        result.append(dept_dict)
                    
                    return result
                
                # 开始构建树形结构
                return build_department_tree(parent_id)
                
            except Exception as e:
                if DEBUG_MODE:
                    raise DepartmentModelException(code=500, message=f"构建部门树失败: {e}")
                else:
                    raise DepartmentModelException(code=500, message="构建部门树失败")
    
    
    def check_is_direct_child(self, child_id: int) -> bool:
        """
        检查指定部门是否为当前部门的直接下级部门。
        
        Args:
            child_id (int): 子部门ID

        Returns:
            bool: 如果是直接下级部门返回True，否则返回False

        Raises:
            DepartmentModelException: 如果查询失败，抛出异常
        """
        with Session(application_sqlmodel_engine) as session:
            try:
                # 查询子部门
                child_department = session.exec(
                    select(Department).where(Department.id == child_id)
                ).first()
                
                if not child_department:
                    raise DepartmentModelException(code=404, message="子部门不存在")
                # 检查是否为直接下级关系
                return child_department.parent_id == self.id
                
            except Exception as e:
                if DEBUG_MODE:
                    raise DepartmentModelException(code=500, message=f"检查部门关系失败: {e}")
                else:
                    raise DepartmentModelException(code=500, message="检查部门关系失败")

    def check_is_child(self, child_id: int) -> bool:
        """
        检查指定部门是否为当前部门的子部门（包括直接和间接子部门）。
        
        Args:
            child_id (int): 子部门ID

        Returns:
            bool: 如果是子部门返回True，否则返回False

        Raises:
            DepartmentModelException: 如果查询失败，抛出异常
        """
        with Session(application_sqlmodel_engine) as session:
            try:
                # 查询子部门
                child_department = session.exec(
                    select(Department).where(Department.id == child_id)
                ).first()
                
                if not child_department:
                    raise DepartmentModelException(code=404, message="子部门不存在")
                
                # 如果子部门ID等于当前部门ID，返回False（自己不是自己的子部门）
                if child_id == self.id:
                    return False
                
                # 递归向上查找父部门，直到找到当前部门或到达根部门
                current_parent_id = child_department.parent_id
                
                while current_parent_id is not None:
                    # 如果找到当前部门，说明是子部门
                    if current_parent_id == self.id:
                        return True
                    
                    # 查找上一级父部门
                    parent_department = session.exec(
                        select(Department).where(Department.id == current_parent_id)
                    ).first()
                    
                    if not parent_department:
                        # 如果父部门不存在，说明数据有问题，返回False
                        return False
                    
                    # 继续向上查找
                    current_parent_id = parent_department.parent_id
                
                # 如果遍历完所有父部门都没有找到当前部门，返回False
                return False
                
            except Exception as e:
                if DEBUG_MODE:
                    raise DepartmentModelException(code=500, message=f"检查部门关系失败: {e}")
                else:
                    raise DepartmentModelException(code=500, message="检查部门关系失败")

