// 搜索请求
export interface SearchRequest {
    keyword: string;
    max_results?: number;
}

// 视频信息
export interface VideoInfo {
    video_id: string;
    title: string;
    channel_title: string;
    duration: string;
    view_count: number;
    published_at: string;
    thumbnail_url: string;
    description: string;
    has_subtitles: boolean;
}

// 搜索结果总结
export interface SearchSummary {
    total_videos: number;
    overview: string;
}

// 搜索响应
export interface SearchResponse {
    session_id: string;
    keyword: string;
    summary: SearchSummary;
    videos: VideoInfo[];
    created_at: string;
    expires_at: string;
}

// 会话分析请求
export interface SessionAnalysisRequest {
    session_id: string;
    query: string;
}

// 视频片段
export interface VideoClip {
    video_id: string;
    video_title: string;
    content: string;
    timestamp: string;
    relevance: number;
    url: string;
}

// 会话分析响应
export interface SessionAnalysisResponse {
    clips: VideoClip[];
    total_clips: number;
} 