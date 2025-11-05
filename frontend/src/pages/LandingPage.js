import React, { useEffect } from 'react';
import { Button, message } from 'antd';
import { GoogleOutlined } from '@ant-design/icons';
import { useAuth } from '../utils/AuthContext';

const GOOGLE_CLIENT_ID = process.env.REACT_APP_GOOGLE_CLIENT_ID;

const LandingPage = () => {
  const { login } = useAuth();

  useEffect(() => {
    // Initialize Google Identity Services
    if (window.google && GOOGLE_CLIENT_ID) {
      window.google.accounts.id.initialize({
        client_id: GOOGLE_CLIENT_ID,
        callback: handleGoogleResponse,
        auto_select: false,
        cancel_on_tap_outside: true,
      });
    }
  }, []);

  const handleGoogleResponse = async (response) => {
    try {
      const success = await login(response.credential);
      if (!success) {
        message.error('Authentication failed. Please try again.');
      }
    } catch (error) {
      console.error('Google authentication error:', error);
      message.error('Authentication failed. Please try again.');
    }
  };

  const handleGoogleLogin = () => {
    if (!GOOGLE_CLIENT_ID) {
      message.error('Google authentication is not configured. Please check your environment variables.');
      return;
    }

    if (window.google) {
      window.google.accounts.id.prompt((notification) => {
        if (notification.isNotDisplayed() || notification.isSkippedMoment()) {
          // Fallback to popup if prompt is not displayed
          window.google.accounts.id.renderButton(
            document.getElementById('google-signin-button'),
            {
              theme: 'outline',
              size: 'large',
              width: 250,
              text: 'signin_with',
            }
          );
        }
      });
    } else {
      message.error('Google authentication is not available. Please refresh the page and try again.');
    }
  };

  return (
    <div className="landing-container hero-background">
      <div className="hero-content">
        <div className="hero-section">
          <h1>🩺 Audio Transcription Service</h1>
          <p>
            Secure and efficient audio transcription platform designed specifically 
            for healthcare professionals. Record patient notes, get accurate transcriptions, 
            and manage your documentation workflow seamlessly.
          </p>
          
          <div style={{ marginBottom: '32px' }}>
            <Button
              type="primary"
              size="large"
              icon={<GoogleOutlined />}
              onClick={handleGoogleLogin}
              className="google-login-button"
            >
              Sign in with Google
            </Button>
          </div>

          {/* Hidden div for Google Sign-In button fallback */}
          <div id="google-signin-button" style={{ display: 'none' }}></div>

          <div style={{ marginTop: '48px', opacity: 0.8 }}>
            <h3 style={{ color: 'white', marginBottom: '16px' }}>Key Features</h3>
            <div style={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
              gap: '16px',
              maxWidth: '600px',
              margin: '0 auto'
            }}>
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '24px', marginBottom: '8px' }}>🔒</div>
                <div>HIPAA Compliant</div>
              </div>
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '24px', marginBottom: '8px' }}>🎤</div>
                <div>Long Recordings</div>
              </div>
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '24px', marginBottom: '8px' }}>🤖</div>
                <div>AI Transcription</div>
              </div>
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '24px', marginBottom: '8px' }}>📊</div>
                <div>Easy Management</div>
              </div>
            </div>
          </div>

          <div style={{ marginTop: '32px', fontSize: '14px', opacity: 0.7 }}>
            <p>
              Secure authentication via Google • End-to-end encryption • 
              Professional-grade transcription accuracy
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LandingPage;
