import os
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass

from .models import SearchConfig, VideoMetadata
from .client import YouTubeSearchClient
from .subtitle import SubtitleFetcher
from .openai_client import OpenAIClient
from .utils import format_duration

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
        """初始化服务

        Args:
            youtube_api_key: YouTube API密钥，如果为None则从环境变量获取
            openai_api_key: OpenAI API密钥，如果为None则从环境变量获取
        """
        self.youtube_api_key = youtube_api_key or os.getenv('YOUTUBE_API_KEY')
        if not self.youtube_api_key:
            raise ValueError("YouTube API key is required")

        # 初始化搜索客户端
        self.search_client = YouTubeSearchClient(
            SearchConfig(
                api_key=self.youtube_api_key,
                max_results=5,
                language='zh'
            )
        )

        # 初始化字幕获取器
        self.subtitle_fetcher = SubtitleFetcher()

        # 初始化OpenAI客户端（如果提供了API密钥）
        self.openai_client = None
        if openai_api_key or os.getenv('OPENAI_API_KEY'):
            self.openai_client = OpenAIClient(openai_api_key)

    async def search_videos_with_subtitles(
        self,
        query: str,
        prefer_language: str = 'zh-Hans',
        analyze_content: bool = True
    ) -> List[VideoResult]:
        """搜索视频并获取字幕

        Args:
            query: 搜索关键词
            prefer_language: 首选字幕语言
            analyze_content: 是否使用OpenAI分析内容

        Returns:
            List[VideoResult]: 视频结果列表，每个结果包含视频信息和字幕
        """
        # 搜索视频
        logger.info(f"搜索视频: {query}")
        try:
            videos = await self.search_client.search(query)
            if not videos:
                logger.warning(f"未找到相关视频: {query}")
                return []
        except Exception as e:
            logger.error(f"搜索视频时出错: {str(e)}")
            raise

        # 获取字幕和分析内容
        results = []
        for video in videos:
            try:
                # 获取字幕
                logger.info(f"获取视频字幕: {video.video_id}")
                subtitle = self.subtitle_fetcher.get_transcript(
                    video.video_id,
                    prefer_language=prefer_language
                )

                # 创建结果对象
                result = VideoResult(video=video, subtitle=subtitle)

                # 如果有字幕且启用了内容分析
                if subtitle and analyze_content and self.openai_client:
                    try:
                        # 获取内容总结
                        result.summary = await self.openai_client.summarize_subtitles(
                            subtitle
                        )

                        # 分析与查询的相关性
                        result.analysis = await self.openai_client.analyze_subtitle(
                            query,
                            result.get_subtitle_text()
                        )
                    except Exception as e:
                        logger.warning(f"内容分析出错: {str(e)}")

                results.append(result)

            except Exception as e:
                logger.warning(f"获取视频 {video.video_id} 的字幕时出错: {str(e)}")
                # 即使获取字幕失败，也添加视频信息
                results.append(VideoResult(video=video))

        return results

    async def search_with_content_analysis(self, query: str, max_results: int = 5) -> List[Dict]:
        """搜索视频并分析内容

        Args:
            query: 搜索关键词
            max_results: 最大返回结果数

        Returns:
            List[Dict]: 搜索结果列表，包含视频信息和内容分析
        """
        try:
            # 搜索视频
            videos = await self.search_client.search(query, max_results)
            results = []

            for video in videos:
                video_info = {
                    "title": video.title,
                    "channel": video.channel_title,
                    "duration": video.duration,
                    "views": video.view_count,
                    "link": f"https://youtube.com/watch?v={video.video_id}"
                }

                try:
                    # 获取字幕
                    subtitles = self.subtitle_fetcher.get_transcript(
                        video.video_id)
                    if not subtitles:
                        logger.warning(
                            f"No subtitles found for video {video.video_id}")
                        continue

                    # 分析内容
                    analysis = await self.openai_client.analyze_subtitle(
                        query=query,
                        subtitles=subtitles
                    )

                    # 处理时间戳和直达链接
                    timestamps = analysis.get("timestamps", [])
                    for moment in timestamps:
                        # 解析时间字符串 (MM:SS) 转换为秒数
                        time_parts = moment["time"].split(":")
                        seconds = int(time_parts[0]) * 60 + int(time_parts[1])
                        # 添加直达链接
                        moment["direct_link"] = f"{video_info['link']}&t={seconds}"

                    # 添加分析结果
                    video_info.update({
                        "content_analysis": {
                            "summary": analysis.get("summary", ""),
                            "relevant": analysis.get("relevant", False),
                            "details": analysis.get("details"),
                            "key_moments": timestamps
                        }
                    })

                    results.append(video_info)

                except Exception as e:
                    logger.error(
                        f"Error analyzing video {video.video_id}: {str(e)}")
                    continue

            return results

        except Exception as e:
            logger.error(f"Error in search_with_content_analysis: {str(e)}")
            raise
