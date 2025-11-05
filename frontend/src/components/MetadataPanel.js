import React, { useState } from 'react';
import { Card, Descriptions, Input, Button, message, Tag } from 'antd';
import { EditOutlined, SaveOutlined, CloseOutlined } from '@ant-design/icons';
import apiService from '../services/apiService';

const { TextArea } = Input;

const MetadataPanel = ({ recording, onRecordingUpdate }) => {
  const [editingNotes, setEditingNotes] = useState(false);
  const [notesValue, setNotesValue] = useState('');
  const [saving, setSaving] = useState(false);

  const handleEditNotes = () => {
    setNotesValue(recording?.notes || '');
    setEditingNotes(true);
  };

  const handleSaveNotes = async () => {
    if (!recording) return;

    try {
      setSaving(true);
      const updatedRecording = await apiService.updateRecordingNotes(recording.id, notesValue);
      onRecordingUpdate(updatedRecording);
      setEditingNotes(false);
      message.success('Notes updated successfully');
    } catch (error) {
      console.error('Error updating notes:', error);
      message.error('Failed to update notes');
    } finally {
      setSaving(false);
    }
  };

  const handleCancelEdit = () => {
    setEditingNotes(false);
    setNotesValue('');
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
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString();
  };

  const formatDuration = (createdAt, updatedAt) => {
    if (!createdAt || !updatedAt) return 'N/A';
    
    const start = new Date(createdAt);
    const end = new Date(updatedAt);
    const diffInMinutes = Math.floor((end - start) / (1000 * 60));
    
    if (diffInMinutes < 1) return '< 1 min';
    if (diffInMinutes < 60) return `${diffInMinutes} min`;
    
    const hours = Math.floor(diffInMinutes / 60);
    const minutes = diffInMinutes % 60;
    return `${hours}h ${minutes}m`;
  };

  if (!recording) {
    return (
      <div style={{ textAlign: 'center', padding: '40px 20px', color: '#999' }}>
        <p>Select a recording to view details</p>
      </div>
    );
  }

  return (
    <div className="metadata-panel-content">
      <Card size="small" style={{ marginBottom: '16px' }}>
        <Descriptions column={1} size="small">
          <Descriptions.Item label="Status">
            <Tag color={getStatusColor(recording.status)}>
              {recording.status.toUpperCase()}
            </Tag>
          </Descriptions.Item>
          <Descriptions.Item label="Created">
            {formatDate(recording.created_at)}
          </Descriptions.Item>
          <Descriptions.Item label="Duration">
            {formatDuration(recording.created_at, recording.updated_at)}
          </Descriptions.Item>
          <Descriptions.Item label="Chunks">
            {recording.chunk_count || 0}
          </Descriptions.Item>
          <Descriptions.Item label="Provider">
            {recording.llm_provider || 'N/A'}
          </Descriptions.Item>
        </Descriptions>
      </Card>

      <Card 
        size="small" 
        title="Notes" 
        extra={
          !editingNotes && (
            <Button 
              type="text" 
              size="small" 
              icon={<EditOutlined />}
              onClick={handleEditNotes}
            >
              Edit
            </Button>
          )
        }
      >
        {editingNotes ? (
          <div>
            <TextArea
              value={notesValue}
              onChange={(e) => setNotesValue(e.target.value)}
              placeholder="Add notes about this recording session..."
              rows={4}
              style={{ marginBottom: '8px' }}
            />
            <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
              <Button 
                size="small" 
                icon={<CloseOutlined />}
                onClick={handleCancelEdit}
              >
                Cancel
              </Button>
              <Button 
                type="primary" 
                size="small" 
                icon={<SaveOutlined />}
                loading={saving}
                onClick={handleSaveNotes}
              >
                Save
              </Button>
            </div>
          </div>
        ) : (
          <div style={{ minHeight: '60px' }}>
            {recording.notes ? (
              <p style={{ margin: 0, whiteSpace: 'pre-wrap', fontSize: '14px' }}>
                {recording.notes}
              </p>
            ) : (
              <p style={{ margin: 0, color: '#999', fontStyle: 'italic' }}>
                No notes added yet. Click Edit to add notes.
              </p>
            )}
          </div>
        )}
      </Card>

      {recording.transcription_text && (
        <Card size="small" title="Transcription Status" style={{ marginTop: '16px' }}>
          <div style={{ fontSize: '12px', color: '#666' }}>
            <p>✅ Transcription completed</p>
            <p>Length: {recording.transcription_text.length} characters</p>
            <p>Words: ~{recording.transcription_text.split(' ').length}</p>
          </div>
        </Card>
      )}

      {recording.audio_file_path && (
        <Card size="small" title="Audio File" style={{ marginTop: '16px' }}>
          <div style={{ fontSize: '12px', color: '#666' }}>
            <p>✅ Audio file assembled</p>
            <p style={{ wordBreak: 'break-all' }}>
              {recording.audio_file_path.split('/').pop()}
            </p>
          </div>
        </Card>
      )}
    </div>
  );
};

export default MetadataPanel;
