import os
import asyncio
from dotenv import load_dotenv
from src.youtube_search.models import SearchConfig
from src.youtube_search.client import YouTubeSearchClient
from src.youtube_search.utils import format_duration

# 加载环境变量
load_dotenv()


async def test_search():
    """测试YouTube搜索功能"""
    # 创建搜索配置
    config = SearchConfig(
        api_key=os.getenv('YOUTUBE_API_KEY'),
        max_results=5,
        language='zh'
    )

    # 创建搜索客户端
    client = YouTubeSearchClient(config)

    try:
        # 执行搜索
        print("搜索'小米音箱'相关视频:")
        results = await client.search('小米音箱 评测')

        # 打印结果
        if results:
            for video in results:
                print(f"\n视频标题: {video.title}")
                print(f"频道: {video.channel_title}")
                print(f"时长: {format_duration(video.duration) or '未知'}")
                print(f"观看次数: {video.view_count:,}")
                print(f"链接: https://youtube.com/watch?v={video.video_id}")
                print("-" * 80)
        else:
            print("未找到相关视频")

    except Exception as e:
        print(f"搜索出错: {str(e)}")


if __name__ == '__main__':
    asyncio.run(test_search())
