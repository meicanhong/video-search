import os
import structlog
from datetime import datetime, timedelta
from typing import List, Dict
import uuid

from .client import YouTubeClient
from .models import SearchResponse, SearchSummary, VideoInfo
from .openai_client import OpenAIClient
from .subtitle import SubtitleFetcher
from .session import SearchSession

logger = structlog.get_logger()


class YouTubeService:
    def __init__(self):
        self.youtube_client = YouTubeClient(
            api_key=os.getenv("YOUTUBE_API_KEY", ""))
        self.openai_client = OpenAIClient(
            api_key=os.getenv("OPENAI_API_KEY", ""))
        self.subtitle_fetcher = SubtitleFetcher()
        self.sessions: Dict[str, SearchSession] = {}

    async def search_videos(self, keyword: str, max_results: int = 3) -> SearchResponse:
        """搜索视频并创建会话

        Args:
            keyword: 搜索关键词
            max_results: 最大返回结果数

        Returns:
            SearchResponse: 搜索响应
        """
        try:
            # 搜索视频
            logger.info("searching_videos", keyword=keyword,
                        max_results=max_results)
            videos = await self.youtube_client.search_videos(keyword, max_results)

            # 创建会话
            session_id = str(uuid.uuid4())
            session = SearchSession(session_id)
            session.search_keyword = keyword
            self.sessions[session_id] = session

            # 获取视频详细信息和字幕
            video_infos: List[VideoInfo] = []
            all_subtitles = []

            for video in videos:
                log = logger.bind(video_id=video.video_id)

                # 获取字幕信息
                transcript = self.subtitle_fetcher.get_transcript(
                    video.video_id)
                has_subtitles = transcript is not None

                video_info = VideoInfo(
                    video_id=video.video_id,
                    title=video.title,
                    channel_title=video.channel_title,
                    duration=video.duration,
                    view_count=video.view_count,
                    published_at=video.published_at,
                    thumbnail_url=f"https://i.ytimg.com/vi/{video.video_id}/hqdefault.jpg",
                    description=video.description,
                    has_subtitles=has_subtitles
                )
                video_infos.append(video_info)

                # 存储视频和字幕信息到会话
                session.add_video(video_info.dict(), transcript)

                if transcript:
                    all_subtitles.extend([{
                        "video_id": video.video_id,
                        "video_title": video.title,
                        **sub
                    } for sub in transcript])

            transcript_text = ""
            for sub in all_subtitles:
                transcript_text += f"[{sub['video_title']}] {sub['text']}\n"

            overview = await self.openai_client.generate_answer(
                transcript=transcript_text,
                max_tokens=300
            )

            # 创建总结
            summary = SearchSummary(
                total_videos=len(video_infos),
                overview=overview if overview else f"找到{len(video_infos)}个相关视频。"
            )

            # 创建响应
            now = datetime.utcnow()
            response = SearchResponse(
                session_id=session_id,
                keyword=keyword,
                summary=summary,
                videos=video_infos,
                created_at=now,
                expires_at=now + timedelta(hours=1)
            )

            logger.info("search_response_created",
                        session_id=session_id,
                        keyword=keyword,
                        total_videos=len(video_infos))
            return response

        except Exception as e:
            logger.error("search_videos_failed",
                         keyword=keyword,
                         error=str(e),
                         exc_info=True)
            raise
