import React from 'react';
import './LoadingSpinner.css';

const LoadingSpinner = ({ 
  size = 'medium', 
  text = 'Loading...', 
  fullScreen = false,
  className = '',
  color = '#2196f3' 
}) => {
  const sizeMap = {
    small: 16,
    medium: 24,
    large: 32,
    xl: 48,
    xxl: 64
  };

  const spinnerSize = sizeMap[size] || sizeMap.medium;

  // Custom spinner component using CSS animations
  const SpinnerIcon = ({ size, color }) => (
    <div 
      className="loading-spinner-icon"
      style={{
        width: size,
        height: size,
        border: `3px solid rgba(33, 150, 243, 0.1)`,
        borderTop: `3px solid ${color}`,
        borderRadius: '50%',
        display: 'inline-block'
      }}
    />
  );

  if (fullScreen) {
    return (
      <div className="loading-spinner-fullscreen">
        <div className="loading-spinner-container">
          <SpinnerIcon size={spinnerSize} color={color} />
          {text && <p className="loading-spinner-text">{text}</p>}
        </div>
      </div>
    );
  }

  return (
    <div className={`loading-spinner-inline ${className}`}>
      <SpinnerIcon size={spinnerSize} color={color} />
      {text && <span className="loading-spinner-text">{text}</span>}
    </div>
  );
};

export default LoadingSpinner;
