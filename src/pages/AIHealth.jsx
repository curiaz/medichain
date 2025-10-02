import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { aiService } from '../services/aiService';
import { showToast } from '../components/CustomToast';
import '../assets/styles/AIHealth_Modern.css';
import medichainLogo from '../assets/medichain_logo.png';

// Icons
const HeartIcon = () => (
  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
  </svg>
);

const ClipboardIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
  </svg>
);

const UserIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
  </svg>
);

const SparklesIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2V5a2 2 0 00-2-2H5zM5 11a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2v-2a2 2 0 00-2-2H5zM11 5a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V5zM11 13a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
  </svg>
);

const ExclamationIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.664-.833-2.464 0L4.35 16.5c-.77.833.192 2.5 1.732 2.5z" />
  </svg>
);

const DatabaseIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4" />
  </svg>
);

const ShieldIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
  </svg>
);

// Disclaimer Component
const DisclaimerNotice = () => (
  <div className="disclaimer-notice">
    <div className="disclaimer-header">
      <ExclamationIcon />
      <span>Disclaimer:</span>
    </div>
    <div className="disclaimer-content">
      <p>
        Our system is designed to provide symptom-based health insights using AI trained on medical datasets. 
        It may suggest possible conditions, recommended actions, and general treatment information. However, 
        the system is not a substitute for professional medical advice, diagnosis, or treatment.
      </p>
      <p>
        The outputs are predictions based on patterns in medical data and should be used only as a supportive tool, 
        not as a final medical decision-maker. Always consult a licensed healthcare provider before starting, 
        changing, or stopping any medical treatment.
      </p>
    </div>
  </div>
);

const ActivityIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
  </svg>
);

const ChevronLeftIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
  </svg>
);

const ChevronRightIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
  </svg>
);

