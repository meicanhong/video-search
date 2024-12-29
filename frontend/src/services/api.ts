/// <reference types="vite/client" />

import axios from 'axios';
import type {
    SearchRequest,
    SearchResponse,
    SessionAnalysisResponse,
} from '@/types/api';


const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8001';


const api = axios.create({
    baseURL: BACKEND_URL,
    timeout: 30000,
});

export const searchVideos = async (params: SearchRequest): Promise<SearchResponse> => {
    const { data } = await api.post<SearchResponse>('/search', params);
    return data;
};

export const analyzeSessionContent = async (
    sessionId: string,
    query: string
): Promise<SessionAnalysisResponse> => {
    const { data } = await api.post<SessionAnalysisResponse>(
        `/sessions/${sessionId}/analyze`,
        {
            session_id: sessionId,
            query
        }
    );
    return data;
}; 