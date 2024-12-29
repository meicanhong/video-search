import axios from 'axios';
import type {
    SearchRequest,
    SearchResponse,
    SessionAnalysisRequest,
    SessionAnalysisResponse,
} from '@/types/api';

const api = axios.create({
    baseURL: '/api',
    timeout: 30000,
});

export const searchVideos = async (params: SearchRequest): Promise<SearchResponse> => {
    const { data } = await api.post<SearchResponse>('/search', params);
    return data;
};

export const analyzeSessionContent = async (
    sessionId: string,
    params: Omit<SessionAnalysisRequest, 'session_id'>
): Promise<SessionAnalysisResponse> => {
    const { data } = await api.post<SessionAnalysisResponse>(
        `/sessions/${sessionId}/analyze`,
        params
    );
    return data;
}; 