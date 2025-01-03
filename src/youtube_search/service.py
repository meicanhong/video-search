import os
import structlog
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, TypedDict
import uuid
import asyncio

from .client import YouTubeClient
from .models import SearchResponse, SearchSummary, VideoInfo
from .openai_client import OpenAIClient
from .subtitle import SubtitleFetcher
from .session import SearchSession

logger = structlog.get_logger()


class SearchResult(TypedDict):
    """搜索结果"""
    clips: List[Dict]  # 视频片段列表
    answer: str        # LLM回答


class YouTubeService:
    def __init__(self):
        self.youtube_client = YouTubeClient(
            api_key=os.getenv("YOUTUBE_API_KEY", ""))
        self.openai_client = OpenAIClient(
            api_key=os.getenv("OPENAI_API_KEY", ""))
        self.subtitle_fetcher = SubtitleFetcher()
        self.sessions: Dict[str, SearchSession] = {}

    async def _fetch_video_info(self, video) -> Tuple[VideoInfo, List[Dict]]:
        """获取单个视频的信息和字幕

        Args:
            video: YouTube视频信息

        Returns:
            Tuple[VideoInfo, List[Dict]]: 视频信息和字幕列表
        """
        logger.info("fetching_video_info", video_id=video.video_id)

        # 获取字幕信息
        transcript = await self.subtitle_fetcher.get_transcript(video.video_id)
        has_subtitles = transcript is not None

        video_info = VideoInfo(
            video_id=video.video_id,
            title=video.title,
            channel_title=video.channel_title,
            duration=video.duration,
            view_count=video.view_count,
            published_at=video.published_at,
            thumbnail_url=f"https://i.ytimg.com/vi/{video.video_id}/hqdefault.jpg",
            description=video.description,
            has_subtitles=has_subtitles
        )

        subtitles = []
        if transcript:
            subtitles = [{
                "video_id": video.video_id,
                "video_title": video.title,
                **sub
            } for sub in transcript]

        return video_info, (transcript, subtitles)

    async def search_videos(self, keyword: str, max_results: int = 3) -> SearchResponse:
        """搜索视频并创建会话

        Args:
            keyword: 搜索关键词
            max_results: 最大返回结果数

        Returns:
            SearchResponse: 搜索响应
        """
        try:
            # 搜索视频
            logger.info("searching_videos", keyword=keyword,
                        max_results=max_results)
            videos = await self.youtube_client.search_videos(keyword, max_results)

            # 创建会话
            session_id = str(uuid.uuid4())
            session = SearchSession(session_id)
            session.search_keyword = keyword
            self.sessions[session_id] = session

            # 并发获取视频详细信息和字幕
            tasks = [self._fetch_video_info(video) for video in videos]
            results = await asyncio.gather(*tasks)

            video_infos = []
            all_subtitles = []

            # 处理结果
            for video_info, (transcript, subtitles) in results:
                video_infos.append(video_info)
                all_subtitles.extend(subtitles)
                # 存储视频和字幕信息到会话
                session.add_video(video_info.dict(), transcript)

            transcript_text = ""
            for sub in all_subtitles:
                transcript_text += f"[{sub['video_title']}] {sub['text']}\n"

            overview = await self.openai_client.generate_video_sumary(
                transcript=transcript_text,
                max_tokens=300
            )

            # 创建总结
            summary = SearchSummary(
                total_videos=len(video_infos),
                overview=overview if overview else f"找到{len(video_infos)}个相关视频。"
            )

            # 创建响应
            now = datetime.utcnow()
            response = SearchResponse(
                session_id=session_id,
                keyword=keyword,
                summary=summary,
                videos=video_infos,
                created_at=now,
                expires_at=now + timedelta(hours=1)
            )

            logger.info("search_response_created",
                        session_id=session_id,
                        keyword=keyword,
                        total_videos=len(video_infos))
            return response

        except Exception as e:
            logger.error("search_videos_failed",
                         keyword=keyword,
                         error=str(e),
                         exc_info=True)
            raise

    async def _find_relevant_clips_from_session(self, session_id: str, query: str) -> List[Dict]:
        """在会话中查找与问题相关的视频片段

        Args:
            session_id: 会话ID
            query: 用户问题

        Returns:
            List[Dict]: 相关视频片段列表，每个片段包含视频信息和时间点
        """
        logger.info("finding_relevant_clips",
                    session_id=session_id, query=query)
        try:
            # 获取会话
            session = self.sessions.get(session_id)
            if not session:
                raise ValueError(f"Session {session_id} not found")

            if session.is_expired():
                raise ValueError(f"Session {session_id} has expired")

            # 更新最后访问时间
            session.update_last_accessed()

            # 分析每个视频的字幕
            results = []
            for video in session.videos:
                video_id = video["video_id"]
                subtitles = session.subtitles.get(video_id)

                if not subtitles:
                    continue

                # 分析字幕内容
                analysis = await self.openai_client.analyze_subtitle(
                    query=query,
                    subtitles=subtitles,
                    video_info=video
                )

                if analysis and analysis.get("clip"):
                    clip = analysis["clip"]
                    # 添加视频信息
                    result = {
                        "video_id": video_id,
                        "video_title": video["title"],
                        "content": clip["content"],
                        "timestamp": clip["timestamp"],
                        "relevance": clip["relevance"],
                        "url": f"https://youtube.com/watch?v={video_id}&t={self._timestamp_to_seconds(clip['timestamp'])}"
                    }
                    results.append(result)

            # 按相关度排序
            results.sort(key=lambda x: x["relevance"], reverse=True)
            return results

        except Exception as e:
            logger.error("find_relevant_clips_failed",
                         session_id=session_id,
                         query=query,
                         error=str(e),
                         exc_info=True)
            raise

    def _timestamp_to_seconds(self, timestamp: str) -> int:
        """将 MM:SS 格式的时间戳转换为秒数

        Args:
            timestamp: MM:SS 格式的时间戳

        Returns:
            int: 秒数
        """
        try:
            minutes, seconds = map(int, timestamp.split(":"))
            return minutes * 60 + seconds
        except Exception:
            return 0

    async def _answer_question_from_clips(
        self,
        session: SearchSession,
        clips: List[Dict],
        query: str
    ) -> str:
        """基于相关视频片段回答用户问题，如果没有相关片段则使用 LLM 知识回答

        Args:
            session: 会话实例
            clips: 相关视频片段列表
            query: 用户问题

        Returns:
            str: 生成的回答
        """
        logger.info("answering_question_from_clips",
                    session_id=session.session_id,
                    query=query,
                    clips=clips)

        # 收集相关视频的字幕
        relevant_subtitles = []

        if clips:
            for clip in clips:
                video_id = clip["video_id"]
                video_title = clip["video_title"]
                timestamp = clip["timestamp"]

                # 获取视频字幕
                subtitles = session.subtitles.get(video_id, [])
                if not subtitles:
                    continue

                # 将时间戳转换为秒数
                clip_time = self._timestamp_to_seconds(timestamp)

                # 获取片段前后的上下文（前后1分钟）
                context_subtitles = []
                for sub in subtitles:
                    sub_time = int(sub.get("start", 0))
                    if abs(sub_time - clip_time) <= 60:  # 获取片段前后1分钟的内容
                        context_subtitles.append({
                            "video_title": video_title,
                            "text": sub.get("text", ""),
                            "start": sub.get("start", 0)
                        })

                # 按时间排序
                context_subtitles.sort(key=lambda x: x["start"])
                relevant_subtitles.extend(context_subtitles)

        # 构建上下文
        context = ""
        if relevant_subtitles:
            for sub in relevant_subtitles:
                context += f"[{sub['video_title']}] {sub['text']}\n"

            # 生成基于视频内容的回答
            answer = await self.openai_client.answer_question(
                query=query,
                transcript=context,
                max_tokens=500
            )
            if answer:
                return answer

        # 如果没有相关片段或无法基于视频内容回答，使用 LLM 知识回答
        answer = await self.openai_client.answer_question(
            query=query,
            transcript="",  # 空字幕表示使用 LLM 知识回答
            max_tokens=800
        )
        return answer if answer else "抱歉，我无法回答这个问题。"

    async def search_session_content(self, session_id: str, query: str) -> SearchResult:
        """搜索会话内容并生成回答

        Args:
            session_id: 会话ID
            query: 用户问题

        Returns:
            SearchResult: 包含视频片段和LLM回答的搜索结果
        """
        try:
            # 获取会话
            session = self.sessions.get(session_id)
            if not session:
                raise ValueError(f"Session {session_id} not found")

            if session.is_expired():
                raise ValueError(f"Session {session_id} has expired")

            # 更新最后访问时间
            session.update_last_accessed()

            # 1. 先找到相关视频片段
            clips = await self._find_relevant_clips_from_session(session_id, query)

            # 2. 基于相关片段生成回答
            answer = await self._answer_question_from_clips(session, clips, query)

            return SearchResult(
                clips=clips,
                answer=answer
            )

        except Exception as e:
            logger.error("search_session_content_failed",
                         session_id=session_id,
                         query=query,
                         error=str(e),
                         exc_info=True)
            raise
