# YouTube Video Search

一个用于搜索 YouTube 视频并获取字幕的工具。

## 功能特点

- YouTube 视频搜索
- 自动获取视频字幕（支持多语言）
- 字幕优先级：人工字幕 > 自动生成字幕 > 翻译字幕
- 支持代理配置

## 项目结构

```
.
├── docs/                  # 文档目录
│   ├── project_overview.md    # 项目概述
│   ├── search_module.md      # 搜索模块设计
│   └── subtitle_module.md    # 字幕模块设计
├── src/                   # 源代码目录
│   └── youtube_search/       # 主要代码包
│       ├── __init__.py
│       ├── client.py         # YouTube API 客户端
│       ├── models.py         # 数据模型
│       ├── service.py        # 服务层
│       ├── subtitle.py       # 字幕处理
│       └── utils.py          # 工具函数
├── tests/                 # 测试代码目录
│   ├── test_search.py        # 搜索功能测试
│   ├── test_service.py       # 服务功能测试
│   └── test_subtitle.py      # 字幕功能测试
├── .env                   # 环境变量配置
├── .gitignore            # Git 忽略文件
├── README.md             # 项目说明
└── requirements.txt      # 项目依赖
```

## 安装

1. 克隆项目：
```bash
git clone [repository_url]
cd youtube-video-search
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 配置环境变量：
创建 `.env` 文件并添加以下内容：
```
YOUTUBE_API_KEY=your_api_key_here
```

## 使用示例

```python
import asyncio
from youtube_search.service import YouTubeService

async def main():
    # 创建服务实例
    service = YouTubeService()
    
    # 搜索视频并获取字幕
    results = await service.search_videos_with_subtitles('搜索关键词')
    
    # 处理结果
    for result in results:
        print(result.format_info())
        if result.subtitle:
            print(result.get_subtitle_text())

if __name__ == '__main__':
    asyncio.run(main())
```

## 测试

运行测试：
```bash
# 运行所有测试
python -m pytest tests/

# 运行特定测试
python -m tests.test_service
python -m tests.test_subtitle
```

## 依赖项

- google-api-python-client==2.108.0
- python-dotenv==1.0.0
- pydantic==2.5.2
- aiohttp==3.9.1
- tenacity==8.2.3
- youtube-transcript-api==0.6.2

## 注意事项

1. 需要有效的 YouTube Data API 密钥
2. 字幕获取依赖于视频是否启用了字幕功能
3. 建议使用代理以提高访问稳定性

## License

MIT License