// Medical Analysis Slideshow Component
const MedicalAnalysisSlideshow = ({ formattedResponse, diagnosis, symptoms, patientAge, patientGender }) => {
  const [currentSlide, setCurrentSlide] = useState(0);
  const [isTransitioning, setIsTransitioning] = useState(false);
  
  // Parse the formatted response into sections
  const parseResponse = (response) => {
    const sections = [];
    
    // Add the "Symptoms Reported" slide as the first slide
    const symptomsReported = {
      type: 'reported-symptoms',
      title: 'Symptoms Reported',
      content: [
        symptoms || 'No symptoms described'
      ]
    };
    sections.push(symptomsReported);
    
    // Filter out disclaimer lines from the entire response first
    const cleanResponse = response
      .replace(/.*Disclaimer:.*\n?/gi, '')
      .replace(/.*I am not a doctor.*\n?/gi, '')
      .replace(/.*informational purposes only.*\n?/gi, '');
    
    // Split by sections using --- markers
    const sectionParts = cleanResponse.split('---').filter(part => part.trim());
    
    for (const part of sectionParts) {
      const trimmedPart = part.trim();
      if (!trimmedPart) continue;
      
      // Identify section type and extract content more carefully
      let title = '';
      let type = '';
      let content = [];
      
      const lines = trimmedPart.split('\n').map(line => line.trim()).filter(line => line);
      
      for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        
        // Check if it's a title line
        if (line.match(/^###?\s*[🔎📋🚦✅]/)) {
          title = line.replace(/^###?\s*/, '').trim();
          
          // Determine section type
          if (title.includes('🔎') || title.includes('Possible Conditions')) {
            type = 'conditions';
          } else if (title.includes('📋') || title.includes('Symptoms')) {
            type = 'symptoms';  
          } else if (title.includes('🚦') || title.includes('Severity')) {
            type = 'severity';
          } else if (title.includes('✅') || title.includes('Recommended')) {
            type = 'recommendations';
          }
          
          // Collect content after title
          content = lines.slice(i + 1);
          break;
        }
      }
      
      if (title && content.length > 0) {
        sections.push({ 
          type, 
          title, 
          content: content.filter(line => line !== '' && line !== '---') 
        });
      }
    }
    
    return sections;
  };
  
  const sections = parseResponse(formattedResponse);
  
  // Navigation functions for slideshow with transition animations
  const nextSlide = () => {
    if (isTransitioning) return;
    setIsTransitioning(true);
    setTimeout(() => {
      setCurrentSlide((prev) => (prev + 1) % sections.length);
      setTimeout(() => setIsTransitioning(false), 50);
    }, 150);
  };
  
  const prevSlide = () => {
    if (isTransitioning) return;
    setIsTransitioning(true);
    setTimeout(() => {
      setCurrentSlide((prev) => (prev - 1 + sections.length) % sections.length);
      setTimeout(() => setIsTransitioning(false), 50);
    }, 150);
  };
  
  const goToSlide = (index) => {
    if (isTransitioning || index === currentSlide) return;
    setIsTransitioning(true);
    setTimeout(() => {
      setCurrentSlide(index);
      setTimeout(() => setIsTransitioning(false), 50);
    }, 150);
  };
  
  if (sections.length === 0) return null;
  
  return (
    <div className="medical-slideshow-container">
      {/* Slideshow Navigation */}
      <div className="slideshow-navigation">
        {sections.map((section, index) => (
          <button
            key={index}
            className={`nav-dot ${index === currentSlide ? 'active' : ''}`}
            onClick={() => goToSlide(index)}
            title={section.title}
          >
            {index + 1}
          </button>
        ))}
      </div>
      
      {/* Slideshow Content */}
      <div className="slideshow-content">
        {sections.length > 0 && (
          <div 
            className={`slide ${isTransitioning ? 'slide-transitioning' : 'slide-active'}`}
            data-slide-type={sections[currentSlide].type}
          >
            <h3 className="slide-title">{sections[currentSlide].title}</h3>
            <div className="slide-content">
              {sections[currentSlide].content.map((line, idx) => (
                <p key={idx}>{line}</p>
              ))}
            </div>
          </div>
        )}
      </div>
      
      {/* Arrow Navigation - positioned above New Diagnosis button */}
      {sections.length > 1 && (
        <div className="arrow-navigation">
          <button 
            className="arrow-nav arrow-left" 
            onClick={prevSlide}
            title="Previous"
          >
            <ChevronLeftIcon />
          </button>
          <span className="slide-indicator">
            {currentSlide + 1} of {sections.length}
          </span>
          <button 
            className="arrow-nav arrow-right" 
            onClick={nextSlide}
            title="Next"
          >
            <ChevronRightIcon />
          </button>
        </div>
      )}
    </div>
  );
};

const AIHealth = () => {
  const [symptoms, setSymptoms] = useState('');
  const [patientAge, setPatientAge] = useState('');
  const [patientGender, setPatientGender] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [diagnosis, setDiagnosis] = useState(null);
  const [error, setError] = useState(null);
  const [progress, setProgress] = useState(0);
  // const [progressStatus, setProgressStatus] = useState(''); // Unused
  const [aiStatus, setAiStatus] = useState('checking');
  const [saveData, setSaveData] = useState(false);
  // const [showAuthPrompt, setShowAuthPrompt] = useState(false); // Unused
  
  const { user } = useAuth();
  // const navigate = useNavigate(); // Unused

  useEffect(() => {
    checkAiStatus();
  }, []);

  const checkAiStatus = async () => {
    const healthCheck = await aiService.healthCheck();
    setAiStatus(healthCheck.status);
    if (!healthCheck.success) {
      console.warn('AI service unavailable:', healthCheck.error);
    }
  };

  // Network-aware delay calculation
  const calculateDelay = () => {
    const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
    let baseDelay = 3000;
    
    if (connection) {
      if (connection.effectiveType === '2g') {
        baseDelay += 4000;
      } else if (connection.effectiveType === '3g') {
        baseDelay += 2000;
      } else if (connection.effectiveType === '4g') {
        baseDelay += 1000;
      }
    }
    
    return Math.max(baseDelay, 3000);
  };

  // Progress simulation
  const simulateProgress = async () => {
    const totalDelay = calculateDelay();
    const steps = 100;
    const interval = totalDelay / steps;
    
    // More detailed progress messages with medical terminology
    const progressStages = [
      { milestone: 0, message: 'Initializing AI diagnostic system...' },
      { milestone: 10, message: 'Parsing symptom descriptions...' },
      { milestone: 20, message: 'Analyzing symptom patterns...' },
      { milestone: 30, message: 'Evaluating potential conditions...' },
      { milestone: 40, message: 'Correlating with medical database...' },
      { milestone: 50, message: 'Applying differential diagnosis protocols...' },
      { milestone: 60, message: 'Calculating condition probabilities...' },
      { milestone: 70, message: 'Generating primary diagnosis...' },
      { milestone: 80, message: 'Formulating treatment recommendations...' },
      { milestone: 90, message: 'Preparing prescription details...' },
      { milestone: 95, message: 'Finalizing medical recommendations...' },
      { milestone: 100, message: 'Diagnosis complete!' }
    ];
    
    setProgress(0);
    // setProgressStatus('Initializing AI analysis...'); // Commented out - variable not defined
    
    // A bit of randomness for a more realistic feeling
    const addJitter = () => Math.random() * 0.5 - 0.25; // ±0.25
    
    let currentStageIndex = 0;
    
    for (let i = 0; i <= steps; i++) {
      // Add small random delay variation for more realistic progress
      const jitteredInterval = interval * (1 + addJitter());
      await new Promise(resolve => setTimeout(resolve, jitteredInterval));
      
      setProgress(i);
      
      // Check if we've reached a new milestone to update the message
      if (currentStageIndex < progressStages.length - 1 && 
          i >= progressStages[currentStageIndex + 1].milestone) {
        currentStageIndex++;
        // setProgressStatus(progressStages[currentStageIndex].message); // Commented out - variable not defined
      }
    }
  };

  const handleDiagnosis = async (e) => {
    e.preventDefault();
    
    if (!symptoms.trim()) {
      showToast.error('Please enter symptoms');
      return;
    }

    if (!patientAge || !patientGender) {
      showToast.error('Please select age and gender');
      return;
    }

    setIsLoading(true);
    setError(null);
    setDiagnosis(null);

    try {
      // Start progress simulation
      simulateProgress();

      const diagnosisRequest = {
        symptoms: symptoms.trim(),
        patient_data: {
          age: patientAge,
          gender: patientGender,
          patient_id: user ? (user.profile?.id || user.uid) : `guest_${Date.now()}`,
          name: user && user.profile ? `${user.profile.first_name} ${user.profile.last_name}` : 'Guest'
        },
        doctor_id: null, // No doctor for public access
        include_recommendations: true,
        detailed_analysis: true,
        save_to_database: saveData && user // Only save if user is logged in and wants to save
      };

      console.log('Sending diagnosis request:', diagnosisRequest);
      
      const result = await aiService.getDiagnosis(diagnosisRequest);
      
      if (result.success) {
        console.log('✅ Frontend received diagnosis data:', result.data);
        console.log('🔍 Has formatted_response?', !!result.data.formatted_response);
        setDiagnosis(result.data);
        showToast.success('AI diagnosis completed successfully');
        
        if (saveData && user) {
          showToast.info('Your diagnosis has been saved to your medical record');
        }
      } else {
        throw new Error(result.error || 'Failed to get diagnosis');
      }
    } catch (err) {
      console.error('Diagnosis error:', err);
      setError(err.message || 'Failed to get AI diagnosis. Please try again.');
      showToast.error('Failed to get diagnosis');
    } finally {
      setIsLoading(false);
      // Reset progress after a short delay
      setTimeout(() => {
        setProgress(0);
        // setProgressStatus(''); // Commented out - variable not defined
      }, 1000);
    }
  };

  const handleNewDiagnosis = () => {
    setSymptoms('');
    setPatientAge('');
    setPatientGender('');
    setDiagnosis(null);
    setError(null);
    setSaveData(false);
    // setShowAuthPrompt(false); // Commented out - variable not defined
  };

  return (
    <div className="medichain-container ai-health-page">
      {/* Background Animation */}
      <div className="background-crosses">
        <div className="cross cross-1">+</div>
        <div className="cross cross-2">+</div>
        <div className="cross cross-3">+</div>
        <div className="cross cross-4">+</div>
      </div>

      {/* Header */}
      <header className="header">
        <div className="logo-container">
          <div className="logo-icon">
            <img src={medichainLogo} alt="MediChain" className="medichain-logo" />
          </div>
          <h1>AI Health Assistant</h1>
        </div>
      </header>

      <main className="main-content">
        {/* Medical Disclaimer */}
        <DisclaimerNotice />
        
        <div className="content-layout">
          {/* Left Side - Symptom Input Form */}
          <div className="form-container">
            <div className="form-header">
              <div className="form-icon">
                <ClipboardIcon />
              </div>
              <h2>Describe Your Symptoms</h2>
              <p>Tell us what symptoms you're experiencing for AI-powered analysis</p>
            </div>

            <form onSubmit={handleDiagnosis} className="modern-form">
            <div className="form-row">
              <div className="input-group">
                <label className="input-label">
                  <UserIcon />
                  Age Group
                </label>
                <select
                  value={patientAge}
                  onChange={(e) => setPatientAge(e.target.value)}
                  className="modern-select"
                  required
                >
                  <option value="">Select age group</option>
                  <option value="child">Child (0 – 12 years)</option>
                  <option value="teen">Teenager (13 – 19 years)</option>
                  <option value="adult">Adult (20 – 59 years)</option>
                  <option value="senior">Senior (60+ years)</option>
                </select>
              </div>
              
              <div className="input-group">
                <label className="input-label">
                  <UserIcon />
                  Gender
                </label>
                <select
                  value={patientGender}
                  onChange={(e) => setPatientGender(e.target.value)}
                  className="modern-select"
                  required
                >
                  <option value="">Select gender</option>
                  <option value="male">Male</option>
                  <option value="female">Female</option>
                  <option value="other">Other</option>
                </select>
              </div>
            </div>

            <div className="input-group">
              <label className="input-label">
                <ClipboardIcon />
                Describe Your Symptoms
              </label>
              <textarea
                value={symptoms}
                onChange={(e) => setSymptoms(e.target.value)}
                placeholder="Please describe your symptoms in detail... (e.g., I have a high fever for 3 days, severe cough, and feeling tired)"
                className="modern-textarea"
                required
              />
            </div>

            <button 
              type="submit" 
              className="submit-button" 
              disabled={isLoading || aiStatus !== 'connected'}
            >
              {isLoading ? (
                <>
                  <div className="loading-spinner" />
                  Analyzing...
                </>
              ) : (
                <>
                  <SparklesIcon />
                  Get AI Diagnosis
                </>
              )}
            </button>
          </form>

          {/* Simple Loading State */}
          {isLoading && (
            <div className="simple-loading">
              <div className="loading-spinner large" />
              <p className="loading-text">Analyzing your symptoms...</p>
              <div className="loading-bar">
                <div className="loading-progress" style={{width: `${progress}%`}} />
              </div>
            </div>
          )}

          {/* Error Display */}
          {error && (
            <div className="error-container">
              <ExclamationIcon />
              {error}
            </div>
          )}

          {/* System Information */}
          <div className="system-info">
            <div className="system-info-item">
              <ActivityIcon />
              AI Status: {aiStatus === 'connected' ? 'Online' : 'Checking...'}
            </div>
            <div className="system-info-item">
              <ShieldIcon />
              {user && user.profile ? `Logged in as ${user.profile.first_name}` : 'Guest Mode'}
            </div>
            <div className="system-info-item">
              <DatabaseIcon />
              Data Saving: {user && saveData ? 'Enabled' : 'Disabled'}
            </div>
          </div>
        </div>

        {/* Right Side - AI Response Output */}
        <div className="results-side">
          {diagnosis && diagnosis.formatted_response && (
            <div className="results-container">
              <div className="results-header">
                <div className="results-icon">
                  <ActivityIcon />
                </div>
                <h3>AI Medical Analysis</h3>
              </div>
              
              {/* Medical Analysis Slideshow */}
              <MedicalAnalysisSlideshow 
                formattedResponse={diagnosis.formatted_response} 
                diagnosis={diagnosis.diagnosis}
                symptoms={symptoms}
                patientAge={patientAge}
                patientGender={patientGender}
              />

              {/* New Diagnosis Button */}
              <button 
                onClick={handleNewDiagnosis}
                className="submit-button"
                style={{ marginTop: '24px' }}
              >
                <ClipboardIcon />
                New Diagnosis
              </button>
            </div>
          )}
        </div>
      </div>
      </main>
    </div>
  );
};

export default AIHealth;