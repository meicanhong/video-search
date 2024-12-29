import os
import logging
from typing import List, Dict, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .service import YouTubeService

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="YouTube Search API",
    description="搜索 YouTube 视频并分析内容的 API 服务",
    version="1.0.0"
)

# 初始化服务
try:
    youtube_service = YouTubeService(
        youtube_api_key=os.getenv('YOUTUBE_API_KEY'),
        openai_api_key=os.getenv('OPENAI_API_KEY')
    )
    logger.info("YouTube service initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize YouTube service: {str(e)}")
    raise


class SearchRequest(BaseModel):
    """搜索请求"""
    keyword: str
    max_results: Optional[int] = 10


class QuestionRequest(BaseModel):
    """问题请求"""
    session_id: str
    question: str


class SearchResponse(BaseModel):
    """搜索响应"""
    session_id: str
    search_keyword: str
    video_count: int
    created_at: str


class AnswerResponse(BaseModel):
    """回答响应"""
    answer: Optional[str]
    relevant_clips: List[Dict]


@app.post("/search", response_model=SearchResponse)
async def create_search(request: SearchRequest):
    """创建新的搜索会话

    Args:
        request: 搜索请求参数

    Returns:
        SearchResponse: 搜索会话信息
    """
    try:
        logger.info(f"Creating search session for keyword: {request.keyword}")
        result = await youtube_service.create_search_session(
            keyword=request.keyword,
            max_results=request.max_results
        )
        logger.info(f"Search session created: {result}")
        return result
    except Exception as e:
        logger.error(f"Error creating search session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    """在会话中提问

    Args:
        request: 问题请求参数

    Returns:
        AnswerResponse: 回答和相关视频片段
    """
    try:
        logger.info(
            f"Processing question for session {request.session_id}: {request.question}")
        result = await youtube_service.answer_question(
            session_id=request.session_id,
            question=request.question
        )
        logger.info(f"Answer generated: {result}")
        return result
    except ValueError as e:
        logger.error(f"Session error: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.on_event("shutdown")
def shutdown_event():
    """服务关闭时清理过期会话"""
    try:
        youtube_service.cleanup_expired_sessions()
        logger.info("Expired sessions cleaned up")
    except Exception as e:
        logger.error(f"Error cleaning up sessions: {str(e)}")
