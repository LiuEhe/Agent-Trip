"""
LangGraph Checkpoint 配置
职责：
- 根据CHECKPOINT_BACKEND初始化对应的checkpointer（memory/sqlite/redis/postgres）
- 供main.py在生命周期启动时调用，并传入agent/graph.py构建图时使用
- 仅负责LangGraph运行状态持久化，不涉及业务数据
  （用户↔thread映射等业务数据走 models/session.py + repository/session_repo.py）
"""

import logging
from pathlib import Path
from typing import Any

from app.core.config import settings

logger = logging.getLogger("app.memory.checkpoint")


async def init_checkpointer() -> Any:
    """
    应用启动时调用：根据配置初始化checkpointer。

    支持：
    - memory:   使用LangGraph内置MemorySaver，进程重启后状态丢失（适合开发/测试）
    - sqlite:   使用AsyncSqliteSaver，本地文件持久化
    - redis:    使用Redis持久化（需自行安装对应checkpoint包）
    - postgres: 使用Postgres持久化（需自行安装对应checkpoint包）
    """
    backend = settings.CHECKPOINT_BACKEND.lower()

    if backend == "memory":
        from langgraph.checkpoint.memory import MemorySaver

        logger.info("Checkpoint backend: memory (进程重启后状态丢失)")
        return MemorySaver()

    if backend == "sqlite":
        from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

        db_path = Path(settings.CHECKPOINT_SQLITE_PATH)
        db_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info("Checkpoint backend: sqlite (%s)", db_path)
        # AsyncSqliteSaver.from_conn_string 返回的是一个异步上下文管理器
        cm = AsyncSqliteSaver.from_conn_string(str(db_path))
        saver = await cm.__aenter__()
        # 把上下文管理器挂在saver上，关闭时需要用到
        saver._cm = cm
        return saver

    if backend == "redis":
        try:
            from langgraph.checkpoint.redis.aio import AsyncRedisSaver
        except ImportError as e:
            raise RuntimeError(
                "使用redis checkpoint需先安装：pip install langgraph-checkpoint-redis"
            ) from e

        logger.info("Checkpoint backend: redis (%s)", settings.CHECKPOINT_REDIS_URL)
        cm = AsyncRedisSaver.from_conn_string(settings.CHECKPOINT_REDIS_URL)
        saver = await cm.__aenter__()
        saver._cm = cm
        return saver

    if backend == "postgres":
        try:
            from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
        except ImportError as e:
            raise RuntimeError(
                "使用postgres checkpoint需先安装：pip install langgraph-checkpoint-postgres"
            ) from e

        logger.info("Checkpoint backend: postgres")
        cm = AsyncPostgresSaver.from_conn_string(settings.CHECKPOINT_POSTGRES_URL)
        saver = await cm.__aenter__()
        saver._cm = cm
        if hasattr(saver, "setup"):
            await saver.setup()
        return saver

    raise ValueError(f"不支持的CHECKPOINT_BACKEND: {settings.CHECKPOINT_BACKEND}")


async def close_checkpointer(checkpointer: Any) -> None:
    """应用关闭时调用：释放checkpointer持有的连接资源"""
    cm = getattr(checkpointer, "_cm", None)
    if cm is not None:
        await cm.__aexit__(None, None, None)
        logger.info("Checkpointer connection closed")