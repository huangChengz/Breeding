from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import init_db
from app.api import auth
from app.api import data_collection
from app.api import outline
from app.api import doc_agent
from app.api import budget


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时初始化数据库
    await init_db()
    yield
    # 关闭时清理资源


app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    lifespan=lifespan
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(auth.router, prefix="/api", tags=["项目管理"])
app.include_router(data_collection.router, prefix="/api", tags=["数据采集"])
app.include_router(outline.router, prefix="/api", tags=["大纲管理"])
app.include_router(doc_agent.router, prefix="/api", tags=["DocAgent"])
app.include_router(budget.router, prefix="/api", tags=["预算管理"])


@app.get("/")
async def root():
    return {"message": "欢迎使用 AI育种项目申报系统 API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
