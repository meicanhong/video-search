import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Layout, Input, Card, Typography, message } from 'antd';
import { SearchOutlined } from '@ant-design/icons';
import { useQuery } from 'react-query';
import { searchVideos } from '@/services/api';
import type { SearchResponse } from '@/types/api';

const { Header, Content } = Layout;
const { Search } = Input;
const { Title } = Typography;

function SearchPage() {
  const [keyword, setKeyword] = useState('');
  const navigate = useNavigate();

  // 搜索视频
  const { data: searchResult, isLoading } = useQuery<SearchResponse>(
    ['search', keyword],
    () => searchVideos({ keyword, max_results: 5 }),
    {
      enabled: !!keyword,
      onSuccess: (data) => {
        // 搜索成功后跳转到分析页面
        navigate(`/session/${data.session_id}`, {
          state: { searchResult: data }
        });
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
        <div className="flex flex-col items-center justify-center min-h-[60vh]">
          <Card className="w-full max-w-2xl card-hover">
            <div className="text-center mb-8">
              <Title level={2} className="text-primary-700">
                搜索 YouTube 视频
              </Title>
              <p className="text-gray-600 mt-4">
                输入关键词搜索视频，我们将帮助你分析视频内容
              </p>
            </div>
            <Search
              placeholder="输入关键词搜索视频"
              enterButton={<><SearchOutlined /> 搜索</>}
              size="large"
              loading={isLoading}
              onSearch={handleSearch}
            />
          </Card>
        </div>
      </Content>
    </Layout>
  );
}

export default SearchPage; 