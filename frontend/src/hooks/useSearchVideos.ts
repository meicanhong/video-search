import { useQuery } from 'react-query';
import { searchVideos } from '@/services/api';
import type { SearchResponse } from '@/types/api';

interface UseSearchVideosOptions {
    onSuccess?: (data: SearchResponse) => void;
}

export function useSearchVideos(keyword: string, { onSuccess }: UseSearchVideosOptions = {}) {
    return useQuery<SearchResponse>(
        ['search', keyword],
        () => searchVideos({ keyword, max_results: 5 }),
        {
            enabled: !!keyword,
            onSuccess,
        }
    );
} 