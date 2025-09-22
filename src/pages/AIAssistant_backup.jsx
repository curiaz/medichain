import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Brain, User, Activity, FileText, RefreshCw, Plus, AlertCircle, ThumbsUp, ThumbsDown, Info, LogIn, UserPlus } from 'lucide-react';
import LoadingSpinner from '../components/LoadingSpinner';
import AIProgressBar from '../components/AIProgressBar';
import { showToast } from '../components/CustomToast';
import { aiService } from '../services/aiService';
import { useAuth } from '../context/AuthContext';
import '../assets/styles/LandingPage.css';
import '../assets/styles/AIHealth.css';

// Add CSS animations
const animationStyles = `
  @keyframes gradientShift {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.8; }
  }
  
  .ai-float {
    animation: float var(--transition-slow) infinite;
  }
`;

// Inject styles
if (!document.getElementById('ai-assistant-animations')) {
  const style = document.createElement('style');
  style.id = 'ai-assistant-animations';
  style.textContent = animationStyles;
  document.head.appendChild(style);
}

const AIAssistant = () => {
  const [symptoms, setSymptoms] = useState('');
  const [patientAge, setPatientAge] = useState('');
  const [patientGender, setPatientGender] = useState('');
  const [diagnosis, setDiagnosis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [progress, setProgress] = useState(0);
  const [progressStatus, setProgressStatus] = useState('');
  const [aiStatus, setAiStatus] = useState('checking');
  const [modelInfo, setModelInfo] = useState(null);
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false);
  const { user } = useAuth();

  useEffect(() => {
    checkAiStatus();
    loadModelInfo();
  }, []);

  const checkAiStatus = async () => {
    const healthCheck = await aiService.healthCheck();
    setAiStatus(healthCheck.status);
    if (!healthCheck.success) {
      console.warn('AI service unavailable:', healthCheck.error);
    }
  };

  const loadModelInfo = async () => {
    const result = await aiService.getModelInfo();
    if (result.success) {
      setModelInfo(result.data);
    }
  };

  // Network-aware delay calculation
  const calculateDelay = () => {
    // Simulate network speed detection
    const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
    let baseDelay = 3000; // Minimum 3 seconds
    
    if (connection) {
      if (connection.effectiveType === '2g') {
        baseDelay += 4000; // Slow network
      } else if (connection.effectiveType === '3g') {
        baseDelay += 2000; // Medium network
      } else if (connection.effectiveType === '4g') {
        baseDelay += 1000; // Fast network
      }
    }
    
    return Math.max(baseDelay, 3000); // Ensure minimum 3 seconds
  };

  // Progress simulation with network-aware delay
  const simulateProgress = async () => {
    const totalDelay = calculateDelay();
    const steps = 100;
    const interval = totalDelay / steps;
    
    setProgress(0);
    setProgressStatus('Initializing AI analysis...');
    
    for (let i = 0; i <= steps; i++) {
      await new Promise(resolve => setTimeout(resolve, interval));
      
      setProgress(i);
      
      if (i < 25) {
        setProgressStatus('Analyzing patient symptoms...');
      } else if (i < 50) {
        setProgressStatus('Processing medical data...');
      } else if (i < 75) {
        setProgressStatus('Generating diagnosis...');
      } else if (i < 100) {
        setProgressStatus('Finalizing prescription...');
      } else {
        setProgressStatus('Complete!');
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

    setLoading(true);
    setError(null);
    setDiagnosis(null);
    setProgress(0);
    setFeedbackSubmitted(false);
    
    // Start progress simulation
    await simulateProgress();

    try {
      const diagnosisRequest = {
        symptoms: symptoms.trim(),
        patient_data: {
          age: parseInt(patientAge),
          gender: patientGender,
          patient_id: `temp_${Date.now()}`,
          name: 'Patient'
        },
        doctor_id: user?.id || 'doctor_001',
        include_recommendations: true,
        detailed_analysis: true
      };

      console.log('Sending diagnosis request:', diagnosisRequest);
      
      const result = await aiService.getDiagnosis(diagnosisRequest);
      
      if (result.success) {
        setDiagnosis(result.data);
        showToast.success('AI diagnosis completed successfully');
      } else {
        throw new Error(result.error || 'Failed to get diagnosis');
      }
      
    } catch (err) {
      console.error('Diagnosis error:', err);
      setError(err.message);
      
      // Show enhanced fallback with AI service status
      if (aiStatus === 'disconnected') {
        showToast.error('AI service is unavailable. Please ensure the AI diagnosis server is running on port 5001.');
        return; // Don't show mock data if AI service is down
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

  const handleFeedback = async (isCorrect, additionalFeedback = '') => {
    if (!diagnosis) return;
    
    try {
      const feedbackData = {
        session_id: diagnosis.session_id || `session_${Date.now()}`,
        actual_diagnosis: isCorrect ? diagnosis.diagnosis : 'Incorrect diagnosis',
        doctor_notes: additionalFeedback || '',
        treatment_outcome: isCorrect ? 'Successful' : 'Requires revision',
        doctor_id: user?.id || 'doctor_001',
        timestamp: new Date().toISOString()
      };

      const result = await aiService.provideFeedback(feedbackData);
      
      if (result.success) {
        setFeedbackSubmitted(true);
        showToast.success('Thank you! Your feedback helps improve our AI model.');
      } else {
        showToast.error('Failed to submit feedback: ' + result.error);
      }
    } catch (error) {
      console.error('Feedback error:', error);
      showToast.error('Failed to submit feedback');
    }
  };

  const handleClear = () => {
    setSymptoms('');
    setPatientAge('');
    setPatientGender('');
    setDiagnosis(null);
    setError(null);
    setProgress(0);
    setProgressStatus('');
    setFeedbackSubmitted(false);
    showToast.info('Form cleared');
  };

  return (
    <div className="ai-assistant-container" style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #e0f2fe 0%, #b3e5fc 30%, #81d4fa 70%, #4dd0e1 100%)',
      position: 'relative',
      overflow: 'hidden'
    }}>
      {/* Animated Background */}
      <div style={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: `
          radial-gradient(circle at 20% 80%, rgba(33, 150, 243, 0.1) 0%, transparent 50%),
          radial-gradient(circle at 80% 20%, rgba(0, 188, 212, 0.1) 0%, transparent 50%),
          radial-gradient(circle at 40% 40%, rgba(2, 136, 209, 0.05) 0%, transparent 50%)
        `,
        animation: 'gradientShift 15s ease-in-out infinite'
      }}>
      </div>

      {/* Floating Medical Crosses */}
      <div style={{ position: 'absolute', top: '10%', left: '10%', color: 'rgba(2, 136, 209, 0.1)', animation: 'float 8s ease-in-out infinite', fontSize: '24px', fontWeight: 'bold', pointerEvents: 'none' }}>+</div>
      <div style={{ position: 'absolute', top: '20%', right: '15%', color: 'rgba(2, 136, 209, 0.1)', animation: 'float 8s ease-in-out infinite 2s', fontSize: '24px', fontWeight: 'bold', pointerEvents: 'none' }}>+</div>
      <div style={{ position: 'absolute', top: '60%', left: '8%', color: 'rgba(2, 136, 209, 0.1)', animation: 'float 8s ease-in-out infinite 4s', fontSize: '24px', fontWeight: 'bold', pointerEvents: 'none' }}>+</div>
      <div style={{ position: 'absolute', bottom: '20%', right: '10%', color: 'rgba(2, 136, 209, 0.1)', animation: 'float 8s ease-in-out infinite 1s', fontSize: '24px', fontWeight: 'bold', pointerEvents: 'none' }}>+</div>
      <div style={{ position: 'absolute', top: '45%', left: '85%', color: 'rgba(2, 136, 209, 0.1)', animation: 'float 8s ease-in-out infinite 3s', fontSize: '24px', fontWeight: 'bold', pointerEvents: 'none' }}>+</div>

      {user ? (
        <Header />
      ) : (
        <div style={{
          background: 'rgba(255, 255, 255, 0.95)',
          backdropFilter: 'blur(10px)',
          padding: '20px 0',
          borderBottom: '1px solid rgba(255, 255, 255, 0.2)',
          position: 'relative',
          zIndex: 100,
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center'
        }}>
          {/* Back button positioned absolutely in the corner */}
          <button
            onClick={() => window.location.href = '/'}
            style={{
              position: 'absolute',
              left: '20px',
              top: '50%',
              transform: 'translateY(-50%)',
              padding: '8px 16px',
              backgroundColor: 'transparent',
              color: '#2196f3',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: '500',
              transition: 'all 0.3s ease'
            }}
            onMouseOver={(e) => {
              e.target.style.color = '#1976d2';
              e.target.style.transform = 'translateY(-50%) scale(1.05)';
            }}
            onMouseOut={(e) => {
              e.target.style.color = '#2196f3';
              e.target.style.transform = 'translateY(-50%) scale(1)';
            }}
          >
            ← Back to Home
          </button>
          
          {/* Centered MEDICHAIN logo */}
          <div style={{
            fontSize: '28px',
            fontWeight: 'bold',
            color: '#333',
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            letterSpacing: '1px'
          }}>
            <span style={{
              width: '40px',
              height: '40px',
              background: 'linear-gradient(135deg, #4dd0e1, #2196f3)',
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'white',
              fontSize: '20px',
              fontWeight: 'bold',
              boxShadow: '0 4px 15px rgba(77, 208, 225, 0.3)'
            }}>+</span>
            MEDICHAIN
          </div>
        </div>
      )}
      
      <main className="ai-main-content" style={{ position: 'relative', zIndex: 10 }}>
        <div className="max-w-7xl mx-auto px-4 py-8">
          {/* Header Section */}
          <div className="ai-header" style={{
            background: 'rgba(255, 255, 255, 0.95)',
            backdropFilter: 'blur(10px)',
            borderRadius: '20px',
            padding: '60px 40px',
            marginBottom: '40px',
            border: '1px solid rgba(255, 255, 255, 0.2)',
            boxShadow: '0 20px 60px rgba(0, 0, 0, 0.1)',
            textAlign: 'center',
            position: 'relative',
            overflow: 'hidden'
          }}>
            {/* Header background pattern */}
            <div style={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              background: `
                radial-gradient(circle at 20% 80%, rgba(33, 150, 243, 0.05) 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, rgba(0, 188, 212, 0.05) 0%, transparent 50%)
              `,
              pointerEvents: 'none'
            }}></div>
            
            <div className="ai-header-icon" style={{
              margin: '0 auto 30px auto',
              width: '100px',
              height: '100px',
              background: 'linear-gradient(135deg, #4dd0e1, #2196f3)',
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 20px 60px rgba(77, 208, 225, 0.4)',
              position: 'relative',
              zIndex: 1
            }}>
              <Brain className="w-12 h-12 text-white" />
            </div>
            
            <div style={{ position: 'relative', zIndex: 1 }}>
              <div style={{
                display: 'inline-block',
                background: 'rgba(33, 150, 243, 0.1)',
                color: '#2196f3',
                padding: '8px 20px',
                borderRadius: '25px',
                fontSize: '14px',
                fontWeight: '600',
                marginBottom: '20px',
                border: '1px solid rgba(33, 150, 243, 0.2)'
              }}>
                🤖 AI-Powered Healthcare Platform
              </div>
              
              <h1 style={{
                fontSize: '3.5rem',
                fontWeight: '800',
                color: '#333',
                marginBottom: '20px',
                lineHeight: '1.1'
              }}>
                AI <span style={{
                  background: 'linear-gradient(135deg, #2196f3, #00bcd4)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  backgroundClip: 'text'
                }}>Assistant</span>
              </h1>
              
              <p style={{
                fontSize: '1.2rem',
                color: '#555',
                maxWidth: '700px',
                margin: '0 auto 30px auto',
                lineHeight: '1.6'
              }}>
                Advanced AI-Driven Diagnosis and Prescription System with Blockchain-Integrated Health Records
              </p>
            
            {/* AI Status Indicator */}
            <div className="flex items-center justify-center mt-8 space-x-6">
              <div className={`flex items-center px-6 py-3 rounded-full text-sm font-medium shadow-lg backdrop-filter backdrop-blur-sm ${
                aiStatus === 'connected' ? 'bg-green-50 text-green-800 border border-green-200' :
                aiStatus === 'disconnected' ? 'bg-red-50 text-red-800 border border-red-200' :
                'bg-yellow-50 text-yellow-800 border border-yellow-200'
              }`} style={{ position: 'relative', zIndex: 1 }}>
                <div className={`w-3 h-3 rounded-full mr-3 ${
                  aiStatus === 'connected' ? 'bg-green-500 animate-pulse' :
                  aiStatus === 'disconnected' ? 'bg-red-500' :
                  'bg-yellow-500 animate-pulse'
                }`}></div>
                AI Service: {aiStatus === 'connected' ? 'Connected' : 
                           aiStatus === 'disconnected' ? 'Disconnected' : 'Checking...'}
              </div>
              
              {modelInfo && (
                <div className="text-sm text-gray-600 bg-white px-6 py-3 rounded-full border border-gray-200 shadow-lg backdrop-filter backdrop-blur-sm" style={{ position: 'relative', zIndex: 1 }}>
                  Model: {modelInfo.version} | Accuracy: {modelInfo.accuracy}%
                </div>
              )}
            </div>
            </div>
          </div>

          <div className="ai-grid" style={{ 
            display: 'grid', 
            gridTemplateColumns: '1fr 1fr', 
            gap: '30px', 
            marginBottom: '50px' 
          }}>
            {/* Input Section */}
            <div className="ai-card" style={{
              background: 'rgba(255, 255, 255, 0.95)',
              backdropFilter: 'blur(10px)',
              borderRadius: '20px',
              padding: '40px',
              border: '1px solid rgba(255, 255, 255, 0.2)',
              boxShadow: '0 20px 60px rgba(0, 0, 0, 0.1)',
              position: 'relative',
              overflow: 'hidden'
            }}>
              <div style={{
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                background: `
                  radial-gradient(circle at 10% 20%, rgba(33, 150, 243, 0.05) 0%, transparent 50%),
                  radial-gradient(circle at 90% 80%, rgba(0, 188, 212, 0.05) 0%, transparent 50%)
                `,
                pointerEvents: 'none'
              }}></div>
              
              <div className="ai-card-header" style={{
                display: 'flex',
                alignItems: 'center',
                marginBottom: '30px',
                fontSize: '20px',
                fontWeight: '700',
                color: '#333',
                position: 'relative',
                zIndex: 1
              }}>
                <div style={{
                  width: '50px',
                  height: '50px',
                  background: 'linear-gradient(135deg, #4dd0e1, #2196f3)',
                  borderRadius: '15px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  marginRight: '15px',
                  boxShadow: '0 8px 25px rgba(77, 208, 225, 0.3)'
                }}>
                  <Activity className="w-6 h-6 text-white" />
                </div>
                Patient Symptoms
              </div>

              <div className="space-y-6" style={{ position: 'relative', zIndex: 1 }}>
                {/* Patient Age */}
                <div className="ai-form-group">
                  <label className="ai-label" style={{
                    display: 'flex',
                    alignItems: 'center',
                    fontSize: '16px',
                    fontWeight: '600',
                    color: '#333',
                    marginBottom: '10px'
                  }}>
                    <User className="w-4 h-4 inline mr-2" />
                    Patient Age
                  </label>
                  <input
                    type="number"
                    value={patientAge}
                    onChange={(e) => setPatientAge(e.target.value)}
                    placeholder="Enter patient age (e.g., 35)"
                    min="1"
                    max="120"
                    style={{
                      width: '100%',
                      padding: '15px 20px',
                      borderRadius: '12px',
                      border: '2px solid #e5e7eb',
                      fontSize: '16px',
                      transition: 'all 0.3s ease',
                      background: 'rgba(255, 255, 255, 0.8)',
                      backdropFilter: 'blur(5px)'
                    }}
                    onFocus={(e) => e.target.style.borderColor = '#2196f3'}
                    onBlur={(e) => e.target.style.borderColor = '#e5e7eb'}
                  />
                </div>

                {/* Patient Gender */}
                <div className="ai-form-group">
                  <label className="ai-label" style={{
                    display: 'flex',
                    alignItems: 'center',
                    fontSize: '16px',
                    fontWeight: '600',
                    color: '#333',
                    marginBottom: '10px'
                  }}>
                    <User className="w-4 h-4 inline mr-2" />
                    Patient Gender
                  </label>
                  <select
                    value={patientGender}
                    onChange={(e) => setPatientGender(e.target.value)}
                    style={{
                      width: '100%',
                      padding: '15px 20px',
                      borderRadius: '12px',
                      border: '2px solid #e5e7eb',
                      fontSize: '16px',
                      transition: 'all 0.3s ease',
                      background: 'rgba(255, 255, 255, 0.8)',
                      backdropFilter: 'blur(5px)'
                    }}
                    onFocus={(e) => e.target.style.borderColor = '#2196f3'}
                    onBlur={(e) => e.target.style.borderColor = '#e5e7eb'}
                  >
                    <option value="">Select gender...</option>
                    <option value="Male">Male</option>
                    <option value="Female">Female</option>
                    <option value="Other">Other</option>
                  </select>
                </div>

                {/* Symptoms Input */}
                <div className="ai-form-group">
                  <label className="ai-label" style={{
                    display: 'flex',
                    alignItems: 'center',
                    fontSize: '16px',
                    fontWeight: '600',
                    color: '#333',
                    marginBottom: '10px'
                  }}>
                    <FileText className="w-4 h-4 inline mr-2" />
                    Describe Symptoms
                  </label>
                  <textarea
                    value={symptoms}
                    onChange={(e) => setSymptoms(e.target.value)}
                    placeholder="Enter patient symptoms (e.g., fever, cough, headache, fatigue...)"
                    rows={6}
                    style={{
                      width: '100%',
                      padding: '15px 20px',
                      borderRadius: '12px',
                      border: '2px solid #e5e7eb',
                      fontSize: '16px',
                      transition: 'all 0.3s ease',
                      background: 'rgba(255, 255, 255, 0.8)',
                      backdropFilter: 'blur(5px)',
                      resize: 'vertical',
                      minHeight: '120px'
                    }}
                    onFocus={(e) => e.target.style.borderColor = '#2196f3'}
                    onBlur={(e) => e.target.style.borderColor = '#e5e7eb'}
                  />
                </div>

                {/* Action Buttons */}
                <div className="ai-button-group" style={{ display: 'flex', gap: '15px', marginTop: '30px' }}>
                  <button
                    onClick={handleDiagnosis}
                    disabled={loading || !patientAge || !patientGender || !symptoms.trim()}
                    style={{
                      flex: 1,
                      padding: '16px 24px',
                      background: loading || !patientAge || !patientGender || !symptoms.trim() 
                        ? 'linear-gradient(135deg, #ccc, #999)' 
                        : 'linear-gradient(135deg, #4dd0e1, #2196f3)',
                      color: 'white',
                      border: 'none',
                      borderRadius: '12px',
                      fontSize: '16px',
                      fontWeight: '600',
                      cursor: loading || !patientAge || !patientGender || !symptoms.trim() ? 'not-allowed' : 'pointer',
                      transition: 'all 0.3s ease',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: '10px',
                      boxShadow: '0 8px 25px rgba(77, 208, 225, 0.3)'
                    }}
                    onMouseOver={(e) => {
                      if (!loading && patientAge && patientGender && symptoms.trim()) {
                        e.target.style.transform = 'translateY(-2px)';
                        e.target.style.boxShadow = '0 12px 35px rgba(77, 208, 225, 0.4)';
                      }
                    }}
                    onMouseOut={(e) => {
                      e.target.style.transform = 'translateY(0)';
                      e.target.style.boxShadow = '0 8px 25px rgba(77, 208, 225, 0.3)';
                    }}
                  >
                    {loading ? 'Processing...' : (
                      <>
                        <Brain className="w-5 h-5" />
                        Run AI Diagnosis
                      </>
                    )}
                  </button>
                  <button
                    onClick={handleClear}
                    disabled={loading}
                    style={{
                      padding: '16px 24px',
                      background: 'rgba(107, 114, 128, 0.1)',
                      color: '#6b7280',
                      border: '2px solid #e5e7eb',
                      borderRadius: '12px',
                      fontSize: '16px',
                      fontWeight: '600',
                      cursor: loading ? 'not-allowed' : 'pointer',
                      transition: 'all 0.3s ease',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: '10px'
                    }}
                    onMouseOver={(e) => {
                      if (!loading) {
                        e.target.style.background = 'rgba(107, 114, 128, 0.2)';
                        e.target.style.borderColor = '#9ca3af';
                      }
                    }}
                    onMouseOut={(e) => {
                      e.target.style.background = 'rgba(107, 114, 128, 0.1)';
                      e.target.style.borderColor = '#e5e7eb';
                    }}
                  >
                    <RefreshCw className="w-5 h-5" />
                    Clear
                  </button>
                </div>
              </div>
            </div>

            {/* Output Section */}
            <div className="ai-card" style={{
              background: 'rgba(255, 255, 255, 0.95)',
              backdropFilter: 'blur(10px)',
              borderRadius: '20px',
              padding: '40px',
              border: '1px solid rgba(255, 255, 255, 0.2)',
              boxShadow: '0 20px 60px rgba(0, 0, 0, 0.1)',
              position: 'relative',
              overflow: 'hidden'
            }}>
              <div style={{
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                background: `
                  radial-gradient(circle at 90% 20%, rgba(33, 150, 243, 0.05) 0%, transparent 50%),
                  radial-gradient(circle at 10% 80%, rgba(0, 188, 212, 0.05) 0%, transparent 50%)
                `,
                pointerEvents: 'none'
              }}></div>
              
              <div className="ai-card-header" style={{
                display: 'flex',
                alignItems: 'center',
                marginBottom: '30px',
                fontSize: '20px',
                fontWeight: '700',
                color: '#333',
                position: 'relative',
                zIndex: 1
              }}>
                <div style={{
                  width: '50px',
                  height: '50px',
                  background: 'linear-gradient(135deg, #10b981, #059669)',
                  borderRadius: '15px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  marginRight: '15px',
                  boxShadow: '0 8px 25px rgba(16, 185, 129, 0.3)'
                }}>
                  <FileText className="w-6 h-6 text-white" />
                </div>
                AI Diagnosis & Prescription
              </div>

              {loading && (
                <div className="ai-loading-container">
                  <AIProgressBar 
                    isLoading={loading} 
                    progress={progress} 
                    status={progressStatus} 
                  />
                </div>
              )}

              {error && (
                <div className="ai-output-card red">
                  <div className="flex items-center">
                    <AlertCircle className="w-5 h-5 mr-2" />
                    <p className="ai-output-content">{error}</p>
                  </div>
                </div>
              )}

              {diagnosis && !loading && (
                <div className="space-y-6">
                  {/* Patient Info */}
                  <div className="ai-output-card gray">
                    <h3 className="ai-output-title">Patient Information</h3>
                    <p className="ai-output-content">
                      Age: {patientAge} years, Gender: {patientGender}
                    </p>
                    <p className="text-sm text-gray-600">
                      Symptoms: {symptoms}
                    </p>
                  </div>

                  {/* Diagnosis */}
                  <div className="ai-output-card blue">
                    <h3 className="ai-output-title">AI Diagnosis</h3>
                    <p className="ai-output-content">{diagnosis.diagnosis}</p>
                    <div className="mt-2 flex items-center justify-between">
                      <span className="text-sm">
                        Confidence: {Math.round((diagnosis.confidence || 0) * 100)}%
                      </span>
                      {diagnosis.severity && (
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          diagnosis.severity === 'Critical' ? 'bg-red-100 text-red-800' :
                          diagnosis.severity === 'Moderate' ? 'bg-orange-100 text-orange-800' :
                          'bg-green-100 text-green-800'
                        }`}>
                          {diagnosis.severity}
                        </span>
                      )}
                    </div>
                    
                    {diagnosis.urgency && (
                      <div className="mt-2">
                        <span className="text-sm text-gray-600">
                          Urgency: <span className="capitalize">{diagnosis.urgency}</span>
                        </span>
                      </div>
                    )}
                  </div>

                  {/* Prescription */}
                  <div className="ai-output-card green">
                    <h3 className="ai-output-title">Recommended Prescription</h3>
                    {typeof diagnosis.prescription === 'object' ? (
                      <div className="space-y-2">
                        <p className="ai-output-content">
                          <strong>Medication:</strong> {diagnosis.prescription.medication}
                        </p>
                        <p className="text-sm">
                          <strong>Dosage:</strong> {diagnosis.prescription.dosage}
                        </p>
                        <p className="text-sm">
                          <strong>Instructions:</strong> {diagnosis.prescription.instructions}
                        </p>
                      </div>
                    ) : (
                      <p className="ai-output-content">{diagnosis.prescription}</p>
                    )}
                  </div>

                  {/* Differential Diagnoses */}
                  {diagnosis.differential_diagnoses && diagnosis.differential_diagnoses.length > 0 && (
                    <div className="ai-output-card purple">
                      <h3 className="ai-output-title">Differential Diagnoses</h3>
                      <ul className="ai-output-list">
                        {diagnosis.differential_diagnoses.map((diff, index) => (
                          <li key={index}>
                            {typeof diff === 'string' ? diff : (
                              <div>
                                <strong>{diff.condition || diff.diagnosis || 'Unknown Condition'}</strong>
                                {diff.confidence && (
                                  <span className="confidence-score">
                                    {' '}({Math.round((diff.confidence || 0) * 100)}% confidence)
                                  </span>
                                )}
                                {diff.description && (
                                  <div className="diagnosis-description">{diff.description}</div>
                                )}
                              </div>
                            )}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Red Flags */}
                  {diagnosis.red_flags && diagnosis.red_flags.length > 0 && (
                    <div className="ai-output-card red">
                      <h3 className="ai-output-title">⚠️ Red Flags</h3>
                      <ul className="ai-output-list">
                        {diagnosis.red_flags.map((flag, index) => (
                          <li key={index}>
                            {typeof flag === 'string' ? flag : (
                              typeof flag === 'object' && flag !== null ? 
                                JSON.stringify(flag) : String(flag)
                            )}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Recommendations */}
                  {diagnosis.recommendations && diagnosis.recommendations.length > 0 && (
                    <div className="ai-output-card yellow">
                      <h3 className="ai-output-title">Care Recommendations</h3>
                      <ul className="ai-output-list">
                        {diagnosis.recommendations.map((rec, index) => (
                          <li key={index}>
                            {typeof rec === 'string' ? rec : (
                              typeof rec === 'object' && rec !== null ? 
                                JSON.stringify(rec) : String(rec)
                            )}
                          </li>
                        ))}
                      </ul>
                      {diagnosis.follow_up_days && (
                        <p className="text-sm text-gray-600 mt-2">
                          Follow-up recommended in {diagnosis.follow_up_days} days
                        </p>
                      )}
                    </div>
                  )}

                  {/* Patient Education */}
                  {diagnosis.patient_education && (
                    <div className="ai-output-card blue">
                      <h3 className="ai-output-title">Patient Education</h3>
                      <p className="ai-output-content">{diagnosis.patient_education}</p>
                    </div>
                  )}

                  {/* Clinical Notes */}
                  {diagnosis.notes && (
                    <div className="ai-output-card gray">
                      <h3 className="ai-output-title">Clinical Notes</h3>
                      <p className="ai-output-content">{diagnosis.notes}</p>
                    </div>
                  )}

                  {/* AI Model Information */}
                  <div className="ai-output-card purple">
                    <h3 className="ai-output-title">AI Analysis Details</h3>
                    {diagnosis.metadata ? (
                      <div className="space-y-1 text-sm">
                        <p><strong>Model Version:</strong> {diagnosis.metadata.model_version}</p>
                        <p><strong>Processing Time:</strong> {diagnosis.metadata.processing_time}ms</p>
                        <p><strong>Timestamp:</strong> {new Date(diagnosis.metadata.timestamp).toLocaleString()}</p>
                        {diagnosis.metadata.is_mock && (
                          <p className="text-orange-600"><strong>Note:</strong> Mock data (AI service unavailable)</p>
                        )}
                      </div>
                    ) : (
                      <p className="text-sm">
                        <strong>AI Model:</strong> {diagnosis.ai_model_version || 'MediChain-AI'}
                      </p>
                    )}
                  </div>

                  {/* Feedback Section */}
                  {!feedbackSubmitted && (
                    <div className="ai-output-card gray border-2 border-dashed">
                      <h3 className="ai-output-title">Provide Feedback</h3>
                      <p className="text-sm text-gray-600 mb-4">
                        Help improve our AI model by providing feedback on this diagnosis.
                      </p>
                      <div className="flex space-x-3">
                        <button
                          onClick={() => handleFeedback(true)}
                          className="flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                        >
                          <ThumbsUp className="w-4 h-4 mr-2" />
                          Accurate
                        </button>
                        <button
                          onClick={() => handleFeedback(false)}
                          className="flex items-center px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                        >
                          <ThumbsDown className="w-4 h-4 mr-2" />
                          Incorrect
                        </button>
                      </div>
                    </div>
                  )}

                  {feedbackSubmitted && (
                    <div className="ai-output-card green">
                      <h3 className="ai-output-title">✓ Feedback Submitted</h3>
                      <p className="text-sm">Thank you! Your feedback helps improve our AI model.</p>
                    </div>
                  )}
                </div>
              )}

              {!diagnosis && !loading && !error && (
                <div className="ai-empty-state">
                  <Brain className="ai-empty-icon" />
                  <p className="ai-empty-title">Enter patient symptoms to get AI diagnosis</p>
                  <p className="ai-empty-subtitle">
                    {aiStatus === 'connected' 
                      ? 'AI diagnosis service is ready' 
                      : 'Make sure the AI diagnosis server is running on port 5001'
                    }
                  </p>
                  {aiStatus === 'disconnected' && (
                    <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                      <div className="flex items-center">
                        <Info className="w-4 h-4 text-yellow-600 mr-2" />
                        <p className="text-sm text-yellow-800">
                          To start the AI service, run: <code className="bg-yellow-100 px-1 rounded">python ai_diagnosis.py</code>
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* System Information */}
          <div style={{
            background: 'rgba(255, 255, 255, 0.95)',
            backdropFilter: 'blur(10px)',
            borderRadius: '20px',
            padding: '50px 40px',
            border: '1px solid rgba(255, 255, 255, 0.2)',
            boxShadow: '0 20px 60px rgba(0, 0, 0, 0.1)',
            position: 'relative',
            overflow: 'hidden'
          }}>
            <div style={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              background: `
                radial-gradient(circle at 30% 40%, rgba(33, 150, 243, 0.05) 0%, transparent 50%),
                radial-gradient(circle at 70% 60%, rgba(0, 188, 212, 0.05) 0%, transparent 50%)
              `,
              pointerEvents: 'none'
            }}></div>
            
            <div style={{ position: 'relative', zIndex: 1 }}>
              <div style={{
                textAlign: 'center',
                marginBottom: '40px'
              }}>
                <div style={{
                  display: 'inline-block',
                  background: 'rgba(33, 150, 243, 0.1)',
                  color: '#2196f3',
                  padding: '8px 20px',
                  borderRadius: '25px',
                  fontSize: '14px',
                  fontWeight: '600',
                  marginBottom: '20px',
                  border: '1px solid rgba(33, 150, 243, 0.2)'
                }}>
                  ⚡ Advanced AI System Features
                </div>
                
                <h3 style={{
                  fontSize: '2.5rem',
                  fontWeight: '800',
                  color: '#333',
                  marginBottom: '16px',
                  lineHeight: '1.1'
                }}>
                  Enhanced AI <span style={{
                    background: 'linear-gradient(135deg, #2196f3, #00bcd4)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    backgroundClip: 'text'
                  }}>Capabilities</span>
                </h3>
                
                <p style={{
                  fontSize: '1.1rem',
                  color: '#666',
                  maxWidth: '600px',
                  margin: '0 auto',
                  lineHeight: '1.6'
                }}>
                  Experience cutting-edge medical AI technology with continuous learning and blockchain integration
                </p>
              </div>
              
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
                gap: '30px',
                marginBottom: '40px'
              }}>
                <div style={{
                  background: 'rgba(255, 255, 255, 0.8)',
                  borderRadius: '16px',
                  padding: '30px',
                  border: '1px solid rgba(255, 255, 255, 0.3)',
                  boxShadow: '0 8px 25px rgba(0, 0, 0, 0.05)',
                  transition: 'all 0.3s ease'
                }}
                onMouseOver={(e) => {
                  e.currentTarget.style.transform = 'translateY(-5px)';
                  e.currentTarget.style.boxShadow = '0 15px 35px rgba(0, 0, 0, 0.1)';
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = '0 8px 25px rgba(0, 0, 0, 0.05)';
                }}>
                  <div style={{
                    width: '60px',
                    height: '60px',
                    background: 'linear-gradient(135deg, #3b82f6, #1d4ed8)',
                    borderRadius: '16px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    margin: '0 auto 20px auto',
                    boxShadow: '0 8px 25px rgba(59, 130, 246, 0.3)'
                  }}>
                    <Brain className="w-7 h-7 text-white" />
                  </div>
                  <h4 style={{
                    fontSize: '18px',
                    fontWeight: '700',
                    color: '#333',
                    marginBottom: '12px'
                  }}>AI Model</h4>
                  <p style={{
                    fontSize: '14px',
                    color: '#666',
                    lineHeight: '1.5'
                  }}>Random Forest with continuous learning</p>
                </div>
                
                <div style={{
                  background: 'rgba(255, 255, 255, 0.8)',
                  borderRadius: '16px',
                  padding: '30px',
                  border: '1px solid rgba(255, 255, 255, 0.3)',
                  boxShadow: '0 8px 25px rgba(0, 0, 0, 0.05)',
                  transition: 'all 0.3s ease'
                }}
                onMouseOver={(e) => {
                  e.currentTarget.style.transform = 'translateY(-5px)';
                  e.currentTarget.style.boxShadow = '0 15px 35px rgba(0, 0, 0, 0.1)';
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = '0 8px 25px rgba(0, 0, 0, 0.05)';
                }}>
                  <div style={{
                    width: '60px',
                    height: '60px',
                    background: 'linear-gradient(135deg, #8b5cf6, #7c3aed)',
                    borderRadius: '16px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    margin: '0 auto 20px auto',
                    boxShadow: '0 8px 25px rgba(139, 92, 246, 0.3)'
                  }}>
                    <Activity className="w-7 h-7 text-white" />
                  </div>
                  <h4 style={{
                    fontSize: '18px',
                    fontWeight: '700',
                    color: '#333',
                    marginBottom: '12px'
                  }}>Features</h4>
                  <p style={{
                    fontSize: '14px',
                    color: '#666',
                    lineHeight: '1.5'
                  }}>Treatment recommendations & personalized care</p>
                </div>
                
                <div style={{
                  background: 'rgba(255, 255, 255, 0.8)',
                  borderRadius: '16px',
                  padding: '30px',
                  border: '1px solid rgba(255, 255, 255, 0.3)',
                  boxShadow: '0 8px 25px rgba(0, 0, 0, 0.05)',
                  transition: 'all 0.3s ease'
                }}
                onMouseOver={(e) => {
                  e.currentTarget.style.transform = 'translateY(-5px)';
                  e.currentTarget.style.boxShadow = '0 15px 35px rgba(0, 0, 0, 0.1)';
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = '0 8px 25px rgba(0, 0, 0, 0.05)';
                }}>
                  <div style={{
                    width: '60px',
                    height: '60px',
                    background: 'linear-gradient(135deg, #10b981, #059669)',
                    borderRadius: '16px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    margin: '0 auto 20px auto',
                    boxShadow: '0 8px 25px rgba(16, 185, 129, 0.3)'
                  }}>
                    <FileText className="w-7 h-7 text-white" />
                  </div>
                  <h4 style={{
                    fontSize: '18px',
                    fontWeight: '700',
                    color: '#333',
                    marginBottom: '12px'
                  }}>Feedback</h4>
                  <p style={{
                    fontSize: '14px',
                    color: '#666',
                    lineHeight: '1.5'
                  }}>Continuous learning from doctor feedback</p>
                </div>
                
                <div style={{
                  background: 'rgba(255, 255, 255, 0.8)',
                  borderRadius: '16px',
                  padding: '30px',
                  border: '1px solid rgba(255, 255, 255, 0.3)',
                  boxShadow: '0 8px 25px rgba(0, 0, 0, 0.05)',
                  transition: 'all 0.3s ease'
                }}
                onMouseOver={(e) => {
                  e.currentTarget.style.transform = 'translateY(-5px)';
                  e.currentTarget.style.boxShadow = '0 15px 35px rgba(0, 0, 0, 0.1)';
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = '0 8px 25px rgba(0, 0, 0, 0.05)';
                }}>
                  <div style={{
                    width: '60px',
                    height: '60px',
                    background: 'linear-gradient(135deg, #ef4444, #dc2626)',
                    borderRadius: '16px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    margin: '0 auto 20px auto',
                    boxShadow: '0 8px 25px rgba(239, 68, 68, 0.3)'
                  }}>
                    <AlertCircle className="w-7 h-7 text-white" />
                  </div>
                  <h4 style={{
                    fontSize: '18px',
                    fontWeight: '700',
                    color: '#333',
                    marginBottom: '12px'
                  }}>Safety</h4>
                  <p style={{
                    fontSize: '14px',
                    color: '#666',
                    lineHeight: '1.5'
                  }}>Medical disclaimers & red flag detection</p>
                </div>
                
                <div style={{
                  background: 'rgba(255, 255, 255, 0.8)',
                  borderRadius: '16px',
                  padding: '30px',
                  border: '1px solid rgba(255, 255, 255, 0.3)',
                  boxShadow: '0 8px 25px rgba(0, 0, 0, 0.05)',
                  transition: 'all 0.3s ease'
                }}
                onMouseOver={(e) => {
                  e.currentTarget.style.transform = 'translateY(-5px)';
                  e.currentTarget.style.boxShadow = '0 15px 35px rgba(0, 0, 0, 0.1)';
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = '0 8px 25px rgba(0, 0, 0, 0.05)';
                }}>
                  <div style={{
                    width: '60px',
                    height: '60px',
                    background: 'linear-gradient(135deg, #f97316, #ea580c)',
                    borderRadius: '16px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    margin: '0 auto 20px auto',
                    boxShadow: '0 8px 25px rgba(249, 115, 22, 0.3)'
                  }}>
                    <User className="w-7 h-7 text-white" />
                  </div>
                  <h4 style={{
                    fontSize: '18px',
                    fontWeight: '700',
                    color: '#333',
                    marginBottom: '12px'
                  }}>Integration</h4>
                  <p style={{
                    fontSize: '14px',
                    color: '#666',
                    lineHeight: '1.5'
                  }}>Patient data & blockchain records</p>
                </div>
                
                <div style={{
                  background: 'rgba(255, 255, 255, 0.8)',
                  borderRadius: '16px',
                  padding: '30px',
                  border: '1px solid rgba(255, 255, 255, 0.3)',
                  boxShadow: '0 8px 25px rgba(0, 0, 0, 0.05)',
                  transition: 'all 0.3s ease'
                }}
                onMouseOver={(e) => {
                  e.currentTarget.style.transform = 'translateY(-5px)';
                  e.currentTarget.style.boxShadow = '0 15px 35px rgba(0, 0, 0, 0.1)';
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = '0 8px 25px rgba(0, 0, 0, 0.05)';
                }}>
                  <div style={{
                    width: '60px',
                    height: '60px',
                    background: 'linear-gradient(135deg, #06b6d4, #0891b2)',
                    borderRadius: '16px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    margin: '0 auto 20px auto',
                    boxShadow: '0 8px 25px rgba(6, 182, 212, 0.3)'
                  }}>
                    <RefreshCw className="w-7 h-7 text-white" />
                  </div>
                  <h4 style={{
                    fontSize: '18px',
                    fontWeight: '700',
                    color: '#333',
                    marginBottom: '12px'
                  }}>Adaptability</h4>
                  <p style={{
                    fontSize: '14px',
                    color: '#666',
                    lineHeight: '1.5'
                  }}>Handles unknown symptoms intelligently</p>
                </div>
              </div>
              
              {/* AI Service Status */}
              <div style={{
                background: 'rgba(249, 250, 251, 0.8)',
                borderRadius: '16px',
                padding: '30px',
                border: '1px solid rgba(229, 231, 235, 0.5)'
              }}>
                <h4 style={{
                  fontSize: '18px',
                  fontWeight: '700',
                  color: '#333',
                  marginBottom: '20px'
                }}>Service Status</h4>
                
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  marginBottom: '20px'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center' }}>
                    <div className={`w-3 h-3 rounded-full mr-3 ${
                      aiStatus === 'connected' ? 'bg-green-500' :
                      aiStatus === 'disconnected' ? 'bg-red-500' :
                      'bg-yellow-500'
                    }`}></div>
                    <span style={{ fontSize: '14px', color: '#666' }}>
                      AI Diagnosis Service: {aiStatus === 'connected' ? 'Connected' : 
                                           aiStatus === 'disconnected' ? 'Offline' : 'Checking...'}
                    </span>
                  </div>
                  <button
                    onClick={checkAiStatus}
                    style={{
                      fontSize: '14px',
                      color: '#2196f3',
                      background: 'none',
                      border: 'none',
                      cursor: 'pointer',
                      textDecoration: 'underline'
                    }}
                    onMouseOver={(e) => e.target.style.color = '#1976d2'}
                    onMouseOut={(e) => e.target.style.color = '#2196f3'}
                  >
                    Refresh Status
                  </button>
                </div>
                
                {modelInfo && (
                  <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(2, 1fr)',
                    gap: '20px',
                    fontSize: '14px',
                    color: '#666'
                  }}>
                    <div>Model Version: {modelInfo.version}</div>
                    <div>Accuracy: {modelInfo.accuracy}%</div>
                    <div>Training Samples: {modelInfo.training_samples || 'N/A'}</div>
                    <div>Last Updated: {modelInfo.last_updated || 'Unknown'}</div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default AIAssistant;
