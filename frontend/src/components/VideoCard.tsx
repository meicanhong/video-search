import { Card, Typography } from 'antd';
import type { VideoInfo } from '@/types/api';

const { Text } = Typography;

interface VideoCardProps {
  video: VideoInfo;
}

export function VideoCard({ video }: VideoCardProps) {
  return (
    <Card className="w-full card-hover">
      <div className="flex gap-3 items-start">
        <img
          src={video.thumbnail_url}
          alt={video.title}
          className="w-32 h-auto rounded-lg object-cover flex-shrink-0"
        />
        <div className="flex flex-col gap-1 flex-1 min-w-0">
          <Text strong className="text-lg text-primary-700 line-clamp-2">
            {video.title}
          </Text>
          <Text className="text-gray-500">{video.channel_title}</Text>
          <div className="flex gap-3 text-gray-600">
            <Text>时长: {video.duration}</Text>
            <Text>观看次数: {video.view_count.toLocaleString()}</Text>
          </div>
        </div>
      </div>
    </Card>
  );
} 