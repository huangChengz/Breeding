from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID


# ============ 大纲节点 ============
class OutlineNodeBase(BaseModel):
    node_code: str
    node_title: str
    node_level: int
    content: Optional[str] = None
    is_leaf: bool = False
    is_locked: bool = False
    is_expanded: bool = True


class OutlineNodeCreate(OutlineNodeBase):
    parent_id: Optional[UUID] = None
    species_ids: List[UUID] = []


class OutlineNodeUpdate(BaseModel):
    node_title: Optional[str] = None
    content: Optional[str] = None
    is_leaf: Optional[bool] = None
    is_locked: Optional[bool] = None
    is_expanded: Optional[bool] = None
    species_ids: Optional[List[UUID]] = None


class OutlineNodeResponse(OutlineNodeBase):
    id: UUID
    project_id: UUID
    parent_id: Optional[UUID] = None
    species_ids: List[UUID] = []
    sort_order: int
    created_at: datetime
    updated_at: datetime
    children: List['OutlineNodeResponse'] = []

    class Config:
        from_attributes = True


# ============ 节点引用 ============
class NodeReferenceBase(BaseModel):
    ref_entity_type: str
    ref_entity_id: UUID
    ref_type_id: UUID
    reference_note: Optional[str] = None


class NodeReferenceCreate(NodeReferenceBase):
    """创建节点引用 - node_id 在URL路径中，不需要在请求体中"""
    pass


class NodeReferenceResponse(NodeReferenceBase):
    id: UUID
    project_id: UUID
    node_id: UUID
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ============ 引用类型 ============
class ReferenceTypeResponse(BaseModel):
    id: UUID
    type_code: str
    type_name: str
    description: Optional[str] = None
    sort_order: int

    class Config:
        from_attributes = True


# ============ 生成记录 ============
class DocGenerationBase(BaseModel):
    generation_content: str
    prompt_template_id: Optional[UUID] = None
    prompt_version: Optional[str] = None
    generation_source: str = 'ai'


class DocGenerationCreate(DocGenerationBase):
    node_id: UUID


class DocGenerationResponse(DocGenerationBase):
    id: UUID
    project_id: UUID
    node_id: UUID
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    model_used: Optional[str] = None
    is_current_version: bool
    parent_generation_id: Optional[UUID] = None
    entity_snapshot: Optional[dict] = None
    generation_time_ms: Optional[int] = None
    cost_usd: Optional[float] = None
    created_by: Optional[UUID] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ============ Prompt模板 ============
class PromptTemplateBase(BaseModel):
    template_code: str
    template_name: str
    template_category: Optional[str] = None
    template_content: str
    variables: Optional[dict] = None
    description: Optional[str] = None
    version: str = '1.0'


class PromptTemplateCreate(PromptTemplateBase):
    pass


class PromptTemplateResponse(PromptTemplateBase):
    id: UUID
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
