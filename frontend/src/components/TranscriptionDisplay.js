import React, { useState, useEffect } from 'react';
import { Card, Button, message, Spin, Typography } from 'antd';
import { CopyOutlined, DownloadOutlined, ReloadOutlined } from '@ant-design/icons';
import apiService from '../services/apiService';

const { Text, Paragraph } = Typography;

const TranscriptionDisplay = ({ recording }) => {
  const [refreshing, setRefreshing] = useState(false);
  const [localRecording, setLocalRecording] = useState(recording);

  useEffect(() => {
    setLocalRecording(recording);
  }, [recording]);

  const handleRefresh = async () => {
    if (!recording?.id) return;

    try {
      setRefreshing(true);
      const updatedRecording = await apiService.getRecording(recording.id);
      setLocalRecording(updatedRecording);
      
      if (updatedRecording.transcription_text && !recording.transcription_text) {
        message.success('Transcription completed!');
      }
    } catch (error) {
      console.error('Error refreshing recording:', error);
      message.error('Failed to refresh recording');
    } finally {
      setRefreshing(false);
    }
  };

  const handleCopyTranscription = () => {
    if (localRecording?.transcription_text) {
      navigator.clipboard.writeText(localRecording.transcription_text);
      message.success('Transcription copied to clipboard');
    }
  };

  const handleDownloadTranscription = () => {
    if (!localRecording?.transcription_text) return;

    const element = document.createElement('a');
    const file = new Blob([localRecording.transcription_text], { type: 'text/plain' });
    element.href = URL.createObjectURL(file);
    element.download = `transcription_${localRecording.id.slice(-8)}.txt`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
    
    message.success('Transcription downloaded');
  };

  if (!recording) {
    return null;
  }

  const isProcessing = recording.status === 'ended' && !localRecording?.transcription_text;
  const hasTranscription = localRecording?.transcription_text;

  return (
    <Card
      title="Transcription"
      style={{ marginTop: '24px' }}
      extra={
        <div style={{ display: 'flex', gap: '8px' }}>
          {hasTranscription && (
            <>
              <Button
                size="small"
                icon={<CopyOutlined />}
                onClick={handleCopyTranscription}
              >
                Copy
              </Button>
              <Button
                size="small"
                icon={<DownloadOutlined />}
                onClick={handleDownloadTranscription}
              >
                Download
              </Button>
            </>
          )}
          {(isProcessing || hasTranscription) && (
            <Button
              size="small"
              icon={<ReloadOutlined />}
              onClick={handleRefresh}
              loading={refreshing}
            >
              Refresh
            </Button>
          )}
        </div>
      }
    >
      <div className="transcription-display">
        {isProcessing ? (
          <div style={{ textAlign: 'center', padding: '40px 20px' }}>
            <Spin size="large" />
            <div style={{ marginTop: '16px' }}>
              <Text type="secondary">
                Processing audio and generating transcription...
              </Text>
            </div>
            <div style={{ marginTop: '8px', fontSize: '12px', color: '#999' }}>
              This may take a few minutes depending on the recording length
            </div>
          </div>
        ) : hasTranscription ? (
          <div>
            <Paragraph
              style={{
                whiteSpace: 'pre-wrap',
                lineHeight: '1.8',
                fontSize: '14px',
                margin: 0,
                padding: '16px',
                backgroundColor: '#fafafa',
                border: '1px solid #e8e8e8',
                borderRadius: '6px',
                maxHeight: '400px',
                overflowY: 'auto'
              }}
            >
              {localRecording.transcription_text}
            </Paragraph>
            
            <div style={{ marginTop: '12px', fontSize: '12px', color: '#666' }}>
              <Text type="secondary">
                Transcription completed • {localRecording.transcription_text.length} characters • 
                ~{localRecording.transcription_text.split(' ').length} words
              </Text>
            </div>
          </div>
        ) : recording.status === 'ended' ? (
          <div className="transcription-display empty">
            <div style={{ textAlign: 'center' }}>
              <Text type="secondary">
                Recording finished. Transcription will appear here once processing is complete.
              </Text>
              <div style={{ marginTop: '12px' }}>
                <Button
                  type="link"
                  icon={<ReloadOutlined />}
                  onClick={handleRefresh}
                  loading={refreshing}
                >
                  Check for updates
                </Button>
              </div>
            </div>
          </div>
        ) : (
          <div className="transcription-display empty">
            <Text type="secondary">
              Transcription will appear here after recording is finished
            </Text>
          </div>
        )}
      </div>
    </Card>
  );
};

export default TranscriptionDisplay;
