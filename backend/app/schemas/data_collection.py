from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
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
    research_output_type: Optional[str] = None  # 科研产出（成果类型）
    research_output_data: Optional[str] = None  # 科研产出-数据产出
    data_output_type: Optional[str] = None  # 数据产出类型
    data_total_tb: Optional[float] = None  # 数据总量(TB)
    file_size_description: Optional[str] = None  # 文件大小描述
    data_output_description: Optional[str] = None  # 数据产出说明


class SceneCreate(SceneBase):
    species_id: Optional[UUID] = None


class SceneUpdate(BaseModel):
    scene_name: Optional[str] = None
    scene_description: Optional[str] = None
    research_output_type: Optional[str] = None
    research_output_data: Optional[str] = None
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
    equipment_name: str  # 设备名称
    equipment_type: str  # 设备类型（存储、虚拟、计算等）
    key_level: Optional[int] = 1  # 关键星级
    procurement_method: Optional[str] = None  # 采购方式
    usage_plan: Optional[str] = None  # 使用计划情况
    unit_price: Optional[float] = None  # 单价（元）
    total_price: Optional[float] = None  # 总价（元）
    supplier: Optional[str] = None  # 供应商
    is_imported: Optional[bool] = False  # 是否进口
    need_quote_seal: Optional[bool] = False  # 是否需要报价盖章
    origin_country: Optional[str] = None  # 国产or进口
    supplier_1: Optional[str] = None  # 供应商1
    supplier_2: Optional[str] = None  # 供应商2
    supplier_3: Optional[str] = None  # 供应商3
    final_supplier: Optional[str] = None  # 最终选择供应商
    plan_usage_value: Optional[float] = None  # 计划使用-数值
    plan_usage_unit: Optional[str] = None  # 计划使用-单位
    plan_usage_description: Optional[str] = None  # 计划使用-说明
    necessity_description: Optional[str] = None  # 必要性与匹配性说明
    purchase_time: Optional[str] = None  # 计划购置时间
    commissioning_time: Optional[str] = None  # 计划投用时间
    data_output_type: Optional[str] = None  # 数据输出类型


class EquipmentCreate(EquipmentBase):
    scene_ids: Optional[List[UUID]] = []  # 关联场景


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
    updated_at: datetime

    class Config:
        from_attributes = True


# ============ 数据集 ============
class DatasetBase(BaseModel):
    data_name: str  # 数据名称
    data_type: str  # 数据类型
    other_data_type: Optional[str] = None  # 其他数据类型
    data_total_tb: Optional[float] = None  # 数据总量
    access_permission: Optional[str] = 'public'  # 访问权限
    is_shared_with_lab: Optional[bool] = False  # 是否与实验室共享
    data_description: Optional[str] = None  # 数据描述
    processing_fee: Optional[float] = 0  # 数据处理费（万元）
    compute_cycle_value: Optional[int] = None  # 计算周期-数值
    compute_cycle_unit: Optional[str] = None  # 计算周期-单位
    compute_cycle_total_days: Optional[int] = None  # 总计（天）
    source_cycle_months: Optional[int] = None  # 来源周期（月）
    cycle_data_gb: Optional[float] = None  # 周期数据量（GB）
    need_purchase: Optional[bool] = False  # 是否需要购买
    purchase_fee: Optional[float] = 0  # 购买费用（万元）


class DatasetCreate(DatasetBase):
    source_equipment_ids: Optional[List[UUID]] = []  # 来源设备（多选）
    scene_ids: Optional[List[UUID]] = []  # 关联场景（多选）


class DatasetUpdate(BaseModel):
    data_name: Optional[str] = None
    data_type: Optional[str] = None
    other_data_type: Optional[str] = None
    data_total_tb: Optional[float] = None
    access_permission: Optional[str] = None
    is_shared_with_lab: Optional[bool] = None
    data_description: Optional[str] = None
    processing_fee: Optional[float] = None
    compute_cycle_value: Optional[int] = None
    compute_cycle_unit: Optional[str] = None
    compute_cycle_total_days: Optional[int] = None
    source_cycle_months: Optional[int] = None
    cycle_data_gb: Optional[float] = None
    need_purchase: Optional[bool] = None
    purchase_fee: Optional[float] = None
    source_equipment_ids: Optional[List[UUID]] = None
    scene_ids: Optional[List[UUID]] = None


class DatasetResponse(DatasetBase):
    id: UUID
    project_id: UUID
    source_equipment_ids: List[UUID] = []
    scene_ids: List[UUID] = []
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============ AI模型 ============
class AIModelBase(BaseModel):
    model_name: str
    model_type: str
    estimated_total_fee: Optional[float] = None
    model_description: Optional[str] = None
    model_scale: Optional[str] = None
    parameter_count: Optional[str] = None
    function_type: Optional[str] = None


class AIModelCreate(AIModelBase):
    related_data_ids: Optional[List[UUID]] = []
    scene_ids: Optional[List[UUID]] = []
    source_equipment_ids: Optional[List[UUID]] = []


class AIModelUpdate(BaseModel):
    model_name: Optional[str] = None
    model_type: Optional[str] = None
    estimated_total_fee: Optional[float] = None
    model_description: Optional[str] = None
    model_scale: Optional[str] = None
    parameter_count: Optional[str] = None
    function_type: Optional[str] = None
    related_data_ids: Optional[List[UUID]] = None
    scene_ids: Optional[List[UUID]] = None
    source_equipment_ids: Optional[List[UUID]] = None


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
    estimated_fee: Optional[float] = None


class RDProjectCreate(RDProjectBase):
    scene_ids: Optional[List[UUID]] = []


class RDProjectUpdate(BaseModel):
    rd_name: Optional[str] = None
    rd_direction: Optional[str] = None
    rd_content: Optional[str] = None
    expected_output: Optional[str] = None
    estimated_fee: Optional[float] = None
    scene_ids: Optional[List[UUID]] = None


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
