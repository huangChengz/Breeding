from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


# 用户相关
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    real_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    department: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserUpdate(BaseModel):
    real_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    status: Optional[int] = None


class UserResponse(UserBase):
    id: UUID
    status: int
    created_at: datetime

    class Config:
        from_attributes = True


# 角色相关
class RoleBase(BaseModel):
    role_code: str
    role_name: str
    description: Optional[str] = None


class RoleCreate(RoleBase):
    pass


class RoleResponse(RoleBase):
    id: UUID
    is_system: bool
    created_at: datetime

    class Config:
        from_attributes = True


# 权限相关
class PermissionBase(BaseModel):
    perm_code: str
    perm_name: str
    module: Optional[str] = None
    description: Optional[str] = None


class PermissionResponse(PermissionBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# 认证相关
class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class CurrentUser(BaseModel):
    id: UUID
    username: str
    real_name: Optional[str]
    email: Optional[str]
    roles: List[str] = []


# 项目相关
class ProjectBase(BaseModel):
    project_name: str
    project_code: Optional[str] = None
    description: Optional[str] = None
    construction_period_months: Optional[int] = None
    location: Optional[str] = None
    owner_unit: Optional[str] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    project_name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[int] = None


class ProjectResponse(ProjectBase):
    id: UUID
    status: int
    created_at: datetime

    class Config:
        from_attributes = True
