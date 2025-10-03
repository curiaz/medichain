import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { aiService } from '../services/aiService';
import LoadingSpinner from '../components/LoadingSpinner';
import AIProgressBar from '../components/AIProgressBar';
import { showToast } from '../components/CustomToast';
import '../assets/styles/AIHealth_Modern.css';
import '../assets/styles/AIHealth_Slides.css';
import '../assets/styles/NewDiagnosisButton.css';

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
  
  // Parse the formatted response into 4-slide structure
  const parseResponse = (response) => {
    const sections = [];
    
    if (response && typeof response === 'string') {
      // Split response by slide markers
      const slideContent = {
        symptoms: '',
        conditions: '',
        severity: '',
        recommendations: ''
      };
      
      // Extract content for each slide
      const symptomsMatch = response.match(/\*\*SLIDE_1_SYMPTOMS\*\*(.*?)\*\*SLIDE_2_CONDITIONS\*\*/s);
      if (symptomsMatch) {
        slideContent.symptoms = symptomsMatch[1].trim();
      }
      
      const conditionsMatch = response.match(/\*\*SLIDE_2_CONDITIONS\*\*(.*?)\*\*SLIDE_3_SEVERITY\*\*/s);
      if (conditionsMatch) {
        slideContent.conditions = conditionsMatch[1].trim();
      }
      
      const severityMatch = response.match(/\*\*SLIDE_3_SEVERITY\*\*(.*?)\*\*SLIDE_4_RECOMMENDATIONS\*\*/s);
      if (severityMatch) {
        slideContent.severity = severityMatch[1].trim();
      }
      
      const recommendationsMatch = response.match(/\*\*SLIDE_4_RECOMMENDATIONS\*\*(.*?)$/s);
      if (recommendationsMatch) {
        slideContent.recommendations = recommendationsMatch[1].trim();
      }
      
      // Create the 4 slides
      sections.push({
        type: 'symptoms',
        title: 'Symptoms Reported',
        content: slideContent.symptoms || symptoms || 'No symptoms specified',
        patientAge,
        patientGender
      });
      
      sections.push({
        type: 'conditions', 
        title: 'Possible Conditions',
        content: slideContent.conditions || 'Analysis in progress...'
      });
      
      sections.push({
        type: 'severity',
        title: 'Severity Assessment', 
        content: slideContent.severity || 'Assessment pending...'
      });
      
      sections.push({
        type: 'recommendations',
        title: 'Recommended Action',
        content: slideContent.recommendations || 'Recommendations loading...'
      });
    } else {
      // Fallback structure when no response available
      sections.push({
        type: 'symptoms',
        title: 'Symptoms Reported',
        content: symptoms || 'No symptoms specified',
        patientAge,
        patientGender
      });
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
              <div className="slide-icon">📋</div>
              <h2 className="slide-title">Symptoms Reported</h2>
            </div>
            <div className="symptoms-summary">
              {typeof slide.content === 'string' 
                ? slide.content.split('\n').filter(line => line.trim()).join(', ').replace(/•/g, '').trim()
                : slide.content.symptoms || symptoms
              }
            </div>
            <div className="patient-info">
              <div className="patient-detail">
                <span className="detail-label">Age:</span> {slide.patientAge || 'Not specified'}
              </div>
              <div className="patient-detail">
                <span className="detail-label">Gender:</span> {slide.patientGender || 'Not specified'}
              </div>
            </div>
          </div>
        );

      case 'conditions':
        return (
          <div className="slide-content conditions-slide">
            <div className="slide-header">
              <div className="slide-icon">🔍</div>
              <h2 className="slide-title">Possible Conditions</h2>
            </div>
            <div className="conditions-list">
              {slide.content.split(/\d+\.\s+/).filter(section => section.trim()).map((condition, index) => {
                const [title, ...descriptionParts] = condition.split('\n').filter(line => line.trim());
                const description = descriptionParts.join(' ').trim();
                
                return (
                  <div key={index} className="condition-item">
                    <div className="condition-number">{index + 1}</div>
                    <div className="condition-content">
                      <h4 className="condition-title">{title}</h4>
                      {description && (
                        <p className="condition-description">{description}</p>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        );

      case 'severity':
        return (
          <div className="slide-content severity-slide">
            <div className="slide-header">
              <div className="slide-icon">🚦</div>
              <h2 className="slide-title">Severity Assessment</h2>
            </div>
            <div className="severity-content">
              {slide.content.split('\n').filter(line => line.trim()).map((point, index) => (
                <div key={index} className="severity-point">
                  {point.replace('•', '').trim()}
                </div>
              ))}
            </div>
          </div>
        );

      case 'recommendations':
        return (
          <div className="slide-content recommendations-slide">
            <div className="slide-header">
              <div className="slide-icon">✅</div>
              <h2 className="slide-title">Recommended Action</h2>
            </div>
            <div className="recommendations-list">
              {slide.content.split('\n').filter(line => line.trim()).map((recommendation, index) => (
                <div key={index} className="recommendation-item">
                  {recommendation.replace('•', '').trim()}
                </div>
              ))}
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
    <div className="ai-analysis-container">
      {/* Slide Number Navigation */}
      <div className="slide-numbers">
        {slides.map((_, index) => (
          <button
            key={index}
            className={`slide-number ${currentSlide === index ? 'active' : ''}`}
            onClick={() => goToSlide(index)}
            disabled={isTransitioning}
          >
            {index + 1}
          </button>
        ))}
      </div>
      
      {/* Main Content Area */}
      <div className="slide-content-wrapper">
        <div className={`slide ${isTransitioning ? 'transitioning' : ''}`}>
          {renderSlideContent(currentSlideData)}
        </div>
      </div>
      
      {/* Bottom Navigation */}
      <div className="slide-navigation">
        <button 
          onClick={prevSlide} 
          disabled={currentSlide === 0 || isTransitioning}
          className="nav-arrow prev"
        >
          ◀
        </button>
        
        <span className="slide-indicator">
          {currentSlide + 1} of {slides.length}
        </span>
        
        <button 
          onClick={nextSlide} 
          disabled={currentSlide === slides.length - 1 || isTransitioning}
          className="nav-arrow next"
        >
          ▶
        </button>
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
        const response = await fetch('http://localhost:5000/api/health');
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
      showToast.error('Please describe your symptoms');
      return;
    }

    if (!patientAge) {
      showToast.error('Please select your age group');
      return;
    }

    if (!patientGender) {
      showToast.error('Please select your gender');
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
        showToast.success('Analysis completed successfully');
      } else {
        throw new Error(result.error || 'Failed to get diagnosis');
      }
    } catch (error) {
      console.error('Diagnosis error:', error);
      setError(error.message || 'Failed to analyze symptoms. Please try again.');
      showToast.error('Analysis failed. Please try again.');
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
      <header className="header">
        <div className="logo-container">
          <div className="logo-icon">
            <HeartIcon />
          </div>
          <h1>AI Health Assistant</h1>
        </div>
        <div style={{ color: '#718096', fontSize: '16px' }}>Advanced Medical Analysis & Consultation</div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginTop: '8px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <div style={{ 
              width: '8px', 
              height: '8px', 
              borderRadius: '50%', 
              backgroundColor: aiStatus === 'connected' ? '#10b981' : '#ef4444' 
            }}></div>
            <span style={{ fontSize: '14px', color: '#4a5568' }}>
              AI {aiStatus === 'connected' ? 'Online' : 'Offline'}
            </span>
          </div>
          {!user && (
            <div style={{ display: 'flex', gap: '8px' }}>
              <button 
                onClick={() => navigate('/login')} 
                style={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  gap: '4px', 
                  padding: '6px 12px', 
                  background: '#0288d1', 
                  color: 'white', 
                  border: 'none', 
                  borderRadius: '6px', 
                  fontSize: '14px' 
                }}
              >
                <LoginIcon />
                Login
              </button>
              <button 
                onClick={() => navigate('/register')} 
                style={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  gap: '4px', 
                  padding: '6px 12px', 
                  background: '#10b981', 
                  color: 'white', 
                  border: 'none', 
                  borderRadius: '6px', 
                  fontSize: '14px' 
                }}
              >
                <UserPlusIcon />
                Register
              </button>
            </div>
          )}
        </div>
      </header>

      {/* Main Content */}
      <main className="main-content">
        {/* Disclaimer Notice */}
        <div className="disclaimer-notice">
          <div className="disclaimer-header">
            <svg width="20" height="20" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            Disclaimer:
          </div>
          <div className="disclaimer-content">
            <p>Our system is designed to provide symptom-based health insights using AI trained on medical datasets. It may suggest possible conditions, recommended actions, and general treatment information. However, the system is not a substitute for professional medical advice, diagnosis, or treatment.</p>
            <p>The outputs are predictions based on patterns in medical data and should be used only as a supportive tool, not as a final medical decision-maker. Always consult a licensed healthcare provider before starting, changing, or stopping any medical treatment.</p>
          </div>
        </div>

        {/* Content Layout */}
        <div className="content-layout">
          {/* Left Section - Input Form */}
          <div className="form-container" style={{ animation: 'slideInFromLeft 0.6s ease-out' }}>
            <div className="form-header">
              <div className="form-icon">
                <SparklesIcon />
              </div>
              <h2>Describe Your Symptoms</h2>
              <p>Tell us what symptoms you're experiencing for AI-powered analysis</p>
            </div>

            <form onSubmit={handleSubmit} className="modern-form">
              {/* Patient Information Row */}
              <div className="form-row">
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
              <button
                type="submit"
                disabled={loading || !symptoms.trim() || !patientAge || !patientGender}
                className="submit-button"
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
                  style={{
                    marginTop: '12px',
                    padding: '12px 24px',
                    background: '#e2e8f0',
                    color: '#4a5568',
                    border: 'none',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    width: '100%'
                  }}
                >
                  New Consultation
                </button>
              )}

              {/* Progress Indicator */}
              {loading && (
                <div style={{ marginTop: '20px' }}>
                  <AIProgressBar />
                </div>
              )}
            </form>
          </div>

          {/* Right Section - Analysis Results */}
          <div className="results-side">
            {loading && (
              <div className="simple-loading">
                <LoadingSpinner size="large" />
                <div className="loading-text">AI Analysis in Progress</div>
                <p>Analyzing your symptoms with advanced medical AI...</p>
                <div className="loading-bar">
                  <div className="loading-progress" style={{ width: '75%' }}></div>
                </div>
              </div>
            )}

            {error && (
              <div className="error-container">
                <div style={{ color: '#c53030', fontWeight: '600', marginBottom: '8px' }}>Analysis Error</div>
                <div>{error}</div>
              </div>
            )}

            {diagnosis && formattedResponse && !loading && (
              <div className="results-container" style={{ animation: 'slideInFromRight 0.6s ease-out' }}>
                <div className="results-header">
                  <div className="results-icon">
                    <ActivityIcon />
                  </div>
                  <h3>AI Health Analysis</h3>
                </div>
                <MedicalAnalysisSlideshow
                  formattedResponse={formattedResponse}
                  diagnosis={diagnosis}
                  symptoms={symptoms}
                  patientAge={patientAge}
                  patientGender={patientGender}
                />
                <div className="results-footer">
                  <button 
                    className="submit-button new-diagnosis-btn"
                    onClick={handleNewDiagnosis}
                  >
                    <ClipboardIcon />
                    <span>New Diagnosis</span>
                  </button>
                </div>
              </div>
            )}

            {!loading && !diagnosis && !error && (
              <div className="results-container">
                <div className="results-header">
                  <h2>AI Health Analysis</h2>
                  <p>Enter your symptoms to receive detailed medical analysis and recommendations.</p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* System Information Footer */}
        <div className="system-info">
          <div className="system-info-item">
            <ActivityIcon />
            AI Status: {aiStatus === 'connected' ? 'Online' : 'Checking...'}
          </div>
          <div className="system-info-item">
            <SparklesIcon />
            Enhanced AI Engine v2.1
          </div>
          <div className="system-info-item">
            <ClipboardIcon />
            Medical Database: 1700+ Conditions
          </div>
        </div>
      </main>
    </div>
  );
};

export default AIHealth;