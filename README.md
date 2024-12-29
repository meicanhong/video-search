# YouTube Video Search API

这是一个基于 FastAPI 的 Web 服务，用于搜索 YouTube 视频并分析内容。

## 功能特点

- 搜索 YouTube 视频
- 获取视频字幕
- 使用 GPT-4o 分析视频内容
- 基于会话的问答系统

## 安装

1. 确保已安装 [Rye](https://rye-up.com/guide/installation/)

2. 克隆项目并安装依赖：
```bash
git clone <repository-url>
cd video-search
rye sync
```

3. 配置环境变量：
创建 `.env` 文件并填入以下内容：
```
YOUTUBE_API_KEY=your_youtube_api_key
OPENAI_API_KEY=your_openai_api_key
```

## 运行服务

```bash
rye run python src/run.py
```

服务将在 http://localhost:8000 启动。

## API 文档

访问以下地址查看 API 文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 使用示例

1. 创建搜索会话：
```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"keyword": "熊猫速汇教程", "max_results": 3}'
```

2. 在会话中提问：
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"session_id": "your_session_id", "question": "熊猫速汇的手续费是多少？"}'
```

## 开发

1. 运行测试：
```bash
rye run pytest
```

2. 格式化代码：
```bash
rye run black src tests
```

## 许可证

MIT