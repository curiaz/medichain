import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { API_CONFIG } from '../config/api';
import { aiService } from '../services/aiService';
import LoadingSpinner from '../components/LoadingSpinner';
import AIProgressBar from '../components/AIProgressBar';
import { showToast } from '../components/CustomToast';
import '../assets/styles/AIHealth_Modern.css';

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

const LoginIcon = () => (
  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
  </svg>
);

const UserPlusIcon = () => (
  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
  </svg>
);

// Medical Analysis Slideshow Component
const MedicalAnalysisSlideshow = ({ formattedResponse, diagnosis, symptoms, patientAge, patientGender }) => {
  const [currentSlide, setCurrentSlide] = useState(0);
  const [isTransitioning, setIsTransitioning] = useState(false);
  
  // Parse the formatted response into sections
  const parseResponse = (response) => {
    const sections = [];
    
    // Slide 1: Symptoms Overview
    sections.push({
      type: 'symptoms',
      title: 'Symptoms Overview',
      content: {
        symptoms: symptoms,
        patientAge,
        patientGender
      }
    });

    // Parse sections from response
    if (response && typeof response === 'string') {
      const lines = response.split('\n');
      let currentSection = null;
      let currentContent = [];

      lines.forEach(line => {
        const trimmedLine = line.trim();
        
        // Check for section headers
        if (trimmedLine.includes('**PRELIMINARY DIAGNOSIS**')) {
          if (currentSection) {
            sections.push({ type: currentSection.type, title: currentSection.title, content: currentContent.join('\n') });
          }
          currentSection = { type: 'diagnosis', title: 'Preliminary Diagnosis' };
          currentContent = [];
        } else if (trimmedLine.includes('**POSSIBLE CONDITIONS**')) {
          if (currentSection) {
            sections.push({ type: currentSection.type, title: currentSection.title, content: currentContent.join('\n') });
          }
          currentSection = { type: 'conditions', title: 'Possible Conditions' };
          currentContent = [];
        } else if (trimmedLine.includes('**RECOMMENDATIONS**')) {
          if (currentSection) {
            sections.push({ type: currentSection.type, title: currentSection.title, content: currentContent.join('\n') });
          }
          currentSection = { type: 'recommendations', title: 'Recommendations' };
          currentContent = [];
        } else if (trimmedLine.includes('**PRECAUTIONS**')) {
          if (currentSection) {
            sections.push({ type: currentSection.type, title: currentSection.title, content: currentContent.join('\n') });
          }
          currentSection = { type: 'precautions', title: 'Precautions' };
          currentContent = [];
        } else if (currentSection && trimmedLine) {
          currentContent.push(trimmedLine);
        }
      });

      // Add the last section
      if (currentSection && currentContent.length > 0) {
        sections.push({ type: currentSection.type, title: currentSection.title, content: currentContent.join('\n') });
      }
    }

    return sections;
  };

  const slides = parseResponse(formattedResponse);

  const nextSlide = () => {
    if (isTransitioning || currentSlide >= slides.length - 1) return;
    setIsTransitioning(true);
    setTimeout(() => {
      setCurrentSlide(prev => prev + 1);
      setIsTransitioning(false);
    }, 150);
  };

  const prevSlide = () => {
    if (isTransitioning || currentSlide <= 0) return;
    setIsTransitioning(true);
    setTimeout(() => {
      setCurrentSlide(prev => prev - 1);
      setIsTransitioning(false);
    }, 150);
  };

  const goToSlide = (slideIndex) => {
    if (isTransitioning || slideIndex === currentSlide) return;
    setIsTransitioning(true);
    setTimeout(() => {
      setCurrentSlide(slideIndex);
      setIsTransitioning(false);
    }, 150);
  };

  if (!slides || slides.length === 0) {
    return <div>No analysis available</div>;
  }

  const currentSlideData = slides[currentSlide];

  const renderSlideContent = (slide) => {
    switch (slide.type) {
      case 'symptoms':
        return (
          <div className="slide-content symptoms-slide">
            <div className="slide-header">
              <h2 className="slide-title">Patient Information & Symptoms</h2>
            </div>
            <div className="patient-info-grid">
              <div className="patient-detail">
                <span className="detail-label">Age Group:</span>
                <span className="detail-value">{slide.content.patientAge}</span>
              </div>
              <div className="patient-detail">
                <span className="detail-label">Gender:</span>
                <span className="detail-value">{slide.content.patientGender}</span>
              </div>
            </div>
            <div className="symptoms-content">
              <h3>Reported Symptoms:</h3>
              <div className="symptoms-text">{slide.content.symptoms}</div>
            </div>
          </div>
        );

      case 'diagnosis':
        return (
          <div className="slide-content diagnosis-slide">
            <div className="slide-header">
              <h2 className="slide-title">Preliminary Diagnosis</h2>
            </div>
            <div className="diagnosis-content">
              <div className="content-text">{slide.content}</div>
            </div>
          </div>
        );

      case 'conditions':
        return (
          <div className="slide-content conditions-slide">
            <div className="slide-header">
              <h2 className="slide-title">Possible Conditions</h2>
            </div>
            <div className="conditions-content">
              <div className="content-text">{slide.content}</div>
            </div>
          </div>
        );

      case 'recommendations':
        return (
          <div className="slide-content recommendations-slide">
            <div className="slide-header">
              <h2 className="slide-title">Medical Recommendations</h2>
            </div>
            <div className="recommendations-content">
              <div className="content-text">{slide.content}</div>
            </div>
          </div>
        );

      case 'precautions':
        return (
          <div className="slide-content precautions-slide">
            <div className="slide-header">
              <h2 className="slide-title">Important Precautions</h2>
            </div>
            <div className="precautions-content">
              <div className="content-text">{slide.content}</div>
            </div>
          </div>
        );

      default:
        return (
          <div className="slide-content default-slide">
            <div className="slide-header">
              <h2 className="slide-title">{slide.title}</h2>
            </div>
            <div className="default-content">
              <div className="content-text">{slide.content}</div>
            </div>
          </div>
        );
    }
  };

  return (
    <div className="slideshow-container">
      <div className={`slide ${isTransitioning ? 'transitioning' : ''}`}>
        {renderSlideContent(currentSlideData)}
      </div>

      {/* Navigation Controls */}
      <div className="slideshow-navigation">
        <button 
          onClick={prevSlide} 
          disabled={currentSlide === 0 || isTransitioning}
          className="nav-btn prev-btn"
        >
          <ChevronLeftIcon />
        </button>

        <div className="slide-indicators">
          {slides.map((_, index) => (
            <button
              key={index}
              onClick={() => goToSlide(index)}
              className={`indicator ${index === currentSlide ? 'active' : ''}`}
              disabled={isTransitioning}
            />
          ))}
        </div>

        <button 
          onClick={nextSlide} 
          disabled={currentSlide === slides.length - 1 || isTransitioning}
          className="nav-btn next-btn"
        >
          <ChevronRightIcon />
        </button>
      </div>

      {/* Slide Counter */}
      <div className="slide-counter">
        {currentSlide + 1} / {slides.length}
      </div>
    </div>
  );
};

