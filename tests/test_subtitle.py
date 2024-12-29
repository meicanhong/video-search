import pytest
from src.youtube_search.subtitle import SubtitleFetcher


def test_get_transcript_with_subtitles():
    """测试获取有字幕的视频"""
    fetcher = SubtitleFetcher()
    # 使用已知有字幕的视频ID
    video_id = "K8nPfwwQXXY"
    transcript = fetcher.get_transcript(video_id, prefer_language='zh-Hans')

    assert transcript is not None
    assert len(transcript) > 0
    assert all(isinstance(item, dict) for item in transcript)
    assert all('text' in item for item in transcript)
    assert all('start' in item for item in transcript)
    assert all('duration' in item for item in transcript)


def test_get_transcript_without_subtitles():
    """测试获取无字幕的视频"""
    fetcher = SubtitleFetcher()
    # 使用已知无字幕的视频ID
    video_id = "JyUcmU4CX6g"
    transcript = fetcher.get_transcript(video_id, prefer_language='zh-Hans')

    assert transcript is None


def test_get_transcript_invalid_video():
    """测试获取无效视频ID"""
    fetcher = SubtitleFetcher()
    transcript = fetcher.get_transcript(
        "invalid_video_id", prefer_language='zh-Hans')

    assert transcript is None


if __name__ == '__main__':
    pytest.main([__file__])
