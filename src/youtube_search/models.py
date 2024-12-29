from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    """搜索请求"""
    keyword: str = Field(..., description="搜索关键词")
    max_results: int = Field(default=3, ge=1, le=10, description="返回结果数量")


class VideoInfo(BaseModel):
    """视频信息"""
    video_id: str
    title: str
    channel_title: str
    duration: str
    view_count: int
    published_at: datetime
    thumbnail_url: str
    description: str
    has_subtitles: bool


class SearchSummary(BaseModel):
    """搜索结果总结"""
    total_videos: int
    overview: str


class SearchResponse(BaseModel):
    """搜索响应"""
    session_id: str
    keyword: str
    summary: SearchSummary
    videos: List[VideoInfo]
    created_at: datetime
    expires_at: datetime
