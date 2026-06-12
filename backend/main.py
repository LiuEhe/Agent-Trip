from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db, close_db
from app.memory.checkpoint import init_checkpointer, close_checkpointer
from app.agent.graph import build_agent_graph
from app.middlewares.logging_middleware import LoggingMiddleware
from app.middlewares.exception_handler import register_exception_handlers
from app.api.v1.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理：
    - 启动时：初始化数据库连接、初始化checkpointer、构建Agent图（只构建一次）
    - 关闭时：释放数据库连接、关闭checkpointer连接
    """
    # ---------- 启动阶段 ----------
    await init_db()

    checkpointer = await init_checkpointer()
    app.state.checkpointer = checkpointer

    # Agent图只在启动时构建一次，避免每次请求重建图结构
    app.state.agent_graph = build_agent_graph(checkpointer=checkpointer)

    yield

    # ---------- 关闭阶段 ----------
    await close_checkpointer(checkpointer)
    await close_db()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        lifespan=lifespan,
    )

    # ---------- 中间件 ----------
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(LoggingMiddleware)

    # ---------- 全局异常处理 ----------
    register_exception_handlers(app)

    # ---------- 路由挂载 ----------
    app.include_router(api_router, prefix="/api/v1")

    # ---------- 健康检查 ----------
    @app.get("/health", tags=["health"])
    async def health_check():
        return {"status": "ok"}

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
