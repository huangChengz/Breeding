from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, cast, Integer, text
from sqlalchemy.orm import selectinload
from typing import List
from datetime import datetime
import uuid

from app.core.database import get_db
from app.api.auth import get_current_user
from app.schemas.user import CurrentUser
from app.schemas.outline import (
    OutlineNodeCreate, OutlineNodeUpdate, OutlineNodeResponse,
    NodeReferenceCreate, NodeReferenceResponse,
    ReferenceTypeResponse,
    DocGenerationCreate, DocGenerationResponse
)
from app.models.outline import (
    OutlineNode, OutlineTemplate, ReferenceType,
    NodeReference, DocGeneration, PromptTemplate
)
from app.models.data_collection import Scene, Equipment, Dataset, AIModel, RDProject

router = APIRouter()


# ============ 数据库修复 ============

@router.post("/fix-db-constraint")
async def fix_db_constraint(
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """修复数据库约束（允许 ref_type_id 为空）"""
    try:
        await db.execute(text("ALTER TABLE node_references ALTER COLUMN ref_type_id DROP NOT NULL"))
        await db.commit()
        return {"message": "数据库约束已修复"}
    except Exception as e:
        return {"error": str(e)}


# ============ 大纲节点 ============

def sort_key(code: str):
    """将编码转换为可排序的元组"""
    try:
        parts = code.split('.')
        # 将每个部分转换为整数，如果无法转换则置为0
        return tuple(int(p) if p.isdigit() else 0 for p in parts)
    except:
        return (0,)


@router.get("/projects/{project_id}/outline", response_model=List[OutlineNodeResponse])
async def get_outline_tree(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """获取项目大纲树"""
    # 获取顶级节点及其子节点
    result = await db.execute(
        select(OutlineNode)
        .where(
            OutlineNode.project_id == project_id,
            OutlineNode.parent_id == None,
            OutlineNode.deleted_at.is_(None)
        )
    )
    nodes = result.scalars().all()
    # Python排序
    nodes = sorted(nodes, key=lambda n: sort_key(n.node_code))

    # 递归构建树
    async def build_tree(node: OutlineNode) -> OutlineNodeResponse:
        # 获取子节点
        children_result = await db.execute(
            select(OutlineNode)
            .where(
                OutlineNode.parent_id == node.id,
                OutlineNode.deleted_at.is_(None)
            )
        )
        children = children_result.scalars().all()
        children = sorted(children, key=lambda n: sort_key(n.node_code))

        response = OutlineNodeResponse(
            id=node.id,
            project_id=node.project_id,
            parent_id=node.parent_id,
            node_code=node.node_code,
            node_title=node.node_title,
            node_level=node.node_level,
            species_ids=node.species_ids or [],
            content=node.content,
            is_leaf=node.is_leaf,
            sort_order=node.sort_order,
            is_locked=node.is_locked,
            is_expanded=node.is_expanded,
            created_at=node.created_at,
            updated_at=node.updated_at,
            children=[]
        )

        # 递归加载子节点
        child_responses = []
        for child in children:
            child_response = await build_tree(child)
            child_responses.append(child_response)
        response.children = child_responses

        return response

    tree = []
    for node in nodes:
        tree.append(await build_tree(node))

    return tree


@router.post("/projects/{project_id}/outline", response_model=OutlineNodeResponse)
async def create_outline_node(
    project_id: uuid.UUID,
    data: OutlineNodeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """创建大纲节点"""
    node = OutlineNode(**data.model_dump(), project_id=project_id)
    db.add(node)
    await db.commit()
    await db.refresh(node)

    # 返回带空children的响应
    return OutlineNodeResponse(
        id=node.id,
        project_id=node.project_id,
        parent_id=node.parent_id,
        node_code=node.node_code,
        node_title=node.node_title,
        node_level=node.node_level,
        species_ids=node.species_ids or [],
        content=node.content,
        is_leaf=node.is_leaf,
        sort_order=node.sort_order,
        is_locked=node.is_locked,
        is_expanded=node.is_expanded,
        created_at=node.created_at,
        updated_at=node.updated_at,
        children=[]
    )


@router.get("/outline/{node_id}", response_model=OutlineNodeResponse)
async def get_outline_node(
    node_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """获取大纲节点详情"""
    try:
        print(f"[get_outline_node] node_id={node_id}")
        result = await db.execute(select(OutlineNode).where(OutlineNode.id == node_id))
        node = result.scalar_one_or_none()
        if not node:
            raise HTTPException(status_code=404, detail="节点不存在")

        # 构建响应对象
        response = OutlineNodeResponse(
            id=node.id,
            project_id=node.project_id,
            parent_id=node.parent_id,
            node_code=node.node_code,
            node_title=node.node_title,
            node_level=node.node_level,
            species_ids=node.species_ids or [],
            content=node.content,
            is_leaf=node.is_leaf,
            sort_order=node.sort_order,
            is_locked=node.is_locked,
            is_expanded=node.is_expanded,
            created_at=node.created_at,
            updated_at=node.updated_at,
            children=[]
        )
        print(f"[get_outline_node] node_code={node.node_code}, content={node.content[:50] if node.content else 'None'}")
        return response
    except Exception as e:
        import traceback
        print(f"[get_outline_node] ERROR: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/outline/{node_id}")
async def update_outline_node(
    node_id: uuid.UUID,
    data: OutlineNodeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """更新大纲节点"""
    print(f"[update_outline_node] node_id={node_id}, data={data.model_dump()}")
    result = await db.execute(select(OutlineNode).where(OutlineNode.id == node_id))
    node = result.scalar_one_or_none()
    if not node:
        raise HTTPException(status_code=404, detail="节点不存在")

    print(f"[update_outline_node] node_code={node.node_code}, node_title={node.node_title}, current_content={node.content[:50] if node.content else 'None'}")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(node, key, value)

    await db.commit()
    await db.refresh(node)

    print(f"[update_outline_node] after update, content={node.content[:50] if node.content else 'None'}")

    # 返回简化数据，避免关系加载问题
    return {
        "id": node.id,
        "project_id": node.project_id,
        "parent_id": node.parent_id,
        "node_code": node.node_code,
        "node_title": node.node_title,
        "node_level": node.node_level,
        "content": node.content,
        "is_leaf": node.is_leaf,
        "sort_order": node.sort_order,
        "created_at": node.created_at,
        "updated_at": node.updated_at
    }


# ============ 内容保存 ============

class ContentSaveRequest(BaseModel):
    content: str


@router.post("/outline/{node_id}/save-content")
async def save_node_content(
    node_id: uuid.UUID,
    data: ContentSaveRequest,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """保存大纲节点内容"""
    result = await db.execute(select(OutlineNode).where(OutlineNode.id == node_id))
    node = result.scalar_one_or_none()
    if not node:
        raise HTTPException(status_code=404, detail="节点不存在")

    # 更新节点内容
    node.content = data.content
    await db.commit()
    await db.refresh(node)

    return {
        "id": node.id,
        "content": node.content,
        "updated_at": node.updated_at
    }


# ============ 节点引用 ============

@router.get("/outline/{node_id}/references", response_model=List[NodeReferenceResponse])
async def get_node_references(
    node_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """获取节点的引用列表"""
    result = await db.execute(
        select(NodeReference)
        .where(NodeReference.node_id == node_id, NodeReference.is_active == True)
    )
    return result.scalars().all()


@router.post("/outline/{node_id}/references", response_model=NodeReferenceResponse)
async def create_node_reference(
    node_id: uuid.UUID,
    data: NodeReferenceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """创建节点引用"""
    # 验证节点存在
    node_result = await db.execute(select(OutlineNode).where(OutlineNode.id == node_id))
    if not node_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="节点不存在")

    # 获取project_id从节点
    project_id = (await db.execute(
        select(OutlineNode.project_id).where(OutlineNode.id == node_id)
    )).scalar_one()

    # 显式构建引用数据，排除node_id
    reference_data = {
        "ref_entity_type": data.ref_entity_type,
        "ref_entity_id": data.ref_entity_id,
        "ref_type_id": data.ref_type_id,
        "reference_note": data.reference_note,
    }

    reference = NodeReference(
        **reference_data,
        node_id=node_id,
        project_id=project_id,
        created_by=current_user.id
    )

    db.add(reference)
    await db.commit()
    await db.refresh(reference)
    return reference


@router.delete("/references/{reference_id}")
async def delete_node_reference(
    reference_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """删除节点引用"""
    result = await db.execute(select(NodeReference).where(NodeReference.id == reference_id))
    reference = result.scalar_one_or_none()
    if not reference:
        raise HTTPException(status_code=404, detail="引用不存在")

    reference.is_active = False
    await db.commit()
    return {"message": "删除成功"}


# ============ 引用类型 ============

@router.get("/reference-types", response_model=List[ReferenceTypeResponse])
async def list_reference_types(db: AsyncSession = Depends(get_db)):
    """获取引用类型列表"""
    result = await db.execute(select(ReferenceType).order_by(ReferenceType.sort_order))
    types = result.scalars().all()

    # 如果没有数据，初始化默认引用类型
    if not types:
        default_types = [
            ReferenceType(type_code="core", type_name="核心引用", description="作为本子的核心内容", sort_order=1),
            ReferenceType(type_code="background", type_name="参考背景", description="作为背景参考", sort_order=2),
            ReferenceType(type_code="budget", type_name="预算关联", description="关联预算信息", sort_order=3),
        ]
        for ref_type in default_types:
            db.add(ref_type)
        await db.commit()
        result = await db.execute(select(ReferenceType).order_by(ReferenceType.sort_order))
        types = result.scalars().all()

    return types


# ============ 文档生成 ============

@router.get("/outline/{node_id}/generations", response_model=List[DocGenerationResponse])
async def get_node_generations(
    node_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """获取节点的生成历史"""
    result = await db.execute(
        select(DocGeneration)
        .where(DocGeneration.node_id == node_id)
        .order_by(DocGeneration.created_at.desc())
    )
    return result.scalars().all()


@router.post("/outline/{node_id}/generations", response_model=DocGenerationResponse)
async def create_generation(
    node_id: uuid.UUID,
    data: DocGenerationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """创建生成记录"""
    # 获取项目ID
    node_result = await db.execute(select(OutlineNode).where(OutlineNode.id == node_id))
    node = node_result.scalar_one_or_none()
    if not node:
        raise HTTPException(status_code=404, detail="节点不存在")

    # 将旧版本标记为非当前
    await db.execute(
        update(DocGeneration)
        .where(DocGeneration.node_id == node_id, DocGeneration.is_current_version == True)
        .values(is_current_version=False)
    )

    generation = DocGeneration(
        **data.model_dump(),
        node_id=node_id,
        project_id=node.project_id,
        created_by=current_user.id
    )
    db.add(generation)
    await db.commit()
    await db.refresh(generation)
    return generation


# ============ 大纲初始化 ============

@router.post("/projects/{project_id}/outline/initialize")
async def initialize_outline(
    project_id: uuid.UUID,
    force: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """初始化项目大纲（基于预设模板）"""
    # 检查是否已有大纲（不检查软删除的）
    existing = await db.execute(
        select(OutlineNode).where(
            OutlineNode.project_id == project_id,
            OutlineNode.deleted_at.is_(None)
        )
    )
    existing_node = existing.scalars().first()
    if existing_node and not force:
        return {"message": "项目已有大纲"}

    # 如果force为true，删除现有大纲（硬删除以避免唯一约束冲突）
    if force:
        from datetime import datetime
        # 先获取所有节点
        result = await db.execute(
            select(OutlineNode).where(OutlineNode.project_id == project_id)
        )
        nodes = result.scalars().all()
        node_ids = [node.id for node in nodes]

        # 先删除关联的doc_generations记录
        if node_ids:
            doc_gen_result = await db.execute(
                select(DocGeneration).where(DocGeneration.node_id.in_(node_ids))
            )
            doc_gens = doc_gen_result.scalars().all()
            for doc_gen in doc_gens:
                await db.delete(doc_gen)

            # 删除关联的node_references记录
            ref_result = await db.execute(
                select(NodeReference).where(NodeReference.node_id.in_(node_ids))
            )
            refs = ref_result.scalars().all()
            for ref in refs:
                await db.delete(ref)

        # 再删除大纲节点
        for node in nodes:
            await db.delete(node)
        await db.commit()

    # 完整的大纲结构（基于CLAUDE.md）- 核心章节
    chapters = [
        # 第一章 概述
        {"code": "1", "title": "概述", "children": [
            {"code": "1.1", "title": "项目概况", "children": [
                {"code": "1.1.1", "title": "项目名称"},
                {"code": "1.1.2", "title": "建设单位"},
                {"code": "1.1.3", "title": "建设目标和任务"},
                {"code": "1.1.4", "title": "建设地点"},
                {"code": "1.1.5", "title": "建设内容和规模"},
                {"code": "1.1.6", "title": "项目建设进度"},
                {"code": "1.1.7", "title": "投资规模及资金筹措"},
                {"code": "1.1.8", "title": "项目运行管理"}
            ]},
            {"code": "1.2", "title": "项目建设单位"},
            {"code": "1.3", "title": "编制依据"},
            {"code": "1.4", "title": "主要结论和建议"}
        ]},

        # 第二章 项目建设背景和必要性
        {"code": "2", "title": "项目建设背景和必要性", "children": [
            {"code": "2.1", "title": "项目建设背景", "children": [
                {"code": "2.1.1", "title": "项目提出背景", "children": [
                    {"code": "2.1.1.1", "title": "政策环境"},
                    {"code": "2.1.1.2", "title": "行业环境"}
                ]},
                {"code": "2.1.2", "title": "国内外现状和技术发展趋势", "children": [
                    {"code": "2.1.2.1", "title": "国内外现状", "children": [
                        {"code": "2.1.2.1.1", "title": "国外现状", "children": [
                            {"code": "2.1.2.1.1.1", "title": "底层基石：数据底座的战略化与标准化"},
                            {"code": "2.1.2.1.1.2", "title": "核心引擎：AI驱动的科研范式革命"},
                            {"code": "2.1.2.1.1.3", "title": "设计中枢：生成式生物设计与性状编程"},
                            {"code": "2.1.2.1.1.4", "title": "决策大脑：全链条智能导航与商业育种"},
                            {"code": "2.1.2.1.1.5", "title": "执行终端：具身智能与作业闭环"}
                        ]},
                        {"code": "2.1.2.1.2", "title": "国内现状", "children": [
                            {"code": "2.1.2.1.2.1", "title": "数据现状：海量积累下的资产荒"},
                            {"code": "2.1.2.1.2.2", "title": "算法与模型探索：从通用跟跑到垂域深耕"},
                            {"code": "2.1.2.1.2.3", "title": "系统形态：从点状工具向智能体跃迁"},
                            {"code": "2.1.2.1.2.4", "title": "核心短板：缺乏闭环进化的土壤"},
                            {"code": "2.1.2.1.2.5", "title": "总结与展望：迈向系统集成的深水区"}
                        ]}
                    ]},
                    {"code": "2.1.2.2", "title": "技术发展趋势", "children": [
                        {"code": "2.1.2.2.1", "title": "数据基础设施AI化"},
                        {"code": "2.1.2.2.2", "title": "科研与决策范式因果化"},
                        {"code": "2.1.2.2.3", "title": "生命设计生成化"},
                        {"code": "2.1.2.2.4", "title": "生产执行具身化"},
                        {"code": "2.1.2.2.5", "title": "智能生态协同化"}
                    ]},
                    {"code": "2.1.2.3", "title": "差距和不足", "children": [
                        {"code": "2.1.2.3.1", "title": "数据地基不实：标准化缺失与质量瓶颈"},
                        {"code": "2.1.2.3.2", "title": "算法能力局限：学科割裂与因果缺失"},
                        {"code": "2.1.2.3.3", "title": "物理验证缺失：设施短板与迭代断层"},
                        {"code": "2.1.2.3.4", "title": "生态协同断层：产业割裂与信息孤岛"}
                    ]}
                ]}
            ]},
            {"code": "2.2", "title": "规划政策符合性", "children": [
                {"code": "2.2.1", "title": "符合《十四五规划和2035年远景目标纲要》"},
                {"code": "2.2.2", "title": "符合习近平总书记4·13重要讲话精神"},
                {"code": "2.2.3", "title": "符合《加快建设农业强国规划》"},
                {"code": "2.2.4", "title": "符合《种业振兴行动方案》"},
                {"code": "2.2.5", "title": "符合《关于大力发展智慧农业的指导意见》"},
                {"code": "2.2.6", "title": "符合2025年中央一号文件"},
                {"code": "2.2.7", "title": "符合《海南自由贸易港建设总体方案》"},
                {"code": "2.2.8", "title": "符合《国家南繁硅谷建设规划》"}
            ]},
            {"code": "2.3", "title": "项目建设必要性", "children": [
                {"code": "2.3.1", "title": "是加快建设科技强国，提升育种技术国际竞争力的需要"},
                {"code": "2.3.2", "title": "是加速优质品种培育，保障国家粮食安全的需要"},
                {"code": "2.3.3", "title": "是助力海南向种图强，加快形成新质生产力的需要"},
                {"code": "2.3.4", "title": "是强化科研育种创新链条，加快南繁硅谷建设的需要"},
                {"code": "2.3.5", "title": "是完善实验室功能，更好发挥核心战略科技力量的需要"}
            ]}
        ]},

        # 第三章 项目需求分析与产出方案
        {"code": "3", "title": "项目需求分析与产出方案", "children": [
            {"code": "3.1", "title": "需求分析", "children": [
                {"code": "3.1.1", "title": "战略发展需求分析"},
                {"code": "3.1.2", "title": "系统建设需求分析", "children": [
                    {"code": "3.1.2.1", "title": "全链条标准化农业数据资源体系建设需求"},
                    {"code": "3.1.2.2", "title": "复杂性状形成机理推理智能引擎的建设需求"},
                    {"code": "3.1.2.3", "title": "全流程精准育种决策体系的建设需求"},
                    {"code": "3.1.2.4", "title": "工程化生物设计平台的建设需求"},
                    {"code": "3.1.2.5", "title": "农场无人化协同作业建设需求"}
                ]}
            ]},
            {"code": "3.2", "title": "项目建设目标"},
            {"code": "3.3", "title": "项目建设内容和规模", "children": [
                {"code": "3.3.1", "title": "面向生物育种的数据枢纽"},
                {"code": "3.3.2", "title": "面向复杂性状推理的AI科学家"},
                {"code": "3.3.3", "title": "面向智能决策的AI育种家"},
                {"code": "3.3.4", "title": "性状耦合与生物设计智能体系统"},
                {"code": "3.3.5", "title": "具身智能农场系统"}
            ]},
            {"code": "3.4", "title": "项目产出方案", "children": [
                {"code": "3.4.1", "title": "项目产出成果与指标"},
                {"code": "3.4.2", "title": "建设前后国内外水平对比"},
                {"code": "3.4.3", "title": "技术应用场景"}
            ]}
        ]},

        # 第四章 项目选址与要素保障
        {"code": "4", "title": "项目选址与要素保障", "children": [
            {"code": "4.1", "title": "项目选址", "children": [
                {"code": "4.1.1", "title": "数据枢纽"},
                {"code": "4.1.2", "title": "无人实验室"},
                {"code": "4.1.3", "title": "大田作物试验田"},
                {"code": "4.1.4", "title": "畜牧养殖基地"},
                {"code": "4.1.5", "title": "园艺食品经济作物"}
            ]},
            {"code": "4.2", "title": "项目建设条件", "children": [
                {"code": "4.2.1", "title": "技术条件基础"},
                {"code": "4.2.2", "title": "人才资源基础"},
                {"code": "4.2.3", "title": "产业生态基础"},
                {"code": "4.2.4", "title": "自然环境条件"},
                {"code": "4.2.5", "title": "交通运输条件"},
                {"code": "4.2.6", "title": "市政配套条件"}
            ]},
            {"code": "4.3", "title": "要素保障分析", "children": [
                {"code": "4.3.1", "title": "土地要素保障"},
                {"code": "4.3.2", "title": "环境要素保障"},
                {"code": "4.3.3", "title": "资源要素保障"}
            ]}
        ]},

        # 第五章 项目建设方案
        {"code": "5", "title": "项目建设方案", "children": [
            {"code": "5.1", "title": "建设方案概述"},
            {"code": "5.2", "title": "项目技术方案", "children": [
                {"code": "5.2.1", "title": "面向生物育种的数据枢纽", "children": [
                    {"code": "5.2.1.1", "title": "系统建设内容和建设目标"},
                    {"code": "5.2.1.2", "title": "系统技术来源与技术路线"},
                    {"code": "5.2.1.3", "title": "具体技术方案", "children": [
                        {"code": "5.2.1.3.1", "title": "单元一：农业全链条数据协同汇聚", "children": [
                            {"code": "5.2.1.3.1.1", "title": "单元建设内容和目标"},
                            {"code": "5.2.1.3.1.2", "title": "单元技术与功能指标"},
                            {"code": "5.2.1.3.1.3", "title": "各模块功能及技术方案"},
                            {"code": "5.2.1.3.1.4", "title": "接口开发及系统集成"}
                        ]},
                        {"code": "5.2.1.3.2", "title": "单元二：农业高质量数据标准体系构建单元", "children": [
                            {"code": "5.2.1.3.2.1", "title": "单元建设内容和目标"},
                            {"code": "5.2.1.3.2.2", "title": "单元技术与功能指标"},
                            {"code": "5.2.1.3.2.3", "title": "各模块功能及技术方案"},
                            {"code": "5.2.1.3.2.4", "title": "接口开发及系统集成"}
                        ]},
                        {"code": "5.2.1.3.3", "title": "单元三：农业AI中枢单元", "children": [
                            {"code": "5.2.1.3.3.1", "title": "单元建设内容和目标"},
                            {"code": "5.2.1.3.3.2", "title": "单元技术与功能指标"},
                            {"code": "5.2.1.3.3.3", "title": "各模块功能及技术方案"},
                            {"code": "5.2.1.3.3.4", "title": "接口开发及系统集成"}
                        ]}
                    ]}
                ]},
                {"code": "5.2.2", "title": "面向复杂性状推理的AI科学家", "children": [
                    {"code": "5.2.2.1", "title": "系统建设内容和建设目标"},
                    {"code": "5.2.2.2", "title": "技术来源与技术路线"},
                    {"code": "5.2.2.3", "title": "具体技术方案", "children": [
                        {"code": "5.2.2.3.1", "title": "单元一：农业多模态语料库", "children": [
                            {"code": "5.2.2.3.1.1", "title": "单元建设内容和目标"},
                            {"code": "5.2.2.3.1.2", "title": "单元技术与功能指标"},
                            {"code": "5.2.2.3.1.3", "title": "各模块功能及技术方案"},
                            {"code": "5.2.2.3.1.4", "title": "接口开发及系统集成"}
                        ]},
                        {"code": "5.2.2.3.2", "title": "单元二：农业领域AI科学家模型体系", "children": [
                            {"code": "5.2.2.3.2.1", "title": "单元建设内容和目标"},
                            {"code": "5.2.2.3.2.2", "title": "单元技术与功能指标"},
                            {"code": "5.2.2.3.2.3", "title": "各模块功能及技术方案"},
                            {"code": "5.2.2.3.2.4", "title": "接口开发及系统集成"}
                        ]},
                        {"code": "5.2.2.3.3", "title": "单元三：复杂性状知识库", "children": [
                            {"code": "5.2.2.3.3.1", "title": "单元建设内容和目标"},
                            {"code": "5.2.2.3.3.2", "title": "单元技术与功能指标"},
                            {"code": "5.2.2.3.3.3", "title": "各模块功能及技术方案"},
                            {"code": "5.2.2.3.3.4", "title": "接口开发及系统集成"}
                        ]}
                    ]}
                ]},
                {"code": "5.2.3", "title": "面向智能决策的AI育种家", "children": [
                    {"code": "5.2.3.1", "title": "系统建设内容和建设目标"},
                    {"code": "5.2.3.2", "title": "技术来源与技术路线"},
                    {"code": "5.2.3.3", "title": "具体技术方案", "children": [
                        {"code": "5.2.3.3.1", "title": "单元一：跨生态区作物品种演单元", "children": [
                            {"code": "5.2.3.3.1.1", "title": "单元建设内容和目标"},
                            {"code": "5.2.3.3.1.2", "title": "单元技术与功能指标"},
                            {"code": "5.2.3.3.1.3", "title": "各模块功能及技术方案"},
                            {"code": "5.2.3.3.1.4", "title": "接口开发及系统集成"}
                        ]},
                        {"code": "5.2.3.3.2", "title": "单元二：育种路径初始规划及锁定单元", "children": [
                            {"code": "5.2.3.3.2.1", "title": "单元建设内容和目标"},
                            {"code": "5.2.3.3.2.2", "title": "单元技术与功能指标"},
                            {"code": "5.2.3.3.2.3", "title": "各模块功能及技术方案"},
                            {"code": "5.2.3.3.2.4", "title": "接口开发及系统集成"}
                        ]},
                        {"code": "5.2.3.3.3", "title": "单元三：育种路径动态调整单元", "children": [
                            {"code": "5.2.3.3.3.1", "title": "单元建设内容和目标"},
                            {"code": "5.2.3.3.3.2", "title": "单元技术与功能指标"},
                            {"code": "5.2.3.3.3.3", "title": "各模块功能及技术方案"},
                            {"code": "5.2.3.3.3.4", "title": "接口开发及系统集成"}
                        ]},
                        {"code": "5.2.3.3.4", "title": "单元四：育种完成与优化反馈单元", "children": [
                            {"code": "5.2.3.3.4.1", "title": "单元建设内容和目标"},
                            {"code": "5.2.3.3.4.2", "title": "单元技术与功能指标"},
                            {"code": "5.2.3.3.4.3", "title": "各模块功能及技术方案"},
                            {"code": "5.2.3.3.4.4", "title": "接口开发及系统集成"}
                        ]}
                    ]}
                ]},
                {"code": "5.2.4", "title": "性状耦合与生物设计智能体系统", "children": [
                    {"code": "5.2.4.1", "title": "系统建设内容和建设目标"},
                    {"code": "5.2.4.2", "title": "技术来源与技术路线"},
                    {"code": "5.2.4.3", "title": "具体技术方案", "children": [
                        {"code": "5.2.4.3.1", "title": "单元一：基因操作工具创制单元", "children": [
                            {"code": "5.2.4.3.1.1", "title": "单元建设内容和目标"},
                            {"code": "5.2.4.3.1.2", "title": "单元技术与功能指标"},
                            {"code": "5.2.4.3.1.3", "title": "各模块功能及技术方案"},
                            {"code": "5.2.4.3.1.4", "title": "接口开发及系统集成"}
                        ]},
                        {"code": "5.2.4.3.2", "title": "单元二：复杂优良性状模块构建单元", "children": [
                            {"code": "5.2.4.3.2.1", "title": "单元建设内容和目标"},
                            {"code": "5.2.4.3.2.2", "title": "单元技术与功能指标"},
                            {"code": "5.2.4.3.2.3", "title": "各模块功能及技术方案"},
                            {"code": "5.2.4.3.2.4", "title": "接口开发及系统集成"}
                        ]},
                        {"code": "5.2.4.3.3", "title": "单元三：多维性状耦合与路径优化单元", "children": [
                            {"code": "5.2.4.3.3.1", "title": "单元建设内容和目标"},
                            {"code": "5.2.4.3.3.2", "title": "单元技术与功能指标"},
                            {"code": "5.2.4.3.3.3", "title": "各模块功能及技术方案"},
                            {"code": "5.2.4.3.3.4", "title": "接口开发及系统集成"}
                        ]},
                        {"code": "5.2.4.3.4", "title": "单元四：生物体系统重构与编译单元", "children": [
                            {"code": "5.2.4.3.4.1", "title": "单元建设内容和目标"},
                            {"code": "5.2.4.3.4.2", "title": "单元技术与功能指标"},
                            {"code": "5.2.4.3.4.3", "title": "各模块功能及技术方案"},
                            {"code": "5.2.4.3.4.4", "title": "接口开发及系统集成"}
                        ]},
                        {"code": "5.2.4.3.5", "title": "系统接口开发与系统集成"}
                    ]}
                ]},
                {"code": "5.2.5", "title": "具身智能农场系统", "children": [
                    {"code": "5.2.5.1", "title": "系统建设内容和建设目标"},
                    {"code": "5.2.5.2", "title": "系统技术来源与技术路线"},
                    {"code": "5.2.5.3", "title": "具体技术方案", "children": [
                        {"code": "5.2.5.3.1", "title": "单元一：农场智能规划", "children": [
                            {"code": "5.2.5.3.1.1", "title": "单元建设内容和目标"},
                            {"code": "5.2.5.3.1.2", "title": "单元技术与功能指标"},
                            {"code": "5.2.5.3.1.3", "title": "各模块功能及技术方案"},
                            {"code": "5.2.5.3.1.4", "title": "接口开发及系统集成"}
                        ]},
                        {"code": "5.2.5.3.2", "title": "单元二：生产智能决策", "children": [
                            {"code": "5.2.5.3.2.1", "title": "单元建设内容和目标"},
                            {"code": "5.2.5.3.2.2", "title": "单元技术与功能指标"},
                            {"code": "5.2.5.3.2.3", "title": "各模块功能及技术方案"},
                            {"code": "5.2.5.3.2.4", "title": "接口开发及系统集成"}
                        ]},
                        {"code": "5.2.5.3.3", "title": "单元三：具身智能执行", "children": [
                            {"code": "5.2.5.3.3.1", "title": "单元建设内容和目标"},
                            {"code": "5.2.5.3.3.2", "title": "单元技术与功能指标"},
                            {"code": "5.2.5.3.3.3", "title": "各模块功能及技术方案"},
                            {"code": "5.2.5.3.3.4", "title": "接口开发及系统集成"}
                        ]},
                        {"code": "5.2.5.3.4", "title": "单元四：绩效智能评价", "children": [
                            {"code": "5.2.5.3.4.1", "title": "单元建设内容和目标"},
                            {"code": "5.2.5.3.4.2", "title": "单元技术与功能指标"},
                            {"code": "5.2.5.3.4.3", "title": "各模块功能及技术方案"},
                            {"code": "5.2.5.3.4.4", "title": "接口开发及系统集成"}
                        ]}
                    ]}
                ]}
            ]},
            {"code": "5.3", "title": "设备方案", "children": [
                {"code": "5.3.1", "title": "面向生物育种的数据枢纽", "children": [
                    {"code": "5.3.1.1", "title": "硬件设备", "children": [
                        {"code": "5.3.1.1.1", "title": "设备购置方案"},
                        {"code": "5.3.1.1.2", "title": "设备购置必要性与匹配性"},
                        {"code": "5.3.1.1.3", "title": "关键设备说明"},
                        {"code": "5.3.1.1.4", "title": "硬件设备清单"}
                    ]},
                    {"code": "5.3.1.2", "title": "成品软件", "children": [
                        {"code": "5.3.1.2.1", "title": "软件购置方案"},
                        {"code": "5.3.1.2.2", "title": "软件购置必要性与匹配性"},
                        {"code": "5.3.1.2.3", "title": "关键软件说明"},
                        {"code": "5.3.1.2.4", "title": "软件购置清单"}
                    ]},
                    {"code": "5.3.1.3", "title": "定制软件开发", "children": [
                        {"code": "5.3.1.3.1", "title": "定制软件开发方案"},
                        {"code": "5.3.1.3.2", "title": "定制软件开发清单"}
                    ]}
                ]},
                {"code": "5.3.2", "title": "面向复杂性状推理的AI科学家", "children": [
                    {"code": "5.3.2.1", "title": "硬件设备"},
                    {"code": "5.3.2.2", "title": "成品软件"},
                    {"code": "5.3.2.3", "title": "定制软件开发"}
                ]},
                {"code": "5.3.3", "title": "面向智能决策的AI育种家", "children": [
                    {"code": "5.3.3.1", "title": "硬件设备", "children": [
                        {"code": "5.3.3.1.1", "title": "设备购置方案"},
                        {"code": "5.3.3.1.2", "title": "设备购置必要性与匹配性"},
                        {"code": "5.3.3.1.3", "title": "关键设备说明"},
                        {"code": "5.3.3.1.4", "title": "硬件设备清单"}
                    ]},
                    {"code": "5.3.3.2", "title": "成品软件", "children": [
                        {"code": "5.3.3.2.1", "title": "软件购置方案"},
                        {"code": "5.3.3.2.2", "title": "软件购置必要性与匹配性"},
                        {"code": "5.3.3.2.3", "title": "关键软件说明"},
                        {"code": "5.3.3.2.4", "title": "软件购置清单"}
                    ]},
                    {"code": "5.3.3.3", "title": "定制软件开发", "children": [
                        {"code": "5.3.3.3.1", "title": "定制软件开发方案"},
                        {"code": "5.3.3.3.2", "title": "定制软件开发清单"}
                    ]}
                ]},
                {"code": "5.3.4", "title": "性状耦合与生物设计智能体系统", "children": [
                    {"code": "5.3.4.1", "title": "硬件设备", "children": [
                        {"code": "5.3.4.1.1", "title": "设备购置方案"},
                        {"code": "5.3.4.1.2", "title": "设备购置必要性与匹配性"},
                        {"code": "5.3.4.1.3", "title": "关键设备说明"},
                        {"code": "5.3.4.1.4", "title": "硬件设备清单"}
                    ]},
                    {"code": "5.3.4.2", "title": "成品软件", "children": [
                        {"code": "5.3.4.2.1", "title": "软件购置方案"},
                        {"code": "5.3.4.2.2", "title": "软件购置必要性与匹配性"},
                        {"code": "5.3.4.2.3", "title": "关键软件说明"},
                        {"code": "5.3.4.2.4", "title": "软件购置清单"}
                    ]},
                    {"code": "5.3.4.3", "title": "定制软件开发", "children": [
                        {"code": "5.3.4.3.1", "title": "定制软件开发方案"},
                        {"code": "5.3.4.3.2", "title": "定制软件开发清单"}
                    ]}
                ]},
                {"code": "5.3.5", "title": "具身智能农场系统", "children": [
                    {"code": "5.3.5.1", "title": "硬件设备", "children": [
                        {"code": "5.3.5.1.1", "title": "设备购置方案"},
                        {"code": "5.3.5.1.2", "title": "设备购置必要性与匹配性"},
                        {"code": "5.3.5.1.3", "title": "关键设备说明"},
                        {"code": "5.3.5.1.4", "title": "硬件设备清单"}
                    ]},
                    {"code": "5.3.5.2", "title": "成品软件", "children": [
                        {"code": "5.3.5.2.1", "title": "软件购置方案"},
                        {"code": "5.3.5.2.2", "title": "软件购置必要性与匹配性"},
                        {"code": "5.3.5.2.3", "title": "关键软件说明"},
                        {"code": "5.3.5.2.4", "title": "软件购置清单"}
                    ]},
                    {"code": "5.3.5.3", "title": "定制软件开发", "children": [
                        {"code": "5.3.5.3.1", "title": "定制软件开发方案"},
                        {"code": "5.3.5.3.2", "title": "定制软件开发清单"}
                    ]}
                ]}
            ]},
            {"code": "5.4", "title": "租赁方案", "children": [
                {"code": "5.4.1", "title": "面向生物育种的数据枢纽", "children": [
                    {"code": "5.4.1.1", "title": "算力租赁方案"},
                    {"code": "5.4.1.2", "title": "云资源租赁方案"},
                    {"code": "5.4.1.3", "title": "网络租赁方案"}
                ]},
                {"code": "5.4.2", "title": "面向复杂性状推理的AI科学家", "children": [
                    {"code": "5.4.2.1", "title": "算力租赁方案"},
                    {"code": "5.4.2.2", "title": "云资源租赁方案"},
                    {"code": "5.4.2.3", "title": "网络租赁方案"}
                ]},
                {"code": "5.4.3", "title": "面向智能决策的AI育种家"},
                {"code": "5.4.4", "title": "性状耦合与生物设计智能体系统", "children": [
                    {"code": "5.4.4.1", "title": "算力租赁方案"},
                    {"code": "5.4.4.2", "title": "云资源租赁方案"},
                    {"code": "5.4.4.3", "title": "网络租赁方案"}
                ]},
                {"code": "5.4.5", "title": "具身智能农场系统", "children": [
                    {"code": "5.4.5.1", "title": "算力租赁方案"},
                    {"code": "5.4.5.2", "title": "云资源租赁方案"},
                    {"code": "5.4.5.3", "title": "网络租赁方案"}
                ]}
            ]},
            {"code": "5.5", "title": "数据资源建设方案", "children": [
                {"code": "5.5.1", "title": "面向生物育种的数据枢纽"},
                {"code": "5.5.2", "title": "面向复杂性状推理的AI科学家"},
                {"code": "5.5.3", "title": "面向智能决策的AI育种家"},
                {"code": "5.5.4", "title": "性状耦合与生物设计智能体系统"},
                {"code": "5.5.5", "title": "具身智能农场系统"}
            ]},
            {"code": "5.6", "title": "人力资源配置方案", "children": [
                {"code": "5.6.1", "title": "面向生物育种的数据枢纽"},
                {"code": "5.6.2", "title": "面向复杂性状推理的AI科学家"},
                {"code": "5.6.3", "title": "面向智能决策的AI育种家"},
                {"code": "5.6.4", "title": "性状耦合与生物设计智能体系统"},
                {"code": "5.6.5", "title": "具身智能农场系统"}
            ]},
            {"code": "5.7", "title": "建设管理方案", "children": [
                {"code": "5.7.1", "title": "建设管理方式"},
                {"code": "5.7.2", "title": "建设进度计划"},
                {"code": "5.7.3", "title": "项目招标方案"}
            ]}
        ]},

        # 第六章 项目运营方案
        {"code": "6", "title": "项目运营方案", "children": [
            {"code": "6.1", "title": "运营模式选择"},
            {"code": "6.2", "title": "运营组织方案"},
            {"code": "6.3", "title": "运营原则", "children": [
                {"code": "6.3.1", "title": "组织架构与职责"},
                {"code": "6.3.2", "title": "运营管理"},
                {"code": "6.3.3", "title": "科研管理"},
                {"code": "6.3.4", "title": "人员管理"},
                {"code": "6.3.5", "title": "经费管理"},
                {"code": "6.3.6", "title": "成果管理"}
            ]},
            {"code": "6.4", "title": "安全保障方案", "children": [
                {"code": "6.4.1", "title": "基本原则"},
                {"code": "6.4.2", "title": "组织机构及职责"},
                {"code": "6.4.3", "title": "安全管理主要内容"}
            ]},
            {"code": "6.5", "title": "项目运行经费"},
            {"code": "6.6", "title": "绩效管理方案", "children": [
                {"code": "6.6.1", "title": "编制依据"},
                {"code": "6.6.2", "title": "绩效评价指标"},
                {"code": "6.6.3", "title": "绩效计划制定与执行"}
            ]}
        ]},

        # 第七章 项目投融资与财务方案
        {"code": "7", "title": "项目投融资与财务方案", "children": [
            {"code": "7.1", "title": "投资估算", "children": [
                {"code": "7.1.1", "title": "估算依据"},
                {"code": "7.1.2", "title": "估算范围"},
                {"code": "7.1.3", "title": "总投资估算"},
                {"code": "7.1.4", "title": "分年投资计划"}
            ]},
            {"code": "7.2", "title": "盈利能力分析"},
            {"code": "7.3", "title": "融资方案"},
            {"code": "7.4", "title": "债务清偿能力分析"},
            {"code": "7.5", "title": "财务可持续性分析"}
        ]},

        # 第八章 项目影响效果分析
        {"code": "8", "title": "项目影响效果分析", "children": [
            {"code": "8.1", "title": "科学效益分析"},
            {"code": "8.2", "title": "经济效益分析"},
            {"code": "8.3", "title": "社会效益分析"},
            {"code": "8.4", "title": "生态环境影响分析"},
            {"code": "8.5", "title": "资源和能源利用效果分析"},
            {"code": "8.6", "title": "碳达峰、碳中和分析"}
        ]},

        # 第九章 项目风险管控方案
        {"code": "9", "title": "项目风险管控方案", "children": [
            {"code": "9.1", "title": "风险识别与评价", "children": [
                {"code": "9.1.1", "title": "系统开发风险"},
                {"code": "9.1.2", "title": "系统运行风险"},
                {"code": "9.1.3", "title": "数据安全风险"},
                {"code": "9.1.4", "title": "网络安全风险"},
                {"code": "9.1.5", "title": "设备采购风险"}
            ]},
            {"code": "9.2", "title": "风险管控方案", "children": [
                {"code": "9.2.1", "title": "系统开发风险管控方案"},
                {"code": "9.2.2", "title": "系统运行风险管控方案"},
                {"code": "9.2.3", "title": "数据安全风险管控方案"},
                {"code": "9.2.4", "title": "网络安全风险管控方案"},
                {"code": "9.2.5", "title": "设备采购风险管控方案"}
            ]},
            {"code": "9.3", "title": "风险应急预案", "children": [
                {"code": "9.3.1", "title": "组织机构与职责"},
                {"code": "9.3.2", "title": "预警信息与分级"}
            ]},
            {"code": "9.4", "title": "应急处置流程"}
        ]},

        # 第十章 研究结论及建议
        {"code": "10", "title": "研究结论及建议", "children": [
            {"code": "10.1", "title": "主要研究结论"},
            {"code": "10.2", "title": "相关建议"}
        ]}
    ]

    async def create_nodes(parent_id, nodes, level):
        for node_data in nodes:
            children = node_data.pop('children', None)
            is_leaf = children is None or len(children) == 0

            node = OutlineNode(
                project_id=project_id,
                parent_id=parent_id,
                node_code=node_data['code'],
                node_title=node_data['title'],
                node_level=level,
                is_leaf=is_leaf
            )
            db.add(node)
            await db.flush()

            if children:
                await create_nodes(node.id, children, level + 1)

    await create_nodes(None, chapters, 1)
    await db.commit()

    return {"message": "大纲初始化完成"}


@router.delete("/projects/{project_id}/outline")
async def delete_outline(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """删除项目大纲（重新初始化）"""
    from datetime import datetime
    result = await db.execute(
        select(OutlineNode).where(OutlineNode.project_id == project_id)
    )
    nodes = result.scalars().all()
    for node in nodes:
        node.deleted_at = datetime.utcnow()
    await db.commit()
    return {"message": "大纲已删除"}


# ============ Word 导出 ============

from fastapi.responses import StreamingResponse
from app.utils.doc_exporter import export_outline_to_doc


@router.get("/projects/{project_id}/export-word")
async def export_word(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """导出项目大纲为 Word 文档"""
    # 获取项目所有大纲节点（扁平化）
    result = await db.execute(
        select(OutlineNode)
        .where(
            OutlineNode.project_id == project_id,
            OutlineNode.deleted_at.is_(None)
        )
    )
    all_nodes = result.scalars().all()

    if not all_nodes:
        raise HTTPException(status_code=404, detail="项目没有大纲数据")

    # 构建节点映射（使用字符串作为key）
    node_map = {str(node.id): {
        'id': str(node.id),
        'project_id': str(node.project_id),
        'parent_id': str(node.parent_id) if node.parent_id else None,
        'node_code': node.node_code,
        'node_title': node.node_title,
        'node_level': node.node_level,
        'content': node.content or '',
        'children': []
    } for node in all_nodes}

    # 构建树结构
    root_nodes = []
    for node_id, node_data in node_map.items():
        parent_id = node_data['parent_id']
        if parent_id and parent_id in node_map:
            node_map[parent_id]['children'].append(node_data)
        elif parent_id is None:
            root_nodes.append(node_data)

    # 排序子节点
    def sort_children(nodes: list):
        nodes.sort(key=lambda n: sort_key(n['node_code']))
        for node in nodes:
            if node['children']:
                sort_children(node['children'])

    sort_children(root_nodes)

    # 生成 Word 文档
    doc_bytes = export_outline_to_doc(root_nodes)

    # 使用 ASCII 文件名避免编码问题
    filename = "project_outline.docx"

    return StreamingResponse(
        io.BytesIO(doc_bytes),
        media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        headers={
            'Content-Disposition': f'attachment; filename="{filename}"'
        }
    )


# 修复导入
from sqlalchemy import update
import io
