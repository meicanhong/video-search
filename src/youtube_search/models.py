from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class VideoMetadata(BaseModel):
    """YouTube video metadata model"""
    video_id: str = Field(..., description="YouTube video ID")
    title: str = Field(..., description="Video title")
    description: Optional[str] = Field(None, description="Video description")
    published_at: datetime = Field(..., description="Video publish date")
    channel_id: str = Field(..., description="Channel ID")
    channel_title: str = Field(..., description="Channel title")
    duration: str = Field(..., description="Video duration in ISO 8601 format")
    view_count: Optional[int] = Field(None, description="Video view count")
    thumbnail_url: Optional[str] = Field(
        None, description="Video thumbnail URL")


class SearchConfig(BaseModel):
    """Search configuration model"""
    api_key: str = Field(..., description="YouTube Data API key")
    max_results: int = Field(
        50, description="Maximum number of results to return")
    language: Optional[str] = Field(None, description="Result language code")
    region_code: Optional[str] = Field(None, description="Result region code")
    video_duration: Optional[str] = Field(
        None, description="Video duration filter")
    cache_enabled: bool = Field(True, description="Enable result caching")
    cache_ttl: int = Field(3600, description="Cache TTL in seconds")
    retry_count: int = Field(
        3, description="Number of retries for failed requests")
