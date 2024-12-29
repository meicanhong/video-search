import os
import structlog
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .models import SearchRequest, SearchResponse, SessionAnalysisRequest, SessionAnalysisResponse, VideoClip
from .service import YouTubeService

logger = structlog.get_logger()

# 初始化 FastAPI 应用
app = FastAPI(
    title="YouTube Video Search API",
    description="Search and analyze YouTube videos",
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
youtube_service = YouTubeService()


@app.post("/search", response_model=SearchResponse)
async def search_videos(request: SearchRequest) -> SearchResponse:
    """搜索视频并创建会话"""
    try:
        logger.info("search_request_received",
                    keyword=request.keyword,
                    max_results=request.max_results)

        result = await youtube_service.search_videos(
            keyword=request.keyword,
            max_results=request.max_results
        )

        logger.info("search_completed",
                    keyword=request.keyword,
                    total_videos=len(result.videos))
        return result

    except Exception as e:
        logger.error("search_failed",
                     keyword=request.keyword,
                     error=str(e),
                     exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check() -> dict:
    """健康检查接口"""
    logger.info("health_check_called")
    return {"status": "healthy"}


@app.post("/sessions/{session_id}/analyze", response_model=SessionAnalysisResponse)
async def search_session_content(request: SessionAnalysisRequest) -> SessionAnalysisResponse:
    """分析会话内容，找到与问题相关的视频片段并生成回答"""
    try:
        logger.info("analyze_request_received",
                    session_id=request.session_id,
                    query=request.query)

        result = await youtube_service.search_session_content(
            session_id=request.session_id,
            query=request.query
        )

        # 转换为响应模型
        clips = [VideoClip(**clip) for clip in result["clips"]]
        response = SessionAnalysisResponse(
            clips=clips,
            answer=result["answer"]
        )

        logger.info("analyze_completed",
                    session_id=request.session_id,
                    total_clips=len(clips))
        return response

    except ValueError as e:
        logger.error("analyze_failed_invalid_session",
                     session_id=request.session_id,
                     error=str(e))
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("analyze_failed",
                     session_id=request.session_id,
                     error=str(e),
                     exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
