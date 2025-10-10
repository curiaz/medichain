import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { aiService } from '../services/aiService';
import notificationService from '../services/notificationService';
import LoadingSpinner from '../components/LoadingSpinner';
import AIProgressBar from '../components/AIProgressBar';
import { showToast } from '../components/CustomToast';
import medichainLogo from '../assets/medichain_logo.png';
import '../assets/styles/AIHealth_Modern.css';
import '../assets/styles/AIHealth_Slides.css';
import '../assets/styles/NewDiagnosisButton.css';
import '../assets/styles/LandingPage.css';

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

const ArrowLeftIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
  </svg>
);

// Unused icon components removed

// Medical Analysis Slideshow Component
const MedicalAnalysisSlideshow = ({ formattedResponse, diagnosis, symptoms, diagnosisResults }) => {
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
        recommended_action: '',
        medications: ''
      };
      
      // Extract content for each slide
      const symptomsMatch = response.match(/\*\*SLIDE_1_SYMPTOMS\*\*(.*?)\*\*SLIDE_2_CONDITIONS\*\*/s);
      if (symptomsMatch) {
        slideContent.symptoms = symptomsMatch[1].trim();
      }
      
      const conditionsMatch = response.match(/\*\*SLIDE_2_CONDITIONS\*\*(.*?)\*\*SLIDE_3_RECOMMENDED_ACTION\*\*/s);
      if (conditionsMatch) {
        slideContent.conditions = conditionsMatch[1].trim();
      }
      
      const recommendedActionMatch = response.match(/\*\*SLIDE_3_RECOMMENDED_ACTION\*\*(.*?)\*\*SLIDE_4_MEDICATIONS\*\*/s);
      if (recommendedActionMatch) {
        slideContent.recommended_action = recommendedActionMatch[1].trim();
      }
      
      const medicationsMatch = response.match(/\*\*SLIDE_4_MEDICATIONS\*\*(.*?)$/s);
      if (medicationsMatch) {
        slideContent.medications = medicationsMatch[1].trim();
      }
      
      // Create the 4 slides
      sections.push({
        type: 'symptoms',
        title: 'Symptoms Reported',
        content: slideContent.symptoms || symptoms || 'No symptoms specified'
      });
      
      sections.push({
        type: 'conditions', 
        title: 'Possible Conditions',
        content: slideContent.conditions || 'Analysis in progress...',
        diagnosisData: diagnosisResults || {}
      });
      
      // Debug: Log diagnosis data structure
      if (diagnosisResults) {
        console.log('🔍 DiagnosisResults structure:', diagnosisResults);
        console.log('🔍 Detailed Results:', diagnosisResults.detailed_results);
        console.log('🔍 Detailed Results Length:', diagnosisResults.detailed_results?.length);
      }
      
      sections.push({
        type: 'recommendations',
        title: 'Recommended Action', 
        content: slideContent.recommended_action || slideContent.severity || 'Action pending...',
        diagnosisData: diagnosisResults || {}
      });
      
      sections.push({
        type: 'medications',
        title: 'Medication',
        content: slideContent.medications || slideContent.recommendations || 'Medications loading...',
        diagnosisData: diagnosisResults || {}
      });
    } else {
      // Fallback structure when no formatted response available - create all 4 slides
      sections.push({
        type: 'symptoms',
        title: 'Symptoms Reported',
        content: symptoms || 'No symptoms specified'
      });
      
      sections.push({
        type: 'conditions', 
        title: 'Possible Conditions',
        content: 'Analysis complete - showing results...',
        diagnosisData: diagnosisResults || {}
      });
      
      // Debug: Log diagnosis data in fallback
      if (diagnosisResults) {
        console.log('DiagnosisResults (fallback):', diagnosisResults);
      }
      
      sections.push({
        type: 'recommendations',
        title: 'Recommended Action', 
        content: 'Action available...',
        diagnosisData: diagnosisResults || {}
      });
      
      sections.push({
        type: 'medications',
        title: 'Medication',
        content: 'Medications available...',
        diagnosisData: diagnosisResults || {}
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
              <div className="info-note">
                AI Analysis based on reported symptoms only
              </div>
            </div>
          </div>
        );

      case 'conditions':
        // Debug: Log slide data
        console.log('🔍 Conditions slide data:', slide);
        console.log('🔍 Slide diagnosisData:', slide.diagnosisData);
        console.log('🔍 Detailed results available:', slide.diagnosisData?.detailed_results);
        
        return (
          <div className="slide-content conditions-slide">
            <div className="slide-header">
              <div className="slide-icon">🔍</div>
              <h2 className="slide-title">Possible Conditions</h2>
            </div>
            
            {/* FORCE DISPLAY ALL 3 CONDITIONS FROM CSV */}
            <div className="professional-predictions">
              {slide.diagnosisData?.detailed_results?.length > 0 ? (
                // ALWAYS show ALL detailed results (up to 3)
                slide.diagnosisData.detailed_results.slice(0, 3).map((result, index) => (
                  <div key={index} className={`professional-prediction-item ${index === 0 ? 'primary' : 'secondary'}`}>
                    <div className={`professional-condition-header ${index === 0 ? 'primary' : 'alternative'}`}>
                      <div className="condition-badge-inline">
                        <span className="condition-rank">#{index + 1}</span>
                        <span className="confidence-badge">{result.confidence}</span>
                      </div>
                      <h3 className="diagnosis-name">{result.condition}</h3>
                    </div>
                    
                    <div className="condition-details">
                      <div className="reason-section">
                        <p className="explanation-text">{result.reason}</p>
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                // Debug display when no detailed_results
                <div className="debug-info">
                  <p>❌ No detailed_results found in diagnosisData</p>
                  <p>Available data: {JSON.stringify(Object.keys(slide.diagnosisData || {}))}</p>
                  <p>Primary condition: {slide.diagnosisData?.primary_condition}</p>
                </div>
              )}
            </div>
            
            {/* Fallback to text content if no structured data */}
            {!slide.diagnosisData?.detailed_results && !slide.diagnosisData?.primary_condition && (
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
            )}
          </div>
        );

      case 'recommendations':
        return (
          <div className="slide-content recommendations-slide">
            <div className="slide-header">
              <div className="slide-icon">�</div>
              <h2 className="slide-title">Recommended Action</h2>
            </div>
            <div className="recommendations-list">
              {/* Show combined recommended actions from all possible conditions */}
              {slide.diagnosisData?.symptom_explanations && slide.diagnosisData.symptom_explanations.length > 0 ? (
                slide.diagnosisData.symptom_explanations.map((explanation, index) => (
                  explanation.recommended_action && (
                    <div key={index} className="recommendation-item">
                      <strong>{explanation.diagnosis}:</strong> {explanation.recommended_action}
                    </div>
                  )
                ))
              ) : (
                slide.content.split('\n').filter(line => line.trim()).map((recommendation, index) => (
                  <div key={index} className="recommendation-item">
                    {recommendation.replace('•', '').trim()}
                  </div>
                ))
              )}
            </div>
          </div>
        );

      case 'medications':
        // Enhanced medications UI with creative design
        const medicationsData = slide.diagnosisData?.medications_data || [];
        
        return (
          <div className="slide-content medications-slide enhanced">
            <div className="slide-header">
              <div className="slide-icon">💊</div>
              <h2 className="slide-title">Treatment & Medication</h2>
              <p className="slide-subtitle">Based on your possible conditions</p>
            </div>
            
            <div className="medications-grid">
              {medicationsData.length > 0 ? (
                medicationsData.map((medication, index) => (
                  <div key={index} className="medication-card">
                    <div className="card-header">
                      <div className="condition-badge">
                        <span className="condition-rank">#{medication.id}</span>
                        <span className="condition-name">{medication.condition}</span>
                      </div>
                      <div className="confidence-indicator">
                        <span className="confidence-text">{medication.confidence}</span>
                      </div>
                    </div>
                    
                    <div className="medication-info">
                      <div className="medicine-section">
                        <div className="medicine-icon">🏥</div>
                        <div className="medicine-details">
                          <h4 className="medicine-name">{medication.medicine}</h4>
                          <p className="medicine-description">{medication.description}</p>
                        </div>
                      </div>
                      
                      <div className="dosage-grid">
                        <div className="dosage-item adult">
                          <div className="dosage-icon">👨‍⚕️</div>
                          <div className="dosage-info">
                            <span className="dosage-label">Adult Dose</span>
                            <span className="dosage-value">{medication.adult_dose}</span>
                          </div>
                        </div>
                        
                        <div className="dosage-item child">
                          <div className="dosage-icon">👶</div>
                          <div className="dosage-info">
                            <span className="dosage-label">Child Dose</span>
                            <span className="dosage-value">{medication.child_dose}</span>
                          </div>
                        </div>
                        
                        <div className="dosage-item max">
                          <div className="dosage-icon">⚠️</div>
                          <div className="dosage-info">
                            <span className="dosage-label">Max Daily</span>
                            <span className="dosage-value">{medication.max_daily_dose}</span>
                          </div>
                        </div>
                      </div>
                      
                      {medication.notes && (
                        <div className="medication-notes">
                          <div className="notes-icon">📝</div>
                          <p className="notes-text">{medication.notes}</p>
                        </div>
                      )}
                    </div>
                  </div>
                ))
              ) : (
                // Fallback to text-based display
                <div className="medications-fallback">
                  {slide.content.split('\n').filter(line => line.trim()).map((medication, index) => {
                    const cleanMedication = medication.replace('•', '').trim();
                    if (cleanMedication.includes(':')) {
                      const [name, dose] = cleanMedication.split(':');
                      return (
                        <div key={index} className="medication-item-simple">
                          <div className="medication-name">{name.replace(/\*\*/g, '').trim()}</div>
                          <div className="medication-dose">{dose.trim()}</div>
                        </div>
                      );
                    } else {
                      return (
                        <div key={index} className="medication-item-simple">
                          <div className="medication-name">{cleanMedication.replace(/\*\*/g, '')}</div>
                        </div>
                      );
                    }
                  })}
                </div>
              )}
            </div>
            
            <div className="medication-disclaimer">
              <div className="disclaimer-icon">⚕️</div>
              <p className="disclaimer-text">
                Always consult with a qualified healthcare provider before taking any medication. 
                This is for informational purposes only.
              </p>
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
  // Age and gender removed - streamlined system v5.0
  const [diagnosis, setDiagnosis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [aiStatus, setAiStatus] = useState('checking');
  const [formattedResponse, setFormattedResponse] = useState('');
  const [diagnosisResults, setDiagnosisResults] = useState(null);

  // Check AI service status on component mount
  useEffect(() => {
    const checkAIStatus = async () => {
      try {
        const response = await aiService.checkHealth();
        // Check if AI system is actually healthy and loaded
        if (response.status === 'healthy' && response.ai_ready) {
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

    // Age and gender validation removed - streamlined system v5.0

    setLoading(true);
    setError(null);
    setDiagnosis(null);

    try {
      const result = await aiService.getDiagnosis({
        symptoms: symptoms.trim()
      });

      if (result.success) {
        setDiagnosis(result.data.diagnosis);
        setFormattedResponse(result.data.formatted_response);
        setDiagnosisResults(result.data); // Store complete results for enhanced display
        showToast.success('Analysis completed successfully');

        // Notification creation temporarily disabled for streamlined system v5.0
        // This prevents errors while the notification service is being updated
        console.log('✅ Diagnosis completed successfully:', result.data.diagnosis);
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
    // Age and gender fields removed in v5.0
    setDiagnosis(null);
    setFormattedResponse('');
    setDiagnosisResults(null);
    setError(null);
  };

  return (
    <div className="ai-health-page">
      {/* Header */}
      <header className="header">
        <button 
          className="back-button"
          onClick={() => navigate(-1)}
          title="Go Back"
        >
          <ArrowLeftIcon />
        </button>
        <div className="header-content">
          <div className="logo-container">
            <div className="logo-icon">
              <img src={medichainLogo} alt="MediChain Logo" className="logo-image" />
            </div>
            <h1>AI Health Assistant</h1>
          </div>
          <div className="header-subtitle">Medical Analysis & Consultation</div>
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
              {/* Streamlined form - age/gender removed in v5.0 */}
              
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
                disabled={loading || !symptoms.trim()}
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
                  diagnosisResults={diagnosisResults}
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
            AI Status: {aiStatus === 'connected' ? 'Online' : 'Offline'}
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