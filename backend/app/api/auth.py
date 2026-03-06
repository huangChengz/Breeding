from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from typing import List
import uuid

from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token, decode_token
from app.models.user import User, Role, Permission, Project
from app.schemas.user import (
    UserCreate, UserResponse, UserUpdate,
    LoginRequest, TokenResponse, CurrentUser,
    RoleResponse, PermissionResponse,
    ProjectCreate, ProjectResponse, ProjectUpdate
)

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


# ============ 认证相关 ============

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """用户注册"""
    # 检查用户名是否存在
    result = await db.execute(select(User).where(User.username == user_data.username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="用户名已存在")

    # 检查邮箱是否已使用
    if user_data.email:
        result = await db.execute(select(User).where(User.email == user_data.email))
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="邮箱已被使用")

    # 创建用户
    user = User(
        username=user_data.username,
        password_hash=get_password_hash(user_data.password),
        real_name=user_data.real_name,
        email=user_data.email,
        phone=user_data.phone,
        department=user_data.department,
        status=1
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

from pydantic import BaseModel
from typing import Optional


class LoginBody(BaseModel):
    username: str
    password: str


@router.post("/login", response_model=TokenResponse)
async def login(
    login_body: Optional[LoginBody] = None,
    db: AsyncSession = Depends(get_db)
):
    """用户登录 - 支持 JSON 格式"""
    # 使用 JSON 格式
    user_username = login_body.username
    user_password = login_body.password

    result = await db.execute(select(User).where(User.username == user_username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(user_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )

    if user.status != 1:
        raise HTTPException(status_code=400, detail="账户已被禁用")

    # 更新登录信息
    user.last_login_at = datetime.utcnow()
    user.login_attempts = 0
    await db.commit()

    # 生成 token
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username}
    )

    return TokenResponse(access_token=access_token)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> CurrentUser:
    """获取当前登录用户"""
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="无效的令牌")

    user_id = payload.get("sub")
    from sqlalchemy.orm import selectinload
    result = await db.execute(
        select(User)
        .options(selectinload(User.roles))
        .where(User.id == uuid.UUID(user_id))
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 获取用户角色
    roles = [role.role_code for role in user.roles] if user.roles else []

    return CurrentUser(
        id=user.id,
        username=user.username,
        real_name=user.real_name,
        email=user.email,
        roles=roles
    )


@router.get("/me", response_model=CurrentUser)
async def get_me(current_user: CurrentUser = Depends(get_current_user)):
    """获取当前用户信息"""
    return current_user


# ============ 角色权限相关 ============

@router.get("/roles", response_model=List[RoleResponse])
async def list_roles(db: AsyncSession = Depends(get_db)):
    """获取角色列表"""
    result = await db.execute(select(Role))
    roles = result.scalars().all()
    return roles


@router.get("/permissions", response_model=List[PermissionResponse])
async def list_permissions(db: AsyncSession = Depends(get_db)):
    """获取权限列表"""
    result = await db.execute(select(Permission))
    perms = result.scalars().all()
    return perms


# ============ 项目相关 ============

@router.post("/projects", response_model=ProjectResponse)
async def create_project(
    project_data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """创建项目"""
    project = Project(
        project_name=project_data.project_name,
        project_code=project_data.project_code,
        description=project_data.description,
        construction_period_months=project_data.construction_period_months,
        location=project_data.location,
        owner_unit=project_data.owner_unit,
        created_by=current_user.id
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project


@router.get("/projects", response_model=List[ProjectResponse])
async def list_projects(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """获取项目列表"""
    result = await db.execute(
        select(Project).where(Project.deleted_at.is_(None)).offset(skip).limit(limit)
    )
    projects = result.scalars().all()
    return projects


@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """获取项目详情"""
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    return project


@router.delete("/projects/{project_id}")
async def delete_project(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """删除项目"""
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    # 软删除
    project.deleted_at = datetime.utcnow()
    await db.commit()

    return {"message": "删除成功"}
