from datetime import datetime, timezone
from typing import Optional, List, Dict
from sqlalchemy import JSON
from sqlmodel import SQLModel, Field, Session, select
from core.configs import DEBUG_MODE, application_sqlmodel_engine
from models.core.department import Department


class AccountModelException(Exception):
    """账户模型异常类。
    
    用于表示账户模型相关的异常情况。
    继承自Exception类，用于自定义异常处理。
    
    Attributes:
        code: 错误代码
        message: 错误消息
    """
    
    def __init__(self, code: int, message: str):
        """初始化账户模型异常。
        
        Args:
            code: 错误代码
            message: 错误消息
        """
        self.message = message
        self.code = code


class MainAccount(SQLModel, table=True):
    """主账户模型类。
    
    用于表示村社级主账户信息，包含账户基本信息和所属部门关联。
    主账户通常代表村社组织的官方账户。
    
    Attributes:
        id: 主键ID，自动生成
        name: 账户名称
        unified_social_credit_code: 统一社会信用代码
        deparment_id: 所属部门ID，外键关联departments表
        created_at: 创建时间，默认为当前UTC时间
    """
    
    __tablename__ = "main_accounts"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(..., description="账户名称")
    unified_social_credit_code: str = Field(..., description="统一社会信用代码")
    deparment_id: int = Field(..., foreign_key="departments.id", description="所属部门ID")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    @classmethod
    def create(cls, name: str, unified_social_credit_code: str, deparment_id: int) -> Dict[str, str]:
        """创建新的主账户。
        
        验证部门存在性和级别后创建主账户。只允许为村社级部门（level=3）创建主账户。
        
        Args:
            name: 账户名称
            unified_social_credit_code: 统一社会信用代码
            deparment_id: 所属部门ID
            
        Returns:
            Dict[str, str]: 包含操作结果的字典，格式为 {"code": "200", "message": "账户创建成功"}
            
        Raises:
            AccountModelException: 当部门不存在、部门级别错误或创建失败时抛出
        """
        with Session(application_sqlmodel_engine) as session:
            try:
                # 验证部门是否存在
                department = session.get(Department, deparment_id)
                if not department:
                    raise AccountModelException(code=403, message="部门不存在")
                elif department.level != 3:
                    raise AccountModelException(code=403, message="部门级别错误,只能创建村社级主账户")
                
                # 创建主账户
                main_account = MainAccount(
                    name=name,
                    unified_social_credit_code=unified_social_credit_code,
                    deparment_id=deparment_id
                )
                session.add(main_account)
                session.commit()
                return {"code": "200", "message": "账户创建成功"}
            except AccountModelException as e:
                raise e
            except Exception as e:
                session.rollback()
                if DEBUG_MODE:
                    raise AccountModelException(code=500, message=f"账户创建失败: {str(e)}")
                else:
                    raise AccountModelException(code=500, message="账户创建失败")
    
    @classmethod
    def get_accounts(cls, id: Optional[int] = None, deparment_id: Optional[int] = None) -> List["MainAccount"]:
        """获取主账户信息。
        
        根据账户ID或部门ID查询主账户信息。必须提供其中一个参数。
        
        Args:
            id: 账户ID，可选
            deparment_id: 部门ID，可选
            
        Returns:
            List[MainAccount]: 主账户列表
            
        Raises:
            AccountModelException: 当参数错误或查询失败时抛出
        """
        with Session(application_sqlmodel_engine) as session:
            try:
                if id:
                    # 根据ID查询单个账户
                    main_account = session.exec(select(MainAccount).where(MainAccount.id == id)).first()
                    return [main_account] if main_account else []
                elif deparment_id:
                    # 根据部门ID查询所有账户
                    main_accounts = session.exec(select(MainAccount).where(MainAccount.deparment_id == deparment_id)).all()
                    return list(main_accounts)
                else:
                    raise AccountModelException(code=400, message="参数错误,必须提供id或deparment_id")
            except AccountModelException as e:
                raise e
            except Exception as e:
                if DEBUG_MODE:
                    raise AccountModelException(code=500, message=f"账户获取失败: {str(e)}")
                else:
                    raise AccountModelException(code=500, message="账户获取失败")

    @classmethod
    def update(cls, id: int, name: Optional[str] = None, unified_social_credit_code: Optional[str] = None) -> Dict[str, str]:
        """更新主账户信息。
        
        根据账户ID更新账户的名称和/或统一社会信用代码。
        
        Args:
            id: 账户ID
            name: 新的账户名称，可选
            unified_social_credit_code: 新的统一社会信用代码，可选
            
        Returns:
            Dict[str, str]: 包含操作结果的字典，格式为 {"code": "200", "message": "账户更新成功"}
            
        Raises:
            AccountModelException: 当账户不存在或更新失败时抛出
        """
        with Session(application_sqlmodel_engine) as session:
            try:
                # 查找要更新的账户
                main_account = session.exec(select(MainAccount).where(MainAccount.id == id)).first()
                if not main_account:
                    raise AccountModelException(code=404, message="账户不存在")
                
                # 更新字段
                if name:
                    main_account.name = name
                if unified_social_credit_code:
                    main_account.unified_social_credit_code = unified_social_credit_code
                
                session.add(main_account)
                session.commit()
                return {"code": "200", "message": "账户更新成功"}
            except AccountModelException as e:
                raise e
            except Exception as e:
                session.rollback()
                if DEBUG_MODE:
                    raise AccountModelException(code=500, message=f"账户更新失败: {str(e)}")
                else:
                    raise AccountModelException(code=500, message="账户更新失败")


