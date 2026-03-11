import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from decimal import Decimal

from app.core.database import get_db
from app.api.auth import get_current_user
from app.schemas.user import CurrentUser
from app.models.budget import Budget, BudgetItem
from app.models.data_collection import Equipment, Dataset, AIModel, RDProject

router = APIRouter()


# ============ 预算汇总 ============

@router.get("/projects/{project_id}/budget-summary")
async def get_budget_summary(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """获取项目预算汇总"""

    # 设备预算
    eq_result = await db.execute(
        select(func.sum(Equipment.total_price))
        .where(Equipment.project_id == project_id, Equipment.deleted_at.is_(None))
    )
    equipment_budget = eq_result.scalar() or 0

    # 数据处理费
    ds_processing_result = await db.execute(
        select(func.sum(Dataset.processing_fee))
        .where(Dataset.project_id == project_id, Dataset.deleted_at.is_(None))
    )
    data_processing_budget = ds_processing_result.scalar() or 0

    # 数据购买费
    ds_purchase_result = await db.execute(
        select(func.sum(Dataset.purchase_fee))
        .where(Dataset.project_id == project_id, Dataset.deleted_at.is_(None))
    )
    data_purchase_budget = ds_purchase_result.scalar() or 0

    # AI模型费用
    ai_result = await db.execute(
        select(func.sum(AIModel.estimated_total_fee))
        .where(AIModel.project_id == project_id, AIModel.deleted_at.is_(None))
    )
    ai_model_budget = ai_result.scalar() or 0

    # 研发项目费用
    rd_result = await db.execute(
        select(func.sum(RDProject.estimated_fee))
        .where(RDProject.project_id == project_id, RDProject.deleted_at.is_(None))
    )
    rd_budget = rd_result.scalar() or 0

    # 总计
    total_budget = (
        float(equipment_budget) +
        float(data_processing_budget) +
        float(data_purchase_budget) +
        float(ai_model_budget) +
        float(rd_budget)
    )

    # 转换单位：统一转为元
    # 设备是元，数据/AI模型/研发项目是万元，需要乘以10000
    data_processing_budget_yuan = float(data_processing_budget) * 10000 if data_processing_budget else 0
    data_purchase_budget_yuan = float(data_purchase_budget) * 10000 if data_purchase_budget else 0
    ai_model_budget_yuan = float(ai_model_budget) * 10000 if ai_model_budget else 0
    rd_budget_yuan = float(rd_budget) * 10000 if rd_budget else 0

    total_budget_yuan = (
        float(equipment_budget) +
        data_processing_budget_yuan +
        data_purchase_budget_yuan +
        ai_model_budget_yuan +
        rd_budget_yuan
    )

    return {
        "equipment_budget": float(equipment_budget) if equipment_budget else 0,
        "data_processing_budget": data_processing_budget_yuan,
        "data_purchase_budget": data_purchase_budget_yuan,
        "ai_model_budget": ai_model_budget_yuan,
        "rd_budget": rd_budget_yuan,
        "total_budget": total_budget_yuan
    }


# ============ 设备预算明细 ============

@router.get("/projects/{project_id}/budget-equipments")
async def get_equipment_budget(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """获取设备预算明细"""

    result = await db.execute(
        select(Equipment)
        .where(Equipment.project_id == project_id, Equipment.deleted_at.is_(None))
        .order_by(Equipment.equipment_type, Equipment.equipment_name)
    )
    equipments = result.scalars().all()

    return [
        {
            "id": str(e.id),
            "equipment_name": e.equipment_name,
            "equipment_type": e.equipment_type,
            "key_level": e.key_level,
            "unit_price": float(e.unit_price) if e.unit_price else 0,
            "total_price": float(e.total_price) if e.total_price else 0,
            "supplier": e.supplier,
            "is_imported": e.is_imported,
            "necessity_description": e.necessity_description,
            "procurement_method": e.procurement_method
        }
        for e in equipments
    ]


# ============ 数据预算明细 ============

@router.get("/projects/{project_id}/budget-datasets")
async def get_dataset_budget(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """获取数据预算明细"""

    result = await db.execute(
        select(Dataset)
        .where(Dataset.project_id == project_id, Dataset.deleted_at.is_(None))
        .order_by(Dataset.data_type, Dataset.data_name)
    )
    datasets = result.scalars().all()

    return [
        {
            "id": str(d.id),
            "data_name": d.data_name,
            "data_type": d.data_type,
            "data_total_tb": float(d.data_total_tb) if d.data_total_tb else 0,
            "processing_fee": float(d.processing_fee) if d.processing_fee else 0,
            "purchase_fee": float(d.purchase_fee) if d.purchase_fee else 0,
            "total_fee": float(d.processing_fee or 0) + float(d.purchase_fee or 0),
            "need_purchase": d.need_purchase,
            "data_description": d.data_description
        }
        for d in datasets
    ]


# ============ AI模型预算明细 ============

@router.get("/projects/{project_id}/budget-ai-models")
async def get_ai_model_budget(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """获取AI模型预算明细"""

    result = await db.execute(
        select(AIModel)
        .where(AIModel.project_id == project_id, AIModel.deleted_at.is_(None))
        .order_by(AIModel.model_type, AIModel.model_name)
    )
    models = result.scalars().all()

    return [
        {
            "id": str(m.id),
            "model_name": m.model_name,
            "model_type": m.model_type,
            "model_scale": m.model_scale,
            "parameter_count": m.parameter_count,
            "function_type": m.function_type,
            "estimated_total_fee": float(m.estimated_total_fee) if m.estimated_total_fee else 0,
            "model_description": m.model_description
        }
        for m in models
    ]


# ============ 研发项目预算明细 ============

@router.get("/projects/{project_id}/budget-rd-projects")
async def get_rd_project_budget(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """获取研发项目预算明细"""

    result = await db.execute(
        select(RDProject)
        .where(RDProject.project_id == project_id, RDProject.deleted_at.is_(None))
        .order_by(RDProject.rd_direction, RDProject.rd_name)
    )
    rd_projects = result.scalars().all()

    return [
        {
            "id": str(r.id),
            "rd_name": r.rd_name,
            "rd_direction": r.rd_direction,
            "rd_content": r.rd_content,
            "expected_output": r.expected_output,
            "estimated_fee": float(r.estimated_fee) if r.estimated_fee else 0
        }
        for r in rd_projects
    ]


# ============ 导出预算报表 ============

@router.get("/projects/{project_id}/budget-export")
async def export_budget(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """导出预算报表（JSON格式）"""

    # 获取汇总
    summary = await get_budget_summary(project_id, db, current_user)

    # 获取明细
    equipments = await get_equipment_budget(project_id, db, current_user)
    datasets = await get_dataset_budget(project_id, db, current_user)
    ai_models = await get_ai_model_budget(project_id, db, current_user)
    rd_projects = await get_rd_project_budget(project_id, db, current_user)

    return {
        "project_id": str(project_id),
        "summary": summary,
        "details": {
            "equipments": equipments,
            "datasets": datasets,
            "ai_models": ai_models,
            "rd_projects": rd_projects
        }
    }
