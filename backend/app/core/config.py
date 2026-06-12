"""
应用配置
职责：
- 从.env读取环境变量
- 提供数据库地址、模型Key、Redis/Postgres checkpoint地址等配置
- 提供单例settings供全局使用
"""

from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ---------- 基本信息 ----------
    PROJECT_NAME: str = "预约航班智能体"
    VERSION: str = "0.1.0"
    DEBUG: bool = False

    # ---------- CORS ----------
    CORS_ORIGINS: List[str] = ["*"]

    # ---------- 数据库（暂时使用sqlite，后续可切换为postgresql+asyncpg） ----------
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./data/travel/travel.sqlite",
        description="主数据库连接地址（用于repository层）",
    )
    DB_ECHO: bool = False
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    # ---------- LangGraph Checkpoint（暂时使用sqlite） ----------
    CHECKPOINT_BACKEND: str = Field(
        default="sqlite",
        description="checkpoint后端类型：memory / sqlite / redis / postgres",
    )
    CHECKPOINT_SQLITE_PATH: str = "./checkpoints.db"
    CHECKPOINT_REDIS_URL: str = "redis://localhost:6379/0"
    CHECKPOINT_POSTGRES_URL: str = (
        "postgresql://user:password@localhost:5432/flight_agent_checkpoint"
    )

    # ---------- LLM ----------
    LLM_PROVIDER: str = "anthropic"
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    LLM_MODEL_NAME: str = "claude-sonnet-4-6"
    LLM_TEMPERATURE: float = 0.0

    # ---------- 安全/鉴权 ----------
    SECRET_KEY: str = "change-me-in-env"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    # ---------- 日志 ----------
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """缓存配置实例，避免重复读取.env"""
    return Settings()


settings = get_settings()