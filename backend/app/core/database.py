"""
数据库连接管理
职责：
- 创建异步数据库引擎与Session工厂
- 提供init_db/close_db供main.py生命周期管理调用
- 提供get_db依赖供repository层使用（仅repository可持有Session）
"""

from pathlib import Path

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings
from app.core.base_model import Base


def _is_sqlite(url: str) -> bool:
    return url.startswith("sqlite")


def _ensure_sqlite_dir(url: str) -> None:
    """sqlite不会自动创建目录，需提前创建数据库文件所在目录"""
    if not _is_sqlite(url):
        return

    # 形如 sqlite+aiosqlite:///./data/travel/travel.sqlite
    # 取出 ./data/travel/travel.sqlite 部分
    path_part = url.split("///", 1)[-1]
    if path_part in (":memory:", ""):
        return

    db_path = Path(path_part)
    db_path.parent.mkdir(parents=True, exist_ok=True)


_ensure_sqlite_dir(settings.DATABASE_URL)


# ---------- 引擎创建 ----------
_engine_kwargs = {"echo": settings.DB_ECHO, "future": True}

if not _is_sqlite(settings.DATABASE_URL):
    # sqlite不支持pool_size/max_overflow等参数
    _engine_kwargs.update(
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
    )

engine = create_async_engine(settings.DATABASE_URL, **_engine_kwargs)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


# ---------- 生命周期钩子 ----------
async def init_db() -> None:
    """
    应用启动时调用：
    - 建表（开发环境用create_all；生产环境建议用alembic迁移代替）
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """应用关闭时调用：释放连接池"""
    await engine.dispose()


# ---------- 依赖注入 ----------
async def get_db():
    """
    提供DB Session的依赖，仅供repository层使用。
    service层不应直接注入该依赖，避免绕过repository。
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()