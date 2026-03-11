from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from datetime import datetime
import uuid

from app.core.database import get_db
from app.api.auth import get_current_user
from app.schemas.user import CurrentUser
from app.schemas.data_collection import (
    SceneCreate, SceneUpdate, SceneResponse,
    EquipmentCreate, EquipmentUpdate, EquipmentResponse,
    DatasetCreate, DatasetUpdate, DatasetResponse,
    AIModelCreate, AIModelUpdate, AIModelResponse,
    RDProjectCreate, RDProjectUpdate, RDProjectResponse,
    SpeciesCreate, SpeciesResponse,
    DictionaryCreate, DictionaryResponse
)
from app.models.data_collection import (
    Scene, Equipment, Dataset, AIModel, RDProject, Species, Dictionary
)

router = APIRouter()


# ============ 物种分类 ============

@router.get("/species", response_model=List[SpeciesResponse])
async def list_species(db: AsyncSession = Depends(get_db)):
    """获取物种分类列表"""
    result = await db.execute(select(Species).where(Species.is_active == True))
    return result.scalars().all()


@router.post("/species", response_model=SpeciesResponse)
async def create_species(
    data: SpeciesCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """创建物种分类"""
    species = Species(**data.model_dump())
    db.add(species)
    await db.commit()
    await db.refresh(species)
    return species


@router.patch("/species/{species_id}", response_model=SpeciesResponse)
async def update_species(
    species_id: uuid.UUID,
    data: SpeciesCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """更新物种分类"""
    result = await db.execute(select(Species).where(Species.id == species_id))
    species = result.scalar_one_or_none()
    if not species:
        raise HTTPException(status_code=404, detail="物种分类不存在")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(species, key, value)

    await db.commit()
    await db.refresh(species)
    return species


@router.delete("/species/{species_id}")
async def delete_species(
    species_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """删除物种分类"""
    result = await db.execute(select(Species).where(Species.id == species_id))
    species = result.scalar_one_or_none()
    if not species:
        raise HTTPException(status_code=404, detail="物种分类不存在")

    species.is_active = False
    await db.commit()
    return {"message": "删除成功"}


# ============ 场景管理 ============

@router.get("/projects/{project_id}/scenes", response_model=List[SceneResponse])
async def list_scenes(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """获取项目场景列表"""
    result = await db.execute(
        select(Scene).where(
            Scene.project_id == project_id,
            Scene.deleted_at.is_(None)
        )
    )
    return result.scalars().all()


@router.post("/projects/{project_id}/scenes", response_model=SceneResponse)
async def create_scene(
    project_id: uuid.UUID,
    data: SceneCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """创建场景"""
    scene = Scene(**data.model_dump(), project_id=project_id, created_by=current_user.id)
    db.add(scene)
    await db.commit()
    await db.refresh(scene)
    return scene


@router.get("/scenes/{scene_id}", response_model=SceneResponse)
async def get_scene(
    scene_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """获取场景详情"""
    result = await db.execute(select(Scene).where(Scene.id == scene_id))
    scene = result.scalar_one_or_none()
    if not scene:
        raise HTTPException(status_code=404, detail="场景不存在")
    return scene


@router.patch("/scenes/{scene_id}", response_model=SceneResponse)
async def update_scene(
    scene_id: uuid.UUID,
    data: SceneUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """更新场景"""
    result = await db.execute(select(Scene).where(Scene.id == scene_id))
    scene = result.scalar_one_or_none()
    if not scene:
        raise HTTPException(status_code=404, detail="场景不存在")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(scene, key, value)

    await db.commit()
    await db.refresh(scene)
    return scene


@router.delete("/scenes/{scene_id}")
async def delete_scene(
    scene_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """删除场景"""
    result = await db.execute(select(Scene).where(Scene.id == scene_id))
    scene = result.scalar_one_or_none()
    if not scene:
        raise HTTPException(status_code=404, detail="场景不存在")

    scene.deleted_at = datetime.utcnow()
    await db.commit()
    return {"message": "删除成功"}


# ============ 设备管理 ============

@router.get("/projects/{project_id}/equipments", response_model=List[EquipmentResponse])
async def list_equipments(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """获取项目设备列表"""
    result = await db.execute(
        select(Equipment).where(
            Equipment.project_id == project_id,
            Equipment.deleted_at.is_(None)
        )
    )
    return result.scalars().all()


@router.post("/projects/{project_id}/equipments", response_model=EquipmentResponse)
async def create_equipment(
    project_id: uuid.UUID,
    data: EquipmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """创建设备"""
    from datetime import date as date_type

    # Convert string to date for date fields
    equipment_data = data.model_dump()
    if equipment_data.get('purchase_time') and isinstance(equipment_data['purchase_time'], str):
        try:
            equipment_data['purchase_time'] = datetime.strptime(equipment_data['purchase_time'], '%Y-%m-%d').date()
        except:
            equipment_data['purchase_time'] = None
    if equipment_data.get('commissioning_time') and isinstance(equipment_data['commissioning_time'], str):
        try:
            equipment_data['commissioning_time'] = datetime.strptime(equipment_data['commissioning_time'], '%Y-%m-%d').date()
        except:
            equipment_data['commissioning_time'] = None

    equipment = Equipment(**equipment_data, project_id=project_id, created_by=current_user.id)
    db.add(equipment)
    await db.commit()
    await db.refresh(equipment)
    return equipment


@router.get("/equipments/{equipment_id}", response_model=EquipmentResponse)
async def get_equipment(
    equipment_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """获取设备详情"""
    result = await db.execute(select(Equipment).where(Equipment.id == equipment_id))
    equipment = result.scalar_one_or_none()
    if not equipment:
        raise HTTPException(status_code=404, detail="设备不存在")
    return equipment


@router.patch("/equipments/{equipment_id}", response_model=EquipmentResponse)
async def update_equipment(
    equipment_id: uuid.UUID,
    data: EquipmentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """更新设备"""
    result = await db.execute(select(Equipment).where(Equipment.id == equipment_id))
    equipment = result.scalar_one_or_none()
    if not equipment:
        raise HTTPException(status_code=404, detail="设备不存在")

    for key, value in data.model_dump(exclude_unset=True).items():
        # Convert string to date for date fields
        if key in ('purchase_time', 'commissioning_time') and isinstance(value, str):
            try:
                value = datetime.strptime(value, '%Y-%m-%d').date()
            except:
                value = None
        setattr(equipment, key, value)

    await db.commit()
    await db.refresh(equipment)
    return equipment


@router.delete("/equipments/{equipment_id}")
async def delete_equipment(
    equipment_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """删除设备"""
    result = await db.execute(select(Equipment).where(Equipment.id == equipment_id))
    equipment = result.scalar_one_or_none()
    if not equipment:
        raise HTTPException(status_code=404, detail="设备不存在")

    equipment.deleted_at = datetime.utcnow()
    await db.commit()
    return {"message": "删除成功"}


# ============ 数据集管理 ============

@router.get("/projects/{project_id}/datasets", response_model=List[DatasetResponse])
async def list_datasets(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """获取项目数据集列表"""
    result = await db.execute(
        select(Dataset).where(
            Dataset.project_id == project_id,
            Dataset.deleted_at.is_(None)
        )
    )
    return result.scalars().all()


@router.post("/projects/{project_id}/datasets", response_model=DatasetResponse)
async def create_dataset(
    project_id: uuid.UUID,
    data: DatasetCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """创建数据集"""
    dataset = Dataset(**data.model_dump(), project_id=project_id, created_by=current_user.id)
    db.add(dataset)
    await db.commit()
    await db.refresh(dataset)
    return dataset


@router.get("/datasets/{dataset_id}", response_model=DatasetResponse)
async def get_dataset(
    dataset_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """获取数据集详情"""
    result = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise HTTPException(status_code=404, detail="数据集不存在")
    return dataset


@router.patch("/datasets/{dataset_id}", response_model=DatasetResponse)
async def update_dataset(
    dataset_id: uuid.UUID,
    data: DatasetUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """更新数据集"""
    result = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise HTTPException(status_code=404, detail="数据集不存在")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(dataset, key, value)

    await db.commit()
    await db.refresh(dataset)
    return dataset


@router.delete("/datasets/{dataset_id}")
async def delete_dataset(
    dataset_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """删除数据集"""
    result = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise HTTPException(status_code=404, detail="数据集不存在")

    dataset.deleted_at = datetime.utcnow()
    await db.commit()
    return {"message": "删除成功"}


# ============ AI模型管理 ============

@router.get("/projects/{project_id}/ai-models", response_model=List[AIModelResponse])
async def list_ai_models(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """获取项目AI模型列表"""
    result = await db.execute(
        select(AIModel).where(
            AIModel.project_id == project_id,
            AIModel.deleted_at.is_(None)
        )
    )
    return result.scalars().all()


@router.post("/projects/{project_id}/ai-models", response_model=AIModelResponse)
async def create_ai_model(
    project_id: uuid.UUID,
    data: AIModelCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """创建AI模型"""
    ai_model = AIModel(**data.model_dump(), project_id=project_id, created_by=current_user.id)
    db.add(ai_model)
    await db.commit()
    await db.refresh(ai_model)
    return ai_model


@router.get("/ai-models/{ai_model_id}", response_model=AIModelResponse)
async def get_ai_model(
    ai_model_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """获取AI模型详情"""
    result = await db.execute(select(AIModel).where(AIModel.id == ai_model_id))
    ai_model = result.scalar_one_or_none()
    if not ai_model:
        raise HTTPException(status_code=404, detail="AI模型不存在")
    return ai_model


@router.patch("/ai-models/{ai_model_id}", response_model=AIModelResponse)
async def update_ai_model(
    ai_model_id: uuid.UUID,
    data: AIModelUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """更新AI模型"""
    result = await db.execute(select(AIModel).where(AIModel.id == ai_model_id))
    ai_model = result.scalar_one_or_none()
    if not ai_model:
        raise HTTPException(status_code=404, detail="AI模型不存在")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(ai_model, key, value)

    await db.commit()
    await db.refresh(ai_model)
    return ai_model


@router.delete("/ai-models/{ai_model_id}")
async def delete_ai_model(
    ai_model_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """删除AI模型"""
    result = await db.execute(select(AIModel).where(AIModel.id == ai_model_id))
    ai_model = result.scalar_one_or_none()
    if not ai_model:
        raise HTTPException(status_code=404, detail="AI模型不存在")

    ai_model.deleted_at = datetime.utcnow()
    await db.commit()
    return {"message": "删除成功"}


# ============ 研发项目管理 ============

@router.get("/projects/{project_id}/rd-projects", response_model=List[RDProjectResponse])
async def list_rd_projects(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """获取项目研发项目列表"""
    result = await db.execute(
        select(RDProject).where(
            RDProject.project_id == project_id,
            RDProject.deleted_at.is_(None)
        )
    )
    return result.scalars().all()


@router.post("/projects/{project_id}/rd-projects", response_model=RDProjectResponse)
async def create_rd_project(
    project_id: uuid.UUID,
    data: RDProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """创建研发项目"""
    rd_project = RDProject(**data.model_dump(), project_id=project_id, created_by=current_user.id)
    db.add(rd_project)
    await db.commit()
    await db.refresh(rd_project)
    return rd_project


@router.get("/rd-projects/{rd_project_id}", response_model=RDProjectResponse)
async def get_rd_project(
    rd_project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """获取研发项目详情"""
    result = await db.execute(select(RDProject).where(RDProject.id == rd_project_id))
    rd_project = result.scalar_one_or_none()
    if not rd_project:
        raise HTTPException(status_code=404, detail="研发项目不存在")
    return rd_project


@router.patch("/rd-projects/{rd_project_id}", response_model=RDProjectResponse)
async def update_rd_project(
    rd_project_id: uuid.UUID,
    data: RDProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """更新研发项目"""
    result = await db.execute(select(RDProject).where(RDProject.id == rd_project_id))
    rd_project = result.scalar_one_or_none()
    if not rd_project:
        raise HTTPException(status_code=404, detail="研发项目不存在")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(rd_project, key, value)

    await db.commit()
    await db.refresh(rd_project)
    return rd_project


@router.delete("/rd-projects/{rd_project_id}")
async def delete_rd_project(
    rd_project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """删除研发项目"""
    result = await db.execute(select(RDProject).where(RDProject.id == rd_project_id))
    rd_project = result.scalar_one_or_none()
    if not rd_project:
        raise HTTPException(status_code=404, detail="研发项目不存在")

    rd_project.deleted_at = datetime.utcnow()
    await db.commit()
    return {"message": "删除成功"}


# ============ 字典管理 ============

@router.get("/dictionaries", response_model=List[DictionaryResponse])
async def list_dictionaries(
    dict_type: str = None,
    db: AsyncSession = Depends(get_db)
):
    """获取字典列表"""
    query = select(Dictionary).where(Dictionary.is_active == True)
    if dict_type:
        query = query.where(Dictionary.dict_type == dict_type)
    result = await db.execute(query.order_by(Dictionary.sort_order))
    return result.scalars().all()


@router.post("/dictionaries", response_model=DictionaryResponse)
async def create_dictionary(
    data: DictionaryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """创建字典"""
    dictionary = Dictionary(**data.model_dump())
    db.add(dictionary)
    await db.commit()
    await db.refresh(dictionary)
    return dictionary


@router.patch("/dictionaries/{dictionary_id}", response_model=DictionaryResponse)
async def update_dictionary(
    dictionary_id: uuid.UUID,
    data: DictionaryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """更新字典"""
    result = await db.execute(select(Dictionary).where(Dictionary.id == dictionary_id))
    dictionary = result.scalar_one_or_none()
    if not dictionary:
        raise HTTPException(status_code=404, detail="字典不存在")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(dictionary, key, value)

    await db.commit()
    await db.refresh(dictionary)
    return dictionary


@router.delete("/dictionaries/{dictionary_id}")
async def delete_dictionary(
    dictionary_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """删除字典"""
    result = await db.execute(select(Dictionary).where(Dictionary.id == dictionary_id))
    dictionary = result.scalar_one_or_none()
    if not dictionary:
        raise HTTPException(status_code=404, detail="字典不存在")

    dictionary.is_active = False
    await db.commit()
    return {"message": "删除成功"}
