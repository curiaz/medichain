import React, { useState, useEffect } from 'react';
import './AIProgressBar.css';

const AIProgressBar = ({ 
  isLoading = false, 
  progress = 0, 
  status = 'Processing...', 
  steps = null,
  className = '',
  onComplete = null 
}) => {
  const [currentProgress, setCurrentProgress] = useState(0);
  const [currentStep, setCurrentStep] = useState(0);

  const defaultSteps = [
    { label: 'Analyzing', description: 'Processing input data' },
    { label: 'Computing', description: 'Running AI algorithms' },
    { label: 'Diagnosing', description: 'Generating results' },
    { label: 'Complete', description: 'Analysis finished' }
  ];

  const progressSteps = steps || defaultSteps;

  useEffect(() => {
    if (isLoading && progress > currentProgress) {
      const timer = setTimeout(() => {
        setCurrentProgress(progress);
      }, 100);
      return () => clearTimeout(timer);
    }
  }, [progress, isLoading, currentProgress]);

  useEffect(() => {
    const stepIndex = Math.floor((currentProgress / 100) * progressSteps.length);
    setCurrentStep(Math.min(stepIndex, progressSteps.length - 1));
    
    if (currentProgress >= 100 && onComplete) {
      onComplete();
    }
  }, [currentProgress, progressSteps.length, onComplete]);

  if (!isLoading) return null;

  return (
    <div className={`ai-progress-container ${className}`}>
      <div className="ai-progress-header">
        <span className="ai-progress-status">{status}</span>
        <span className="ai-progress-percentage">{Math.round(currentProgress)}%</span>
      </div>
      
      <div className="ai-progress-bar">
        <div 
          className="ai-progress-fill" 
          style={{ width: `${currentProgress}%` }}
        />
      </div>
      
      <div className="ai-progress-steps">
        {progressSteps.map((step, index) => (
          <div 
            key={index}
            className={`ai-progress-step ${index <= currentStep ? 'active' : ''}`}
          >
            <span>{index + 1}</span>
            <div className="step-info">
              <small className="step-label">{step.label}</small>
              {step.description && (
                <small className="step-description">{step.description}</small>
              )}
            </div>
          </div>
        ))}
      </div>
      
      {/* Medical themed animation */}
      <div className="ai-progress-medical-indicator">
        <div className="pulse-indicator">
          <span className="heartbeat">♥</span>
        </div>
      </div>
    </div>
  );
};

// Hook for managing AI progress state
export const useAIProgress = (totalSteps = 4) => {
  const [isLoading, setIsLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState('Ready');
  const [currentStep, setCurrentStep] = useState(0);

  const startProgress = (initialStatus = 'Initializing...') => {
    setIsLoading(true);
    setProgress(0);
    setStatus(initialStatus);
    setCurrentStep(0);
  };

  const updateProgress = (newProgress, newStatus) => {
    setProgress(Math.min(100, Math.max(0, newProgress)));
    if (newStatus) setStatus(newStatus);
    setCurrentStep(Math.floor((newProgress / 100) * totalSteps));
  };

  const completeProgress = (completionMessage = 'Analysis complete!') => {
    setProgress(100);
    setStatus(completionMessage);
    setCurrentStep(totalSteps);
    
    setTimeout(() => {
      setIsLoading(false);
    }, 1000);
  };

  const resetProgress = () => {
    setIsLoading(false);
    setProgress(0);
    setStatus('Ready');
    setCurrentStep(0);
  };

  return {
    isLoading,
    progress,
    status,
    currentStep,
    startProgress,
    updateProgress,
    completeProgress,
    resetProgress
  };
};

export default AIProgressBar;
