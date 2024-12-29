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
    async def generate_video_sumary(
        self,
        transcript: str,
        max_tokens: int = 300
    ) -> str:
        """总结字幕内容

        Args:
            transcript: 字幕文本内容
            max_tokens: 最大返回token数

        Returns:
            str: 内容总结
        """
        system_prompt = """
        你是一个视频内容分析助手。你的任务是：
        1. 分析字幕内容
        2. 生成简洁的内容总结
        3. 总结要点到点，不要太啰嗦
        """

        user_prompt = f"""
        字幕内容:
        {transcript}
        
        请生成一个简洁的总结。
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

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def answer_question(
        self,
        query: str,
        transcript: str,
        max_tokens: int = 800
    ) -> str:
        """基于字幕内容和 LLM 知识回答用户问题

        Args:
            query: 用户问题
            transcript: 字幕文本内容
            max_tokens: 最大返回token数

        Returns:
            str: 问题的回答
        """
        system_prompt = """
        你是一个专业的视频内容分析助手。你的任务是：
        1. 首先基于字幕内容回答用户问题
        2. 然后结合你的知识，对回答进行补充和扩展
        3. 如果字幕内容不足以回答问题，可以使用你的知识来辅助回答
        4. 如果问题涉及多个视频的内容，要综合分析并给出完整答案
        
        回答要求：
        1. 明确区分哪些信息来自视频，哪些是补充知识
        2. 回答分两部分：
           - 第一部分：基于视频内容的回答
           - 第二部分：知识补充和扩展（如果需要）
        3. 回答要简洁、准确、有逻辑性
        4. 适当引用视频内容，增加可信度
        5. 补充知识要确保准确性和相关性
        
        注意事项：
        - 如果视频内容足够回答问题，补充知识部分可以简短或省略
        - 如果视频内容完全不相关，要诚实说明，再用知识回答
        - 确保两部分内容有逻辑联系，不要简单罗列
        """

        user_prompt = f"""
        用户问题: {query}

        字幕内容:
        {transcript}
        
        请先基于字幕内容回答问题，再结合你的知识进行补充和扩展。
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

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return "抱歉，在处理您的问题时遇到了错误。"
