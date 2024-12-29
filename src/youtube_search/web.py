import os
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .client import YouTubeClient
from .models import SearchRequest, SearchResponse
from .openai_client import OpenAIClient
from .service import YouTubeService

# 初始化 FastAPI 应用
app = FastAPI(
    title="YouTube Search API",
    description="搜索 YouTube 视频并分析内容",
    version="1.0.0"
)

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化服务
youtube_client = YouTubeClient(api_key=os.getenv("YOUTUBE_API_KEY", ""))
openai_client = OpenAIClient(api_key=os.getenv("OPENAI_API_KEY", ""))
youtube_service = YouTubeService(youtube_client, openai_client)


@app.post("/search", response_model=SearchResponse)
async def search_videos(request: SearchRequest) -> SearchResponse:
    """搜索视频并创建会话

    Args:
        request: 搜索请求

    Returns:
        SearchResponse: 搜索响应

    Raises:
        HTTPException: 当搜索失败时抛出异常
    """
    try:
        return await youtube_service.search_videos(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check() -> dict:
    """健康检查接口

    Returns:
        dict: 健康状态
    """
    return {"status": "ok"}