// Main AIHealth Component
const AIHealth = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [symptoms, setSymptoms] = useState('');
  const [patientAge, setPatientAge] = useState('');
  const [patientGender, setPatientGender] = useState('');
  const [diagnosis, setDiagnosis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [aiStatus, setAiStatus] = useState('checking');
  const [formattedResponse, setFormattedResponse] = useState('');

  // Check AI service status on component mount
  useEffect(() => {
    const checkAIStatus = async () => {
      try {
        const response = await fetch(`${API_CONFIG.BASE_URL}/health`);
        if (response.ok) {
          setAiStatus('connected');
        } else {
          setAiStatus('error');
        }
      } catch (error) {
        console.log('AI service check:', error.message);
        setAiStatus('error');
      }
    };

    checkAIStatus();
    // Check status every 30 seconds
    const interval = setInterval(checkAIStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!symptoms.trim()) {
      showToast('Please describe your symptoms', 'error');
      return;
    }

    if (!patientAge) {
      showToast('Please select your age group', 'error');
      return;
    }

    if (!patientGender) {
      showToast('Please select your gender', 'error');
      return;
    }

    setLoading(true);
    setError(null);
    setDiagnosis(null);

    try {
      const result = await aiService.getDiagnosis({
        symptoms: symptoms.trim(),
        patientAge,
        patientGender
      });

      if (result.success) {
        setDiagnosis(result.data.diagnosis);
        setFormattedResponse(result.data.formatted_response);
        showToast('Analysis completed successfully', 'success');
      } else {
        throw new Error(result.error || 'Failed to get diagnosis');
      }
    } catch (error) {
      console.error('Diagnosis error:', error);
      setError(error.message || 'Failed to analyze symptoms. Please try again.');
      showToast('Analysis failed. Please try again.', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleNewDiagnosis = () => {
    setSymptoms('');
    setPatientAge('');
    setPatientGender('');
    setDiagnosis(null);
    setFormattedResponse('');
    setError(null);
  };

  return (
    <div className="ai-health-page">
      {/* Header */}
      <header className="page-header">
        <div className="header-content">
          <div className="header-left">
            <h1 className="page-title">
              <HeartIcon />
              AI Health Assistant
            </h1>
            <p className="page-subtitle">Advanced Medical Analysis & Consultation</p>
          </div>
          
          <div className="header-right">
            <div className="ai-status-indicator">
              <div className={`status-dot ${aiStatus === 'connected' ? 'online' : 'offline'}`}></div>
              <span>AI {aiStatus === 'connected' ? 'Online' : 'Offline'}</span>
            </div>
            
            {!user && (
              <div className="auth-buttons">
                <button 
                  onClick={() => navigate('/login')} 
                  className="auth-btn login-btn"
                >
                  <LoginIcon />
                  Login
                </button>
                <button 
                  onClick={() => navigate('/register')} 
                  className="auth-btn register-btn"
                >
                  <UserPlusIcon />
                  Register
                </button>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="main-content">
        <div className="content-container">
          {/* Left Section - Input Form */}
          <div className="left-section">
            <div className="form-container">
              <div className="form-header">
                <SparklesIcon />
                <h2>Describe Your Symptoms</h2>
                <p>Provide detailed information for accurate analysis</p>
              </div>

              <form onSubmit={handleSubmit} className="symptom-form">
                {/* Patient Information */}
                <div className="form-section">
                  <div className="section-title">Patient Information</div>
                  <div className="input-row">
                    <div className="input-group">
                      <label className="input-label">
                        <UserIcon />
                        Age Group
                      </label>
                      <select 
                        className="modern-select" 
                        value={patientAge} 
                        onChange={(e) => setPatientAge(e.target.value)}
                      >
                        <option value="">Select age group</option>
                        <option value="Child (2 - 17 years)">Child (2 - 17 years)</option>
                        <option value="Adult (18 - 64 years)">Adult (18 - 64 years)</option>
                        <option value="Senior (65+ years)">Senior (65+ years)</option>
                      </select>
                    </div>
                    
                    <div className="input-group">
                      <label className="input-label">
                        <UserIcon />
                        Gender
                      </label>
                      <select 
                        className="modern-select" 
                        value={patientGender} 
                        onChange={(e) => setPatientGender(e.target.value)}
                      >
                        <option value="">Select gender</option>
                        <option value="Male">Male</option>
                        <option value="Female">Female</option>
                      </select>
                    </div>
                  </div>
                </div>

                {/* Symptoms Input */}
                <div className="input-group">
                  <label className="input-label">
                    <ClipboardIcon />
                    Describe Your Symptoms
                  </label>
                  <textarea
                    className="modern-textarea"
                    value={symptoms}
                    onChange={(e) => setSymptoms(e.target.value)}
                    placeholder="Please describe your symptoms in detail... (e.g., I have severe headache for 3 days, fatigue, mild dizziness and shortness of breath)"
                    rows={6}
                  />
                </div>

                {/* Submit Button */}
                <div className="form-actions">
                  <button
                    type="submit"
                    disabled={loading || !symptoms.trim() || !patientAge || !patientGender}
                    className={`submit-btn ${loading ? 'loading' : ''}`}
                  >
                    {loading ? (
                      <>
                        <LoadingSpinner size="small" />
                        <span>Analyzing...</span>
                      </>
                    ) : (
                      <>
                        <SparklesIcon />
                        <span>Analyze Symptoms</span>
                      </>
                    )}
                  </button>
                  
                  {diagnosis && (
                    <button
                      type="button"
                      onClick={handleNewDiagnosis}
                      className="secondary-btn"
                    >
                      New Consultation
                    </button>
                  )}
                </div>

                {/* Progress Indicator */}
                {loading && (
                  <div className="progress-container">
                    <AIProgressBar />
                  </div>
                )}
              </form>
            </div>
          </div>

          {/* Right Section - Analysis Results */}
          <div className="right-section">
            {loading && (
              <div className="analysis-loading">
                <div className="loading-content">
                  <LoadingSpinner />
                  <h3>AI Analysis in Progress</h3>
                  <p>Analyzing your symptoms with advanced medical AI...</p>
                </div>
              </div>
            )}

            {error && (
              <div className="error-container">
                <div className="error-header">Analysis Error</div>
                <div className="error-content">{error}</div>
              </div>
            )}

            {diagnosis && formattedResponse && !loading && (
              <div className="results-container">
                <MedicalAnalysisSlideshow
                  formattedResponse={formattedResponse}
                  diagnosis={diagnosis}
                  symptoms={symptoms}
                  patientAge={patientAge}
                  patientGender={patientGender}
                />
              </div>
            )}

            {!loading && !diagnosis && !error && (
              <div className="welcome-panel">
                <div className="welcome-content">
                  <SparklesIcon />
                  <h3>AI Health Analysis</h3>
                  <p>Enter your symptoms to receive detailed medical analysis and recommendations.</p>
                  <div className="features-grid">
                    <div className="feature-item">
                      <ActivityIcon />
                      <span>Advanced AI Diagnosis</span>
                    </div>
                    <div className="feature-item">
                      <ClipboardIcon />
                      <span>Detailed Analysis</span>
                    </div>
                    <div className="feature-item">
                      <UserIcon />
                      <span>Personalized Results</span>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* System Information Footer */}
        <div className="system-info">
          <div className="system-grid">
            <div className="system-item">
              <ActivityIcon />
              AI Status: {aiStatus === 'connected' ? 'Online' : 'Checking...'}
            </div>
            <div className="system-item">
              <SparklesIcon />
              Enhanced AI Engine v2.1
            </div>
            <div className="system-item">
              <ClipboardIcon />
              Medical Database: 1700+ Conditions
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default AIHealth;