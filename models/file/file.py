from datetime import datetime, timezone
from typing import Optional, List, Dict
from sqlmodel import SQLModel, Field, Session, select, Column, LargeBinary
import hashlib
import mimetypes
from core.configs import DEBUG_MODE, application_sqlmodel_engine


class FileModelException(Exception):
    """文件模型异常类。
    
    用于表示文件模型相关的异常情况。
    继承自Exception类，用于自定义异常处理。
    
    Attributes:
        code: 错误代码
        message: 错误消息
    """
    
    def __init__(self, code: int, message: str):
        """初始化文件模型异常。
        
        Args:
            code: 错误代码
            message: 错误消息
        """
        self.message = message
        self.code = code


class File(SQLModel, table=True):
    """文件模型类。
    
    用于存储和管理50MB以下的小文件。
    这是一个简化的文件存储模型，只包含文件的核心信息。
    
    Attributes:
        id: 主键ID，自动生成
        file_size: 文件大小（字节）
        mime_type: 文件MIME类型
        file_hash: 文件SHA256哈希值，用于去重和完整性校验
        file_content: 文件二进制内容
    """
    
    __tablename__ = "files"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    file_size: int = Field(..., description="文件大小（字节）")
    mime_type: str = Field(..., description="文件MIME类型")
    file_hash: str = Field(..., index=True, unique=True, description="文件SHA256哈希值")
    file_content: bytes = Field(..., sa_column=Column(LargeBinary), description="文件二进制内容")
    
    @staticmethod
    def calculate_file_hash(file_content: bytes) -> str:
        """计算文件的SHA256哈希值。
        
        Args:
            file_content: 文件二进制内容
            
        Returns:
            str: 文件的SHA256哈希值（十六进制字符串）
        """
        return hashlib.sha256(file_content).hexdigest()
    
    @staticmethod
    def get_mime_type(filename: str) -> str:
        """根据文件名获取MIME类型。
        
        Args:
            filename: 文件名
            
        Returns:
            str: MIME类型，如果无法识别则返回'application/octet-stream'
        """
        mime_type, _ = mimetypes.guess_type(filename)
        return mime_type or 'application/octet-stream'
    
    @classmethod
    def store_file(cls, file_content: bytes, filename: Optional[str] = None) -> Dict[str, str]:
        """存储文件。
        
        Args:
            file_content: 文件二进制内容
            filename: 文件名（可选，用于确定MIME类型）
            
        Returns:
            Dict[str, str]: 包含文件ID和哈希值的字典
            
        Raises:
            FileModelException: 当文件大小超限或其他错误时抛出
        """
        # 检查文件大小限制（50MB = 50 * 1024 * 1024 bytes）
        max_file_size = 50 * 1024 * 1024
        if len(file_content) > max_file_size:
            raise FileModelException(code=413, message=f"文件大小超过限制，最大允许{max_file_size // (1024 * 1024)}MB")
        
        with Session(application_sqlmodel_engine) as session:
            try:
                # 计算文件哈希值
                file_hash = cls.calculate_file_hash(file_content)
                
                # 检查是否已存在相同哈希值的文件（去重）
                existing_file = session.exec(select(File).where(File.file_hash == file_hash)).first()
                if existing_file:
                    return {
                        "file_id": str(existing_file.id),
                        "file_hash": existing_file.file_hash,
                        "message": "文件已存在，返回现有文件ID"
                    }
                
                # 获取MIME类型
                mime_type = cls.get_mime_type(filename) if filename else 'application/octet-stream'
                
                # 创建文件记录
                file_record = cls(
                    file_size=len(file_content),
                    mime_type=mime_type,
                    file_hash=file_hash,
                    file_content=file_content
                )
                
                session.add(file_record)
                session.commit()
                session.refresh(file_record)
                
                return {
                    "file_id": str(file_record.id),
                    "file_hash": file_record.file_hash,
                    "message": "文件存储成功"
                }
                
            except FileModelException as e:
                session.rollback()
                raise e
            except Exception as e:
                session.rollback()
                if DEBUG_MODE:
                    raise FileModelException(code=500, message=f"文件存储失败: {str(e)}")
                else:
                    raise FileModelException(code=500, message="文件存储失败")
    
    @classmethod
    def get_file(cls, file_id: Optional[int] = None, file_hash: Optional[str] = None) -> Optional["File"]:
        """获取文件。
        
        Args:
            file_id: 文件ID，可选
            file_hash: 文件哈希值，可选
            
        Returns:
            File: 文件对象，如果不存在则返回None
            
        Raises:
            FileModelException: 当参数错误或查询失败时抛出
        """
        if not file_id and not file_hash:
            raise FileModelException(code=400, message="必须提供file_id或file_hash参数")
        
        with Session(application_sqlmodel_engine) as session:
            try:
                if file_id:
                    file_record = session.exec(select(File).where(File.id == file_id)).first()
                else:
                    file_record = session.exec(select(File).where(File.file_hash == file_hash)).first()
                
                return file_record
                
            except Exception as e:
                if DEBUG_MODE:
                    raise FileModelException(code=500, message=f"获取文件失败: {str(e)}")
                else:
                    raise FileModelException(code=500, message="获取文件失败")
    
    
    @classmethod
    def delete_file(cls, file_id: Optional[int] = None, file_hash: Optional[str] = None) -> Dict[str, str]:
        """删除文件。
        
        Args:
            file_id: 文件ID，可选
            file_hash: 文件哈希值，可选
            
        Returns:
            Dict[str, str]: 成功消息
            
        Raises:
            FileModelException: 当文件不存在或删除失败时抛出
        """
        if not file_id and not file_hash:
            raise FileModelException(code=400, message="必须提供file_id或file_hash参数")
        
        with Session(application_sqlmodel_engine) as session:
            try:
                if file_id:
                    file_record = session.exec(select(File).where(File.id == file_id)).first()
                else:
                    file_record = session.exec(select(File).where(File.file_hash == file_hash)).first()
                
                if not file_record:
                    raise FileModelException(code=404, message="文件不存在")
                
                session.delete(file_record)
                session.commit()
                
                return {"message": "文件删除成功"}
                
            except FileModelException as e:
                session.rollback()
                raise e
            except Exception as e:
                session.rollback()
                if DEBUG_MODE:
                    raise FileModelException(code=500, message=f"文件删除失败: {str(e)}")
                else:
                    raise FileModelException(code=500, message="文件删除失败")
    
    @classmethod
    def file_exists(cls, file_hash: str) -> bool:
        """检查文件是否存在。
        
        Args:
            file_hash: 文件哈希值
            
        Returns:
            bool: 文件是否存在
        """
        with Session(application_sqlmodel_engine) as session:
            try:
                file_record = session.exec(select(File).where(File.file_hash == file_hash)).first()
                return file_record is not None
            except Exception:
                return False
    