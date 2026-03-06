import json
from typing import AsyncGenerator, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.outline import OutlineNode, NodeReference, PromptTemplate, ReferenceType
from app.models.data_collection import Scene, Equipment, Dataset, AIModel, RDProject
from app.services.llm import qwen_service


class DocAgentService:
    """DocAgent 服务 - 负责组装 Prompt 和调用 LLM"""

    SYSTEM_PROMPT = """你是一位专业的项目申报书写作专家，擅长撰写农业育种领域的项目申报书。你需要根据提供的大纲节点信息、场景数据、设备信息等，生成高质量、专业的申报书内容。

要求：
1. 内容专业、准确，符合项目申报书的写作规范
2. 充分利用提供的引用数据，使内容具体、详实
3. 语言规范、逻辑清晰、层次分明
4. 适当引用数据增强说服力
5. 遵循中国官方文件写作风格"""

    async def build_prompt(
        self,
        db: AsyncSession,
        node: OutlineNode,
        references: list
    ) -> tuple[str, dict]:
        """构建 Prompt"""

        # 1. 当前节点信息
        node_info = {
            "node_code": node.node_code,
            "node_title": node.node_title,
            "node_level": node.node_level,
            "existing_content": node.content or ""
        }

        # 2. 引用数据
        ref_data = await self._load_reference_data(db, references)

        # 3. 构建 Prompt
        prompt = f"""## 任务
请根据以下信息，为大纲节点「{node.node_code} {node.node_title}」生成内容。

## 大纲节点信息
{json.dumps(node_info, ensure_ascii=False, indent=2)}

## 引用数据
{ref_data}

## 要求
1. 生成的内容应与节点标题紧密相关
2. 充分利用提供的引用数据，使内容具体、可信
3. 内容长度适中，详略得当
4. 如果已有部分内容，请在原有基础上完善和扩展

请直接输出生成的内容，不需要其他说明。"""

        return prompt, {"node_info": node_info, "references": list(ref_data.keys())}

    async def _load_reference_data(
        self,
        db: AsyncSession,
        references: list
    ) -> dict:
        """加载引用实体的详细数据"""

        ref_data = {}

        for ref in references:
            entity_type = ref.ref_entity_type
            entity_id = ref.ref_entity_id

            if entity_type == "scene":
                result = await db.execute(select(Scene).where(Scene.id == entity_id))
                scene = result.scalar_one_or_none()
                if scene:
                    ref_data[f"场景: {scene.scene_name}"] = {
                        "description": scene.scene_description,
                        "research_output_type": scene.research_output_type,
                        "data_output_type": scene.data_output_type,
                        "data_total_tb": float(scene.data_total_tb) if scene.data_total_tb else 0
                    }

            elif entity_type == "equipment":
                result = await db.execute(select(Equipment).where(Equipment.id == entity_id))
                eq = result.scalar_one_or_none()
                if eq:
                    ref_data[f"设备: {eq.equipment_name}"] = {
                        "equipment_type": eq.equipment_type,
                        "total_price": float(eq.total_price) if eq.total_price else 0,
                        "supplier": eq.supplier,
                        "necessity": eq.necessity_description
                    }

            elif entity_type == "dataset":
                result = await db.execute(select(Dataset).where(Dataset.id == entity_id))
                ds = result.scalar_one_or_none()
                if ds:
                    ref_data[f"数据: {ds.data_name}"] = {
                        "data_type": ds.data_type,
                        "data_total_tb": float(ds.data_total_tb) if ds.data_total_tb else 0,
                        "processing_fee": float(ds.processing_fee) if ds.processing_fee else 0
                    }

            elif entity_type == "ai_model":
                result = await db.execute(select(AIModel).where(AIModel.id == entity_id))
                model = result.scalar_one_or_none()
                if model:
                    ref_data[f"AI模型: {model.model_name}"] = {
                        "model_type": model.model_type,
                        "parameter_count": model.parameter_count,
                        "function_type": model.function_type,
                        "estimated_fee": float(model.estimated_total_fee) if model.estimated_total_fee else 0
                    }

            elif entity_type == "rd_project":
                result = await db.execute(select(RDProject).where(RDProject.id == entity_id))
                rd = result.scalar_one_or_none()
                if rd:
                    ref_data[f"研发项目: {rd.rd_name}"] = {
                        "direction": rd.rd_direction,
                        "content": rd.rd_content,
                        "expected_output": rd.expected_output,
                        "estimated_fee": float(rd.estimated_fee) if rd.estimated_fee else 0
                    }

        return ref_data

    async def generate_content(
        self,
        db: AsyncSession,
        node: OutlineNode,
        references: list,
        streaming: bool = True
    ) -> AsyncGenerator[str, None]:
        """生成内容（流式）"""

        try:
            prompt, context = await self.build_prompt(db, node, references)

            if streaming:
                async for chunk in qwen_service.generate(
                    prompt=prompt,
                    system_prompt=self.SYSTEM_PROMPT,
                    temperature=0.7,
                    max_tokens=4000
                ):
                    yield chunk
            else:
                result = await qwen_service.generate_complete(
                    prompt=prompt,
                    system_prompt=self.SYSTEM_PROMPT,
                    temperature=0.7,
                    max_tokens=4000
                )
                yield result["content"]
        except Exception as e:
            import traceback
            error_msg = f"生成内容时出错: {str(e)}"
            print(f"Error in generate_content: {error_msg}")
            print(traceback.format_exc())
            raise


# 单例
doc_agent_service = DocAgentService()
