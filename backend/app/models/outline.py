from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, Text, ARRAY, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.core.database import Base


class OutlineNode(Base):
    """大纲节点表"""
    __tablename__ = "outline_nodes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("outline_nodes.id"), nullable=True)
    node_code = Column(String(50), nullable=False)  # 如 "1.1.1", "2.3.4.1"
    node_title = Column(String(500), nullable=False)
    node_level = Column(Integer, nullable=False)  # 1-10章
    species_ids = Column(ARRAY(UUID(as_uuid=True)), default=[])  # 关联的物种分类ID数组
    content = Column(Text)  # 手动填写的内容（不是AI生成的）
    is_leaf = Column(Boolean, default=False)  # 是否叶子节点（可编辑生成）
    sort_order = Column(Integer, default=0)
    is_locked = Column(Boolean, default=False)  # 是否锁定（不允许编辑）
    is_expanded = Column(Boolean, default=True)  # 是否展开
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True)

    # 关系
    project = relationship("Project", backref="outline_nodes")
    parent = relationship("OutlineNode", remote_side=[id], backref="children")


class OutlineTemplate(Base):
    """大纲模板（预设模板，可复制到项目）"""
    __tablename__ = "outline_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_name = Column(String(100), nullable=False)
    template_code = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    template_data = Column(JSONB, nullable=False)  # 模板JSON结构
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class ReferenceType(Base):
    """引用类型表"""
    __tablename__ = "reference_types"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type_code = Column(String(50), unique=True, nullable=False)  # core, background, budget
    type_name = Column(String(100), nullable=False)
    description = Column(Text)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())


class NodeReference(Base):
    """节点引用表（场景、设备、数据、AI模型与大纲节点的关联）"""
    __tablename__ = "node_references"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    node_id = Column(UUID(as_uuid=True), ForeignKey("outline_nodes.id", ondelete="CASCADE"), nullable=False)
    ref_type_id = Column(UUID(as_uuid=True), ForeignKey("reference_types.id"), nullable=False)
    ref_entity_type = Column(String(50), nullable=False)  # scene, equipment, dataset, ai_model, rd_project
    ref_entity_id = Column(UUID(as_uuid=True), nullable=False)  # 关联的实体ID
    reference_note = Column(Text)  # 引用备注
    is_active = Column(Boolean, default=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, server_default=func.now())

    # 关系
    project = relationship("Project", backref="node_references")
    node = relationship("OutlineNode", backref="references")


class DocGeneration(Base):
    """生成记录表"""
    __tablename__ = "doc_generations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    node_id = Column(UUID(as_uuid=True), ForeignKey("outline_nodes.id", ondelete="CASCADE"), nullable=False)
    generation_content = Column(Text, nullable=False)  # AI生成的内容
    prompt_template_id = Column(UUID(as_uuid=True), ForeignKey("prompt_templates.id"), nullable=True)
    prompt_version = Column(String(50))  # Prompt版本
    input_tokens = Column(Integer)  # 输入token数
    output_tokens = Column(Integer)  # 输出token数
    model_used = Column(String(100))  # 使用的模型
    generation_source = Column(String(50), default='ai')  # ai, manual, hybrid
    is_current_version = Column(Boolean, default=True)  # 是否当前版本
    parent_generation_id = Column(UUID(as_uuid=True), ForeignKey("doc_generations.id"))  # 父版本
    entity_snapshot = Column(JSONB)  # 实体快照（血缘溯源）
    generation_time_ms = Column(Integer)  # 生成耗时（毫秒）
    cost_usd = Column(Numeric(10, 6))  # 成本（美元）
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, server_default=func.now())

    # 关系
    project = relationship("Project", backref="doc_generations")
    node = relationship("OutlineNode", backref="generations")


class GenerationHistory(Base):
    """生成历史版本表"""
    __tablename__ = "generation_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    generation_id = Column(UUID(as_uuid=True), ForeignKey("doc_generations.id", ondelete="CASCADE"), nullable=False)
    version_number = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    entity_snapshot = Column(JSONB)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, server_default=func.now())


class PromptTemplate(Base):
    """Prompt模板表"""
    __tablename__ = "prompt_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_code = Column(String(100), unique=True, nullable=False)
    template_name = Column(String(255), nullable=False)
    template_category = Column(String(50))  # outline, optimize, translate
    template_content = Column(Text, nullable=False)  # Prompt模板内容
    variables = Column(JSONB)  # 变量定义
    description = Column(Text)
    version = Column(String(50), default='1.0')
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
