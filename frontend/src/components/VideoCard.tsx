import type { VideoInfo } from '@/types/api';

interface VideoCardProps {
  video: VideoInfo;
}

export function VideoCard({ video }: VideoCardProps) {
  return (
    <div className="w-full p-4 bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow duration-200">
      <div className="flex gap-3 items-start">
        <img
          src={video.thumbnail_url}
          alt={video.title}
          className="w-32 h-auto rounded-lg object-cover flex-shrink-0"
        />
        <div className="flex flex-col gap-1 flex-1 min-w-0">
          <h3 className="text-lg font-semibold text-primary-700 line-clamp-2">
            {video.title}
          </h3>
          <p className="text-gray-500">{video.channel_title}</p>
          <div className="flex gap-3 text-gray-600">
            <span>时长: {video.duration}</span>
            <span>观看次数: {video.view_count.toLocaleString()}</span>
          </div>
        </div>
      </div>
    </div>
  );
} 