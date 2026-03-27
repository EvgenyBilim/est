from pydantic import BaseModel, PositiveInt
from pydantic_settings import BaseSettings


class SqlAlchemySettings(BaseModel):
    postgres_dsn: str

    pg_pool_size: PositiveInt = 10
    pool_pre_ping: bool = True
    pool_timeout: float = 5.0
    pool_use_lifo: bool = True

    pg_connection_timeout: int = 5


class Settings(BaseSettings, SqlAlchemySettings):
    port: PositiveInt = 8000

    class Config:
        env_file = "local.env"
