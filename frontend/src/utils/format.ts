/**
 * 格式化数字为带千分位的字符串
 */
export function formatNumber(num: number): string {
    return num.toLocaleString('zh-CN');
}

/**
 * 格式化相关度为百分比
 */
export function formatRelevance(relevance: number): string {
    return `${(relevance * 100).toFixed(0)}%`;
}

/**
 * 生成带时间戳的 YouTube 视频链接
 */
export function generateVideoUrl(videoId: string, timestamp: string): string {
    const seconds = timestampToSeconds(timestamp);
    return `https://youtube.com/watch?v=${videoId}&t=${seconds}`;
}

/**
 * 将 MM:SS 格式的时间戳转换为秒数
 */
export function timestampToSeconds(timestamp: string): number {
    const [minutes, seconds] = timestamp.split(':').map(Number);
    return minutes * 60 + seconds;
} 