import os
import json
import logging
from typing import List, Dict, Optional
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class OpenAIClient:
    """OpenAI API 客户端"""

    def __init__(self, api_key: Optional[str] = None):
        """初始化 OpenAI 客户端

        Args:
            api_key: OpenAI API密钥，如果为None则从环境变量获取
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key is required")

        self.client = AsyncOpenAI(api_key=self.api_key)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def analyze_subtitle(
        self,
        query: str,
        subtitles: List[Dict],
        max_tokens: int = 300
    ) -> Dict:
        """分析字幕内容，找到与查询相关的片段和时间点

        Args:
            query: 用户查询
            subtitles: 字幕列表，每项包含 text 和 start 时间
            max_tokens: 最大返回token数

        Returns:
            Dict: 分析结果，包含相关片段、时间点和相关度
        """
        # 构建字幕文本，保留时间信息
        subtitle_entries = []
        for item in subtitles:
            start_time = int(item.get('start', 0))
            minutes = start_time // 60
            seconds = start_time % 60
            time_str = f"{minutes:02d}:{seconds:02d}"
            subtitle_entries.append(f"[{time_str}] {item.get('text', '')}")

        subtitle_text = "\n".join(subtitle_entries)

        system_prompt = """
        你是一个视频内容分析助手。你的任务是：
        1. 分析用户的查询和视频字幕内容
        2. 找出字幕中与查询最相关的片段
        3. 提供时间点和相关度评分
        
        输出格式要求：
        {
            "relevant": bool,      # 是否找到相关内容
            "summary": str,        # 简短总结（限50字）
            "details": str,        # 详细说明（如果relevant为true）
            "timestamps": [        # 相关时间点列表（最多返回3个最相关的点）
                {
                    "time": str,   # 时间点 (MM:SS)
                    "text": str,   # 相关内容
                    "relevance": float  # 相关度 0.0-1.0
                }
            ]
        }
        
        请确保输出是有效的JSON格式。时间点按相关度从高到低排序。
        """

        user_prompt = f"""
        用户查询: {query}
        
        字幕内容:
        {subtitle_text}
        
        请分析字幕内容，找出与用户查询最相关的部分，并标注具体时间点。
        """

        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.7
            )

            content = response.choices[0].message.content
            try:
                # 尝试解析JSON
                result = json.loads(content)
                # 确保返回格式完整
                if "timestamps" not in result:
                    result["timestamps"] = []
                return result
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse OpenAI response: {e}")
                # 如果解析失败，返回一个标准格式
                return {
                    "relevant": True,
                    "summary": content[:100],
                    "details": None,
                    "timestamps": []
                }

        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def summarize_subtitles(
        self,
        subtitles: List[Dict],
        max_tokens: int = 150
    ) -> str:
        """总结字幕内容

        Args:
            subtitles: 字幕列表
            max_tokens: 最大返回token数

        Returns:
            str: 总结内容
        """
        # 将字幕转换为文本
        subtitle_text = ", ".join(item["text"] for item in subtitles)

        system_prompt = """
        你是一个视频内容总结助手。请将提供的字幕内容总结为简洁的几点要点。
        重点关注：
        1. 视频的主要话题
        2. 关键信息点
        3. 重要的结论或建议
        
        输出格式：
        1. [主要话题]
        2. [关键点1]
        3. [关键点2]
        ...
        """

        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": subtitle_text}
                ],
                max_tokens=max_tokens,
                temperature=0.7
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise
