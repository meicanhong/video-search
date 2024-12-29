# YouTube 智能搜索 API

基于 FastAPI 的 YouTube 视频智能搜索服务，支持视频内容分析和精确时间点定位。

## 功能特点

- 🔍 智能视频搜索：基于关键词搜索相关视频
- 📝 字幕处理：支持多语言字幕，包括自动生成和手动字幕
- 🤖 GPT 分析：使用 GPT-4o 模型分析视频内容
- ⏱️ 时间点定位：精确定位到相关内容的时间点
- 🔄 会话管理：支持基于会话的持续对话
- 🌐 RESTful API：标准的 HTTP 接口

## 环境要求

- Python >= 3.8
- [Rye](https://rye-up.com/guide/installation/) 包管理器
- [Just](https://github.com/casey/just) 命令运行器

## 快速开始

1. 克隆项目：
```bash
git clone <repository-url>
cd video-search
```

2. 安装依赖：
```bash
just install
```

3. 配置环境变量：
创建 `.env` 文件：
```bash
# YouTube API 密钥
YOUTUBE_API_KEY=your_youtube_api_key_here

# OpenAI API 密钥
OPENAI_API_KEY=your_openai_api_key_here
```

4. 启动服务：
```bash
just dev
```

服务将在 http://localhost:8000 启动

## API 使用

### 1. 创建搜索会话

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "keyword": "熊猫速汇教程",
    "max_results": 3
  }'
```

返回：
```json
{
  "session_id": "xxx",
  "search_keyword": "熊猫速汇教程",
  "video_count": 3,
  "created_at": "2024-01-20T10:00:00"
}
```

### 2. 在会话中提问

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "xxx",
    "question": "熊猫速汇的手续费是多少？"
  }'
```

返回：
```json
{
  "answer": {
    "summary": "熊猫速汇每笔收取80元人民币的手续费",
    "confidence": 0.95
  },
  "relevant_clips": [
    {
      "video_title": "熊猫速汇使用教程",
      "timestamp": "01:39",
      "content": "熊猫速汇每笔收费是80人民币",
      "relevance": 0.95,
      "direct_link": "https://youtube.com/watch?v=xxx&t=99"
    }
  ]
}
```

## 开发命令

- `just install` - 安装依赖
- `just dev` - 启动开发服务器
- `just test` - 运行测试
- `just format` - 格式化代码
- `just lint` - 运行代码检查
- `just clean` - 清理临时文件

## 项目结构

```
src/youtube_search/
├── __init__.py
├── client.py      # YouTube API 客户端
├── models.py      # 数据模型
├── service.py     # 业务逻辑
├── session.py     # 会话管理
├── subtitle.py    # 字幕处理
├── openai_client.py # GPT 分析
├── utils.py       # 工具函数
└── web.py         # Web API

tests/             # 测试用例
docs/              # 文档
```

## 测试

运行所有测试：
```bash
just test
```

## 贡献

1. Fork 项目
2. 创建特性分支：`git checkout -b feature/amazing-feature`
3. 提交更改：`git commit -m 'Add amazing feature'`
4. 推送分支：`git push origin feature/amazing-feature`
5. 提交 Pull Request

## 许可证

MIT