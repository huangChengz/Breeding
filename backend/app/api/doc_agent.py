import uuid
import json
import time
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
import asyncio

from app.core.database import get_db
from app.api.auth import get_current_user
from app.schemas.user import CurrentUser
from app.models.outline import OutlineNode, NodeReference, DocGeneration
from app.models.data_collection import Scene, Equipment, Dataset, AIModel, RDProject
from app.services.doc_agent import doc_agent_service

router = APIRouter()


@router.get("/outline/{node_id}/generate-stream")
async def generate_content_stream(
    node_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """流式生成内容 (SSE)"""

    # 1. 获取节点
    result = await db.execute(select(OutlineNode).where(OutlineNode.id == node_id))
    node = result.scalar_one_or_none()
    if not node:
        raise HTTPException(status_code=404, detail="节点不存在")

    # 允许任意节点生成内容（不再限制 is_leaf）

    # 2. 获取引用
    ref_result = await db.execute(
        select(NodeReference).where(
            NodeReference.node_id == node_id,
            NodeReference.is_active == True
        )
    )
    references = ref_result.scalars().all()

    # 3. 获取当前项目的项目ID
    project_id = node.project_id

    # 4. 将旧版本标记为非当前
    await db.execute(
        text(f"UPDATE doc_generations SET is_current_version = FALSE WHERE node_id = '{node_id}' AND is_current_version = TRUE")
    )

    # 5. 流式生成
    async def generate():
        full_content = ""

        try:
            async for chunk in doc_agent_service.generate_content(
                db=db,
                node=node,
                references=references,
                streaming=True
            ):
                full_content += chunk
                # 发送 SSE 格式
                data = json.dumps({"content": chunk}, ensure_ascii=False)
                yield f"data: {data}\n\n"

            # 生成完成，保存记录
            generation = DocGeneration(
                id=uuid.uuid4(),
                project_id=project_id,
                node_id=node_id,
                generation_content=full_content,
                generation_source='ai',
                is_current_version=True,
                created_by=current_user.id,
                model_used="qwen-turbo"
            )
            db.add(generation)
            await db.commit()

            # 发送完成信号
            yield f"data: {json.dumps({'done': True})}\n\n"

        except Exception as e:
            error_data = json.dumps({"error": str(e)}, ensure_ascii=False)
            yield f"data: {error_data}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.post("/outline/{node_id}/generate")
async def generate_content_async(
    node_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """异步生成内容（非流式）"""

    # 获取节点
    result = await db.execute(select(OutlineNode).where(OutlineNode.id == node_id))
    node = result.scalar_one_or_none()
    if not node:
        raise HTTPException(status_code=404, detail="节点不存在")

    # 允许任意节点生成内容（不再限制 is_leaf）

    # 获取引用
    ref_result = await db.execute(
        select(NodeReference).where(
            NodeReference.node_id == node_id,
            NodeReference.is_active == True
        )
    )
    references = ref_result.scalars().all()

    # 获取项目ID
    project_id = node.project_id

    # 生成内容
    full_content = ""
    async for chunk in doc_agent_service.generate_content(
        db=db,
        node=node,
        references=references,
        streaming=True
    ):
        full_content += chunk

    # 保存生成记录
    generation = DocGeneration(
        id=uuid.uuid4(),
        project_id=project_id,
        node_id=node_id,
        generation_content=full_content,
        generation_source='ai',
        is_current_version=True,
        created_by=current_user.id,
        model_used="qwen-turbo"
    )
    db.add(generation)

    # 更新节点内容
    node.content = full_content

    await db.commit()

    return {
        "content": full_content,
        "node_id": str(node_id),
        "generation_id": str(generation.id)
    }


# ============ Prompt 模板管理 ============

@router.get("/prompt-templates")
async def list_prompt_templates(
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """获取 Prompt 模板列表"""
    from app.models.outline import PromptTemplate
    result = await db.execute(
        select(PromptTemplate).where(PromptTemplate.is_active == True)
    )
    templates = result.scalars().all()
    return [
        {
            "id": str(t.id),
            "template_code": t.template_code,
            "template_name": t.template_name,
            "template_category": t.template_category,
            "description": t.description,
            "version": t.version
        }
        for t in templates
    ]


@router.post("/prompt-templates")
async def create_prompt_template(
    template_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """创建 Prompt 模板"""
    from app.models.outline import PromptTemplate

    template = PromptTemplate(
        id=uuid.uuid4(),
        template_code=template_data["template_code"],
        template_name=template_data["template_name"],
        template_category=template_data.get("template_category"),
        template_content=template_data["template_content"],
        variables=template_data.get("variables"),
        description=template_data.get("description"),
        version=template_data.get("version", "1.0")
    )
    db.add(template)
    await db.commit()
    return {"id": str(template.id)}
