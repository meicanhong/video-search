import { useMutation } from 'react-query';
import { message } from 'antd';
import { analyzeSessionContent } from '@/services/api';
import type { VideoClip } from '@/types/api';

interface UseAnalyzeContentOptions {
    onSuccess?: (clips: VideoClip[]) => void;
}

export function useAnalyzeContent({ onSuccess }: UseAnalyzeContentOptions = {}) {
    return useMutation(
        ({ sessionId, query }: { sessionId: string; query: string }) =>
            analyzeSessionContent(sessionId, query),
        {
            onSuccess: (data) => {
                onSuccess?.(data.clips);
            },
            onError: (error) => {
                message.error('分析失败，请重试');
                console.error('Analysis failed:', error);
            },
        }
    );
} 