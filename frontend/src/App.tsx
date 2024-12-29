import { useState } from 'react';
import { Layout, Input, Button, List, Card, Typography, Space, message } from 'antd';
import { SearchOutlined, QuestionCircleOutlined } from '@ant-design/icons';
import { useQuery, useMutation } from 'react-query';
import { searchVideos, analyzeSessionContent } from '@/services/api';
import type { SearchResponse, SessionAnalysisResponse, VideoClip } from '@/types/api';

const { Header, Content } = Layout;
const { Search } = Input;
const { Title, Paragraph, Text } = Typography;

function App() {
  const [keyword, setKeyword] = useState('');
  const [sessionId, setSessionId] = useState('');
  const [query, setQuery] = useState('');
  const [clips, setClips] = useState<VideoClip[]>([]);

  // 搜索视频
  const { data: searchResult, isLoading: isSearching } = useQuery<SearchResponse>(
    ['search', keyword],
    () => searchVideos({ keyword, max_results: 5 }),
    {
      enabled: !!keyword,
      onSuccess: (data) => {
        setSessionId(data.session_id);
        setClips([]);
      },
    }
  );

  // 分析内容
  const { mutate: analyze, isLoading: isAnalyzing } = useMutation(
    (query: string) => analyzeSessionContent(sessionId, { query }),
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

  // 处理搜索
  const handleSearch = (value: string) => {
    if (!value.trim()) {
      message.warning('请输入搜索关键词');
      return;
    }
    setKeyword(value);
  };

  // 处理分析
  const handleAnalyze = () => {
    if (!sessionId) {
      message.warning('请先搜索视频');
      return;
    }
    if (!query.trim()) {
      message.warning('请输入问题');
      return;
    }
    analyze(query);
  };

  return (
    <Layout className="min-h-screen bg-gray-50">
      <Header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <Title level={3} className="my-4 text-primary-700">
            YouTube 视频搜索与分析
          </Title>
        </div>
      </Header>
      <Content className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Space direction="vertical" size="large" className="w-full">
          {/* 搜索区域 */}
          <Card className="card-hover">
            <Search
              placeholder="输入关键词搜索视频"
              enterButton={<><SearchOutlined /> 搜索</>}
              size="large"
              loading={isSearching}
              onSearch={handleSearch}
              className="max-w-2xl mx-auto"
            />
          </Card>

          {/* 搜索结果 */}
          {searchResult && (
            <Card className="card-hover">
              <Title level={4} className="text-primary-700 mb-6">搜索结果</Title>
              <Paragraph className="text-gray-600 mb-8">{searchResult.summary.overview}</Paragraph>
              <List
                dataSource={searchResult.videos}
                renderItem={(video) => (
                  <List.Item>
                    <Card className="w-full card-hover">
                      <div className="flex gap-6">
                        <img
                          src={video.thumbnail_url}
                          alt={video.title}
                          className="w-48 h-auto rounded-lg object-cover"
                        />
                        <div className="flex flex-col gap-2">
                          <Text strong className="text-lg text-primary-700">{video.title}</Text>
                          <Text className="text-gray-500">{video.channel_title}</Text>
                          <div className="flex gap-4 text-gray-600">
                            <Text>时长: {video.duration}</Text>
                            <Text>观看次数: {video.view_count.toLocaleString()}</Text>
                          </div>
                        </div>
                      </div>
                    </Card>
                  </List.Item>
                )}
                className="flex flex-col gap-4"
              />
            </Card>
          )}

          {/* 问答区域 */}
          {sessionId && (
            <Card className="card-hover">
              <Title level={4} className="text-primary-700 mb-6">视频内容分析</Title>
              <div className="flex gap-4 max-w-2xl mx-auto">
                <Input
                  placeholder="输入你的问题"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  disabled={isAnalyzing}
                  className="flex-1"
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
          )}

          {/* 分析结果 */}
          {clips.length > 0 && (
            <Card className="card-hover">
              <Title level={4} className="text-primary-700 mb-6">相关片段</Title>
              <List
                dataSource={clips}
                renderItem={(clip) => (
                  <List.Item>
                    <Card className="w-full card-hover">
                      <div className="flex flex-col gap-3">
                        <div className="flex items-center gap-4">
                          <Text strong className="text-primary-700">{clip.video_title}</Text>
                          <Text className="text-gray-500">时间点: {clip.timestamp}</Text>
                          <Text className="text-gray-500">
                            相关度: {(clip.relevance * 100).toFixed(0)}%
                          </Text>
                        </div>
                        <Paragraph className="text-gray-600">{clip.content}</Paragraph>
                        <Button
                          type="link"
                          href={clip.url}
                          target="_blank"
                          className="text-primary-500 hover:text-primary-600 p-0"
                        >
                          查看片段
                        </Button>
                      </div>
                    </Card>
                  </List.Item>
                )}
                className="flex flex-col gap-4"
              />
            </Card>
          )}
        </Space>
      </Content>
    </Layout>
  );
}

export default App; 