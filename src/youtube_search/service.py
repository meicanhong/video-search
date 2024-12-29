import uuid
from datetime import datetime, timedelta
from typing import List, Optional

from .client import YouTubeClient
from .models import SearchRequest, SearchResponse, SearchSummary, VideoInfo
from .openai_client import OpenAIClient
from .session import SearchSession
from .subtitle import SubtitleFetcher


class YouTubeService:
    """YouTube 服务"""

    def __init__(self, youtube_client: YouTubeClient, openai_client: OpenAIClient):
        """初始化服务

        Args:
            youtube_client: YouTube API 客户端
            openai_client: OpenAI API 客户端
        """
        self.youtube_client = youtube_client
        self.openai_client = openai_client
        self.subtitle_fetcher = SubtitleFetcher()
        self.sessions: dict[str, SearchSession] = {}

    async def search_videos(self, request: SearchRequest) -> SearchResponse:
        """搜索视频并创建会话

        Args:
            request: 搜索请求

        Returns:
            SearchResponse: 搜索响应
        """
        # 搜索视频
        videos = await self.youtube_client.search_videos(
            query=request.keyword,
            max_results=request.max_results
        )

        # 获取视频字幕和详细信息
        video_infos: List[VideoInfo] = []
        total_duration = 0
        latest_video_date = datetime.min

        for video in videos:
            # 获取字幕信息
            transcript = self.subtitle_fetcher.get_transcript(video.video_id)
            has_subtitles = transcript is not None
            languages = []
            if has_subtitles:
                # TODO: 获取支持的语言列表
                languages = ["zh-Hans"]

            # 更新统计信息
            duration_minutes = self._parse_duration(video.duration)
            total_duration += duration_minutes
            if video.published_at > latest_video_date:
                latest_video_date = video.published_at

            # 构建视频信息
            video_info = VideoInfo(
                video_id=video.video_id,
                title=video.title,
                channel_title=video.channel_title,
                duration=video.duration,
                view_count=video.view_count or 0,
                published_at=video.published_at,
                thumbnail_url=video.thumbnail_url or "",
                description=video.description or "",
                has_subtitles=has_subtitles,
                languages=languages
            )
            video_infos.append(video_info)

        # 使用 GPT 生成搜索结果概述
        overview = await self._generate_overview(request.keyword, video_infos)

        # 生成搜索结果总结
        summary = SearchSummary(
            total_videos=len(video_infos),
            total_duration=total_duration,
            latest_video_date=latest_video_date,
            overview=overview
        )

        # 创建会话
        session_id = str(uuid.uuid4())
        created_at = datetime.utcnow()
        expires_at = created_at + timedelta(hours=1)  # 会话有效期1小时

        # 存储会话
        session = SearchSession(
            session_id=session_id,
            search_keyword=request.keyword,
            videos=video_infos,
            created_at=created_at
        )
        self.sessions[session_id] = session

        # 构建响应
        return SearchResponse(
            session_id=session_id,
            search_keyword=request.keyword,
            summary=summary,
            videos=video_infos,
            created_at=created_at,
            expires_at=expires_at
        )

    async def _generate_overview(self, keyword: str, videos: List[VideoInfo]) -> str:
        """使用 GPT 生成搜索结果概述

        Args:
            keyword: 搜索关键词
            videos: 视频列表

        Returns:
            str: 概述文本
        """
        # 构建提示信息
        video_info = []
        for video in videos:
            info = {
                "title": video.title,
                "description": video.description,
                "duration": video.duration,
                "published_at": video.published_at.strftime("%Y-%m-%d")
            }
            video_info.append(info)

        # 调用 GPT 生成概述
        try:
            result = await self.openai_client.analyze_content(
                query=f"为搜索关键词'{keyword}'生成视频列表概述",
                content=video_info
            )
            return result.get("summary", self._generate_default_overview(keyword, videos))
        except Exception:
            return self._generate_default_overview(keyword, videos)

    def _generate_default_overview(self, keyword: str, videos: List[VideoInfo]) -> str:
        """生成默认的搜索结果概述

        Args:
            keyword: 搜索关键词
            videos: 视频列表

        Returns:
            str: 概述文本
        """
        total_duration = sum(self._parse_duration(v.duration) for v in videos)
        latest_video = max(videos, key=lambda x: x.published_at)
        return (
            f"找到{len(videos)}个关于{keyword}的视频。"
            f"视频总时长约{total_duration}分钟，"
            f"最新更新时间为{latest_video.published_at.strftime('%Y-%m-%d')}。"
        )

    def _parse_duration(self, duration: str) -> int:
        """解析视频时长字符串为分钟数

        Args:
            duration: 时长字符串 (如 "10分钟")

        Returns:
            int: 分钟数
        """
        try:
            return int(duration.replace("分钟", ""))
        except ValueError:
            return 0
