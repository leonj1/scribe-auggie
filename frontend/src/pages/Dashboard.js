import React, { useState, useEffect } from 'react';
import { Layout, Avatar, Dropdown, Button, message, Spin } from 'antd';
import { UserOutlined, LogoutOutlined, PlusOutlined } from '@ant-design/icons';
import { useAuth } from '../utils/AuthContext';
import RecordingsList from '../components/RecordingsList';
import RecordingInterface from '../components/RecordingInterface';
import MetadataPanel from '../components/MetadataPanel';
import apiService from '../services/apiService';

const { Header, Content } = Layout;

const Dashboard = () => {
  const { user, logout } = useAuth();
  const [recordings, setRecordings] = useState([]);
  const [selectedRecording, setSelectedRecording] = useState(null);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    loadRecordings();
  }, []);

  const loadRecordings = async () => {
    try {
      setLoading(true);
      const response = await apiService.getRecordings();
      setRecordings(response.recordings || []);
    } catch (error) {
      console.error('Error loading recordings:', error);
      message.error('Failed to load recordings');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateRecording = async () => {
    try {
      setCreating(true);
      const newRecording = await apiService.createRecording();
      
      // Add to recordings list and select it
      setRecordings(prev => [newRecording, ...prev]);
      setSelectedRecording(newRecording);
      
      message.success('New recording session created');
    } catch (error) {
      console.error('Error creating recording:', error);
      message.error('Failed to create recording');
    } finally {
      setCreating(false);
    }
  };

  const handleRecordingSelect = (recording) => {
    setSelectedRecording(recording);
  };

  const handleRecordingUpdate = (updatedRecording) => {
    // Update the recording in the list
    setRecordings(prev => 
      prev.map(r => r.id === updatedRecording.id ? updatedRecording : r)
    );
    
    // Update selected recording if it's the same one
    if (selectedRecording?.id === updatedRecording.id) {
      setSelectedRecording(updatedRecording);
    }
  };

  const userMenuItems = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: user?.display_name || 'Profile',
      disabled: true,
    },
    {
      type: 'divider',
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: 'Logout',
      onClick: logout,
    },
  ];

  return (
    <Layout className="dashboard-layout">
      <Header className="dashboard-header">
        <h1>🩺 Audio Transcription Service</h1>
        <div className="user-menu">
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={handleCreateRecording}
            loading={creating}
          >
            New Recording
          </Button>
          <Dropdown
            menu={{ items: userMenuItems }}
            placement="bottomRight"
            trigger={['click']}
          >
            <div style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Avatar 
                src={user?.avatar_url} 
                icon={<UserOutlined />}
                size="small"
              />
              <span>{user?.display_name}</span>
            </div>
          </Dropdown>
        </div>
      </Header>

      <Content className="dashboard-content">
        {loading ? (
          <div style={{ 
            display: 'flex', 
            justifyContent: 'center', 
            alignItems: 'center', 
            height: '100%' 
          }}>
            <Spin size="large" />
          </div>
        ) : (
          <div className="dashboard-grid">
            {/* Left Panel - Recordings List */}
            <div className="recordings-panel">
              <div className="panel-header">
                <span>Recordings ({recordings.length})</span>
              </div>
              <div className="panel-content">
                <RecordingsList
                  recordings={recordings}
                  selectedRecording={selectedRecording}
                  onRecordingSelect={handleRecordingSelect}
                  onRecordingUpdate={handleRecordingUpdate}
                />
              </div>
            </div>

            {/* Center Panel - Recording Interface */}
            <div className="recording-panel">
              <div className="panel-header">
                {selectedRecording ? (
                  <span>
                    Recording Session - {new Date(selectedRecording.created_at).toLocaleDateString()}
                  </span>
                ) : (
                  <span>Select or Create a Recording</span>
                )}
              </div>
              <div className="panel-content">
                <RecordingInterface
                  recording={selectedRecording}
                  onRecordingUpdate={handleRecordingUpdate}
                />
              </div>
            </div>

            {/* Right Panel - Metadata */}
            <div className="metadata-panel">
              <div className="panel-header">
                <span>Details</span>
              </div>
              <div className="panel-content">
                <MetadataPanel
                  recording={selectedRecording}
                  onRecordingUpdate={handleRecordingUpdate}
                />
              </div>
            </div>
          </div>
        )}
      </Content>
    </Layout>
  );
};

export default Dashboard;
