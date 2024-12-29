from datetime import datetime
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
        """格式化视频时长

        Args:
            duration: ISO 8601 格式的时长字符串

        Returns:
            str: 格式化后的时长字符串
        """
        # 简单处理，只考虑分钟
        minutes = 0
        if 'M' in duration:
            minutes = int(duration.split('M')[0].split('T')[-1])
        return f"{minutes}分钟"
