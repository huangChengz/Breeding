from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from decimal import Decimal


# ============ 物种分类 ============
class SpeciesBase(BaseModel):
    species_code: str
    species_name: str
    category: str
    description: Optional[str] = None


class SpeciesCreate(SpeciesBase):
    parent_id: Optional[UUID] = None


class SpeciesResponse(SpeciesBase):
    id: UUID
    parent_id: Optional[UUID] = None
    sort_order: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ============ 场景 ============
class SceneBase(BaseModel):
    scene_name: str
    scene_description: Optional[str] = None
    research_output_type: Optional[str] = None
    data_output_type: Optional[str] = None
    data_total_tb: Optional[float] = None
    file_size_description: Optional[str] = None
    data_output_description: Optional[str] = None


class SceneCreate(SceneBase):
    species_id: Optional[UUID] = None


class SceneUpdate(BaseModel):
    scene_name: Optional[str] = None
    scene_description: Optional[str] = None
    research_output_type: Optional[str] = None
    data_output_type: Optional[str] = None
    data_total_tb: Optional[float] = None
    file_size_description: Optional[str] = None
    data_output_description: Optional[str] = None


class SceneResponse(SceneBase):
    id: UUID
    project_id: UUID
    species_id: Optional[UUID] = None
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============ 设备 ============
class EquipmentBase(BaseModel):
    equipment_name: str
    equipment_type: str
    total_price: float
    unit_price: Optional[float] = None
    key_level: Optional[int] = 1
    procurement_method: Optional[str] = None
    usage_plan: Optional[str] = None
    supplier: Optional[str] = None
    is_imported: Optional[bool] = False
    origin_country: Optional[str] = None
    necessity_description: Optional[str] = None
    plan_usage_value: Optional[float] = None
    plan_usage_unit: Optional[str] = None
    plan_usage_description: Optional[str] = None


class EquipmentCreate(EquipmentBase):
    scene_ids: Optional[List[UUID]] = []
    purchase_time: Optional[datetime] = None
    commissioning_time: Optional[datetime] = None
    data_output_type: Optional[str] = None


class EquipmentUpdate(BaseModel):
    equipment_name: Optional[str] = None
    equipment_type: Optional[str] = None
    scene_ids: Optional[List[UUID]] = None
    total_price: Optional[float] = None
    supplier: Optional[str] = None


class EquipmentResponse(EquipmentBase):
    id: UUID
    project_id: UUID
    scene_ids: List[UUID] = []
    created_by: Optional[UUID] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ============ 数据集 ============
class DatasetBase(BaseModel):
    data_name: str
    data_type: str
    other_data_type: Optional[str] = None
    data_total_tb: Optional[float] = None
    access_permission: Optional[str] = 'public'
    is_shared_with_lab: Optional[bool] = False
    data_description: Optional[str] = None
    processing_fee: Optional[float] = 0
    compute_cycle_value: Optional[int] = None
    compute_cycle_unit: Optional[str] = None
    compute_cycle_total_days: Optional[int] = None
    source_cycle_months: Optional[int] = None
    cycle_data_gb: Optional[float] = None
    need_purchase: Optional[bool] = False
    purchase_fee: Optional[float] = 0


class DatasetCreate(DatasetBase):
    source_equipment_ids: Optional[List[UUID]] = []
    scene_ids: Optional[List[UUID]] = []


class DatasetUpdate(BaseModel):
    data_name: Optional[str] = None
    data_type: Optional[str] = None
    processing_fee: Optional[float] = None


class DatasetResponse(DatasetBase):
    id: UUID
    project_id: UUID
    source_equipment_ids: List[UUID] = []
    scene_ids: List[UUID] = []
    created_by: Optional[UUID] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ============ AI模型 ============
class AIModelBase(BaseModel):
    model_name: str
    model_type: str
    estimated_total_fee: float
    model_description: Optional[str] = None
    model_scale: Optional[str] = None
    parameter_count: Optional[str] = None
    function_type: Optional[str] = None


class AIModelCreate(AIModelBase):
    related_data_ids: Optional[List[UUID]] = []
    scene_ids: Optional[List[UUID]] = []


class AIModelUpdate(BaseModel):
    model_name: Optional[str] = None
    estimated_total_fee: Optional[float] = None


class AIModelResponse(AIModelBase):
    id: UUID
    project_id: UUID
    related_data_ids: List[UUID] = []
    scene_ids: List[UUID] = []
    created_by: Optional[UUID] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ============ 研发项目 ============
class RDProjectBase(BaseModel):
    rd_name: str
    rd_direction: Optional[str] = None
    rd_content: Optional[str] = None
    expected_output: Optional[str] = None
    estimated_fee: float


class RDProjectCreate(RDProjectBase):
    scene_ids: Optional[List[UUID]] = []


class RDProjectUpdate(BaseModel):
    rd_name: Optional[str] = None
    estimated_fee: Optional[float] = None


class RDProjectResponse(RDProjectBase):
    id: UUID
    project_id: UUID
    scene_ids: List[UUID] = []
    created_by: Optional[UUID] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ============ 字典 ============
class DictionaryBase(BaseModel):
    dict_type: str
    dict_code: str
    dict_label: str
    dict_value: Optional[str] = None


class DictionaryCreate(DictionaryBase):
    parent_id: Optional[UUID] = None


class DictionaryResponse(DictionaryBase):
    id: UUID
    parent_id: Optional[UUID] = None
    sort_order: int
    is_active: bool

    class Config:
        from_attributes = True
