import logging
from typing import Optional, Dict, List
from youtube_transcript_api import YouTubeTranscriptApi

logger = logging.getLogger(__name__)


def get_proxy() -> Dict[str, str]:
    """获取代理配置

    Returns:
        Dict[str, str]: 代理配置字典
    """
    # TODO: 从配置文件或环境变量获取代理设置
    return {}


class SubtitleFetcher:
    """YouTube字幕获取器"""

    def __init__(self, proxy: Optional[Dict[str, str]] = None):
        """初始化字幕获取器

        Args:
            proxy: 代理配置，默认为None
        """
        self.proxy = proxy or get_proxy()

    def get_transcript(self, video_id: str, prefer_language: str = None) -> Optional[List[Dict]]:
        """获取视频字幕，按优先级获取：人工字幕 > 自动生成字幕 > 翻译字幕

        Args:
            video_id: YouTube视频ID
            prefer_language: 首选语言代码，默认为None

        Returns:
            Optional[List[Dict]]: 字幕数据列表，每项包含text、start和duration，获取失败返回None
            示例：
            [
                {
                    'text': '字幕文本',
                    'start': 0.0,      # 开始时间（秒）
                    'duration': 1.5     # 持续时间（秒）
                },
                ...
            ]
        """
        try:
            # 获取字幕对象
            transcripts = YouTubeTranscriptApi.list_transcripts(
                video_id,
                proxies=self.proxy
            )

            # 获取可用的语言列表（按优先级）
            language_codes = []

            # 1. 优先获取人工生成的字幕
            for key in transcripts._manually_created_transcripts:
                language_codes.append(key)

            # 2. 如果没有人工字幕，获取自动生成的字幕
            if not language_codes:
                for key in transcripts._generated_transcripts:
                    language_codes.append(key)

            # 3. 如果还是没有，获取可翻译的语言
            if not language_codes:
                for key in transcripts._translation_languages:
                    language_codes.append(key)

            if not language_codes:
                logger.warning(f"No subtitles available for video {video_id}")
                return None

            # 如果指定了首选语言且可用，将其放在语言列表首位
            if prefer_language and prefer_language in language_codes:
                language_codes.remove(prefer_language)
                language_codes.insert(0, prefer_language)

            # 获取字幕
            return YouTubeTranscriptApi.get_transcript(
                video_id=video_id,
                languages=language_codes,
                proxies=self.proxy
            )

        except Exception as e:
            logger.error(f"Error getting transcript for video {video_id}: {e}")
            return None
