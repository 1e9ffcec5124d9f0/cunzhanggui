from sqlmodel import SQLModel, Field, Column, JSON, Session, select
from typing import Dict, Optional, List
from datetime import datetime, timezone
from core.configs import DEBUG_MODE
from core.crypto.sm3_hash import sm3_hexhash
from core.configs import application_sqlmodel_engine
from sqlalchemy.exc import IntegrityError
from models.core.department import Department
from models.core.role import Role
class UserModelException(Exception):
    """用户模型异常类。
    
    用于表示用户模型相关的异常情况。
    继承自Exception类，用于自定义异常处理。"""
    def __init__(self, code: int,message: str):
        self.message=message
        self.code=code
    


class User(SQLModel, table=True):
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    password_hash: str = Field(..., description="密码")
    id_card_number: str = Field(...,description="身份证号码")
    phone_number: str = Field(...,description="手机号码")
    real_name: str = Field(..., description="真实姓名")
    department_id: int = Field(..., foreign_key="departments.id", description="所属部门ID")
    login_attempts: int = Field(default=0, description="登录尝试次数")
    role_ids: List[int] = Field(default=[], sa_type=JSON, description="角色ID列表")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    def get_roles(self)->List[Role]:
        """获取用户角色列表。
        
        Returns:
            List[Role]: 用户角色列表
        """
        with Session(application_sqlmodel_engine) as session:
            try:
                roles=session.exec(select(Role).where(Role.id.in_(self.role_ids))).all()
                return roles
            except Exception as e:
                if DEBUG_MODE:
                    raise UserModelException(code=500,message=f"获取角色失败: {e}")
                else:
                    raise UserModelException(code=500,message="获取角色失败")
    def get_department(self)->Department:
        """获取用户所属部门。
        
        Returns:
            Department: 用户所属部门
        """
        with Session(application_sqlmodel_engine) as session:
            try:
                department=session.exec(select(Department).where(Department.id==self.department_id)).first()
                return department
            except Exception as e:
                if DEBUG_MODE:
                    raise UserModelException(code=500,message=f"获取部门失败: {e}")
                else:
                    raise UserModelException(code=500,message="获取部门失败")
    @staticmethod
    def hash_password(password: str) -> str:
        """将明文密码进行哈希处理。
        
        使用SM3哈希算法对密码进行加密处理，添加固定的盐值以增强安全性。
        该方法为静态方法，可以直接通过类调用，无需实例化。
        
        Args:
            password (str): 需要进行哈希处理的明文密码
            
        Returns:
            str: 经过SM3哈希处理后的密码字符串（十六进制格式）
            
        Example:
            >>> User.hash_password("mypassword123")
            "a1b2c3d4e5f6..."
            
        Note:
            - 使用了固定的盐值"舒一君"和"1e9ffcec"来增强密码安全性
            - 返回的哈希值为十六进制字符串格式
            - 相同的输入密码总是产生相同的哈希值
        """
        try:
            return sm3_hexhash(f"舒一君{password}1e9ffcec".encode('utf-8'))
        except Exception as e:
            if DEBUG_MODE:
                raise UserModelException(code=500,message=f"密码哈希处理失败: {e}")
            else:
                raise UserModelException(code=500,message="密码哈希处理失败")
    @classmethod
    def create(cls,username:str,password:str,id_card_number:str,phone_number:str,real_name:str,department_id:int)->str:
        """创建用户。
        
        该方法用于创建新的用户记录。
        
        Args:
            username (str): 用户名
            password (str): 密码
            id_card_number (str): 身份证号码
            phone_number (str): 手机号码
            real_name (str): 真实姓名
            department_id (int): 所属部门ID

        Returns:
            str: 创建成功返回"用户创建成功"
            
        Raises:
            UserModelException: 如果创建失败，抛出异常
        """
        with Session(application_sqlmodel_engine) as session:
            try:
                department=session.exec(select(Department).where(Department.id==department_id)).first()
                if not department:
                    raise UserModelException(code=404,message="指定的部门不存在")
                
                user=cls(
                    username=username,
                    password_hash=cls.hash_password(password),
                    id_card_number=id_card_number,
                    phone_number=phone_number,
                    real_name=real_name,
                    department_id=department_id
                )
                session.add(user)
                session.commit()
                return "用户创建成功"
            except IntegrityError as e:
                session.rollback()
                error_message=str(e)
                if "username" in error_message:
                    raise UserModelException(code=400,message="用户名已存在")
            except Exception as e:
                session.rollback()
                if DEBUG_MODE:
                    raise UserModelException(code=500,message=f"用户创建失败: {e}")
                else:
                    raise UserModelException(code=500,message="用户创建失败")
    @classmethod
    def update(cls,user_id:int,username:str = None,id_card_number:str = None,phone_number:str = None,real_name:str = None,department_id:int = None,role_ids:List[int] = None)->str:
        """更新用户信息。
        
        该方法用于更新用户信息。
        
        Args:
            user_id (int): 用户ID
            username (str,optional): 用户名
            id_card_number (str,optional): 身份证号码
            phone_number (str,optional): 手机号码
            real_name (str,optional): 真实姓名
            department_id (int,optional): 所属部门ID
            role_ids (List[int],optional): 角色ID列表
        
        Returns:
            str: 更新成功返回"用户更新成功"
            
        Raises:
            UserModelException: 如果更新失败，抛出异常
        """
        with Session(application_sqlmodel_engine) as session:
            try:
                user=session.exec(select(User).where(User.id==user_id)).first()
                if not user:
                    raise UserModelException(code=404,message="指定的用户不存在")
                
                if username:
                    user.username=username
                if id_card_number:
                    user.id_card_number=id_card_number
                if phone_number:
                    user.phone_number=phone_number
                if real_name:
                    user.real_name=real_name
                if department_id:
                    department=session.exec(select(Department).where(Department.id==department_id)).first()
                    if not department:
                        raise UserModelException(code=404,message="指定的部门不存在")
                    user.department_id=department_id
                if role_ids:
                    user.role_ids=role_ids
                user.updated_at=datetime.now(timezone.utc)
                session.add(user)
                session.commit()
                return "用户更新成功"
            except IntegrityError as e:
                session.rollback()
                error_message=str(e)
                if "username" in error_message:
                    raise UserModelException(code=400,message="用户名已存在")
            except Exception as e:
                session.rollback()
                if DEBUG_MODE:
                    raise UserModelException(code=500,message=f"用户更新失败: {e}")
                else:
                    raise UserModelException(code=500,message="用户更新失败")
    @classmethod
    def delete(cls,user_id:int)->str:
        """删除用户。
        
        该方法用于删除用户。
        
        Args:
            user_id (int): 用户ID
        
        Returns:
            str: 删除成功返回"用户删除成功"
            
        Raises:
            UserModelException: 如果删除失败，抛出异常
        """
        with Session(application_sqlmodel_engine) as session:
            try:
                user=session.exec(select(User).where(User.id==user_id)).first()
                if not user:
                    raise UserModelException(code=404,message="指定的用户不存在")
                session.delete(user)
                session.commit()
                return "用户删除成功"
            except Exception as e:
                session.rollback()
                if DEBUG_MODE:
                    raise UserModelException(code=500,message=f"用户删除失败: {e}")
                else:
                    raise UserModelException(code=500,message="用户删除失败")
    @classmethod
    def get_users_by_department_id(cls,department_id:int)->List["User"]:
        """根据部门ID获取用户信息。
        
        Args:
            department_id (int): 部门ID
        
        Returns:
            List[User]: 返回用户对象列表
            
        Raises:
            UserModelException: 如果获取失败，抛出异常
        """
        with Session(application_sqlmodel_engine) as session:
            try:
                users=session.exec(select(User).where(User.department_id==department_id)).all()
                return users
            except Exception as e:
                if DEBUG_MODE:
                    raise UserModelException(code=500,message=f"获取用户失败: {e}")
                else:
                    raise UserModelException(code=500,message="获取用户失败")
    @classmethod
    def get_user(cls,user_id:Optional[int] = None,username:Optional[str] = None)->"User":
        """根据用户ID获取用户信息。
        
        Args:
            user_id (int,optional): 用户ID
            username (str,optional): 用户名

        Returns:
            User: 返回用户对象
            
        Raises:
            UserModelException: 如果获取失败，抛出异常
        """
        with Session(application_sqlmodel_engine) as session:
            try:
                if user_id:
                    user=session.exec(select(User).where(User.id==user_id)).first()
                elif username:
                    user=session.exec(select(User).where(User.username==username)).first()
                else:
                    raise UserModelException(code=400,message="用户ID或用户名不能同时为空")
                if not user:
                    raise UserModelException(code=404,message="指定的用户不存在")
                return user
            except Exception as e:
                if DEBUG_MODE:
                    raise UserModelException(code=500,message=f"获取用户失败: {e}")
                else:
                    raise UserModelException(code=500,message="获取用户失败")
    @classmethod
    def verify_password(cls,username:str,password:str)->bool:
        """验证用户密码。
        
        该方法用于验证用户密码。
        
        Args:
            username (str): 用户名
            password (str): 密码
        
        Returns:
            bool: 验证成功返回True,验证失败返回False
        
        Raises:
            UserModelException: 如果验证失败，抛出异常
        """
        with Session(application_sqlmodel_engine) as session:
            try:
                user=session.exec(select(User).where(User.username==username)).first()
                if not user:
                    return False
                if user.password_hash==cls.hash_password(password):
                    return True
                else:
                    return False
            except Exception as e:
                if DEBUG_MODE:
                    raise UserModelException(code=500,message=f"密码验证失败: {e}")
    @classmethod
    def change_password(cls,user_id:int,new_password:str)->str:
        """修改用户密码。
        
        该方法用于修改用户密码。
        
        Args:
            user_id (int): 用户ID
            new_password (str): 新密码
        
        Returns:
            str: 修改成功返回"密码修改成功"
            
        Raises:
            UserModelException: 如果修改失败，抛出异常
        """
        with Session(application_sqlmodel_engine) as session:
            try:
                user=session.exec(select(User).where(User.id==user_id)).first()
                if not user:
                    raise UserModelException(code=404,message="指定的用户不存在")
                user.password_hash=cls.hash_password(new_password)
                session.add(user)
                session.commit()
                return "密码修改成功"
            except Exception as e:
                session.rollback()
                if DEBUG_MODE:
                    raise UserModelException(code=500,message=f"密码修改失败: {e}")
                else:
                    raise UserModelException(code=500,message="密码修改失败")