class ExternalAccount(SQLModel, table=True):
    """外部账户模型类。
    
    用于表示与村社组织有业务往来的外部账户信息。
    外部账户可以是个人或其他组织机构。
    
    Attributes:
        id: 主键ID，自动生成
        name: 账户名称
        unified_social_credit_code: 统一社会信用代码或身份证号码
        account_number: 账户号码
        deparment_id: 所属部门ID，外键关联departments表
        created_at: 创建时间，默认为当前UTC时间
    """
    
    __tablename__ = "external_accounts"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(..., description="账户名称")
    unified_social_credit_code: str = Field(..., description="统一社会信用代码或身份证号码")
    account_number: str = Field(..., description="账户号码")
    deparment_id: int = Field(..., foreign_key="departments.id", description="所属部门ID")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def create(cls, name: str, unified_social_credit_code: str, account_number: str, deparment_id: int) -> Dict[str, str]:
        """创建新的外部账户。
        
        验证部门存在性和级别后创建外部账户。只允许为村社级部门（level=3）创建外部账户。
        
        Args:
            name: 账户名称
            unified_social_credit_code: 统一社会信用代码或身份证号码
            account_number: 账户号码
            deparment_id: 所属部门ID
            
        Returns:
            Dict[str, str]: 包含操作结果的字典，格式为 {"code": "200", "message": "外部账户创建成功"}
            
        Raises:
            AccountModelException: 当部门不存在、部门级别错误或创建失败时抛出
        """
        with Session(application_sqlmodel_engine) as session:
            try:
                # 验证部门是否存在
                department = session.get(Department, deparment_id)
                if not department:
                    raise AccountModelException(code=403, message="部门不存在")
                elif department.level != 3:
                    raise AccountModelException(code=403, message="部门级别错误,只能创建村社级外部账户")
                
                # 创建外部账户
                external_account = ExternalAccount(
                    name=name,
                    unified_social_credit_code=unified_social_credit_code,
                    account_number=account_number,
                    deparment_id=deparment_id
                )
                session.add(external_account)
                session.commit()
                return {"code": "200", "message": "外部账户创建成功"}
            except AccountModelException as e:
                raise e
            except Exception as e:
                session.rollback()
                if DEBUG_MODE:
                    raise AccountModelException(code=500, message=f"外部账户创建失败: {str(e)}")
                else:
                    raise AccountModelException(code=500, message="外部账户创建失败")
    
    @classmethod
    def update(cls, id: int, name: Optional[str] = None, unified_social_credit_code: Optional[str] = None, account_number: Optional[str] = None) -> Dict[str, str]:
        """更新外部账户信息。
        
        根据账户ID更新外部账户的名称和/或统一社会信用代码。
        
        Args:
            id: 账户ID
            name: 新的账户名称，可选
            unified_social_credit_code: 新的统一社会信用代码或身份证号码，可选
            account_number: 新的账户号码，可选
        Returns:
            Dict[str, str]: 包含操作结果的字典，格式为 {"code": "200", "message": "外部账户更新成功"}
            
        Raises:
            AccountModelException: 当外部账户不存在或更新失败时抛出
        """
        with Session(application_sqlmodel_engine) as session:
            try:
                # 查找要更新的外部账户
                external_account = session.exec(select(ExternalAccount).where(ExternalAccount.id == id)).first()
                if not external_account:
                    raise AccountModelException(code=404, message="外部账户不存在")
                
                # 更新字段
                if name:
                    external_account.name = name
                if unified_social_credit_code:
                    external_account.unified_social_credit_code = unified_social_credit_code
                if account_number:
                    external_account.account_number = account_number
                session.add(external_account)
                session.commit()
                return {"code": "200", "message": "外部账户更新成功"}
            except AccountModelException as e:
                raise e
            except Exception as e:
                session.rollback()
                if DEBUG_MODE:
                    raise AccountModelException(code=500, message=f"外部账户更新失败: {str(e)}")
                else:
                    raise AccountModelException(code=500, message="外部账户更新失败")

    @classmethod
    def get_accounts(cls, id: Optional[int] = None, deparment_id: Optional[int] = None) -> List["ExternalAccount"]:
        """获取外部账户信息。
        
        根据账户ID或部门ID查询外部账户信息。必须提供其中一个参数。
        
        Args:
            id: 账户ID，可选
            deparment_id: 部门ID，可选
            
        Returns:
            List[ExternalAccount]: 外部账户列表
            
        Raises:
            AccountModelException: 当参数错误或查询失败时抛出
        """
        with Session(application_sqlmodel_engine) as session:
            try:
                if id:
                    # 根据ID查询单个外部账户
                    external_account = session.exec(select(ExternalAccount).where(ExternalAccount.id == id)).first()
                    return [external_account] if external_account else []
                elif deparment_id:
                    # 根据部门ID查询所有外部账户
                    external_accounts = session.exec(select(ExternalAccount).where(ExternalAccount.deparment_id == deparment_id)).all()
                    return list(external_accounts)
                else:
                    raise AccountModelException(code=400, message="参数错误,必须提供id或deparment_id")
            except AccountModelException as e: 
                raise e
            except Exception as e:
                if DEBUG_MODE:
                    raise AccountModelException(code=500, message=f"外部账户获取失败: {str(e)}")
                else:
                    raise AccountModelException(code=500, message="外部账户获取失败")