import os
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass
import uuid

from .models import SearchConfig, VideoMetadata
from .client import YouTubeSearchClient
from .subtitle import SubtitleFetcher
from .openai_client import OpenAIClient
from .utils import format_duration
from .session import SearchSession

logger = logging.getLogger(__name__)


@dataclass
class VideoResult:
    """视频结果，包含视频信息和字幕"""
    video: VideoMetadata
    subtitle: Optional[List[Dict]] = None
    summary: Optional[str] = None
    analysis: Optional[Dict] = None

    def format_info(self) -> str:
        """格式化视频信息"""
        info = [
            f"标题: {self.video.title}",
            f"频道: {self.video.channel_title}",
            f"时长: {format_duration(self.video.duration) or '未知'}",
            f"观看次数: {self.video.view_count:,}",
            f"链接: https://youtube.com/watch?v={self.video.video_id}"
        ]

        if self.summary:
            info.extend(["", "内容总结:", self.summary])

        if self.analysis:
            info.extend(["", "相关性分析:", self.analysis.get("summary", "")])
            if self.analysis.get("details"):
                info.extend(["详细信息:", self.analysis["details"]])

        return "\n".join(info)

    def get_subtitle_text(self) -> Optional[str]:
        """获取字幕文本"""
        if not self.subtitle:
            return None
        return ", ".join(item["text"] for item in self.subtitle)


class YouTubeService:
    """YouTube搜索和字幕服务"""

    def __init__(
        self,
        youtube_api_key: Optional[str] = None,
        openai_api_key: Optional[str] = None
    ):
        """初始化服务"""
        self.youtube_api_key = youtube_api_key or os.getenv('YOUTUBE_API_KEY')
        if not self.youtube_api_key:
            raise ValueError("YouTube API key is required")

        # 初始化搜索客户端
        self.search_client = YouTubeSearchClient(
            SearchConfig(
                api_key=self.youtube_api_key,
                max_results=10,
                language='zh'
            )
        )

        # 初始化字幕获取器
        self.subtitle_fetcher = SubtitleFetcher()

        # 初始化OpenAI客户端（如果提供了API密钥）
        self.openai_client = None
        if openai_api_key or os.getenv('OPENAI_API_KEY'):
            self.openai_client = OpenAIClient(openai_api_key)

        # 会话存储
        self.sessions: Dict[str, SearchSession] = {}

    async def create_search_session(
        self,
        keyword: str,
        max_results: int = 10
    ) -> Dict:
        """创建新的搜索会话

        Args:
            keyword: 搜索关键词
            max_results: 最大返回结果数

        Returns:
            Dict: 会话信息
        """
        # 创建会话
        session_id = str(uuid.uuid4())
        session = SearchSession(session_id)
        session.search_keyword = keyword

        try:
            # 搜索视频
            videos = await self.search_client.search(keyword, max_results)

            # 获取字幕并存储到会话
            for video in videos:
                video_info = {
                    "video_id": video.video_id,
                    "title": video.title,
                    "channel_title": video.channel_title,
                    "duration": video.duration,
                    "views": video.view_count
                }

                # 获取字幕
                subtitles = self.subtitle_fetcher.get_transcript(
                    video.video_id)
                session.add_video(video_info, subtitles)

            # 存储会话
            self.sessions[session_id] = session

            # 返回会话信息
            return session.get_session_info()

        except Exception as e:
            logger.error(f"Error creating search session: {str(e)}")
            raise

    async def answer_question(
        self,
        session_id: str,
        question: str
    ) -> Dict:
        """在会话中回答问题

        Args:
            session_id: 会话ID
            question: 用户问题

        Returns:
            Dict: 包含答案和相关片段的字典
        """
        # 获取会话
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        if session.is_expired():
            raise ValueError(f"Session {session_id} has expired")

        try:
            # 更新访问时间
            session.update_last_accessed()

            # 获取所有字幕
            all_subtitles = session.get_all_subtitles()
            if not all_subtitles:
                return {
                    "answer": None,
                    "relevant_clips": []
                }

            # 分析所有视频的字幕内容
            all_clips = []
            for video in session.videos:
                if video["video_id"] not in session.subtitles:
                    continue

                subtitles = session.subtitles[video["video_id"]]
                clip = await self.openai_client.analyze_subtitle(
                    query=question,
                    subtitles=subtitles,
                    video_info=video
                )

                if clip:
                    # 添加视频信息到片段
                    clip_info = {
                        "content": clip["clip"]["content"],
                        "timestamp": clip["clip"]["timestamp"],
                        "relevance": clip["clip"]["relevance"],
                        "video_title": video["title"],
                        "direct_link": f"https://youtube.com/watch?v={video['video_id']}&t={self._time_to_seconds(clip['clip']['timestamp'])}"
                    }
                    all_clips.append(clip_info)

            # 按相关度排序
            all_clips.sort(key=lambda x: x["relevance"], reverse=True)

            # 生成综合答案
            answer = await self.openai_client.generate_answer(
                query=question,
                clips=all_clips
            ) if all_clips else None

            return {
                "answer": answer,
                "relevant_clips": all_clips
            }

        except Exception as e:
            logger.error(
                f"Error answering question in session {session_id}: {str(e)}")
            raise

    def cleanup_expired_sessions(self):
        """清理过期的会话"""
        expired_sessions = [
            session_id
            for session_id, session in self.sessions.items()
            if session.is_expired()
        ]
        for session_id in expired_sessions:
            del self.sessions[session_id]

    def _time_to_seconds(self, time_str: str) -> int:
        """将时间字符串转换为秒数

        Args:
            time_str: 时间字符串 (MM:SS)

        Returns:
            int: 秒数
        """
        parts = time_str.split(":")
        return int(parts[0]) * 60 + int(parts[1])
