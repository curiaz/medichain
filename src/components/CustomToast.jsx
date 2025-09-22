import React from 'react';
import './CustomToast.css';

// Simple toast implementation without external libraries
let toastContainer = null;
let toastIdCounter = 0;

const createToastContainer = () => {
  if (!toastContainer) {
    toastContainer = document.createElement('div');
    toastContainer.className = 'toast-container';
    toastContainer.style.cssText = `
      position: fixed;
      top: 1rem;
      right: 1rem;
      z-index: 9999;
      pointer-events: none;
    `;
    document.body.appendChild(toastContainer);
  }
  return toastContainer;
};

const createToast = (message, type, duration = 3000) => {
  const container = createToastContainer();
  const toastId = `toast-${++toastIdCounter}`;
  
  const toastWrapper = document.createElement('div');
  toastWrapper.id = toastId;
  toastWrapper.style.cssText = `
    margin-bottom: 0.5rem;
    pointer-events: auto;
    animation: slideInToast 0.3s ease-out;
  `;
  
  // Add animations if not already added
  if (!document.getElementById('toast-animations')) {
    const style = document.createElement('style');
    style.id = 'toast-animations';
    style.textContent = `
      @keyframes slideInToast {
        from {
          opacity: 0;
          transform: translateX(100%);
        }
        to {
          opacity: 1;
          transform: translateX(0);
        }
      }
      @keyframes slideOutToast {
        from {
          opacity: 1;
          transform: translateX(0);
        }
        to {
          opacity: 0;
          transform: translateX(100%);
        }
      }
    `;
    document.head.appendChild(style);
  }
  
  // Create toast content
  const toastContent = document.createElement('div');
  toastContent.className = `custom-toast custom-toast-${type}`;
  
  // Add icon based on type
  let iconHTML = '';
  if (type === 'success') {
    iconHTML = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 6L9 17l-5-5"/></svg>';
  } else if (type === 'error') {
    iconHTML = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>';
  } else if (type === 'info') {
    iconHTML = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>';
  }
  
  toastContent.innerHTML = `${iconHTML}<span>${message}</span>`;
  toastWrapper.appendChild(toastContent);
  container.appendChild(toastWrapper);
  
  // Auto remove after duration
  setTimeout(() => {
    if (toastWrapper && toastWrapper.parentNode) {
      toastWrapper.style.animation = 'slideOutToast 0.3s ease-in';
      setTimeout(() => {
        if (toastWrapper && toastWrapper.parentNode) {
          toastWrapper.parentNode.removeChild(toastWrapper);
        }
      }, 300);
    }
  }, duration);
  
  return toastId;
};

// Simple toast functions
export const showToast = {
  success: (message) => createToast(message, 'success', 3000),
  error: (message) => createToast(message, 'error', 4000),
  info: (message) => createToast(message, 'info', 3000)
};

export default { showToast };
