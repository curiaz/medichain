import React from 'react';

const MedichainLogo = ({ 
  size = 40, 
  showText = false, 
  textSize = 'md',
  className = '' 
}) => {
  const textSizes = {
    sm: '16px',
    md: '20px',
    lg: '24px',
    xl: '28px'
  };

  return (
    <div className={`medichain-logo-container ${className}`} style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
      {/* Medical Cross SVG Logo */}
      <div 
        style={{
          width: size,
          height: size,
          background: 'linear-gradient(135deg, #4dd0e1, #2196f3)',
          borderRadius: '50%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'white',
          fontSize: size * 0.45,
          fontWeight: 'bold',
          boxShadow: '0 4px 15px rgba(77, 208, 225, 0.3)',
          position: 'relative',
          overflow: 'hidden'
        }}
      >
        {/* Medical Cross */}
        <span style={{ fontSize: size * 0.6, lineHeight: 1 }}>+</span>
        
        {/* Shimmer effect */}
        <div 
          style={{
            position: 'absolute',
            top: '-50%',
            left: '-50%',
            width: '200%',
            height: '200%',
            background: 'linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.3), transparent)',
            animation: 'logoShimmer 2s ease-in-out infinite',
            transform: 'rotate(45deg)'
          }}
        />
      </div>

      {/* Text Logo */}
      {showText && (
        <span 
          style={{
            fontSize: textSizes[textSize],
            fontWeight: '700',
            color: '#333',
            letterSpacing: '1px',
            background: 'linear-gradient(135deg, #2196f3, #00bcd4)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text'
          }}
        >
          MEDICHAIN
        </span>
      )}

      <style>
        {`
          @keyframes logoShimmer {
            0% { transform: rotate(45deg) translateX(-200%); }
            50% { transform: rotate(45deg) translateX(200%); }
            100% { transform: rotate(45deg) translateX(200%); }
          }
        `}
      </style>
    </div>
  );
};

export default MedichainLogo;
