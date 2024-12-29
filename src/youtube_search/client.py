from datetime import datetime
import re
from typing import List, Optional

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .models import VideoInfo


class YouTubeClient:
    """YouTube API 客户端"""

    def __init__(self, api_key: str):
        """初始化客户端

        Args:
            api_key: YouTube API 密钥
        """
        self.youtube = build('youtube', 'v3', developerKey=api_key)

    async def search_videos(self, query: str, max_results: int = 3) -> List[VideoInfo]:
        """搜索视频

        Args:
            query: 搜索关键词
            max_results: 最大返回结果数

        Returns:
            List[VideoInfo]: 视频信息列表
        """
        try:
            # 搜索视频
            search_response = self.youtube.search().list(
                q=query,
                part='id,snippet',
                type='video',
                maxResults=max_results,
                videoCaption='any'
            ).execute()

            # 获取视频ID列表
            video_ids = [item['id']['videoId']
                         for item in search_response['items']]

            # 获取视频详细信息
            videos_response = self.youtube.videos().list(
                part='snippet,contentDetails,statistics',
                id=','.join(video_ids)
            ).execute()

            # 解析视频信息
            videos = []
            for item in videos_response['items']:
                video = VideoInfo(
                    video_id=item['id'],
                    title=item['snippet']['title'],
                    channel_title=item['snippet']['channelTitle'],
                    duration=self._format_duration(
                        item['contentDetails']['duration']),
                    view_count=int(item['statistics'].get('viewCount', 0)),
                    published_at=datetime.strptime(
                        item['snippet']['publishedAt'], '%Y-%m-%dT%H:%M:%SZ'),
                    thumbnail_url=item['snippet']['thumbnails']['high']['url'],
                    description=item['snippet']['description'],
                    has_subtitles=False,  # 默认值，后续会更新
                    languages=[]  # 默认值，后续会更新
                )
                videos.append(video)

            return videos

        except HttpError as e:
            print(f'YouTube API 错误: {e}')
            return []

    def _format_duration(self, duration: str) -> str:
        """将ISO 8601格式的时长转换为人类可读格式

        Args:
            duration: ISO 8601格式的时长字符串，如 'PT1H2M10S'

        Returns:
            str: 格式化后的时长字符串，如 '1小时2分钟10秒'

        Examples:
            >>> format_duration('PT1H2M10S')
            '1小时2分钟10秒'
            >>> format_duration('PT5M')
            '5分钟'
            >>> format_duration('PT30S')
            '30秒'
        """
        if not duration:
            return None

        # 使用正则表达式提取时、分、秒
        pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
        match = re.match(pattern, duration)
        if not match:
            return None

        hours, minutes, seconds = match.groups()

        # 构建人类可读的时长字符串
        parts = []
        if hours:
            parts.append(f"{int(hours)}小时")
        if minutes:
            parts.append(f"{int(minutes)}分钟")
        if seconds:
            parts.append(f"{int(seconds)}秒")

        return "".join(parts) if parts else None
