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

application_sqlmodel_engine = create_engine(f"mysql+pymysql://{db_config['user']}:{db_config['password']}@{db_config['host']}/{db_config['database']}")

redis_pool = redis.ConnectionPool(
    host=redis_db_config["host"],
    port=redis_db_config["port"],
    db=redis_db_config["db"],
    password=redis_db_config["password"],
)

def get_redis_client():
    return redis.Redis(connection_pool=redis_pool)


