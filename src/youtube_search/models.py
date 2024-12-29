from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    """搜索请求"""
    keyword: str = Field(..., description="搜索关键词")
    max_results: int = Field(default=3, ge=1, le=10, description="最大返回结果数")


class VideoInfo(BaseModel):
    """视频信息"""
    video_id: str = Field(..., description="视频ID")
    title: str = Field(..., description="视频标题")
    channel_title: str = Field(..., description="频道名称")
    duration: str = Field(..., description="视频时长")
    view_count: int = Field(..., description="观看次数")
    published_at: datetime = Field(..., description="发布时间")
    thumbnail_url: str = Field(..., description="缩略图URL")
    description: str = Field(..., description="视频描述")
    has_subtitles: bool = Field(default=False, description="是否有字幕")
    languages: List[str] = Field(default_factory=list, description="支持的语言列表")


class SearchSummary(BaseModel):
    """搜索结果总结"""
    total_videos: int = Field(..., description="视频总数")
    total_duration: int = Field(..., description="视频总时长(分钟)")
    latest_video_date: datetime = Field(..., description="最新视频日期")
    overview: str = Field(..., description="GPT生成的总体概述")


class SearchResponse(BaseModel):
    """搜索响应"""
    session_id: str = Field(..., description="会话ID")
    search_keyword: str = Field(..., description="搜索关键词")
    summary: SearchSummary = Field(..., description="搜索结果总结")
    videos: List[VideoInfo] = Field(..., description="视频列表")
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="创建时间")
    expires_at: datetime = Field(..., description="过期时间")
