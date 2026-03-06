import asyncio
import json
import time
from typing import AsyncGenerator, Optional
import httpx
from app.core.config import settings


class QwenService:
    """通义千问服务"""

    def __init__(self):
        self.api_key = settings.DASHSCOPE_API_KEY
        self.model = settings.QWEN_MODEL
        self.base_url = "https://dashscope.aliyuncs.com/api/v1"

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000
    ) -> AsyncGenerator[str, None]:
        """流式生成文本"""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        messages = []
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        messages.append({
            "role": "user",
            "content": prompt
        })

        payload = {
            "model": self.model,
            "input": {"messages": messages},
            "parameters": {
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": True,
                "incremental_output": True
            }
        }

        print(f"[LLM] Calling API with model: {self.model}")

        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/services/aigc/text-generation/generation",
                headers=headers,
                json=payload
            ) as response:
                if response.status_code != 200:
                    error_body = await response.aread()
                    raise Exception(f"API Error: {response.status_code} - {error_body.decode()}")

                async for line in response.aiter_lines():
                    print(f"[LLM] Received line: {line[:200]}...")

                    # 处理数据行
                    data_str = line
                    if line.startswith("data: "):
                        data_str = line[6:]

                    if data_str.strip() == "[DONE]" or data_str.strip() == "":
                        print("[LLM] Received DONE signal")
                        break

                    if not data_str.strip():
                        continue

                    try:
                        data = json.loads(data_str)
                        # 尝试多种响应格式
                        content = None
                        if "output" in data and "text" in data["output"]:
                            content = data["output"]["text"]
                            print(f"[LLM] Found content in output.text: {content[:50]}...")
                        elif "output" in data and "choices" in data["output"] and len(data["output"]["choices"]) > 0:
                            content = data["output"]["choices"][0].get("delta", {}).get("content", "") or data["output"]["choices"][0].get("message", {}).get("content", "")
                        elif "choices" in data and len(data["choices"]) > 0:
                            content = data["choices"][0].get("delta", {}).get("content", "") or data["choices"][0].get("message", {}).get("content", "")

                        if content:
                            print(f"[LLM] Yielding content: {content[:50]}...")
                            yield content
                        else:
                            print(f"[LLM] No content in data keys: {list(data.keys())}")
                    except json.JSONDecodeError as e:
                        print(f"[LLM] JSON decode error: {e}, data_str: {data_str[:100]}")
                        continue

    async def generate_complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000
    ) -> dict:
        """非流式生成，返回完整结果"""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        messages = []
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        messages.append({
            "role": "user",
            "content": prompt
        })

        payload = {
            "model": self.model,
            "input": {"messages": messages},
            "parameters": {
                "temperature": temperature,
                "max_tokens": max_tokens,
                "result_format": "message"
            }
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.base_url}/services/aigc/text-generation/generation",
                headers=headers,
                json=payload
            )

            if response.status_code != 200:
                raise Exception(f"API Error: {response.status_code} - {response.text}")

            data = response.json()
            return {
                "content": data.get("output", {}).get("choices", [{}])[0].get("message", {}).get("content", ""),
                "usage": data.get("usage", {}),
                "request_id": data.get("request_id")
            }

    def estimate_tokens(self, text: str) -> int:
        """简单估算token数量（中英文混合）"""
        # 中文约1.5字符/token，英文约4字符/token
        chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        other_chars = len(text) - chinese_chars
        return int(chinese_chars / 1.5 + other_chars / 4)


# 单例
qwen_service = QwenService()
