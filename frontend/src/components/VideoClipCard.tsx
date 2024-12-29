import type { VideoClip } from '@/types/api';

interface VideoClipCardProps {
  clip: VideoClip;
}

export function VideoClipCard({ clip }: VideoClipCardProps) {
  return (
    <div className="w-full p-4 bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow duration-200">
      <div className="flex flex-col gap-2">
        <div className="flex items-center gap-3 flex-wrap">
          <span className="font-semibold text-primary-700">
            {clip.video_title}
          </span>
          <span className="text-gray-500">时间点: {clip.timestamp}</span>
          <span className="text-gray-500">
            相关度: {(clip.relevance * 100).toFixed(0)}%
          </span>
        </div>
        <p className="text-gray-600 mb-2">{clip.content}</p>
        <a
          href={clip.url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-primary-500 hover:text-primary-600 inline-flex items-center gap-2 no-underline"
        >
          <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
            <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z" />
          </svg>
          在 YouTube 查看详情
        </a>
      </div>
    </div>
  );
} 