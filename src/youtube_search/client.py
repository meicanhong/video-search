import logging
from typing import List, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from tenacity import retry, stop_after_attempt, wait_exponential

from .models import SearchConfig, VideoMetadata

logger = logging.getLogger(__name__)


class YouTubeSearchClient:
    """YouTube search client implementation"""

    def __init__(self, config: SearchConfig):
        """Initialize the YouTube search client

        Args:
            config: Search configuration
        """
        self.config = config
        self.youtube = build('youtube', 'v3', developerKey=config.api_key)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    async def search(
        self,
        query: str,
        max_results: Optional[int] = None,
        language: Optional[str] = None
    ) -> List[VideoMetadata]:
        """Search YouTube videos

        Args:
            query: Search query
            max_results: Maximum number of results to return
            language: Result language code

        Returns:
            List of video metadata
        """
        try:
            # Build search request
            search_request = self.youtube.search().list(
                q=query,
                part='snippet',
                maxResults=max_results or self.config.max_results,
                type='video',
                relevanceLanguage=language or self.config.language,
                fields='items(id(videoId),snippet(title,description,channelId,channelTitle,publishedAt))'
            )

            # Execute search request
            search_response = search_request.execute()

            # Get video IDs
            video_ids = [item['id']['videoId']
                         for item in search_response['items']]

            if not video_ids:
                logger.warning(f"No videos found for query: {query}")
                return []

            # Get video details
            videos_request = self.youtube.videos().list(
                part='contentDetails,statistics',
                id=','.join(video_ids),
                fields='items(id,contentDetails(duration),statistics(viewCount))'
            )
            videos_response = videos_request.execute()

            # Create video metadata objects
            results = []
            for search_item, video_item in zip(
                search_response['items'],
                videos_response['items']
            ):
                snippet = search_item['snippet']
                content_details = video_item['contentDetails']
                statistics = video_item.get('statistics', {})

                metadata = VideoMetadata(
                    video_id=search_item['id']['videoId'],
                    title=snippet['title'],
                    description=snippet.get('description'),
                    published_at=snippet['publishedAt'],
                    channel_id=snippet['channelId'],
                    channel_title=snippet['channelTitle'],
                    duration=content_details['duration'],
                    view_count=int(statistics.get('viewCount', 0)),
                    thumbnail_url=snippet.get(
                        'thumbnails', {}).get('high', {}).get('url')
                )
                results.append(metadata)

            return results

        except HttpError as e:
            logger.error(f"YouTube API error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise
