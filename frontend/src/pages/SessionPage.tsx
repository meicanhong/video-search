import { useState } from 'react';
import { useParams, useLocation, useNavigate } from 'react-router-dom';
import { Layout, Input, Button, List, Card, Typography, Space, message } from 'antd';
import { SearchOutlined, QuestionCircleOutlined, ArrowLeftOutlined } from '@ant-design/icons';
import { useMutation } from 'react-query';
import { analyzeSessionContent } from '@/services/api';
import type { SearchResponse, SessionAnalysisResponse, VideoClip } from '@/types/api';

const { Header, Content } = Layout;
const { Title, Paragraph, Text } = Typography;

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
        message.error('分析失败，请重试');
        console.error('Analysis failed:', error);
      },
    }
  );

  // 处理分析
  const handleAnalyze = () => {
    if (!query.trim()) {
      message.warning('请输入问题');
      return;
    }
    analyze(query);
  };

  return (
    <Layout className="min-h-screen bg-gray-50">
      <Header className="bg-white shadow-sm fixed w-full z-10">
        <div className="flex items-center h-full px-4">
          <Button
            type="link"
            icon={<ArrowLeftOutlined />}
            onClick={() => navigate('/')}
            className="text-primary-700"
          >
            返回搜索
          </Button>
          <Title level={3} className="my-4 text-primary-700 ml-4 mb-0">
            视频内容分析
          </Title>
        </div>
      </Header>
      <Content className="pt-16">
        <div className="flex h-[calc(100vh-64px)]">
          {/* 左侧：提问和分析结果 */}
          <div className="w-1/2 p-8 overflow-y-auto">
            <Space direction="vertical" size="large" className="w-full">
              {/* 问答区域 */}
              <Card className="card-hover sticky top-4">
                <Title level={4} className="text-primary-700 mb-4">提问分析</Title>
                <div className="flex gap-2">
                  <Input
                    placeholder="输入你的问题，例如：视频中讲了什么内容？"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    disabled={isAnalyzing}
                    className="flex-1"
                    onPressEnter={handleAnalyze}
                  />
                  <Button
                    type="primary"
                    icon={<QuestionCircleOutlined />}
                    loading={isAnalyzing}
                    onClick={handleAnalyze}
                  >
                    分析
                  </Button>
                </div>
              </Card>

              {/* 分析结果 */}
              {clips.length > 0 && (
                <Card className="card-hover">
                  <Title level={4} className="text-primary-700 mb-4">相关片段</Title>
                  <List
                    dataSource={clips}
                    renderItem={(clip) => (
                      <List.Item>
                        <Card className="w-full card-hover">
                          <div className="flex flex-col gap-2">
                            <div className="flex items-center gap-3 flex-wrap">
                              <Text strong className="text-primary-700">{clip.video_title}</Text>
                              <Text className="text-gray-500">时间点: {clip.timestamp}</Text>
                              <Text className="text-gray-500">
                                相关度: {(clip.relevance * 100).toFixed(0)}%
                              </Text>
                            </div>
                            <Paragraph className="text-gray-600 mb-2">{clip.content}</Paragraph>
                            <Button
                              type="link"
                              href={clip.url}
                              target="_blank"
                              className="text-primary-500 hover:text-primary-600 p-0 flex items-center gap-2"
                            >
                              <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                                <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
                              </svg>
                              在 YouTube 查看详情
                            </Button>
                          </div>
                        </Card>
                      </List.Item>
                    )}
                    className="flex flex-col gap-2"
                  />
                </Card>
              )}
            </Space>
          </div>

          {/* 右侧：搜索结果概览和视频列表 */}
          <div className="w-1/2 border-l border-gray-200 p-8 overflow-y-auto bg-gray-50">
            <Space direction="vertical" size="large" className="w-full">
              {/* 搜索结果概览 */}
              <Card className="card-hover">
                <Title level={4} className="text-primary-700 mb-4">搜索结果概览</Title>
                <Paragraph className="text-gray-600">{searchResult.summary.overview}</Paragraph>
              </Card>

              {/* 视频列表 */}
              <Card className="card-hover">
                <Title level={4} className="text-primary-700 mb-4">找到的视频</Title>
                <List
                  dataSource={searchResult.videos}
                  renderItem={(video) => (
                    <List.Item>
                      <Card className="w-full card-hover">
                        <div className="flex gap-3 items-start">
                          <img
                            src={video.thumbnail_url}
                            alt={video.title}
                            className="w-32 h-auto rounded-lg object-cover flex-shrink-0"
                          />
                          <div className="flex flex-col gap-1 flex-1 min-w-0">
                            <Text strong className="text-lg text-primary-700 line-clamp-2">{video.title}</Text>
                            <Text className="text-gray-500">{video.channel_title}</Text>
                            <div className="flex gap-3 text-gray-600">
                              <Text>时长: {video.duration}</Text>
                              <Text>观看次数: {video.view_count.toLocaleString()}</Text>
                            </div>
                          </div>
                        </div>
                      </Card>
                    </List.Item>
                  )}
                  className="flex flex-col gap-2"
                />
              </Card>
            </Space>
          </div>
        </div>
      </Content>
    </Layout>
  );
}

export default SessionPage; 