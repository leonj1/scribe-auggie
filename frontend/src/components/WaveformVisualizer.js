import React, { useEffect, useState } from 'react';

const WaveformVisualizer = ({ isRecording }) => {
  const [bars, setBars] = useState([]);

  useEffect(() => {
    if (isRecording) {
      // Generate random heights for waveform bars to simulate audio visualization
      const interval = setInterval(() => {
        const newBars = Array.from({ length: 20 }, () => 
          Math.random() * 40 + 10 // Random height between 10 and 50
        );
        setBars(newBars);
      }, 150);

      return () => clearInterval(interval);
    } else {
      setBars([]);
    }
  }, [isRecording]);

  if (!isRecording) {
    return (
      <div className="waveform-container">
        <div style={{ color: '#d9d9d9', fontSize: '14px' }}>
          Audio waveform will appear here during recording
        </div>
      </div>
    );
  }

  return (
    <div className="waveform-container">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '2px' }}>
        {bars.map((height, index) => (
          <div
            key={index}
            className="waveform-bar"
            style={{
              height: `${height}px`,
              width: '3px',
              backgroundColor: '#1890ff',
              borderRadius: '1px',
              transition: 'height 0.1s ease'
            }}
          />
        ))}
      </div>
      <div style={{ marginTop: '8px', color: '#666', fontSize: '12px' }}>
        🎤 Recording audio...
      </div>
    </div>
  );
};

export default WaveformVisualizer;
