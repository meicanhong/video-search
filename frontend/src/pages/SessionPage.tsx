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
  const [answer, setAnswer] = useState<string>('');

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
        setAnswer(data.answer);
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
      {/* 顶部导航 */}
      <header className="bg-white shadow-sm fixed w-full z-10">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex items-center h-16">
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
        </div>
      </header>

      {/* 主要内容 */}
      <main className="pt-20 pb-8 px-4">
        <div className="max-w-7xl mx-auto">
          {/* 问答区域 */}
          <div className="mb-6">
            <div className="bg-white p-4 rounded-lg shadow-sm">
              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="输入你的问题，例如：视频中讲了什么内容？"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  disabled={isAnalyzing}
                  onKeyPress={(e) => e.key === 'Enter' && handleAnalyze()}
                  className="flex-1 px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-1 focus:ring-primary-500 focus:border-transparent disabled:bg-gray-100"
                />
                <button
                  onClick={handleAnalyze}
                  disabled={isAnalyzing}
                  className={`px-3 py-1.5 bg-primary-600 text-white text-sm rounded-lg flex items-center gap-1.5 ${
                    isAnalyzing ? 'opacity-75 cursor-not-allowed' : 'hover:bg-primary-700'
                  }`}
                >
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  {isAnalyzing ? '分析中...' : '分析'}
                </button>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* 分析结果 */}
            <div className="flex flex-col gap-4">
              {/* AI 回答 */}
              {answer && (
                <div className="bg-white p-4 rounded-lg shadow-sm">
                  <h2 className="text-base font-bold text-primary-700 mb-3">AI 回答</h2>
                  <div className="prose prose-sm max-w-none">
                    {answer.split('\n').map((line, index) => (
                      <p key={index} className="text-sm text-gray-600 mb-2">
                        {line}
                      </p>
                    ))}
                  </div>
                </div>
              )}

              {/* 相关片段 */}
              {clips.length > 0 && (
                <div className="bg-white p-4 rounded-lg shadow-sm">
                  <h2 className="text-base font-bold text-primary-700 mb-2">相关片段</h2>
                  <div className="flex flex-col gap-2">
                    {clips.map((clip, index) => (
                      <a
                        key={index}
                        href={clip.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="block px-3 py-2 bg-white border border-gray-200 rounded-lg hover:shadow-sm hover:border-primary-200 transition-all duration-200 no-underline group"
                      >
                        <div className="flex flex-col gap-1">
                          <h3 className="text-sm font-medium text-gray-900 group-hover:text-primary-800 mb-0 line-clamp-1">
                            {clip.video_title}
                          </h3>
                          <p className="text-sm text-gray-500 mb-0 whitespace-pre-wrap">
                            [{clip.timestamp}] {clip.content}
                          </p>
                        </div>
                      </a>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* 搜索结果概览和视频列表 */}
            <div className="flex flex-col gap-4">
              {/* 搜索结果概览 */}
              <div className="bg-white p-4 rounded-lg shadow-sm">
                <h2 className="text-base font-bold text-primary-700 mb-2">搜索结果概览</h2>
                <p className="text-sm text-gray-600">{searchResult.summary.overview}</p>
              </div>

              {/* 视频列表 */}
              <div className="lg:col-span-2 max-w-2xl mx-auto w-full">
                <div className="bg-white p-4 rounded-lg shadow-sm">
                  <h2 className="text-base font-bold text-primary-700 mb-3">找到的视频</h2>
                  <div className="grid grid-cols-1 gap-4">
                    {searchResult.videos.map((video, index) => (
                      <a
                        key={index}
                        href={`https://www.youtube.com/watch?v=${video.video_id}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="group block bg-white hover:bg-gray-50 transition-colors duration-200 no-underline"
                      >
                        <div className="flex gap-3">
                          {/* 缩略图容器 */}
                          <div className="relative aspect-video w-40 flex-shrink-0 rounded-lg overflow-hidden bg-gray-100">
                            <img
                              src={video.thumbnail_url}
                              alt={video.title}
                              className="absolute inset-0 w-full h-full object-cover"
                            />
                            {/* 持续时间标签 */}
                            <div className="absolute bottom-1 right-1 bg-black/80 text-white text-xs px-1 py-0.5 rounded leading-none">
                              {video.duration}
                            </div>
                          </div>

                          {/* 视频信息 */}
                          <div className="flex-1 min-w-0 py-0.5">
                            <h3 className="text-sm font-medium text-gray-900 line-clamp-2 group-hover:text-primary-600">
                              {video.title}
                            </h3>
                            <div className="mt-1 flex flex-col text-xs text-gray-500">
                              <span>{video.channel_title}</span>
                              <div className="flex items-center gap-1">
                                <span>{video.view_count.toLocaleString()} 次观看</span>
                                <span className="inline-block w-1 h-1 rounded-full bg-gray-300"></span>
                                <span>{new Date(video.published_at).toLocaleDateString()}</span>
                              </div>
                            </div>
                            <p className="mt-1 text-xs text-gray-500 line-clamp-1">
                              {video.description}
                            </p>
                          </div>
                        </div>
                      </a>
                    ))}
                  </div>
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