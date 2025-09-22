import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Brain, User, Activity, FileText, RefreshCw, Plus, AlertCircle, ThumbsUp, ThumbsDown, Info, LogIn, UserPlus, MessageCircle } from 'lucide-react';
import LoadingSpinner from '../components/LoadingSpinner';
import AIProgressBar from '../components/AIProgressBar';
import ConversationalAI from '../components/ConversationalAI';
import { showToast } from '../components/CustomToast';
import { aiService } from '../services/aiService';
import { useAuth } from '../context/AuthContext';
import Header from './Header';
import '../assets/styles/LandingPage.css';

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
  const [mode, setMode] = useState('quick'); // 'quick' or 'conversational'
  const { user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    checkAiStatus();
    loadModelInfo();
  }, []);

  const checkAiStatus = async () => {
    try {
      setAiStatus('checking');
      const response = await aiService.checkStatus();
      setAiStatus(response.status === 'ready' ? 'ready' : 'error');
    } catch (error) {
      console.error('AI status check failed:', error);
      setAiStatus('error');
    }
  };

  const loadModelInfo = async () => {
    try {
      const info = await aiService.getModelInfo();
      setModelInfo(info);
    } catch (error) {
      console.error('Failed to load model info:', error);
    }
  };

  const handleAnalyze = async () => {
    if (!symptoms.trim()) {
      setError('Please describe your symptoms');
      return;
    }

    setLoading(true);
    setError(null);
    setDiagnosis(null);
    setProgress(0);
    setProgressStatus('Initializing AI analysis...');

    try {
      // Progress simulation
      const progressInterval = setInterval(() => {
        setProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return prev;
          }
          return prev + 10;
        });
      }, 200);

      setProgressStatus('Analyzing symptoms...');
      
      const result = await aiService.diagnose({
        symptoms: symptoms.trim(),
        age: patientAge || null,
        gender: patientGender || null,
        user_id: user?.id || null
      });

      clearInterval(progressInterval);
      setProgress(100);
      setProgressStatus('Analysis complete!');
      
      setTimeout(() => {
        setDiagnosis(result);
        setLoading(false);
        setProgress(0);
        setProgressStatus('');
      }, 500);

    } catch (error) {
      setLoading(false);
      setProgress(0);
      setProgressStatus('');
      setError(error.message || 'Failed to analyze symptoms. Please try again.');
      console.error('Diagnosis error:', error);
    }
  };

  const handleFeedback = async (isPositive) => {
    if (!diagnosis || feedbackSubmitted) return;

    try {
      await aiService.submitFeedback({
        diagnosis_id: diagnosis.id,
        is_positive: isPositive,
        user_id: user?.id || null
      });
      setFeedbackSubmitted(true);
      showToast.success('Thank you for your feedback!');
    } catch (error) {
      console.error('Feedback error:', error);
      showToast.error('Failed to submit feedback');
    }
  };

  const clearForm = () => {
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
    <div className="medichain">
      {/* Floating Medical Crosses */}
      <div className="floating-cross">+</div>
      <div className="floating-cross">+</div>
      <div className="floating-cross">+</div>
      <div className="floating-cross">+</div>
      <div className="floating-cross">+</div>

      {/* AI Assistant Section */}
      <section className="hero">
        {/* Header */}
        {user ? (
          <Header />
        ) : (
          <header className="header">
            <div className="nav-container">
              <div className="logo-container">
                <div className="logo-icon">+</div>
                <div className="logo-text">MEDICHAIN</div>
              </div>
              <nav className="nav-links">
                <span className="nav-link" style={{ color: '#2196f3', fontWeight: '600' }}>
                  AI Health Assistant
                </span>
              </nav>
              <div className="cta-buttons">
                <button
                  className="btn btn-secondary"
                  onClick={() => navigate('/login')}
                >
                  <LogIn size={16} style={{ marginRight: '8px' }} />
                  Log In
                </button>
                <button
                  className="btn btn-primary"
                  onClick={() => navigate('/signup')}
                >
                  <UserPlus size={16} style={{ marginRight: '8px' }} />
                  Sign Up
                </button>
              </div>
            </div>
          </header>
        )}

        {/* AI Assistant Content */}
        <div className="hero-content">
          <div className="hero-text">
            <div className="hero-badge">🤖 AI-Powered Medical Diagnosis</div>
            <h1 className="hero-title">
              AI Health <span className="gradient-text">Assistant</span>
            </h1>
            <p className="hero-subtitle">
              Get instant AI-powered health insights and symptom analysis. 
              Our advanced machine learning model provides preliminary medical assessments 
              to help you understand your symptoms better.
            </p>

            {/* AI Status Indicator */}
            <div style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '12px',
              background: aiStatus === 'ready' ? 'rgba(34, 197, 94, 0.1)' : 'rgba(251, 191, 36, 0.1)',
              color: aiStatus === 'ready' ? '#16a34a' : '#d97706',
              padding: '12px 20px',
              borderRadius: '50px',
              border: `1px solid ${aiStatus === 'ready' ? 'rgba(34, 197, 94, 0.3)' : 'rgba(251, 191, 36, 0.3)'}`,
              marginBottom: '40px',
              fontSize: '14px',
              fontWeight: '600'
            }}>
              <div style={{
                width: '8px',
                height: '8px',
                borderRadius: '50%',
                background: aiStatus === 'ready' ? '#16a34a' : '#d97706',
                animation: 'pulse 2s infinite'
              }}></div>
              AI Model Status: {aiStatus === 'ready' ? 'Ready' : 'Checking...'}
            </div>
          </div>

          {/* AI Form Container */}
          <div style={{
            background: 'rgba(255, 255, 255, 0.95)',
            backdropFilter: 'blur(20px)',
            borderRadius: '25px',
            padding: '40px',
            border: '1px solid rgba(255, 255, 255, 0.2)',
            boxShadow: '0 20px 60px rgba(0, 0, 0, 0.1)',
            maxWidth: '800px',
            width: '100%',
            margin: '0 auto',
            position: 'relative',
            overflow: 'hidden'
          }}>
            {/* Form background pattern */}
            <div style={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              background: `
                radial-gradient(circle at 20% 80%, rgba(33, 150, 243, 0.02) 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, rgba(0, 188, 212, 0.02) 0%, transparent 50%)
              `,
              pointerEvents: 'none'
            }}></div>

            <div style={{ position: 'relative', zIndex: 1 }}>
              {/* Form Title */}
              <div style={{ textAlign: 'center', marginBottom: '30px' }}>
                <h2 style={{
                  fontSize: '2rem',
                  fontWeight: '700',
                  color: '#333',
                  marginBottom: '10px'
                }}>
                  AI Health Diagnosis
                </h2>
                <p style={{
                  color: '#666',
                  fontSize: '1rem',
                  lineHeight: '1.5'
                }}>
                  Choose your preferred diagnosis method
                </p>
              </div>

              {/* Mode Selection */}
              <div style={{ marginBottom: '30px' }}>
                <div style={{
                  display: 'flex',
                  justifyContent: 'center',
                  gap: '15px',
                  marginBottom: '20px'
                }}>
                  <button
                    onClick={() => setMode('quick')}
                    style={{
                      padding: '15px 25px',
                      borderRadius: '10px',
                      border: mode === 'quick' ? '2px solid #3B82F6' : '2px solid #E5E7EB',
                      backgroundColor: mode === 'quick' ? '#EBF4FF' : 'white',
                      color: mode === 'quick' ? '#1D4ED8' : '#6B7280',
                      fontWeight: '600',
                      cursor: 'pointer',
                      transition: 'all 0.2s',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px'
                    }}
                  >
                    <Brain className="w-5 h-5" />
                    Quick Diagnosis
                  </button>
                  <button
                    onClick={() => setMode('conversational')}
                    style={{
                      padding: '15px 25px',
                      borderRadius: '10px',
                      border: mode === 'conversational' ? '2px solid #3B82F6' : '2px solid #E5E7EB',
                      backgroundColor: mode === 'conversational' ? '#EBF4FF' : 'white',
                      color: mode === 'conversational' ? '#1D4ED8' : '#6B7280',
                      fontWeight: '600',
                      cursor: 'pointer',
                      transition: 'all 0.2s',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px'
                    }}
                  >
                    <MessageCircle className="w-5 h-5" />
                    Conversational Diagnosis
                  </button>
                </div>
                <p style={{
                  textAlign: 'center',
                  color: '#6B7280',
                  fontSize: '0.875rem'
                }}>
                  {mode === 'quick' 
                    ? 'Describe all your symptoms at once for immediate diagnosis'
                    : 'Interactive conversation with follow-up questions for precise diagnosis'
                  }
                </p>
              </div>

              {/* Show appropriate interface based on mode */}
              {mode === 'conversational' ? (
                <ConversationalAI
                  onDiagnosisComplete={(diagnosisData) => {
                    setDiagnosis(diagnosisData);
                    setProgress(100);
                    setProgressStatus('Diagnosis complete!');
                  }}
                />
              ) : (
                <>
                  <div style={{ textAlign: 'center', marginBottom: '20px' }}>
                    <h3 style={{
                      fontSize: '1.5rem',
                      fontWeight: '600',
                      color: '#333',
                      marginBottom: '5px'
                    }}>
                      Describe Your Symptoms
                    </h3>
                    <p style={{
                      color: '#666',
                      fontSize: '0.9rem'
                    }}>
                      Provide detailed information about your symptoms for accurate AI analysis
                    </p>
                  </div>

              {/* Progress Bar */}
              {loading && (
                <div style={{ marginBottom: '20px' }}>
                  <AIProgressBar progress={progress} status={progressStatus} />
                </div>
              )}

              {/* Symptoms Input */}
              <div style={{ marginBottom: '25px' }}>
                <label style={{
                  display: 'block',
                  marginBottom: '8px',
                  fontWeight: '600',
                  color: '#333',
                  fontSize: '1rem'
                }}>
                  Symptoms Description *
                </label>
                <textarea
                  value={symptoms}
                  onChange={(e) => setSymptoms(e.target.value)}
                  placeholder="Describe your symptoms in detail (e.g., headache, fever, cough, stomach pain, severity...)"
                  style={{
                    width: '100%',
                    minHeight: '120px',
                    padding: '16px 20px',
                    border: '2px solid rgba(79, 172, 254, 0.2)',
                    borderRadius: '15px',
                    fontSize: '1rem',
                    background: 'rgba(255, 255, 255, 0.9)',
                    transition: 'all 0.3s ease',
                    resize: 'vertical',
                    fontFamily: 'inherit',
                    lineHeight: '1.5'
                  }}
                  onFocus={(e) => {
                    e.target.style.borderColor = '#4facfe';
                    e.target.style.boxShadow = '0 0 0 3px rgba(79, 172, 254, 0.1)';
                    e.target.style.background = 'white';
                  }}
                  onBlur={(e) => {
                    e.target.style.borderColor = 'rgba(79, 172, 254, 0.2)';
                    e.target.style.boxShadow = 'none';
                    e.target.style.background = 'rgba(255, 255, 255, 0.9)';
                  }}
                />
              </div>

              {/* Patient Information Row */}
              <div style={{
                display: 'grid',
                gridTemplateColumns: '1fr 1fr',
                gap: '20px',
                marginBottom: '30px'
              }}>
                {/* Age Input */}
                <div>
                  <label style={{
                    display: 'block',
                    marginBottom: '8px',
                    fontWeight: '600',
                    color: '#333',
                    fontSize: '1rem'
                  }}>
                    Age
                  </label>
                  <input
                    type="number"
                    value={patientAge}
                    onChange={(e) => setPatientAge(e.target.value)}
                    placeholder="Enter age"
                    min="1"
                    max="120"
                    style={{
                      width: '100%',
                      padding: '16px 20px',
                      border: '2px solid rgba(79, 172, 254, 0.2)',
                      borderRadius: '15px',
                      fontSize: '1rem',
                      background: 'rgba(255, 255, 255, 0.9)',
                      transition: 'all 0.3s ease'
                    }}
                    onFocus={(e) => {
                      e.target.style.borderColor = '#4facfe';
                      e.target.style.boxShadow = '0 0 0 3px rgba(79, 172, 254, 0.1)';
                      e.target.style.background = 'white';
                    }}
                    onBlur={(e) => {
                      e.target.style.borderColor = 'rgba(79, 172, 254, 0.2)';
                      e.target.style.boxShadow = 'none';
                      e.target.style.background = 'rgba(255, 255, 255, 0.9)';
                    }}
                  />
                </div>

                {/* Gender Select */}
                <div>
                  <label style={{
                    display: 'block',
                    marginBottom: '8px',
                    fontWeight: '600',
                    color: '#333',
                    fontSize: '1rem'
                  }}>
                    Gender
                  </label>
                  <select
                    value={patientGender}
                    onChange={(e) => setPatientGender(e.target.value)}
                    style={{
                      width: '100%',
                      padding: '16px 20px',
                      border: '2px solid rgba(79, 172, 254, 0.2)',
                      borderRadius: '15px',
                      fontSize: '1rem',
                      background: 'rgba(255, 255, 255, 0.9)',
                      transition: 'all 0.3s ease',
                      cursor: 'pointer'
                    }}
                    onFocus={(e) => {
                      e.target.style.borderColor = '#4facfe';
                      e.target.style.boxShadow = '0 0 0 3px rgba(79, 172, 254, 0.1)';
                      e.target.style.background = 'white';
                    }}
                    onBlur={(e) => {
                      e.target.style.borderColor = 'rgba(79, 172, 254, 0.2)';
                      e.target.style.boxShadow = 'none';
                      e.target.style.background = 'rgba(255, 255, 255, 0.9)';
                    }}
                  >
                    <option value="">Select gender</option>
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                    <option value="other">Other</option>
                  </select>
                </div>
              </div>

              {/* Action Buttons */}
              <div style={{
                display: 'flex',
                gap: '15px',
                flexWrap: 'wrap',
                marginBottom: '20px'
              }}>
                <button
                  onClick={handleAnalyze}
                  disabled={!symptoms.trim() || loading || aiStatus !== 'ready'}
                  style={{
                    flex: '1',
                    minWidth: '200px',
                    padding: '16px 32px',
                    background: (!symptoms.trim() || loading || aiStatus !== 'ready') 
                      ? '#e2e8f0' 
                      : 'linear-gradient(135deg, #2196f3, #1565c0)',
                    color: (!symptoms.trim() || loading || aiStatus !== 'ready') ? '#64748b' : 'white',
                    border: 'none',
                    borderRadius: '15px',
                    fontSize: '1rem',
                    fontWeight: '700',
                    cursor: (!symptoms.trim() || loading || aiStatus !== 'ready') ? 'not-allowed' : 'pointer',
                    transition: 'all 0.3s ease',
                    textTransform: 'uppercase',
                    letterSpacing: '0.5px',
                    boxShadow: (!symptoms.trim() || loading || aiStatus !== 'ready') 
                      ? 'none' 
                      : '0 4px 15px rgba(33, 150, 243, 0.3)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '10px'
                  }}
                  onMouseOver={(e) => {
                    if (!(!symptoms.trim() || loading || aiStatus !== 'ready')) {
                      e.target.style.transform = 'translateY(-2px)';
                      e.target.style.boxShadow = '0 8px 25px rgba(33, 150, 243, 0.4)';
                    }
                  }}
                  onMouseOut={(e) => {
                    if (!(!symptoms.trim() || loading || aiStatus !== 'ready')) {
                      e.target.style.transform = 'translateY(0)';
                      e.target.style.boxShadow = '0 4px 15px rgba(33, 150, 243, 0.3)';
                    }
                  }}
                >
                  {loading ? (
                    <>
                      <LoadingSpinner size="small" />
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <Brain size={20} />
                      Analyze Symptoms
                    </>
                  )}
                </button>

                <button
                  onClick={clearForm}
                  disabled={loading}
                  style={{
                    padding: '16px 24px',
                    background: 'rgba(255, 255, 255, 0.9)',
                    color: '#2196f3',
                    border: '1px solid rgba(33, 150, 243, 0.3)',
                    borderRadius: '15px',
                    fontSize: '1rem',
                    fontWeight: '600',
                    cursor: loading ? 'not-allowed' : 'pointer',
                    transition: 'all 0.3s ease',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px'
                  }}
                  onMouseOver={(e) => {
                    if (!loading) {
                      e.target.style.background = 'white';
                      e.target.style.transform = 'translateY(-2px)';
                      e.target.style.boxShadow = '0 8px 25px rgba(255, 255, 255, 0.3)';
                    }
                  }}
                  onMouseOut={(e) => {
                    if (!loading) {
                      e.target.style.background = 'rgba(255, 255, 255, 0.9)';
                      e.target.style.transform = 'translateY(0)';
                      e.target.style.boxShadow = 'none';
                    }
                  }}
                >
                  <RefreshCw size={16} />
                  Clear
                </button>
              </div>
                </>
              )}

              {/* Error Display */}
              {error && (
                <div style={{
                  background: 'linear-gradient(135deg, #fee2e2, #fecaca)',
                  border: '1px solid #f87171',
                  borderRadius: '15px',
                  padding: '16px 20px',
                  marginBottom: '20px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  color: '#dc2626'
                }}>
                  <AlertCircle size={20} />
                  <span style={{ fontWeight: '500' }}>{error}</span>
                </div>
              )}

              {/* Account Creation Prompt for Non-Users */}
              {!user && diagnosis && (
                <div style={{
                  background: 'linear-gradient(135deg, #fff3cd, #ffeaa7)',
                  border: '1px solid #ffd93d',
                  borderRadius: '15px',
                  padding: '20px',
                  marginBottom: '20px',
                  textAlign: 'center',
                  boxShadow: '0 4px 20px rgba(255, 217, 61, 0.2)'
                }}>
                  <h3 style={{
                    color: '#856404',
                    marginBottom: '10px',
                    fontSize: '1.2rem',
                    fontWeight: '700'
                  }}>
                    💾 Save Your Results
                  </h3>
                  <p style={{
                    color: '#856404',
                    marginBottom: '15px',
                    lineHeight: '1.5'
                  }}>
                    Create an account to save your AI diagnosis results and track your health history.
                  </p>
                  <div style={{
                    display: 'flex',
                    gap: '15px',
                    justifyContent: 'center',
                    flexWrap: 'wrap'
                  }}>
                    <button
                      onClick={() => navigate('/signup')}
                      className="btn btn-primary"
                      style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '8px'
                      }}
                    >
                      <UserPlus size={16} />
                      Create Account
                    </button>
                    <button
                      onClick={() => navigate('/login')}
                      className="btn btn-secondary"
                      style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '8px'
                      }}
                    >
                      <LogIn size={16} />
                      Log In
                    </button>
                  </div>
                </div>
              )}

              {/* Diagnosis Results */}
              {diagnosis && (
                <div style={{
                  background: 'linear-gradient(135deg, #d4edda, #c3e6cb)',
                  border: '1px solid #28a745',
                  borderRadius: '20px',
                  padding: '30px',
                  marginTop: '20px',
                  boxShadow: '0 10px 40px rgba(40, 167, 69, 0.2)'
                }}>
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '15px',
                    marginBottom: '20px'
                  }}>
                    <div style={{
                      width: '60px',
                      height: '60px',
                      background: 'linear-gradient(135deg, #28a745, #20c997)',
                      borderRadius: '50%',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      boxShadow: '0 8px 25px rgba(40, 167, 69, 0.3)'
                    }}>
                      <Brain size={24} style={{ color: 'white' }} />
                    </div>
                    <div>
                      <h3 style={{
                        color: '#155724',
                        margin: 0,
                        fontSize: '1.5rem',
                        fontWeight: '700'
                      }}>
                        AI Diagnosis Results
                      </h3>
                      <p style={{
                        color: '#155724',
                        margin: '5px 0 0 0',
                        opacity: 0.8
                      }}>
                        Confidence: {diagnosis.confidence}%
                      </p>
                    </div>
                  </div>

                  <div style={{
                    background: 'rgba(255, 255, 255, 0.7)',
                    borderRadius: '15px',
                    padding: '20px',
                    marginBottom: '20px'
                  }}>
                    <h4 style={{
                      color: '#155724',
                      marginBottom: '15px',
                      fontSize: '1.2rem',
                      fontWeight: '600'
                    }}>
                      Possible Condition: {diagnosis.condition}
                    </h4>
                    
                    {diagnosis.description && (
                      <p style={{
                        color: '#155724',
                        marginBottom: '15px',
                        lineHeight: '1.6'
                      }}>
                        {diagnosis.description}
                      </p>
                    )}

                    {diagnosis.recommendations && diagnosis.recommendations.length > 0 && (
                      <div>
                        <h5 style={{
                          color: '#155724',
                          marginBottom: '10px',
                          fontSize: '1.1rem',
                          fontWeight: '600'
                        }}>
                          Recommendations:
                        </h5>
                        <ul style={{
                          color: '#155724',
                          paddingLeft: '20px',
                          lineHeight: '1.6'
                        }}>
                          {diagnosis.recommendations.map((rec, index) => (
                            <li key={index} style={{ marginBottom: '5px' }}>{rec}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>

                  {/* Disclaimer */}
                  <div style={{
                    background: 'rgba(255, 193, 7, 0.1)',
                    border: '1px solid #ffc107',
                    borderRadius: '10px',
                    padding: '15px',
                    marginBottom: '20px'
                  }}>
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '10px',
                      color: '#856404'
                    }}>
                      <Info size={20} />
                      <strong>Important Medical Disclaimer</strong>
                    </div>
                    <p style={{
                      color: '#856404',
                      margin: '10px 0 0 0',
                      fontSize: '0.9rem',
                      lineHeight: '1.5'
                    }}>
                      This AI diagnosis is for informational purposes only and should not replace professional medical advice. 
                      Please consult with a qualified healthcare provider for proper diagnosis and treatment.
                    </p>
                  </div>

                  {/* Feedback Section */}
                  {user && !feedbackSubmitted && (
                    <div style={{
                      textAlign: 'center',
                      paddingTop: '20px',
                      borderTop: '1px solid rgba(21, 87, 36, 0.2)'
                    }}>
                      <p style={{
                        color: '#155724',
                        marginBottom: '15px',
                        fontWeight: '500'
                      }}>
                        Was this diagnosis helpful?
                      </p>
                      <div style={{ display: 'flex', gap: '10px', justifyContent: 'center' }}>
                        <button
                          onClick={() => handleFeedback(true)}
                          style={{
                            padding: '10px 20px',
                            background: 'rgba(40, 167, 69, 0.1)',
                            color: '#28a745',
                            border: '1px solid #28a745',
                            borderRadius: '10px',
                            cursor: 'pointer',
                            transition: 'all 0.3s ease',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '8px',
                            fontWeight: '500'
                          }}
                          onMouseOver={(e) => {
                            e.target.style.background = '#28a745';
                            e.target.style.color = 'white';
                          }}
                          onMouseOut={(e) => {
                            e.target.style.background = 'rgba(40, 167, 69, 0.1)';
                            e.target.style.color = '#28a745';
                          }}
                        >
                          <ThumbsUp size={16} />
                          Yes, helpful
                        </button>
                        <button
                          onClick={() => handleFeedback(false)}
                          style={{
                            padding: '10px 20px',
                            background: 'rgba(220, 53, 69, 0.1)',
                            color: '#dc3545',
                            border: '1px solid #dc3545',
                            borderRadius: '10px',
                            cursor: 'pointer',
                            transition: 'all 0.3s ease',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '8px',
                            fontWeight: '500'
                          }}
                          onMouseOver={(e) => {
                            e.target.style.background = '#dc3545';
                            e.target.style.color = 'white';
                          }}
                          onMouseOut={(e) => {
                            e.target.style.background = 'rgba(220, 53, 69, 0.1)';
                            e.target.style.color = '#dc3545';
                          }}
                        >
                          <ThumbsDown size={16} />
                          Not helpful
                        </button>
                      </div>
                    </div>
                  )}

                  {feedbackSubmitted && (
                    <div style={{
                      textAlign: 'center',
                      paddingTop: '20px',
                      borderTop: '1px solid rgba(21, 87, 36, 0.2)',
                      color: '#155724',
                      fontWeight: '500'
                    }}>
                      ✅ Thank you for your feedback!
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default AIAssistant;
