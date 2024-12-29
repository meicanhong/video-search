# API 参考文档

## 1. 搜索视频接口

用于搜索 YouTube 视频并创建会话。

### 请求

- 路径: `/search`
- 方法: `POST`
- Content-Type: `application/json`

#### 请求体

```json
{
    "keyword": "搜索关键词",
    "max_results": 3  // 可选，默认为3，范围1-10
}
```

### 响应

```json
{
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "keyword": "搜索关键词",
    "summary": {
        "total_videos": 3,
        "overview": "视频内容总结..."
    },
    "videos": [
        {
            "video_id": "video123",
            "title": "视频标题",
            "channel_title": "频道名称",
            "duration": "10分钟",
            "view_count": 1000,
            "published_at": "2024-01-20T10:00:00Z",
            "thumbnail_url": "https://i.ytimg.com/vi/video123/hqdefault.jpg",
            "description": "视频描述",
            "has_subtitles": true
        }
    ],
    "created_at": "2024-01-20T10:00:00Z",
    "expires_at": "2024-01-20T11:00:00Z"
}
```

### 错误响应

- 500: 服务器内部错误
  ```json
  {
      "detail": "错误信息"
  }
  ```

## 2. 会话内容分析接口

基于已创建的会话分析用户问题，找到相关视频片段。

### 请求

- 路径: `/sessions/{session_id}/analyze`
- 方法: `POST`
- Content-Type: `application/json`

#### 请求体

```json
{
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "query": "用户问题"
}
```

### 响应

```json
{
    "clips": [
        {
            "video_id": "video123",
            "video_title": "视频标题",
            "content": "相关内容片段",
            "timestamp": "01:23",  // MM:SS格式
            "relevance": 0.95,     // 0-1之间的相关度
            "url": "https://youtube.com/watch?v=video123&t=83"  // 带时间戳的直达链接
        }
    ],
    "total_clips": 1
}
```

### 错误响应

- 404: 会话不存在或已过期
  ```json
  {
      "detail": "Session xxx not found"
  }
  ```
- 500: 服务器内部错误
  ```json
  {
      "detail": "错误信息"
  }
  ```

## 注意事项

1. 会话有效期为 1 小时
2. 搜索结果最多返回 10 个视频
3. 分析结果按相关度（relevance）从高到低排序
4. 时间戳使用 MM:SS 格式
5. 视频直达链接会自动定位到相关内容的时间点 