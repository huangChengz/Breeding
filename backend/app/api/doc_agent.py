import uuid
import json
import time
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
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


# ============ 内容优化 ============

class OptimizeRequest(BaseModel):
    content: str
    optimize_type: str = "polish"


@router.post("/outline/{node_id}/optimize")
async def optimize_content(
    node_id: uuid.UUID,
    request: OptimizeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """内容优化/润色

    optimize_type: polish(润色), expand(扩展), shorten(精简), formal(正式)
    """
    import logging
    logger = logging.getLogger(__name__)

    from app.services.llm import qwen_service

    content = request.content
    optimize_type = request.optimize_type

    logger.info(f"[Optimize] node_id={node_id}, optimize_type={optimize_type}, content_length={len(content)}")

    # 获取节点信息
    result = await db.execute(select(OutlineNode).where(OutlineNode.id == node_id))
    node = result.scalar_one_or_none()
    if not node:
        raise HTTPException(status_code=404, detail="节点不存在")

    # 构建优化提示词
    optimize_prompts = {
        "polish": f"请对以下内容进行润色，使语言更加流畅、专业：\n\n{content}",
        "expand": f"请对以下内容进行扩展，增加更多细节和说明：\n\n{content}",
        "shorten": f"请对以下内容进行精简，去除冗余内容，保留核心信息：\n\n{content}",
        "formal": f"请将以下内容改写为更正式、专业的学术风格：\n\n{content}"
    }

    system_prompt = "你是一个专业的申报书文档编辑助手，擅长优化和润色科研项目申报文档。"

    # 调用 LLM 进行优化
    try:
        logger.info(f"[Optimize] Calling LLM with type: {optimize_type}")
        response = await qwen_service.generate_complete(
            prompt=optimize_prompts.get(optimize_type, optimize_prompts["polish"]),
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=4000
        )
        logger.info(f"[Optimize] LLM response: {response}")
        optimized_content = response.get("content", "")
    except Exception as e:
        logger.error(f"[Optimize] LLM error: {str(e)}")
        raise

    # 保存优化后的版本
    project_id = node.project_id

    # 将旧版本标记为非当前
    await db.execute(
        text(f"UPDATE doc_generations SET is_current_version = FALSE WHERE node_id = '{node_id}' AND is_current_version = TRUE")
    )

    # 创建新版本
    generation = DocGeneration(
        id=uuid.uuid4(),
        project_id=project_id,
        node_id=node_id,
        generation_content=optimized_content,
        generation_source='ai_optimize',
        is_current_version=True,
        created_by=current_user.id,
        model_used="qwen-turbo"
    )
    db.add(generation)

    # 更新节点内容
    node.content = optimized_content
    await db.commit()

    return {
        "content": optimized_content,
        "node_id": str(node_id),
        "generation_id": str(generation.id),
        "optimize_type": optimize_type
    }


@router.post("/outline/{node_id}/generations/{generation_id}/set-current")
async def set_current_version(
    node_id: uuid.UUID,
    generation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """设置指定版本为当前版本"""

    # 检查生成记录是否存在
    result = await db.execute(
        select(DocGeneration).where(
            DocGeneration.id == generation_id,
            DocGeneration.node_id == node_id
        )
    )
    generation = result.scalar_one_or_none()
    if not generation:
        raise HTTPException(status_code=404, detail="生成记录不存在")

    # 将所有版本设为非当前
    await db.execute(
        text(f"UPDATE doc_generations SET is_current_version = FALSE WHERE node_id = '{node_id}'")
    )

    # 将指定版本设为当前
    generation.is_current_version = True
    await db.commit()

    # 更新节点内容
    node_result = await db.execute(select(OutlineNode).where(OutlineNode.id == node_id))
    node = node_result.scalar_one()
    node.content = generation.generation_content
    await db.commit()

    return {
        "success": True,
        "generation_id": str(generation_id),
        "content": generation.generation_content
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
