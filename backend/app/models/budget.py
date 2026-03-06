from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, Text, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.core.database import Base


class Budget(Base):
    """预算汇总表"""
    __tablename__ = "budgets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    budget_type = Column(String(50), nullable=False)  # total, hardware, software, data, ai_model, rd
    budget_amount = Column(Numeric(18, 2), nullable=False)  # 预算金额
    currency = Column(String(10), default='CNY')
    fiscal_year = Column(Integer)  # 财年
    status = Column(Integer, default=0)  # 0: 草稿, 1: 已提交, 2: 已审核
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 关系
    project = relationship("Project", backref="budgets")


class BudgetItem(Base):
    """预算明细表"""
    __tablename__ = "budget_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    budget_id = Column(UUID(as_uuid=True), ForeignKey("budgets.id", ondelete="CASCADE"), nullable=False)
    item_type = Column(String(50), nullable=False)  # equipment, dataset, ai_model, rd_project, custom_software, cloud_service
    item_name = Column(String(255), nullable=False)
    item_id = Column(UUID(as_uuid=True), nullable=True)  # 关联的实体ID
    entity_type = Column(String(50))  # equipment, dataset, ai_model, rd_project
    quantity = Column(Integer, default=1)
    unit = Column(String(20))  # 单位
    unit_price = Column(Numeric(15, 2))  # 单价
    total_price = Column(Numeric(18, 2), nullable=False)  # 总价
    budget_category = Column(String(50))  # 预算科目
    necessity_description = Column(Text)  # 必要性与匹配性说明
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 关系
    budget = relationship("Budget", backref="items")
