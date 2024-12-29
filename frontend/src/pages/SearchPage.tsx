import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation } from 'react-query';
import { searchVideos } from '@/services/api';
import type { SearchResponse } from '@/types/api';

function SearchPage() {
  const [keyword, setKeyword] = useState('');
  const navigate = useNavigate();

  const { mutate: search, isLoading } = useMutation(
    (searchKeyword: string) => searchVideos({ keyword: searchKeyword, max_results: 5 }),
    {
      onSuccess: (data: SearchResponse) => {
        navigate(`/session/${data.session_id}`, {
          state: { searchResult: data }
        });
      },
    }
  );

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (!keyword.trim()) {
      alert('请输入搜索关键词');
      return;
    }
    search(keyword.trim());
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      {/* 导航栏 */}
      <nav className="bg-white/80 backdrop-blur-md fixed w-full z-10 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-2">
              <svg className="w-8 h-8 text-primary-600" viewBox="0 0 24 24" fill="currentColor">
                <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814z"/>
              </svg>
              <span className="text-xl font-bold text-gray-900">Video Search</span>
            </div>
            <div className="flex items-center gap-4">
              <a href="https://github.com/yourusername/video-search" target="_blank" rel="noopener noreferrer" 
                className="text-gray-500 hover:text-gray-700 transition-colors">
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/>
                </svg>
              </a>
            </div>
          </div>
        </div>
      </nav>

      {/* 主要内容 */}
      <main className="pt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          {/* 标题区域 */}
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              <span className="text-primary-600">智能</span>搜索与分析
              <br />
              <span className="text-primary-600">YouTube</span> 视频内容
            </h1>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              基于 AI 的视频内容分析工具，帮助你快速找到感兴趣的视频片段，提供智能摘要和关键信息提取。
            </p>
          </div>

          {/* 搜索区域 */}
          <div className="w-1/2 mx-auto mb-16">
            <form onSubmit={handleSearch}>
              <div className="relative w-full">
                {/* 搜索图标 */}
                <div className="absolute inset-y-0 left-0 flex items-center pl-4 pointer-events-none">
                  <svg className="w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </div>

                {/* 输入框 */}
                <input
                  type="text"
                  value={keyword}
                  onChange={(e) => setKeyword(e.target.value)}
                  placeholder="输入关键词搜索视频..."
                  className="w-full h-[46px] pl-10 bg-white
                    border border-primary-300 rounded-full
                    text-[15px] placeholder:text-gray-400
                    focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500
                    transition-colors duration-200"
                />

                {/* 搜索按钮 */}
                <div className="absolute inset-y-0 right-0 flex items-center pr-1">
                  <button
                    type="submit"
                    disabled={isLoading}
                    className={`
                      h-[34px] px-6 rounded-full
                      text-sm font-medium
                      transition-colors duration-200
                      ${isLoading 
                        ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                        : 'bg-primary-500 text-white hover:bg-primary-600 active:bg-primary-700'
                      }
                    `}
                  >
                    {isLoading ? (
                      <div className="flex items-center gap-2">
                        <svg className="animate-spin w-4 h-4" viewBox="0 0 24 24" fill="none">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                        </svg>
                        <span>搜索中</span>
                      </div>
                    ) : '搜索'}
                  </button>
                </div>
              </div>

              {/* 提示文本 */}
              <div className="mt-2 ml-4 text-sm text-gray-500">
                例如：搜索 "编程教程"、"烹饪技巧" 等
              </div>
            </form>
          </div>

          {/* 功能特点 */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-white p-6 rounded-xl shadow-sm">
              <div className="w-12 h-12 bg-primary-50 rounded-lg flex items-center justify-center text-primary-600 mb-4">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">智能搜索</h3>
              <p className="text-gray-600">基于语义的智能搜索，快速定位相关视频内容</p>
            </div>

            <div className="bg-white p-6 rounded-xl shadow-sm">
              <div className="w-12 h-12 bg-primary-50 rounded-lg flex items-center justify-center text-primary-600 mb-4">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">内容总结</h3>
              <p className="text-gray-600">自动生成视频内容摘要，快速了解核心内容</p>
            </div>

            <div className="bg-white p-6 rounded-xl shadow-sm">
              <div className="w-12 h-12 bg-primary-50 rounded-lg flex items-center justify-center text-primary-600 mb-4">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">时间轴定位</h3>
              <p className="text-gray-600">精确定位视频片段，直达感兴趣的内容</p>
            </div>

            <div className="bg-white p-6 rounded-xl shadow-sm">
              <div className="w-12 h-12 bg-primary-50 rounded-lg flex items-center justify-center text-primary-600 mb-4">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5C11.783 10.77 8.07 15.61 3 18.129" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">多语言支持</h3>
              <p className="text-gray-600">支持多语言视频内容的智能分析</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default SearchPage; 