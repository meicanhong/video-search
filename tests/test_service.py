import asyncio
from dotenv import load_dotenv
from src.youtube_search.service import YouTubeService
import json

# 加载环境变量
load_dotenv()


async def test_search_with_subtitles():
    """测试搜索视频并获取字幕的完整流程"""
    # 创建服务实例
    service = YouTubeService()

    try:
        # 搜索视频并获取字幕
        print("搜索'熊猫速汇'相关视频并获取字幕和分析:")
        results = await service.search_videos_with_subtitles(
            query='熊猫速汇 费用',
            prefer_language='zh-Hans',
            analyze_content=True
        )

        # 打印结果
        for i, result in enumerate(results, 1):
            print(f"\n=== 视频 {i} ===")
            print(result.format_info())
            print("=" * 80)

    except Exception as e:
        print(f"错误: {str(e)}")


async def test_search_without_analysis():
    """测试不使用内容分析的搜索"""
    # 创建服务实例
    service = YouTubeService()

    try:
        # 搜索视频并获取字幕（不进行内容分析）
        print("\n搜索视频（不进行内容分析）:")
        results = await service.search_videos_with_subtitles(
            query='熊猫速汇 教程',
            prefer_language='zh-Hans',
            analyze_content=False
        )

        # 打印结果
        for i, result in enumerate(results, 1):
            print(f"\n=== 视频 {i} ===")
            print(result.format_info())

            if result.subtitle:
                print("\n字幕预览（前200字）:")
                print(result.get_subtitle_text()[:200] + "...")
            else:
                print("\n未找到字幕")
            print("=" * 80)

    except Exception as e:
        print(f"错误: {str(e)}")


async def test_search_with_content_analysis():
    """测试带内容分析的搜索功能"""
    print("\n=== 测试1: 带内容分析的搜索 ===")

    # 初始化服务
    service = VideoSearchService()

    # 执行搜索
    print("\n搜索'熊猫速汇'相关视频并获取字幕和分析:")
    results = await service.search_with_content_analysis("熊猫速汇", max_results=5)

    # 验证结果
    assert results is not None
    assert len(results) > 0

    # 打印每个视频的信息和分析结果
    for i, video in enumerate(results, 1):
        print(f"\n=== 视频 {i} ===")
        print(f"标题: {video.get('title', '')}")
        print(f"频道: {video.get('channel', '')}")
        print(f"时长: {video.get('duration', '')}")
        print(f"观看次数: {video.get('views', 0)}")
        print(f"链接: {video.get('link', '')}")

        # 打印内容分析
        analysis = video.get('content_analysis', {})
        if analysis:
            print("\n内容总结:")
            print(analysis.get('summary', '').strip())

            # 打印关键时刻
            key_moments = analysis.get('key_moments', [])
            if key_moments:
                print("\n关键时刻:")
                for moment in key_moments:
                    print(
                        f"[{moment['time']}] {moment['text']} (相关度: {moment['relevance']:.2f})")

            print("\n相关性分析:")
            print(json.dumps(analysis, ensure_ascii=False, indent=4))

        print("=" * 80)


async def test_locate_answer():
    """测试定位问题答案功能"""
    print("\n=== 测试: 定位问题答案 ===")

    # 初始化服务
    service = YouTubeService()

    # 测试问题
    question = "熊猫速汇的手续费是多少？"
    print(f"\n搜索问题: {question}")

    # 执行搜索
    results = await service.search_with_content_analysis(question, max_results=3)

    # 验证结果
    assert results is not None
    assert len(results) > 0

    # 打印每个视频的信息和关键时刻
    for i, video in enumerate(results, 1):
        print(f"\n=== 视频 {i} ===")
        print(f"标题: {video.get('title', '')}")
        print(f"链接: {video.get('link', '')}")

        # 打印关键时刻
        analysis = video.get('content_analysis', {})
        if analysis and analysis.get('key_moments'):
            print("\n相关片段:")
            for moment in analysis['key_moments']:
                print(f"时间点: {moment['time']}")
                print(f"内容: {moment['text']}")
                print(f"相关度: {moment['relevance']:.2f}")
                print(f"直达链接: {moment['direct_link']}")
                print("---")
        else:
            print("\n未找到相关内容")

        print("=" * 80)


async def main():
    """运行所有测试"""
    print("=== 测试1: 定位问题答案 ===")
    await test_locate_answer()


if __name__ == '__main__':
    asyncio.run(main())
