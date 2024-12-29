# YouTube 视频搜索与分析工具

基于 FastAPI 和 React 的 YouTube 视频搜索和内容分析工具，支持视频搜索、字幕分析和内容总结。

## 功能特点

- **视频搜索**：
  - 基于关键词搜索 YouTube 视频
  - 支持视频元数据获取（标题、时长、观看次数等）
  - 自动生成搜索结果总结

- **字幕处理**：
  - 自动获取视频字幕
  - 支持多语言字幕
  - 智能选择最佳字幕源

- **内容分析**：
  - 基于 GPT 的内容理解和总结
  - 精确定位相关视频片段
  - 提供带时间戳的直达链接

- **用户界面**：
  - 现代化的 React 前端界面
  - 响应式设计
  - 实时内容分析
  - 优雅的过渡动画

## 技术栈

### 后端
- Python 3.8+
- FastAPI
- YouTube Data API v3
- OpenAI GPT API
- structlog 日志系统

### 前端
- React 18
- TypeScript
- Vite
- Ant Design
- TailwindCSS
- React Query

### 开发工具
- Docker & Docker Compose
- Rye 包管理
- Pre-commit hooks
- ESLint & Prettier

## 快速开始

1. 克隆项目
```bash
git clone https://github.com/yourusername/video-search.git
cd video-search
```

2. 配置环境变量
```bash
# 创建 .env 文件
cp .env.example .env

# 编辑 .env 文件，添加必要的 API 密钥
YOUTUBE_API_KEY=your_youtube_api_key
OPENAI_API_KEY=your_openai_api_key
```

3. 使用 Docker 启动服务
```bash
# 构建并启动服务
docker-compose up --build
```

服务将在以下地址启动：
- 前端：http://localhost:3000
- 后端：http://localhost:8000

## 项目结构

```
video-search/
├── src/                      # 后端源代码
│   └── youtube_search/
│       ├── client.py         # YouTube API 客户端
│       ├── models.py         # 数据模型
│       ├── service.py        # 业务逻辑
│       ├── web.py           # Web API
│       ├── subtitle.py      # 字幕处理
│       ├── session.py       # 会话管理
│       ├── openai_client.py # OpenAI API 客户端
│       └── utils.py         # 工具函数
├── frontend/                 # 前端源代码
│   ├── src/
│   │   ├── components/      # React 组件
│   │   ├── hooks/          # 自定义 Hooks
│   │   ├── pages/          # 页面组件
│   │   ├── services/       # API 服务
│   │   ├── types/          # TypeScript 类型
│   │   └── utils/          # 工具函数
│   ├── vite.config.ts      # Vite 配置
│   └── tailwind.config.js  # Tailwind 配置
├── docs/                    # 项目文档
├── docker-compose.yml       # Docker 编排配置
└── Dockerfile              # 后端 Docker 配置
```

## API 接口

### 搜索视频
```http
POST /search
Content-Type: application/json

{
    "keyword": "搜索关键词",
    "max_results": 5
}
```

### 分析内容
```http
POST /sessions/{session_id}/analyze
Content-Type: application/json

{
    "query": "用户问题"
}
```

详细的 API 文档请参考 `docs/api_reference.md`。

## 开发指南

### 后端开发
```bash
# 安装依赖
just install

# 启动开发服务器
just dev

# 格式化代码
just format
```

### 前端开发
```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build
```

## 注意事项

1. API 密钥安全
   - 请妥善保管 API 密钥
   - 不要将 .env 文件提交到版本控制
   - 建议设置 API 密钥使用限制

2. 资源限制
   - YouTube API 有每日配额限制
   - OpenAI API 按使用量计费
   - 建议实现缓存机制

3. 开发建议
   - 遵循代码规范和提交规范
   - 编写单元测试
   - 使用 TypeScript 类型检查

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

## 许可证

MIT License