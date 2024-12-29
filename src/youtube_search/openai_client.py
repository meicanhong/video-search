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
            api_key: OpenAI API key
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key is required")

        # 初始化 OpenAI 客户端
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            timeout=30.0
        )

    def _parse_json_response(self, content: str) -> Optional[Dict]:
        """解析可能包含 Markdown 代码块的 JSON 响应

        Args:
            content: OpenAI 响应内容

        Returns:
            Dict: 解析后的 JSON 对象，如果解析失败则返回 None
        """
        content = content.strip()

        # 处理 "null" 响应
        if content.lower() == "null":
            return None

        # 尝试直接解析
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass

        # 尝试从 Markdown 代码块中提取
        if content.startswith("```") and content.endswith("```"):
            # 移除首尾的 ``` 标记
            content = content.strip("`")
            # 移除可能的语言标记（如 ```json）
            content = content.split("\n", 1)[1] if "\n" in content else content

            try:
                return json.loads(content.strip())
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON from Markdown block: {e}")
                logger.error(f"Content: {content}")
                return None

        logger.error(f"Failed to parse response: {content}")
        return None

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def analyze_subtitle(
        self,
        query: str,
        subtitles: List[Dict],
        video_info: Dict,
        max_tokens: int = 500
    ) -> Dict:
        """分析字幕内容，找到与查询相关的片段和时间点

        Args:
            query: 用户查询
            subtitles: 字幕列表，每项包含 text 和 start 时间
            video_info: 视频信息，包含标题等
            max_tokens: 最大返回token数

        Returns:
            Dict: 分析结果，包含答案和相关片段
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
        1. 分析用户的问题和视频字幕内容
        2. 找出与问题最相关的内容
        3. 生成准确的答案和相关视频片段
        
        输出格式要求：
        {
            "clip": {
                "content": "相关内容",
                "timestamp": "MM:SS格式的时间点",
                "relevance": 0.0到1.0的相关度
            }
        }
        
        请确保输出是有效的JSON格式。如果找不到相关内容，返回 null。
        """

        user_prompt = f"""
        用户问题: {query}
        
        视频标题: {video_info.get('title', '')}
        
        字幕内容:
        {subtitle_text}
        
        请分析字幕内容，找出与用户问题最相关的片段，并标注具体时间点。
        """

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.7
            )

            return self._parse_json_response(response.choices[0].message.content)

        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def generate_answer(
        self,
        query: str,
        clips: List[Dict],
        max_tokens: int = 300
    ) -> Dict:
        """根据所有相关片段生成综合答案

        Args:
            query: 用户问题
            clips: 相关视频片段列表
            max_tokens: 最大返回token数

        Returns:
            Dict: 包含答案和可信度的字典
        """
        if not clips:
            return None

        system_prompt = """
        你是一个视频内容分析助手。你的任务是：
        1. 分析所有相关视频片段
        2. 生成一个综合的、准确的答案
        3. 评估答案的可信度
        
        输出格式要求：
        {
            "summary": "综合答案",
            "confidence": 0.0到1.0的可信度
        }
        """

        clips_text = "\n".join([
            f"视频: {clip['video_title']}\n"
            f"时间点: {clip['timestamp']}\n"
            f"内容: {clip['content']}\n"
            f"相关度: {clip['relevance']}\n"
            for clip in clips
        ])

        user_prompt = f"""
        用户问题: {query}
        
        相关视频片段:
        {clips_text}
        
        请根据以上视频片段生成一个综合的答案，并评估答案的可信度。
        """

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.7
            )

            return self._parse_json_response(response.choices[0].message.content)

        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise
