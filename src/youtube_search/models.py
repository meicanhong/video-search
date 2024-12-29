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


class SessionAnalysisRequest(BaseModel):
    """会话内容分析请求"""
    session_id: str = Field(..., description="会话ID")
    query: str = Field(..., description="用户问题")


class VideoClip(BaseModel):
    """视频片段信息"""
    video_id: str = Field(..., description="视频ID")
    video_title: str = Field(..., description="视频标题")
    content: str = Field(..., description="相关内容")
    timestamp: str = Field(..., description="时间戳（MM:SS格式）")
    relevance: float = Field(..., ge=0, le=1, description="相关度（0-1）")
    url: str = Field(..., description="带时间戳的YouTube直达链接")


class SessionAnalysisResponse(BaseModel):
    """会话内容分析响应"""
    clips: List[VideoClip] = Field(..., description="相关视频片段列表")
    answer: str = Field(..., description="基于视频内容和LLM知识的回答")
