import os


from sqlmodel import create_engine
import redis

DEBUG_MODE=os.getenv("DEBUG_MODE")
JWT_SECRET_KEY=os.getenv("JWT_SECRET_KEY")
db_config={
    "user": os.getenv("DB_USER"),
    "password":os.getenv("DB_PASSWORD"),
    "host":os.getenv("DB_HOST"),
    "database":os.getenv("DB_DATABASE"),
}

redis_db_config={
    "host":os.getenv("REDIS_HOST"),
    "port":os.getenv("REDIS_PORT"),
    "db":os.getenv("REDIS_DB"),
    "password":os.getenv("REDIS_PASSWORD"),
}

application_sqlmodel_engine = create_engine(
    f"mysql+pymysql://{db_config['user']}:{db_config['password']}@{db_config['host']}/{db_config['database']}",
    pool_size=10,  # 连接池大小
    max_overflow=20,  # 最大溢出连接数
    pool_timeout=30,  # 获取连接的超时时间
    pool_recycle=3600,  # 连接回收时间（1小时）
    pool_pre_ping=True,  # 连接前检查连接是否有效
    echo=False  # 是否打印SQL语句
)

redis_pool = redis.ConnectionPool(
    host=redis_db_config["host"],
    port=redis_db_config["port"],
    db=redis_db_config["db"],
    password=redis_db_config["password"],
)

def get_redis_client():
    return redis.Redis(connection_pool=redis_pool)


