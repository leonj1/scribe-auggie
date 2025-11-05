import React, { useState, useRef, useEffect } from 'react';
import { Button, message, Card, Typography } from 'antd';
import { 
  AudioOutlined, 
  PauseOutlined, 
  StopOutlined, 
  PlayCircleOutlined 
} from '@ant-design/icons';
import WaveformVisualizer from './WaveformVisualizer';
import TranscriptionDisplay from './TranscriptionDisplay';
import apiService from '../services/apiService';

const { Title, Text } = Typography;

const RecordingInterface = ({ recording, onRecordingUpdate }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [chunkIndex, setChunkIndex] = useState(0);
  const [recordingTime, setRecordingTime] = useState(0);
  const [uploading, setUploading] = useState(false);

  const mediaRecorderRef = useRef(null);
  const streamRef = useRef(null);
  const timerRef = useRef(null);
  const chunksRef = useRef([]);

  useEffect(() => {
    // Cleanup on unmount
    return () => {
      stopRecording();
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  useEffect(() => {
    // Update recording state based on recording prop
    if (recording) {
      setIsRecording(recording.status === 'active');
      setIsPaused(recording.status === 'paused');
      
      if (recording.status === 'ended') {
        setIsRecording(false);
        setIsPaused(false);
        setRecordingTime(0);
        setChunkIndex(0);
      }
    } else {
      setIsRecording(false);
      setIsPaused(false);
      setRecordingTime(0);
      setChunkIndex(0);
    }
  }, [recording]);

  const startTimer = () => {
    timerRef.current = setInterval(() => {
      setRecordingTime(prev => prev + 1);
    }, 1000);
  };

  const stopTimer = () => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
  };

  const startRecording = async () => {
    if (!recording) {
      message.error('Please create a recording session first');
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 44100
        } 
      });
      
      streamRef.current = stream;
      
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      });
      
      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        if (chunksRef.current.length > 0) {
          await uploadChunk();
        }
      };

      // Start recording and set up chunk intervals (every 30 seconds)
      mediaRecorder.start();
      setIsRecording(true);
      setIsPaused(false);
      startTimer();

      // Set up automatic chunk upload every 30 seconds
      const chunkInterval = setInterval(() => {
        if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
          mediaRecorderRef.current.stop();
          setTimeout(() => {
            if (streamRef.current && isRecording) {
              const newRecorder = new MediaRecorder(streamRef.current, {
                mimeType: 'audio/webm;codecs=opus'
              });
              
              newRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                  chunksRef.current = [event.data];
                }
              };

              newRecorder.onstop = async () => {
                if (chunksRef.current.length > 0) {
                  await uploadChunk();
                }
              };

              mediaRecorderRef.current = newRecorder;
              newRecorder.start();
            }
          }, 100);
        }
      }, 30000);

      // Store interval reference for cleanup
      mediaRecorderRef.current.chunkInterval = chunkInterval;

      message.success('Recording started');
    } catch (error) {
      console.error('Error starting recording:', error);
      message.error('Failed to start recording. Please check microphone permissions.');
    }
  };

  const pauseRecording = async () => {
    if (!mediaRecorderRef.current || !recording) return;

    try {
      mediaRecorderRef.current.stop();
      stopTimer();
      
      if (mediaRecorderRef.current.chunkInterval) {
        clearInterval(mediaRecorderRef.current.chunkInterval);
      }

      setIsPaused(true);
      setIsRecording(false);

      // Update recording status on server
      const updatedRecording = await apiService.pauseRecording(recording.id);
      onRecordingUpdate(updatedRecording);

      message.success('Recording paused');
    } catch (error) {
      console.error('Error pausing recording:', error);
      message.error('Failed to pause recording');
    }
  };

  const resumeRecording = async () => {
    if (!recording || !streamRef.current) return;

    try {
      const mediaRecorder = new MediaRecorder(streamRef.current, {
        mimeType: 'audio/webm;codecs=opus'
      });
      
      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        if (chunksRef.current.length > 0) {
          await uploadChunk();
        }
      };

      mediaRecorder.start();
      setIsRecording(true);
      setIsPaused(false);
      startTimer();

      message.success('Recording resumed');
    } catch (error) {
      console.error('Error resuming recording:', error);
      message.error('Failed to resume recording');
    }
  };

  const stopRecording = async () => {
    if (!mediaRecorderRef.current || !recording) return;

    try {
      setUploading(true);
      
      mediaRecorderRef.current.stop();
      stopTimer();
      
      if (mediaRecorderRef.current.chunkInterval) {
        clearInterval(mediaRecorderRef.current.chunkInterval);
      }

      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
        streamRef.current = null;
      }

      setIsRecording(false);
      setIsPaused(false);

      // Finish recording on server (this will trigger transcription)
      const updatedRecording = await apiService.finishRecording(recording.id);
      onRecordingUpdate(updatedRecording);

      setRecordingTime(0);
      setChunkIndex(0);

      message.success('Recording finished. Transcription in progress...');
    } catch (error) {
      console.error('Error stopping recording:', error);
      message.error('Failed to stop recording');
    } finally {
      setUploading(false);
    }
  };

  const uploadChunk = async () => {
    if (!recording || chunksRef.current.length === 0) return;

    try {
      const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
      
      await apiService.uploadChunk(
        recording.id,
        chunkIndex,
        blob,
        30 // Approximate duration in seconds
      );

      setChunkIndex(prev => prev + 1);
      chunksRef.current = [];
      
      console.log(`Uploaded chunk ${chunkIndex}`);
    } catch (error) {
      console.error('Error uploading chunk:', error);
      message.error('Failed to upload audio chunk');
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  if (!recording) {
    return (
      <div className="recording-interface">
        <div style={{ textAlign: 'center', padding: '60px 20px' }}>
          <PlayCircleOutlined style={{ fontSize: '64px', color: '#d9d9d9', marginBottom: '16px' }} />
          <Title level={4} style={{ color: '#999' }}>No Recording Selected</Title>
          <Text type="secondary">
            Create a new recording or select an existing one to start
          </Text>
        </div>
      </div>
    );
  }

  return (
    <div className="recording-interface">
      <div style={{ textAlign: 'center', padding: '20px' }}>
        {/* Recording Status */}
        <div style={{ marginBottom: '24px' }}>
          <Title level={4} style={{ margin: 0 }}>
            {isRecording ? 'Recording...' : isPaused ? 'Paused' : 'Ready to Record'}
          </Title>
          {(isRecording || isPaused) && (
            <Text type="secondary" style={{ fontSize: '18px' }}>
              {formatTime(recordingTime)}
            </Text>
          )}
        </div>

        {/* Main Record Button */}
        <div style={{ marginBottom: '24px' }}>
          {!isRecording && !isPaused ? (
            <Button
              type="primary"
              shape="circle"
              size="large"
              icon={<AudioOutlined />}
              onClick={startRecording}
              className="record-button"
              style={{ width: '80px', height: '80px', fontSize: '24px' }}
            />
          ) : (
            <Button
              type="primary"
              shape="circle"
              size="large"
              icon={isRecording ? <PauseOutlined /> : <AudioOutlined />}
              onClick={isRecording ? pauseRecording : resumeRecording}
              className={`record-button ${isRecording ? 'recording' : 'paused'}`}
              style={{ width: '80px', height: '80px', fontSize: '24px' }}
            />
          )}
        </div>

        {/* Waveform Visualization */}
        {(isRecording || isPaused) && (
          <div style={{ marginBottom: '24px' }}>
            <WaveformVisualizer isRecording={isRecording} />
          </div>
        )}

        {/* Control Buttons */}
        {(isRecording || isPaused) && (
          <div className="recording-controls">
            <Button
              icon={<StopOutlined />}
              onClick={stopRecording}
              loading={uploading}
              danger
            >
              Finish Recording
            </Button>
          </div>
        )}

        {/* Recording Info */}
        {recording.chunk_count > 0 && (
          <Card size="small" style={{ marginTop: '24px', textAlign: 'left' }}>
            <Text type="secondary">
              Chunks uploaded: {recording.chunk_count}
            </Text>
          </Card>
        )}
      </div>

      {/* Transcription Display */}
      <TranscriptionDisplay recording={recording} />
    </div>
  );
};

export default RecordingInterface;
