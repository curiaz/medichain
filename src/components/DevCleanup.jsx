/**
 * Development Cleanup Component
 * Adds a cleanup button to the UI during development
 */

import React from 'react';
import clearUserDataUtils from '../utils/clearUserData';

const DevCleanup = () => {
  if (process.env.NODE_ENV !== 'development') {
    return null;
  }

  const handleQuickCleanup = async () => {
    if (window.confirm('⚠️ This will clear all local data and reload the page. Continue?')) {
      console.log('🧹 Starting development cleanup...');
      await clearUserDataUtils.devReset();
    }
  };

  return (
    <div style={{
      position: 'fixed',
      top: '10px',
      right: '10px',
      zIndex: 9999,
      background: '#ff6b6b',
      color: 'white',
      padding: '8px 12px',
      borderRadius: '4px',
      fontSize: '12px',
      cursor: 'pointer',
      boxShadow: '0 2px 8px rgba(0,0,0,0.2)'
    }} onClick={handleQuickCleanup}>
      🧹 DEV: Clear Data
    </div>
  );
};

export default DevCleanup;