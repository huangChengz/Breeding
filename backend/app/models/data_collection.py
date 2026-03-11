from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, Text, Numeric, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.core.database import Base


class Species(Base):
    """物种分类表"""
    __tablename__ = "species"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    species_code = Column(String(50), unique=True, nullable=False)
    species_name = Column(String(100), nullable=False)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("species.id"), nullable=True)
    category = Column(String(50), nullable=False)  # crop, horticulture, poultry, mushroom, microorganism
    description = Column(Text)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 自关联
    parent = relationship("Species", remote_side=[id], backref="children")


class Scene(Base):
    """场景表"""
    __tablename__ = "scenes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    species_id = Column(UUID(as_uuid=True), ForeignKey("species.id"), nullable=True)
    scene_name = Column(String(255), nullable=False)
    scene_description = Column(Text)  # 场景描述（对文本生成很重要）
    research_output_type = Column(String(100))  # 科研产出（成果类型）
    research_output_data = Column(String(100))  # 科研产出-数据产出
    data_output_type = Column(String(100))  # 数据产出类型
    data_total_tb = Column(Numeric(10, 2))  # 数据总量(TB)
    file_size_description = Column(String(500))  # 文件大小描述
    data_output_description = Column(Text)  # 数据产出说明
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True)

    # 关系
    project = relationship("Project", backref="scenes")
    species = relationship("Species", backref="scenes")


class Equipment(Base):
    """设备表"""
    __tablename__ = "equipments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    scene_ids = Column(ARRAY(UUID(as_uuid=True)), default=[])  # 关联场景ID数组
    equipment_name = Column(String(255), nullable=False)
    equipment_type = Column(String(50), nullable=False)  # storage, virtual, computing, sensor, robot
    key_level = Column(Integer, default=1)  # 关键星级 1-5
    procurement_method = Column(String(50))  # 采购方式
    usage_plan = Column(Text)  # 使用计划情况
    unit_price = Column(Numeric(15, 2))  # 单价（元）
    total_price = Column(Numeric(15, 2), nullable=False)  # 总价（元）
    supplier = Column(String(255))  # 供应商
    is_imported = Column(Boolean, default=False)  # 是否进口
    need_quote_seal = Column(Boolean, default=False)  # 是否需要报价盖章
    origin_country = Column(String(50))  # 国产或进口
    supplier_1 = Column(String(255))
    supplier_2 = Column(String(255))
    supplier_3 = Column(String(255))
    final_supplier = Column(String(255))
    plan_usage_value = Column(Numeric(10, 2))  # 计划使用数值
    plan_usage_unit = Column(String(20))  # 计划使用单位
    plan_usage_description = Column(Text)  # 计划使用说明
    necessity_description = Column(Text)  # 必要性与匹配性说明
    purchase_time = Column(DateTime)  # 计划购置时间 (stored as date in DB)
    commissioning_time = Column(DateTime)  # 计划投用时间 (stored as date in DB)
    data_output_type = Column(String(100))  # 数据输出类型
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True)

    # 关系
    project = relationship("Project", backref="equipments")


class Dataset(Base):
    """数据集表"""
    __tablename__ = "datasets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    data_name = Column(String(255), nullable=False)
    data_type = Column(String(50), nullable=False)  # 图像、文本、基因组、表型等
    other_data_type = Column(String(100))  # 其他数据类型
    data_total_tb = Column(Numeric(10, 2))  # 数据总量(TB)
    access_permission = Column(String(50), default='public')  # 访问权限
    is_shared_with_lab = Column(Boolean, default=False)  # 是否与实验室共享
    source_equipment_ids = Column(ARRAY(UUID(as_uuid=True)), default=[])  # 来源设备ID数组
    scene_ids = Column(ARRAY(UUID(as_uuid=True)), default=[])  # 关联场景ID数组
    data_description = Column(Text)  # 数据描述
    processing_fee = Column(Numeric(15, 2), default=0)  # 数据处理费（万元）
    compute_cycle_value = Column(Integer)  # 计算周期数值
    compute_cycle_unit = Column(String(20))  # 计算周期单位
    compute_cycle_total_days = Column(Integer)  # 总计（天）
    source_cycle_months = Column(Integer)  # 来源周期（月）
    cycle_data_gb = Column(Numeric(10, 2))  # 周期数据量(GB)
    need_purchase = Column(Boolean, default=False)  # 是否需要购买
    purchase_fee = Column(Numeric(15, 2), default=0)  # 购买费用（万元）
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True)

    # 关系
    project = relationship("Project", backref="datasets")


class AIModel(Base):
    """AI模型表"""
    __tablename__ = "ai_models"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    model_name = Column(String(255), nullable=False)
    model_description = Column(Text)
    model_type = Column(String(50), nullable=False)  # deep_learning, machine_learning, llm
    model_scale = Column(String(50))  # 模型规模
    parameter_count = Column(String(50))  # 参数量
    function_type = Column(String(50))  # 功能类型：training, inference
    related_data_ids = Column(ARRAY(UUID(as_uuid=True)), default=[])  # 关联数据ID数组
    scene_ids = Column(ARRAY(UUID(as_uuid=True)), default=[])  # 关联场景ID数组
    source_equipment_ids = Column(ARRAY(UUID(as_uuid=True)), default=[])  # 关联设备ID数组
    estimated_total_fee = Column(Numeric(15, 2))  # 预计总费用（万元）
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True)

    # 关系
    project = relationship("Project", backref="ai_models")


class RDProject(Base):
    """研发项目表"""
    __tablename__ = "rd_projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    rd_name = Column(String(255), nullable=False)  # 项目名称
    rd_direction = Column(String(100))  # 研发方向
    rd_content = Column(Text)  # 研发内容
    expected_output = Column(Text)  # 预期成果
    estimated_fee = Column(Numeric(15, 2), nullable=False)  # 预估费用（万元）
    scene_ids = Column(ARRAY(UUID(as_uuid=True)), default=[])  # 关联场景ID数组
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True)

    # 关系
    project = relationship("Project", backref="rd_projects")


class Dictionary(Base):
    """字典表（用于动态扩展）"""
    __tablename__ = "dictionaries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dict_type = Column(String(50), nullable=False)  # equipment_type, data_type, model_type
    dict_code = Column(String(50), nullable=False)
    dict_label = Column(String(100), nullable=False)
    dict_value = Column(String(500))
    parent_id = Column(UUID(as_uuid=True), ForeignKey("dictionaries.id"), nullable=True)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 自关联
    parent = relationship("Dictionary", remote_side=[id], backref="children")
