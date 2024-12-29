import { useState } from 'react';
import { useParams, useLocation, useNavigate } from 'react-router-dom';
import { useMutation } from 'react-query';
import { analyzeSessionContent } from '@/services/api';
import type { SearchResponse, SessionAnalysisResponse, VideoClip } from '@/types/api';

interface LocationState {
  searchResult: SearchResponse;
}

function SessionPage() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const location = useLocation();
  const navigate = useNavigate();
  const { searchResult } = (location.state as LocationState) || {};
  const [query, setQuery] = useState('');
  const [clips, setClips] = useState<VideoClip[]>([]);

  // 如果没有搜索结果，重定向到搜索页面
  if (!searchResult) {
    navigate('/');
    return null;
  }

  // 分析内容
  const { mutate: analyze, isLoading: isAnalyzing } = useMutation(
    (query: string) => analyzeSessionContent(sessionId!, query),
    {
      onSuccess: (data: SessionAnalysisResponse) => {
        setClips(data.clips);
      },
      onError: (error) => {
        alert('分析失败，请重试');
        console.error('Analysis failed:', error);
      },
    }
  );

  // 处理分析
  const handleAnalyze = () => {
    if (!query.trim()) {
      alert('请输入问题');
      return;
    }
    analyze(query);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm fixed w-full z-10">
        <div className="flex items-center h-16 px-4">
          <button
            onClick={() => navigate('/')}
            className="text-primary-700 hover:text-primary-800 flex items-center gap-2"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            返回搜索
          </button>
          <h1 className="text-xl font-bold text-primary-700 ml-4 mb-0">
            视频内容分析
          </h1>
        </div>
      </header>
      <main className="pt-16">
        <div className="flex h-[calc(100vh-64px)]">
          {/* 左侧：提问和分析结果 */}
          <div className="w-1/2 p-8 overflow-y-auto">
            <div className="flex flex-col gap-6 w-full">
              {/* 问答区域 */}
              <div className="bg-white p-6 rounded-lg shadow-sm hover:shadow-md transition-shadow duration-200 sticky top-4">
                <h2 className="text-lg font-bold text-primary-700 mb-4">提问分析</h2>
                <div className="flex gap-2">
                  <input
                    type="text"
                    placeholder="输入你的问题，例如：视频中讲了什么内容？"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    disabled={isAnalyzing}
                    onKeyPress={(e) => e.key === 'Enter' && handleAnalyze()}
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent disabled:bg-gray-100"
                  />
                  <button
                    onClick={handleAnalyze}
                    disabled={isAnalyzing}
                    className={`px-4 py-2 bg-primary-600 text-white rounded-lg flex items-center gap-2 ${
                      isAnalyzing ? 'opacity-75 cursor-not-allowed' : 'hover:bg-primary-700'
                    }`}
                  >
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    {isAnalyzing ? '分析中...' : '分析'}
                  </button>
                </div>
              </div>

              {/* 分析结果 */}
              {clips.length > 0 && (
                <div className="bg-white p-6 rounded-lg shadow-sm hover:shadow-md transition-shadow duration-200">
                  <h2 className="text-lg font-bold text-primary-700 mb-4">相关片段</h2>
                  <div className="flex flex-col gap-4">
                    {clips.map((clip, index) => (
                      <div key={index} className="p-4 bg-white border border-gray-200 rounded-lg hover:shadow-sm transition-shadow duration-200">
                        <div className="flex flex-col gap-2">
                          <div className="flex items-center gap-3 flex-wrap">
                            <span className="font-semibold text-primary-700">{clip.video_title}</span>
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
                              <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
                            </svg>
                            在 YouTube 查看详情
                          </a>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* 右侧：搜索结果概览和视频列表 */}
          <div className="w-1/2 border-l border-gray-200 p-8 overflow-y-auto bg-gray-50">
            <div className="flex flex-col gap-6 w-full">
              {/* 搜索结果概览 */}
              <div className="bg-white p-6 rounded-lg shadow-sm hover:shadow-md transition-shadow duration-200">
                <h2 className="text-lg font-bold text-primary-700 mb-4">搜索结果概览</h2>
                <p className="text-gray-600">{searchResult.summary.overview}</p>
              </div>

              {/* 视频列表 */}
              <div className="bg-white p-6 rounded-lg shadow-sm hover:shadow-md transition-shadow duration-200">
                <h2 className="text-lg font-bold text-primary-700 mb-4">找到的视频</h2>
                <div className="flex flex-col gap-4">
                  {searchResult.videos.map((video, index) => (
                    <div key={index} className="p-4 bg-white border border-gray-200 rounded-lg hover:shadow-sm transition-shadow duration-200">
                      <div className="flex gap-3 items-start">
                        <img
                          src={video.thumbnail_url}
                          alt={video.title}
                          className="w-32 h-auto rounded-lg object-cover flex-shrink-0"
                        />
                        <div className="flex flex-col gap-1 flex-1 min-w-0">
                          <h3 className="text-lg font-semibold text-primary-700 line-clamp-2">{video.title}</h3>
                          <p className="text-gray-500">{video.channel_title}</p>
                          <div className="flex gap-3 text-gray-600">
                            <span>时长: {video.duration}</span>
                            <span>观看次数: {video.view_count.toLocaleString()}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default SessionPage; 