import os
import structlog
from datetime import datetime, timedelta
from typing import List
import uuid

from youtube_search.subtitle import SubtitleFetcher

from .client import YouTubeClient
from .models import SearchResponse, SearchSummary, VideoInfo
from .openai_client import OpenAIClient

logger = structlog.get_logger()


class YouTubeService:
    def __init__(self):
        self.youtube_client = YouTubeClient(
            api_key=os.getenv("YOUTUBE_API_KEY", ""))
        self.openai_client = OpenAIClient(
            api_key=os.getenv("OPENAI_API_KEY", ""))
        self.subtitle_fetcher = SubtitleFetcher()

    async def search_videos(self, keyword: str, max_results: int = 3) -> SearchResponse:
        try:
            # 搜索视频
            logger.info("searching_videos", keyword=keyword,
                        max_results=max_results)
            videos = await self.youtube_client.search_videos(keyword, max_results)

            # 获取视频详细信息
            video_infos: List[VideoInfo] = []

            for video in videos:
                log = logger.bind(video_id=video.video_id)

                # 获取字幕信息
                log.info("checking_subtitles")
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
                log.info("video_info_processed", has_subtitles=has_subtitles)

            # 创建总结
            summary = SearchSummary(
                total_videos=len(video_infos),
                overview=f"找到{len(video_infos)}个相关视频。"
            )

            # 创建响应
            now = datetime.utcnow()
            response = SearchResponse(
                session_id=str(uuid.uuid4()),
                keyword=keyword,
                summary=summary,
                videos=video_infos,
                created_at=now,
                expires_at=now + timedelta(hours=1)
            )

            logger.info("search_response_created",
                        keyword=keyword,
                        total_videos=len(video_infos))
            return response

        except Exception as e:
            logger.error("search_videos_failed",
                         keyword=keyword,
                         error=str(e),
                         exc_info=True)
            raise
