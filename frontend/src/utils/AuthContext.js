import React, { createContext, useContext, useState, useEffect } from 'react';
import { message } from 'antd';
import apiService from '../services/apiService';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(localStorage.getItem('auth_token'));

  useEffect(() => {
    // Initialize authentication state
    const initAuth = async () => {
      const savedToken = localStorage.getItem('auth_token');
      const savedUser = localStorage.getItem('user_data');
      
      if (savedToken && savedUser) {
        try {
          setToken(savedToken);
          setUser(JSON.parse(savedUser));
          apiService.setAuthToken(savedToken);
        } catch (error) {
          console.error('Error parsing saved user data:', error);
          logout();
        }
      }
      
      setLoading(false);
    };

    initAuth();
  }, []);

  const login = async (googleIdToken) => {
    try {
      setLoading(true);
      const response = await apiService.authenticateWithGoogle(googleIdToken);
      
      const { access_token, user: userData } = response;
      
      // Save to localStorage
      localStorage.setItem('auth_token', access_token);
      localStorage.setItem('user_data', JSON.stringify(userData));
      
      // Update state
      setToken(access_token);
      setUser(userData);
      apiService.setAuthToken(access_token);
      
      message.success('Successfully logged in!');
      return true;
    } catch (error) {
      console.error('Login error:', error);
      message.error('Login failed. Please try again.');
      return false;
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    // Clear localStorage
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_data');
    
    // Clear state
    setToken(null);
    setUser(null);
    apiService.setAuthToken(null);
    
    message.success('Successfully logged out!');
  };

  const value = {
    user,
    token,
    loading,
    login,
    logout,
    isAuthenticated: !!user
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
