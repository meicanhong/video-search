# YouTube 字幕获取模块设计

## 技术方案
1. **字幕获取方式**：
   - 使用 youtube_transcript_api
   - 支持多语言字幕
   - 支持自动生成字幕
   - 支持代理配置

## 数据结构
```python
# 字幕行数据结构
{
    'text': str,       # 字幕文本
    'start': float,    # 开始时间（秒）
    'duration': float  # 持续时间（秒）
}
```

## 核心功能实现
```python
import logging
from typing import Optional, Dict, List
from youtube_transcript_api import YouTubeTranscriptApi

logger = logging.getLogger(__name__)


class SubtitleFetcher:
    """YouTube字幕获取器"""

    def __init__(self, proxy: Optional[Dict[str, str]] = None):
        """初始化字幕获取器
        
        Args:
            proxy: 代理配置，默认为None
        """
        self.proxy = proxy or {}

    def get_transcript(self, video_id: str, prefer_language: str = None) -> Optional[List[Dict]]:
        """获取视频字幕
        
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
            return YouTubeTranscriptApi.get_transcript(
                video_id=video_id,
                languages=[prefer_language] if prefer_language else None,
                proxies=self.proxy
            )
        except Exception as e:
            logger.error(f"Error getting transcript for video {video_id}: {e}")
            return None
```

## 使用示例
```python
def main():
    # 创建字幕获取器
    fetcher = SubtitleFetcher()

    # 获取视频字幕
    video_id = "zdY9Al6Fftk"
    transcript = fetcher.get_transcript(video_id, prefer_language='zh-Hans')
    
    if transcript:
        # 打印带时间戳的字幕
        for line in transcript[:5]:  # 只打印前5行
            print(f"{line['start']:.1f}s - {line['text']}")
            
        # 如果需要纯文本
        full_text = ", ".join(line["text"] for line in transcript)
        print("\n完整文本预览:")
        print(full_text[:200] + "...")
    else:
        print("未找到字幕")
```

## 错误处理
1. **字幕不可用**
   - 视频没有字幕
   - 指定语言不可用
   - 返回 None

2. **网络错误**
   - 连接超时
   - 代理错误
   - 记录错误日志并返回 None

## 注意事项
1. **语言代码**
   - 使用标准语言代码（如 'zh-Hans', 'en'）
   - 当指定语言不可用时，会尝试其他可用语言

2. **代理设置**
   - 支持配置 HTTP/HTTPS 代理
   - 格式：{'http': 'http://proxy.example.com:8080', 'https': 'https://proxy.example.com:8080'} 