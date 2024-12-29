from typing import List, Dict, Optional
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class SearchSession:
    """管理视频搜索会话"""

    def __init__(self, session_id: str):
        """初始化搜索会话

        Args:
            session_id: 会话ID
        """
        self.session_id = session_id
        self.created_at = datetime.now()
        self.last_accessed = datetime.now()
        self.search_keyword = ""
        self.videos: List[Dict] = []  # 存储视频信息
        self.subtitles: Dict[str, List[Dict]] = {}  # video_id -> 字幕列表
        self.expire_after = timedelta(hours=1)  # 会话有效期

    def is_expired(self) -> bool:
        """检查会话是否过期"""
        return datetime.now() - self.last_accessed > self.expire_after

    def update_last_accessed(self):
        """更新最后访问时间"""
        self.last_accessed = datetime.now()

    def add_video(self, video_info: Dict, subtitles: Optional[List[Dict]] = None):
        """添加视频和字幕信息

        Args:
            video_info: 视频信息
            subtitles: 字幕列表
        """
        self.videos.append(video_info)
        if subtitles:
            self.subtitles[video_info["video_id"]] = subtitles

    def get_all_subtitles(self) -> List[Dict]:
        """获取所有字幕内容"""
        all_subtitles = []
        for video_id, subs in self.subtitles.items():
            video_info = next(
                (v for v in self.videos if v["video_id"] == video_id), {})
            for sub in subs:
                sub_with_video = {
                    **sub,
                    "video_id": video_id,
                    "video_title": video_info.get("title", ""),
                }
                all_subtitles.append(sub_with_video)
        return all_subtitles

    def get_session_info(self) -> Dict:
        """获取会话信息"""
        return {
            "session_id": self.session_id,
            "search_keyword": self.search_keyword,
            "created_at": self.created_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat(),
            "video_count": len(self.videos),
            "videos": [
                {
                    "title": video.get("title", ""),
                    "channel": video.get("channel_title", ""),
                    "duration": video.get("duration", ""),
                    "link": f"https://youtube.com/watch?v={video.get('video_id', '')}"
                }
                for video in self.videos
            ]
        }
