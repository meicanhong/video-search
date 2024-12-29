import pytest
import asyncio
from dotenv import load_dotenv
from src.youtube_search.openai_client import OpenAIClient

# 加载环境变量
load_dotenv()


@pytest.mark.asyncio
async def test_analyze_subtitle():
    """测试字幕内容分析"""
    client = OpenAIClient()

    # 测试字幕文本
    subtitle_text = """
    大家好啊, 一个香港银行的账户, 可以帮你给美股港股入金, 也可以帮你去买利率很高的美元定存,
    还可以作为资金的枢纽, 帮你的钱在全球流通, 那如果你的主要资金是在中国大陆,
    怎么合法合规的汇款到香港的银行账户呢, 我们用到最多的方式就是银行电汇,
    但你可能也听说过有个产品叫做熊猫速汇, 说能够提供更好的服务, 能够更快更便宜的完成汇款。
    """

    # 测试查询
    query = "熊猫速汇和银行电汇的区别"

    # 分析内容
    result = await client.analyze_subtitle(query, subtitle_text)

    # 验证结果
    assert isinstance(result, str)
    assert len(result) > 0


@pytest.mark.asyncio
async def test_summarize_subtitles():
    """测试字幕内容总结"""
    client = OpenAIClient()

    # 测试字幕数据
    subtitles = [
        {
            "text": "大家好啊, 一个香港银行的账户",
            "start": 0.0,
            "duration": 2.0
        },
        {
            "text": "可以帮你给美股港股入金",
            "start": 2.0,
            "duration": 2.0
        },
        {
            "text": "也可以帮你去买利率很高的美元定存",
            "start": 4.0,
            "duration": 2.0
        }
    ]

    # 总结内容
    result = await client.summarize_subtitles(subtitles)

    # 验证结果
    assert isinstance(result, str)
    assert len(result) > 0


if __name__ == '__main__':
    asyncio.run(pytest.main([__file__]))
