from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.core.database import Base


# 用户角色关联表
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE")),
    Column("role_id", UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE")),
    Column("project_id", UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=True),
    Column("created_at", DateTime, server_default=func.now())
)


class User(Base):
    """用户表"""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    real_name = Column(String(100))
    email = Column(String(255), unique=True, index=True)
    phone = Column(String(20))
    department = Column(String(100))
    status = Column(Integer, default=1)  # 0: 禁用, 1: 正常, 2: 锁定
    last_login_at = Column(DateTime)
    login_attempts = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True)

    # 关系
    roles = relationship("Role", secondary=user_roles, back_populates="users")
    created_projects = relationship("Project", back_populates="creator")


class Role(Base):
    """角色表"""
    __tablename__ = "roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role_code = Column(String(50), unique=True, nullable=False)
    role_name = Column(String(100), nullable=False)
    description = Column(String(500))
    is_system = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 关系
    users = relationship("User", secondary=user_roles, back_populates="roles")
    permissions = relationship("Permission", secondary="role_permissions", back_populates="roles")


# 角色权限关联表
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("role_id", UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE")),
    Column("permission_id", UUID(as_uuid=True), ForeignKey("permissions.id", ondelete="CASCADE")),
    Column("created_at", DateTime, server_default=func.now())
)


class Permission(Base):
    """权限表"""
    __tablename__ = "permissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    perm_code = Column(String(100), unique=True, nullable=False)
    perm_name = Column(String(100), nullable=False)
    module = Column(String(50))  # 对应功能模块
    description = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())

    # 关系
    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")


class Project(Base):
    """项目表"""
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_name = Column(String(255), nullable=False)
    project_code = Column(String(50), unique=True)
    description = Column(String(2000))
    construction_period_months = Column(Integer)  # 建设周期（月）
    location = Column(String(255))  # 建设地点
    owner_unit = Column(String(255))  # 建设单位
    status = Column(Integer, default=0)  # 0: 草稿, 1: 填报中, 2: 审核中, 3: 已完成, 4: 已归档
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True)

    # 关系
    creator = relationship("User", back_populates="created_projects")
