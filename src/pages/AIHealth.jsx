import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { aiService } from '../services/aiService';
import LoadingSpinner from '../components/LoadingSpinner';
import AIProgressBar from '../components/AIProgressBar';
import { showToast } from '../components/CustomToast';
import '../assets/styles/AIHealth.css';

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

const CheckIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
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

const ActivityIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
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

const AIHealth = () => {
  const [symptoms, setSymptoms] = useState('');
  const [patientAge, setPatientAge] = useState('');
  const [patientGender, setPatientGender] = useState('');
  const [diagnosis, setDiagnosis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [progress, setProgress] = useState(0);
  const [progressStatus, setProgressStatus] = useState('');
  const [aiStatus, setAiStatus] = useState('checking');
  const [saveData, setSaveData] = useState(false);
  const [showAuthPrompt, setShowAuthPrompt] = useState(false);
  const [sessionData, setSessionData] = useState(null);
  
  const { user } = useAuth();
  const navigate = useNavigate();

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
    setProgressStatus('Initializing AI analysis...');
    
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
        setProgressStatus(progressStages[currentStageIndex].message);
      }
    }
  };

  const handleDiagnosis = async () => {
    if (!symptoms.trim()) {
      showToast.error('Please enter symptoms');
      return;
    }

    if (!patientAge || !patientGender) {
      showToast.error('Please enter patient age and gender');
      return;
    }

    // If user wants to save data but isn't logged in, show auth prompt
    if (saveData && !user) {
      setShowAuthPrompt(true);
      return;
    }

    setLoading(true);
    setError(null);
    setDiagnosis(null);
    setProgress(0);
    
    // Start progress simulation
    await simulateProgress();

    try {
      // Create the proper format for symptoms
      const symptomText = symptoms.trim();
      
      const diagnosisRequest = {
        symptoms: { symptomText: symptomText }, // Passing as a dictionary with the symptomText key
        patient_data: {
          age: parseInt(patientAge),
          gender: patientGender,
          patient_id: user ? user.id : `guest_${Date.now()}`,
          name: user ? `${user.first_name} ${user.last_name}` : 'Guest'
        },
        doctor_id: null, // No doctor for public access
        include_recommendations: true,
        detailed_analysis: true,
        save_to_database: saveData && user, // Only save if user is logged in and wants to save
        session_type: user ? 'authenticated' : 'guest'
      };

      console.log('Sending diagnosis request:', diagnosisRequest);
      
      const result = await aiService.getDiagnosis(diagnosisRequest);
      
      if (result.success) {
        setDiagnosis(result.data);
        setSessionData({
          symptoms,
          age: patientAge,
          gender: patientGender,
          timestamp: new Date().toISOString(),
          saved: saveData && user
        });
        showToast.success('AI diagnosis completed successfully');
        
        if (saveData && user) {
          showToast.info('Your diagnosis has been saved to your medical record');
        }
      } else {
        throw new Error(result.error || 'Failed to get diagnosis');
      }
      
    } catch (err) {
      console.error('Diagnosis error:', err);
      setError(err.message);
      
      if (aiStatus === 'disconnected') {
        showToast.error('AI service is unavailable. Please try again later.');
      } else {
        showToast.error('Failed to get AI diagnosis: ' + err.message);
      }
    } finally {
      setLoading(false);
      setTimeout(() => {
        setProgress(0);
        setProgressStatus('');
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
    setShowAuthPrompt(false);
    setSessionData(null);
  };

  const handleSignup = () => {
    navigate('/signup');
  };

  const handleLogin = () => {
    navigate('/login');
  };

  const closeAuthPrompt = () => {
    setShowAuthPrompt(false);
    setSaveData(false);
  };

  return (
    <div className="ai-assistant-container">
      {/* Background crosses */}
      <div className="background-crosses">
        {[...Array(12)].map((_, i) => (
          <span key={i} className="cross">+</span>
        ))}
      </div>

      <main className="ai-main-content">
        {/* Header */}
        <div className="ai-header">
          <div className="ai-header-icon">
            <HeartIcon />
          </div>
          <h1>MediChain AI Health Assistant</h1>
          <p>
            Get instant AI-powered health insights and personalized medical recommendations. 
            Our advanced system analyzes your symptoms and provides comprehensive treatment guidance.
          </p>
        </div>

        <div className="ai-layout-container">
          {/* Left Section - Input Form */}
          <div className="ai-left-section">
            <div className="ai-card">
              <div className="ai-card-header">
                <ClipboardIcon />
                Symptom Analysis
              </div>
              
              <div className="ai-form-group">
                <label className="ai-label">
                  <UserIcon />
                  Patient Age
                </label>
                <input
                  type="number"
                  value={patientAge}
                  onChange={(e) => setPatientAge(e.target.value)}
                  placeholder="Enter age"
                  min="1"
                  max="120"
                  className="ai-input"
                />
              </div>
              
              <div className="ai-form-group">
                <label className="ai-label">
                  <UserIcon />
                  Gender
                </label>
                <div className="ai-select-wrapper">
                  <select
                    value={patientGender}
                    onChange={(e) => setPatientGender(e.target.value)}
                    className="ai-select-clean"
                  >
                    <option value="">Select gender</option>
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                    <option value="other">Other</option>
                  </select>
                </div>
              </div>

            <div className="ai-form-group">
              <label className="ai-label">
                <ClipboardIcon />
                Describe Your Symptoms
              </label>
              <textarea
                value={symptoms}
                onChange={(e) => setSymptoms(e.target.value)}
                placeholder="Please describe your symptoms in detail... (e.g., I have a high fever for 3 days, severe cough, and feeling tired)"
                className="ai-textarea"
              />
              
              <div className="symptoms-examples">
                <p>Common symptoms you may include:</p>
                <div className="example-chips">
                  {['Fever', 'Cough', 'Headache', 'Fatigue', 'Sore throat', 
                    'Shortness of breath', 'Nausea', 'Dizziness', 'Body aches', 
                    'Runny nose'].map((example, idx) => (
                    <span 
                      key={idx} 
                      className="example-chip"
                      onClick={() => setSymptoms(prev => {
                        const newText = prev.trim() ? 
                          `${prev}, ${example.toLowerCase()}` : 
                          example.toLowerCase();
                        return newText;
                      })}
                    >
                      + {example}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            {/* Save Data Option for logged-in users */}
            {user && (
              <div className="save-data-option">
                <label className="checkbox-container">
                  <input
                    type="checkbox"
                    checked={saveData}
                    onChange={(e) => setSaveData(e.target.checked)}
                  />
                  <span className="checkmark"></span>
                  <span className="checkbox-text">
                    <DatabaseIcon />
                    Save this consultation to my medical record
                  </span>
                </label>
                <div className="save-data-info">
                  <ShieldIcon />
                  Saved consultations can be reviewed by your doctor during appointments
                </div>
              </div>
            )}

            {/* Guest notice */}
            {!user && (
              <div className="ai-output-card yellow">
                <div className="ai-output-title">
                  <ExclamationIcon />
                  Guest Mode
                </div>
                <div className="ai-output-content">
                  You're using MediChain as a guest. Your consultation will not be saved. 
                  <button onClick={handleSignup} className="link-button">
                    Create an account
                  </button> to save your medical history.
                </div>
              </div>
            )}

            <div className="ai-button-group">
              <button
                onClick={handleDiagnosis}
                disabled={loading}
                className="ai-primary-button"
              >
                {loading ? (
                  <>
                    <LoadingSpinner size="small" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <SparklesIcon />
                    Get AI Diagnosis
                  </>
                )}
              </button>
              
              {diagnosis && (
                <button
                  onClick={handleNewDiagnosis}
                  className="ai-secondary-button"
                >
                  New Consultation
                </button>
              )}
            </div>

            {/* Progress Section moved to right side */}
            </div>
          </div>

          {/* Right Section - AI Analysis & Results */}
          <div className="ai-right-section">
            {/* AI Analysis Loading Panel */}
            {loading && (
              <div className="ai-analysis-panel">
                <div className="ai-analysis-header">
                  <div className="ai-analysis-icon">
                    <SparklesIcon />
                  </div>
                  <div className="ai-analysis-title">AI Medical Analysis</div>
                  <div className="ai-analysis-subtitle">Correlating with medical database...</div>
                </div>
                
                <div className="ai-analysis-progress">
                  <AIProgressBar 
                    isLoading={true} 
                    progress={progress} 
                    status={progressStatus}
                    className="enhanced-progress-bar"
                  />
                </div>
                
                <div className="ai-analysis-steps">
                  <div className={`analysis-step ${progress >= 25 ? 'completed' : progress >= 0 ? 'active' : ''}`}>
                    <div className="step-icon">1</div>
                    <div className="step-content">
                      <div className="step-title">Analyzing</div>
                      <div className="step-description">Processing input data</div>
                    </div>
                  </div>
                  <div className={`analysis-step ${progress >= 50 ? 'completed' : progress >= 25 ? 'active' : ''}`}>
                    <div className="step-icon">2</div>
                    <div className="step-content">
                      <div className="step-title">Computing</div>
                      <div className="step-description">Running AI algorithms</div>
                    </div>
                  </div>
                  <div className={`analysis-step ${progress >= 75 ? 'completed' : progress >= 50 ? 'active' : ''}`}>
                    <div className="step-icon">3</div>
                    <div className="step-content">
                      <div className="step-title">Diagnosing</div>
                      <div className="step-description">Generating results</div>
                    </div>
                  </div>
                  <div className={`analysis-step ${progress >= 100 ? 'completed' : progress >= 75 ? 'active' : ''}`}>
                    <div className="step-icon">4</div>
                    <div className="step-content">
                      <div className="step-title">Complete</div>
                      <div className="step-description">Analysis finished</div>
                    </div>
                  </div>
                </div>
                
                <div className="ai-analysis-status">
                  <div className="status-text">{progressStatus}</div>
                  <div className="status-percentage">{Math.round(progress)}%</div>
                </div>
              </div>
            )}

            {/* Results Panel */}
            {!loading && (
              <div className="ai-card">
                <div className="ai-card-header">
                  <ActivityIcon />
                  Diagnosis Results
                </div>
            
            {!diagnosis && !loading && (
              <div className="ai-empty-state">
                <div className="ai-empty-icon">
                  <HeartIcon />
                </div>
                <div className="ai-empty-title">Ready for Analysis</div>
                <div className="ai-empty-subtitle">
                  Enter your symptoms and patient information to receive an AI-powered health assessment
                </div>
              </div>
            )}

            {diagnosis && (
              <div className="ai-output-section">
                {/* Conversational Response */}
                {diagnosis.conversational_response && (
                  <div className="ai-output-card blue">
                    <div className="ai-output-title">
                      <CheckIcon />
                      AI Health Assessment
                    </div>
                    <div className="ai-output-content conversational-text">
                      {diagnosis.conversational_response.split('\n').map((line, index) => {
                        if (line.trim() === '') return <br key={index} />;
                        
                        if (line.includes('**') && line.includes('**')) {
                          const parts = line.split('**');
                          return (
                            <p key={index}>
                              {parts.map((part, i) => 
                                i % 2 === 1 ? <strong key={i}>{part}</strong> : part
                              )}
                            </p>
                          );
                        } else if (line.startsWith('•')) {
                          return <p key={index} className="bullet-point">{line}</p>;
                        } else if (line.includes('⚠️') || line.includes('✅') || line.includes('👨‍⚕️') || line.includes('🩺') || line.includes('💊') || line.includes('🔬') || line.includes('⏰') || line.includes('🕐') || line.includes('👉')) {
                          return <p key={index} className="icon-line">{line}</p>;
                        } else {
                          return <p key={index}>{line}</p>;
                        }
                      })}
                    </div>
                  </div>
                )}

                {/* Medication Response Toggle */}
                {diagnosis.medication_response && (
                  <div className="ai-output-card green">
                    <div className="ai-output-title">
                      <CheckIcon />
                      Medication Guidance
                    </div>
                    <div className="ai-output-content">
                      <button 
                        className="medication-toggle-btn"
                        onClick={() => {
                          setDiagnosis(prev => ({
                            ...prev,
                            showMedicationResponse: !prev.showMedicationResponse
                          }));
                        }}
                      >
                        {diagnosis.showMedicationResponse ? 'Show General Guidance' : 'Show Medication Focus'}
                      </button>
                      
                      {diagnosis.showMedicationResponse && (
                        <div className="medication-response">
                          {diagnosis.medication_response.split('\n').map((line, index) => {
                            if (line.trim() === '') return <br key={index} />;
                            
                            if (line.includes('**') && line.includes('**')) {
                              const parts = line.split('**');
                              return (
                                <p key={index}>
                                  {parts.map((part, i) => 
                                    i % 2 === 1 ? <strong key={i}>{part}</strong> : part
                                  )}
                                </p>
                              );
                            } else if (line.startsWith('•')) {
                              return <p key={index} className="bullet-point">{line}</p>;
                            } else if (line.includes('⚠️') || line.includes('✅') || line.includes('👨‍⚕️') || line.includes('🩺') || line.includes('💊')) {
                              return <p key={index} className="icon-line">{line}</p>;
                            } else {
                              return <p key={index}>{line}</p>;
                            }
                          })}
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Traditional Diagnosis (fallback) */}
                {!diagnosis.conversational_response && (
                  <>
                    <div className="ai-output-card blue">
                      <div className="ai-output-title">Primary Diagnosis</div>
                      <div className="ai-output-content">{diagnosis.diagnosis}</div>
                    </div>
                    
                    <div className="ai-output-card purple">
                      <div className="ai-output-title">Confidence Level</div>
                      <div className="ai-output-content">
                        <div className="confidence-bar">
                          <div 
                            className="confidence-fill" 
                            style={{ width: `${diagnosis.confidence}%` }}
                          ></div>
                          <span className="confidence-text">{diagnosis.confidence}%</span>
                        </div>
                      </div>
                    </div>
                  </>
                )}

                {/* Top 3 Predictions with Medications */}
                {diagnosis.top_predictions && diagnosis.top_predictions.length > 0 && (
                  <div className="ai-output-card green">
                    <div className="ai-output-title">
                      <SparklesIcon />
                      Top 3 Diagnostic Possibilities
                    </div>
                    <div className="ai-output-content">
                      <div className="predictions-grid">
                        {diagnosis.top_predictions.map((prediction, index) => (
                          <div key={index} className={`prediction-card ${index === 0 ? 'primary' : ''}`}>
                            <div className="prediction-header">
                              <div className="prediction-rank">#{index + 1}</div>
                              <div className="prediction-info">
                                <div className="prediction-name">{prediction.diagnosis.replace(/_/g, ' ')}</div>
                                <div className="prediction-confidence">
                                  <span className="confidence-percentage">{prediction.confidence.toFixed(1)}%</span>
                                  <div className="mini-confidence-bar">
                                    <div 
                                      className="mini-confidence-fill" 
                                      style={{ width: `${prediction.confidence}%` }}
                                    ></div>
                                  </div>
                                </div>
                              </div>
                            </div>
                            
                            {prediction.medications && (
                              <div className="prediction-medications">
                                <div className="medication-title">
                                  💊 Recommended Medications:
                                </div>
                                <ul className="medication-list">
                                  {prediction.medications.map((medication, medIndex) => (
                                    <li key={medIndex} className="medication-item">
                                      {medication}
                                    </li>
                                  ))}
                                </ul>
                                
                                {prediction.dosage && (
                                  <div className="medication-details">
                                    <div className="detail-item">
                                      <strong>Dosage:</strong> {prediction.dosage}
                                    </div>
                                    <div className="detail-item">
                                      <strong>Duration:</strong> {prediction.duration}
                                    </div>
                                    <div className="detail-item">
                                      <strong>Instructions:</strong> {prediction.instructions}
                                    </div>
                                  </div>
                                )}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                      
                      <div className="predictions-disclaimer">
                        <ExclamationIcon />
                        <span>These are AI-generated possibilities. Always consult a healthcare professional for proper diagnosis and treatment.</span>
                      </div>
                    </div>
                  </div>
                )}

                {/* Medical Disclaimer */}
                <div className="ai-output-card red">
                  <div className="ai-output-title">
                    <ExclamationIcon />
                    Medical Disclaimer
                  </div>
                  <div className="ai-output-content">
                    This AI diagnosis is for informational purposes only and should not replace 
                    professional medical advice. Please consult with a qualified healthcare 
                    provider for proper medical evaluation and treatment.
                  </div>
                </div>

                {/* Session Information */}
                {sessionData && (
                  <div className="ai-output-card gray">
                    <div className="ai-output-title">
                      <DatabaseIcon />
                      Session Information
                    </div>
                    <div className="ai-output-content">
                      {sessionData.saved ? (
                        <>
                          <CheckIcon style={{ color: '#16a34a', marginRight: '0.5rem' }} />
                          This consultation has been saved to your medical record
                        </>
                      ) : (
                        <>
                          <ExclamationIcon style={{ color: '#dc2626', marginRight: '0.5rem' }} />
                          This consultation was not saved and will be lost when you leave this page
                        </>
                      )}
                    </div>
                  </div>
                )}
              </div>
            )}

            {error && (
              <div className="ai-output-card red">
                <div className="ai-output-title">
                  <ExclamationIcon />
                  Error
                </div>
                <div className="ai-output-content">{error}</div>
              </div>
            )}
              </div>
            )}
          </div>
        </div>

        {/* System Information */}
        <div className="ai-system-info">
          <div className="ai-system-grid">
            <div className="ai-system-item">
              <ActivityIcon />
              AI Status: {aiStatus === 'connected' ? 'Online' : 'Checking...'}
            </div>
            <div className="ai-system-item">
              <ShieldIcon />
              {user ? `Logged in as ${user.first_name}` : 'Guest Mode'}
            </div>
            <div className="ai-system-item">
              <DatabaseIcon />
              Data Saving: {user && saveData ? 'Enabled' : 'Disabled'}
            </div>
          </div>
        </div>
      </main>

      {/* Auth Prompt Modal */}
      {showAuthPrompt && (
        <div className="modal-overlay">
          <div className="auth-prompt-modal">
            <h3>Account Required</h3>
            <p>To save your consultation history, you need to create an account or log in.</p>
            <div className="auth-prompt-actions">
              <button onClick={handleSignup} className="ai-primary-button">
                <UserPlusIcon />
                Create Account
              </button>
              <button onClick={handleLogin} className="ai-primary-button">
                <LoginIcon />
                Log In
              </button>
              <button onClick={closeAuthPrompt} className="ai-secondary-button">
                Continue as Guest
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AIHealth;
