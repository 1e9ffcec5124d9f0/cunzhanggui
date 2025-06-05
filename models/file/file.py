from datetime import datetime, timezone
from typing import Optional, List, Dict, BinaryIO
from sqlmodel import SQLModel, Field, Session, select
from minio import Minio
from minio.error import S3Error
import uuid
import os
from pathlib import Path

from core.configs import DEBUG_MODE, application_sqlmodel_engine, minio_config


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
    
    用于表示系统中的文件信息，包含文件的基本信息和MinIO存储路径。
    支持文件的上传、下载、删除等操作。
    
    Attributes:
        id: 主键ID，自动生成
        file_name: 存储文件名（hash+扩展名）
        file_path: MinIO中的文件路径
        file_size: 文件大小（字节）
        mime_type: 文件MIME类型
        file_hash: 文件哈希值（用于去重）
        bucket_name: MinIO存储桶名称
        uploader_id: 上传者用户ID
        department_id: 所属部门ID
        created_at: 创建时间，默认为当前UTC时间
    """
    
    __tablename__ = "files"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    file_name: str = Field(..., description="存储文件名")
    file_path: str = Field(..., description="MinIO中的文件路径")
    file_size: int = Field(..., description="文件大小（字节）")
    mime_type: str = Field(..., description="文件MIME类型")
    file_hash: str = Field(..., index=True, description="文件哈希值")
    bucket_name: str = Field(..., description="MinIO存储桶名称")
    uploader_id: int = Field(..., foreign_key="users.id", description="上传者用户ID")
    department_id: int = Field(..., foreign_key="departments.id", description="所属部门ID")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @staticmethod
    def _get_minio_client() -> Minio:
        """获取MinIO客户端实例。
        
        Returns:
            Minio: MinIO客户端实例
            
        Raises:
            FileModelException: 当MinIO连接失败时
        """
        try:
            client = Minio(
                endpoint=minio_config["endpoint"],
                access_key=minio_config["access_key"],
                secret_key=minio_config["secret_key"],
                secure=minio_config["secure"]
            )
            return client
        except Exception as e:
            if DEBUG_MODE:
                raise FileModelException(code=500, message=f"MinIO连接失败: {e}")
            else:
                raise FileModelException(code=500, message="MinIO连接失败")

    @staticmethod
    def _ensure_bucket_exists(client: Minio, bucket_name: str) -> None:
        """确保存储桶存在，如果不存在则创建。
        
        Args:
            client: MinIO客户端实例
            bucket_name: 存储桶名称
            
        Raises:
            FileModelException: 当存储桶创建失败时
        """
        try:
            if not client.bucket_exists(bucket_name):
                client.make_bucket(bucket_name)
        except S3Error as e:
            if DEBUG_MODE:
                raise FileModelException(code=500, message=f"存储桶创建失败: {e}")
            else:
                raise FileModelException(code=500, message="存储桶创建失败")

    @staticmethod
    def _calculate_file_hash(file_data: bytes) -> str:
        """计算文件哈希值。
        
        Args:
            file_data: 文件二进制数据
            
        Returns:
            str: 文件的SHA256哈希值
        """
        import hashlib
        return hashlib.sha256(file_data).hexdigest()

    @staticmethod
    def _get_mime_type(file_name: str) -> str:
        """根据文件名获取MIME类型。
        
        Args:
            file_name: 文件名
            
        Returns:
            str: MIME类型
        """
        import mimetypes
        mime_type, _ = mimetypes.guess_type(file_name)
        return mime_type or "application/octet-stream"

    @classmethod
    def upload_file(
        cls,
        file_data: bytes,
        original_name: str,
        uploader_id: int,
        department_id: int,
        bucket_name: Optional[str] = None
    ) -> "File":
        """上传文件到MinIO并创建文件记录。
        
        Args:
            file_data: 文件二进制数据
            original_name: 原始文件名
            uploader_id: 上传者用户ID
            department_id: 所属部门ID
            bucket_name: MinIO存储桶名称，如果不提供则使用默认的部门桶名
            
        Returns:
            File: 创建的文件对象
            
        Raises:
            FileModelException: 当上传失败时
        """
        # 如果没有指定bucket_name，使用默认的部门桶名
        if bucket_name is None:
            bucket_name = f"department-{department_id}"
            
        try:
            # 计算文件哈希值
            file_hash = cls._calculate_file_hash(file_data)
            
            # 检查是否已存在相同哈希和桶的文件
            with Session(application_sqlmodel_engine) as session:
                existing_file = session.exec(
                    select(File).where(
                        File.file_hash == file_hash,
                        File.bucket_name == bucket_name
                    )
                ).first()
                
                if existing_file:
                    # 如果文件已存在，返回现有文件记录（可选择是否创建新记录）
                    return existing_file
            
            # 生成文件名：hash + 扩展名
            file_extension = Path(original_name).suffix
            file_name = f"{file_hash}{file_extension}"
            file_path = f"{datetime.now().strftime('%Y/%m/%d')}/{file_name}"
            
            # 获取MinIO客户端
            client = cls._get_minio_client()
            cls._ensure_bucket_exists(client, bucket_name)
            
            # 上传文件到MinIO
            from io import BytesIO
            file_stream = BytesIO(file_data)
            client.put_object(
                bucket_name=bucket_name,
                object_name=file_path,
                data=file_stream,
                length=len(file_data),
                content_type=cls._get_mime_type(original_name)
            )
            
            # 创建文件记录
            file_record = cls(
                file_name=file_name,
                file_path=file_path,
                file_size=len(file_data),
                mime_type=cls._get_mime_type(original_name),
                file_hash=file_hash,
                bucket_name=bucket_name,
                uploader_id=uploader_id,
                department_id=department_id
            )
            
            with Session(application_sqlmodel_engine) as session:
                session.add(file_record)
                session.commit()
                session.refresh(file_record)
                
            return file_record
            
        except Exception as e:
            if DEBUG_MODE:
                raise FileModelException(code=500, message=f"文件上传失败: {e}")
            else:
                raise FileModelException(code=500, message="文件上传失败")

    def download_file(self) -> bytes:
        """从MinIO下载文件数据。
        
        Returns:
            bytes: 文件二进制数据
            
        Raises:
            FileModelException: 当下载失败时
        """
        try:
            client = self._get_minio_client()
            response = client.get_object(self.bucket_name, self.file_path)
            file_data = response.read()
            response.close()
            response.release_conn()
            return file_data
        except S3Error as e:
            if DEBUG_MODE:
                raise FileModelException(code=404, message=f"文件下载失败: {e}")
            else:
                raise FileModelException(code=404, message="文件不存在或下载失败")
        except Exception as e:
            if DEBUG_MODE:
                raise FileModelException(code=500, message=f"文件下载失败: {e}")
            else:
                raise FileModelException(code=500, message="文件下载失败")

    def get_download_url(self, expires_in_seconds: int = 3600) -> str:
        """获取文件的预签名下载URL。
        
        Args:
            expires_in_seconds: URL过期时间（秒），默认1小时
            
        Returns:
            str: 预签名下载URL
            
        Raises:
            FileModelException: 当获取URL失败时
        """
        try:
            client = self._get_minio_client()
            from datetime import timedelta
            url = client.presigned_get_object(
                bucket_name=self.bucket_name,
                object_name=self.file_path,
                expires=timedelta(seconds=expires_in_seconds)
            )
            return url
        except Exception as e:
            if DEBUG_MODE:
                raise FileModelException(code=500, message=f"获取下载URL失败: {e}")
            else:
                raise FileModelException(code=500, message="获取下载URL失败")

    def delete_file(self) -> str:
        """删除文件（从MinIO和数据库中删除）。
        
        Returns:
            str: 删除成功消息
            
        Raises:
            FileModelException: 当删除失败时
        """
        try:
            # 从MinIO删除文件
            client = self._get_minio_client()
            client.remove_object(self.bucket_name, self.file_path)
            
            # 从数据库删除记录
            with Session(application_sqlmodel_engine) as session:
                session.delete(self)
                session.commit()
                
            return "文件删除成功"
            
        except S3Error as e:
            if DEBUG_MODE:
                raise FileModelException(code=500, message=f"MinIO文件删除失败: {e}")
            else:
                raise FileModelException(code=500, message="文件删除失败")
        except Exception as e:
            if DEBUG_MODE:
                raise FileModelException(code=500, message=f"文件删除失败: {e}")
            else:
                raise FileModelException(code=500, message="文件删除失败")

    @classmethod
    def get_file_by_id(cls, file_id: int) -> "File":
        """根据文件ID获取文件记录。
        
        Args:
            file_id: 文件ID
            
        Returns:
            File: 文件对象
            
        Raises:
            FileModelException: 当文件不存在时
        """
        with Session(application_sqlmodel_engine) as session:
            try:
                file_record = session.exec(select(File).where(File.id == file_id)).first()
                if not file_record:
                    raise FileModelException(code=404, message="文件不存在")
                return file_record
            except Exception as e:
                if DEBUG_MODE:
                    raise FileModelException(code=500, message=f"获取文件失败: {e}")
                else:
                    raise FileModelException(code=500, message="获取文件失败")

    @classmethod
    def get_files_by_uploader(cls, uploader_id: int, limit: int = 50, offset: int = 0) -> List["File"]:
        """根据上传者ID获取文件列表。
        
        Args:
            uploader_id: 上传者用户ID
            limit: 返回记录数限制，默认50
            offset: 偏移量，默认0
            
        Returns:
            List[File]: 文件对象列表
        """
        with Session(application_sqlmodel_engine) as session:
            try:
                files = session.exec(
                    select(File)
                    .where(File.uploader_id == uploader_id)
                    .order_by(File.created_at.desc())
                    .limit(limit)
                    .offset(offset)
                ).all()
                return list(files)
            except Exception as e:
                if DEBUG_MODE:
                    raise FileModelException(code=500, message=f"获取文件列表失败: {e}")
                else:
                    raise FileModelException(code=500, message="获取文件列表失败")

    @classmethod
    def get_files_by_department(cls, department_id: int, limit: int = 50, offset: int = 0) -> List["File"]:
        """根据部门ID获取文件列表。
        
        Args:
            department_id: 部门ID
            limit: 返回记录数限制，默认50
            offset: 偏移量，默认0
            
        Returns:
            List[File]: 文件对象列表
        """
        with Session(application_sqlmodel_engine) as session:
            try:
                files = session.exec(
                    select(File)
                    .where(File.department_id == department_id)
                    .order_by(File.created_at.desc())
                    .limit(limit)
                    .offset(offset)
                ).all()
                return list(files)
            except Exception as e:
                if DEBUG_MODE:
                    raise FileModelException(code=500, message=f"获取文件列表失败: {e}")
                else:
                    raise FileModelException(code=500, message="获取文件列表失败")

    @classmethod
    def search_files(
        cls,
        keyword: str,
        department_id: Optional[int] = None,
        uploader_id: Optional[int] = None,
        mime_type: Optional[str] = None,
        bucket_name: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List["File"]:
        """搜索文件。
        
        Args:
            keyword: 搜索关键词（在文件名中搜索）
            department_id: 部门ID过滤，可选
            uploader_id: 上传者ID过滤，可选
            mime_type: MIME类型过滤，可选
            bucket_name: 存储桶名称过滤，可选
            limit: 返回记录数限制，默认50
            offset: 偏移量，默认0
            
        Returns:
            List[File]: 文件对象列表
        """
        with Session(application_sqlmodel_engine) as session:
            try:
                query = select(File).where(File.file_name.contains(keyword))
                
                if department_id is not None:
                    query = query.where(File.department_id == department_id)
                    
                if uploader_id is not None:
                    query = query.where(File.uploader_id == uploader_id)
                    
                if mime_type is not None:
                    query = query.where(File.mime_type.contains(mime_type))
                    
                if bucket_name is not None:
                    query = query.where(File.bucket_name == bucket_name)
                
                files = session.exec(
                    query.order_by(File.created_at.desc())
                    .limit(limit)
                    .offset(offset)
                ).all()
                
                return list(files)
            except Exception as e:
                if DEBUG_MODE:
                    raise FileModelException(code=500, message=f"搜索文件失败: {e}")
                else:
                    raise FileModelException(code=500, message="搜索文件失败")

    @classmethod
    def get_files_by_bucket(cls, bucket_name: str, limit: int = 50, offset: int = 0) -> List["File"]:
        """根据存储桶名称获取文件列表。
        
        Args:
            bucket_name: 存储桶名称
            limit: 返回记录数限制，默认50
            offset: 偏移量，默认0
            
        Returns:
            List[File]: 文件对象列表
        """
        with Session(application_sqlmodel_engine) as session:
            try:
                files = session.exec(
                    select(File)
                    .where(File.bucket_name == bucket_name)
                    .order_by(File.created_at.desc())
                    .limit(limit)
                    .offset(offset)
                ).all()
                return list(files)
            except Exception as e:
                if DEBUG_MODE:
                    raise FileModelException(code=500, message=f"获取文件列表失败: {e}")
                else:
                    raise FileModelException(code=500, message="获取文件列表失败")
