# YouTube 视频搜索与分析服务

基于 FastAPI 的 YouTube 视频搜索和内容分析服务，支持视频搜索、字幕获取和内容分析等功能。

## 功能特点

- 视频搜索：根据关键词搜索 YouTube 视频
- 字幕获取：支持获取视频的自动生成字幕和手动上传字幕
- 内容分析：使用 GPT 模型分析视频内容，生成摘要和关键点
- 会话管理：支持创建搜索会话，存储搜索结果和字幕内容
- 直达链接：提供带时间戳的 YouTube 视频直达链接

## 环境要求

- Python >= 3.8
- [Rye](https://rye-up.com/guide/installation/) 包管理工具

## 快速开始

1. 克隆项目
```bash
git clone https://github.com/yourusername/video-search.git
cd video-search
```

2. 配置环境变量
```bash
# 创建 .env 文件并添加以下内容
YOUTUBE_API_KEY=your_youtube_api_key
OPENAI_API_KEY=your_openai_api_key
```

3. 安装依赖
```bash
just install
```

4. 启动服务
```bash
just dev
```

服务将在 http://localhost:8001 启动。

## API 接口

### 搜索视频

```bash
curl -X POST "http://localhost:8001/search" \
     -H "Content-Type: application/json" \
     -d '{
       "keyword": "搜索关键词",
       "max_results": 3
     }'
```

响应示例：
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "search_keyword": "搜索关键词",
  "summary": {
    "total_videos": 3,
    "total_duration": 45,
    "latest_video_date": "2024-01-15T10:00:00Z",
    "overview": "找到3个相关视频，总时长约45分钟..."
  },
  "videos": [
    {
      "video_id": "video_id_1",
      "title": "视频标题",
      "channel_title": "频道名称",
      "duration": "15分钟",
      "view_count": 12000,
      "published_at": "2024-01-15T10:00:00Z",
      "thumbnail_url": "https://i.ytimg.com/vi/video_id_1/hqdefault.jpg",
      "description": "视频描述",
      "has_subtitles": true,
      "languages": ["zh-Hans", "en"]
    }
  ],
  "created_at": "2024-01-20T10:00:00Z",
  "expires_at": "2024-01-20T11:00:00Z"
}
```

### 健康检查

```bash
curl "http://localhost:8001/health"
```

## 项目管理

- 安装依赖：`just install`
- 启动服务：`just dev`
- 同步依赖：`just sync`
- 更新项目：`just update`
- 格式化代码：`just format`

## 开发工具

- FastAPI: Web 框架
- Rye: Python 包管理
- pre-commit: Git 提交前的代码检查
- black/isort/ruff: 代码格式化和检查

## 目录结构

```
video-search/
├── src/
│   └── youtube_search/
│       ├── client.py      # YouTube API 客户端
│       ├── models.py      # 数据模型
│       ├── service.py     # 业务逻辑
│       ├── web.py         # Web API
│       ├── subtitle.py    # 字幕处理
│       ├── session.py     # 会话管理
│       └── openai_client.py # OpenAI API 客户端
├── docs/                  # 文档
├── .env                   # 环境变量
├── .justfile             # 项目管理命令
└── pyproject.toml        # 项目配置
```

## 注意事项

1. 确保 YouTube API 密钥和 OpenAI API 密钥配置正确
2. 会话有效期为 1 小时
3. 视频搜索结果最多返回 10 个
4. 字幕获取可能受 YouTube 限制影响

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 发起 Pull Request

## 许可证

MIT License