import pytest
import os
from src.youtube_search.openai_client import OpenAIClient


@pytest.mark.asyncio
async def test_gpt4o_analyze():
    """测试 gpt-4o 模型分析字幕"""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        pytest.skip("OpenAI API key not found")

    client = OpenAIClient(api_key)

    # 模拟字幕数据
    subtitles = [
        {"text": "今天我们来讨论熊猫速汇的手续费", "start": 99},
        {"text": "熊猫速汇每笔收费是80人民币", "start": 100},
        {"text": "这个价格相对其他平台来说比较合理", "start": 105}
    ]

    video_info = {
        "title": "海外汇款平台对比",
        "video_id": "test123"
    }

    # 测试分析功能
    result = await client.analyze_subtitle(
        query="熊猫速汇的手续费是多少？",
        subtitles=subtitles,
        video_info=video_info
    )

    # 验证返回结果
    assert result is not None
    assert "clip" in result
    assert "content" in result["clip"]
    assert "timestamp" in result["clip"]
    assert "relevance" in result["clip"]
    assert result["clip"]["relevance"] >= 0.8  # 相关度应该很高


@pytest.mark.asyncio
async def test_gpt4o_answer():
    """测试 gpt-4o 模型生成答案"""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        pytest.skip("OpenAI API key not found")

    client = OpenAIClient(api_key)

    # 模拟相关片段
    clips = [
        {
            "video_title": "海外汇款平台对比",
            "timestamp": "01:40",
            "content": "熊猫速汇每笔收费是80人民币",
            "relevance": 0.95
        }
    ]

    # 测试回答功能
    result = await client.generate_answer(
        query="熊猫速汇的手续费是多少？",
        clips=clips
    )

    # 验证返回结果
    assert result is not None
    assert "summary" in result
    assert "confidence" in result
    assert result["confidence"] >= 0.8  # 可信度应该很高
    assert "80" in result["summary"]  # 答案应该包含具体费用
