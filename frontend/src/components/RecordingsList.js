import React from 'react';
import { Empty, Tag } from 'antd';
import { ClockCircleOutlined, CheckCircleOutlined, PauseCircleOutlined } from '@ant-design/icons';

const RecordingsList = ({ recordings, selectedRecording, onRecordingSelect }) => {
  const getStatusIcon = (status) => {
    switch (status) {
      case 'active':
        return <ClockCircleOutlined style={{ color: '#52c41a' }} />;
      case 'paused':
        return <PauseCircleOutlined style={{ color: '#fa8c16' }} />;
      case 'ended':
        return <CheckCircleOutlined style={{ color: '#666' }} />;
      default:
        return <ClockCircleOutlined />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active':
        return 'success';
      case 'paused':
        return 'warning';
      case 'ended':
        return 'default';
      default:
        return 'default';
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = (now - date) / (1000 * 60 * 60);

    if (diffInHours < 1) {
      const diffInMinutes = Math.floor((now - date) / (1000 * 60));
      return `${diffInMinutes} min ago`;
    } else if (diffInHours < 24) {
      return `${Math.floor(diffInHours)} hours ago`;
    } else {
      return date.toLocaleDateString();
    }
  };

  const getRecordingTitle = (recording) => {
    if (recording.transcription_text) {
      // Use first few words of transcription as title
      const words = recording.transcription_text.split(' ').slice(0, 6);
      return words.join(' ') + (recording.transcription_text.split(' ').length > 6 ? '...' : '');
    }
    return `Recording ${recording.id.slice(-8)}`;
  };

  if (recordings.length === 0) {
    return (
      <Empty
        description="No recordings yet"
        image={Empty.PRESENTED_IMAGE_SIMPLE}
      >
        <p style={{ color: '#666', fontSize: '14px' }}>
          Click "New Recording" to start your first session
        </p>
      </Empty>
    );
  }

  return (
    <div className="recordings-list">
      {recordings.map((recording) => (
        <div
          key={recording.id}
          className={`recording-item ${selectedRecording?.id === recording.id ? 'active' : ''}`}
          onClick={() => onRecordingSelect(recording)}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
            <h4 style={{ flex: 1, marginRight: '8px' }}>
              {getRecordingTitle(recording)}
            </h4>
            {getStatusIcon(recording.status)}
          </div>
          
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <p style={{ margin: 0, flex: 1 }}>
              {formatDate(recording.created_at)}
            </p>
            <Tag color={getStatusColor(recording.status)} size="small">
              {recording.status}
            </Tag>
          </div>

          {recording.chunk_count > 0 && (
            <div style={{ marginTop: '4px', fontSize: '11px', color: '#999' }}>
              {recording.chunk_count} chunk{recording.chunk_count !== 1 ? 's' : ''}
            </div>
          )}

          {recording.notes && (
            <div style={{ 
              marginTop: '8px', 
              fontSize: '12px', 
              color: '#666',
              fontStyle: 'italic',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap'
            }}>
              📝 {recording.notes}
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

export default RecordingsList;
