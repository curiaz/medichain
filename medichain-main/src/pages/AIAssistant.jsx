import React, { useState, useEffect } from 'react';
import { aiService } from '../services/aiService';
import Header from './Header';
import { 
  Brain, 
  Activity, 
  FileText, 
  Users, 
  CheckCircle, 
  AlertTriangle, 
  Stethoscope, 
  Clock,
  Send,
  RefreshCw,
  TrendingUp,
  Shield,
  Zap
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import '../assets/styles/Dashboard.css';
import './AIAssistant.css';

const AIAssistant = () => {
  const { user } = useAuth();
  
  // State management
  const [loading, setLoading] = useState(false);
  const [showRationale, setShowRationale] = useState(false);
  const [showAuditTrail, setShowAuditTrail] = useState(false);
  const [aiStatus, setAiStatus] = useState('checking');
  const [error, setError] = useState(null);
  
  // Dynamic AI data state
  const [supportedSymptoms, setSupportedSymptoms] = useState([]);
  const [supportedDiagnoses, setSupportedDiagnoses] = useState([]);
  const [modelInfo, setModelInfo] = useState(null);
  
  // Patient input state
  const [patientInput, setPatientInput] = useState({
    symptomsHistory: '',
    age: '',
    sex: '',
    vitals: {
      bloodPressure: '',
      heartRate: '',
      temperature: '',
      respiratoryRate: ''
    },
    allergies: [],
    currentMeds: []
  });

  // Results state
  const [diagnosisResults, setDiagnosisResults] = useState(null);
  const [auditTrail, setAuditTrail] = useState([]);
  const [isReviewed, setIsReviewed] = useState(false);
  const [dailyStats, setDailyStats] = useState({
    diagnoses: 0,
    reviewed: 0,
    highRisk: 0
  });

  // Check AI service status on mount
  useEffect(() => {
    checkAIStatus();
    loadDailyStats();
    loadAIModelData();
  }, []);

  const loadAIModelData = async () => {
    try {
      // Load supported symptoms and model info
      const [symptomsResult, diagnosesResult, modelResult] = await Promise.all([
        aiService.getSupportedSymptoms(),
        aiService.getSupportedDiagnoses(), 
        aiService.getModelInfo()
      ]);

      if (symptomsResult.success) {
        setSupportedSymptoms(symptomsResult.data);
      }
      
      if (diagnosesResult.success) {
        setSupportedDiagnoses(diagnosesResult.data);
      }
      
      if (modelResult.success) {
        setModelInfo(modelResult.data);
      }
    } catch (error) {
      console.error('Failed to load AI model data:', error);
    }
  };

  const checkAIStatus = async () => {
    setAiStatus('checking');
    try {
      console.log('Checking AI status...');
      const response = await aiService.healthCheck();
      console.log('Health check response:', response);
      setAiStatus(response.success ? 'connected' : 'disconnected');
      if (!response.success) {
        setError(`AI Connection Failed: ${response.message}`);
      } else {
        setError(null);
      }
    } catch (error) {
      console.error('Health check error:', error);
      setAiStatus('disconnected');
      setError(`AI Connection Error: ${error.message}`);
    }
  };

  const debugAIConnection = async () => {
    console.log('=== AI CONNECTION DEBUG ===');
    console.log('AI Base URL:', 'http://localhost:5001');
    
    try {
      // Create dynamic test symptoms (all set to 0)
      const testSymptoms = {};
      supportedSymptoms.forEach(symptom => {
        testSymptoms[symptom] = 0;
      });
      
      // Fallback if symptoms not loaded yet
      if (supportedSymptoms.length === 0) {
        testSymptoms.fever = 1;
        testSymptoms.cough = 0;
        testSymptoms.fatigue = 0;
        testSymptoms.shortness_of_breath = 0;
        testSymptoms.headache = 0;
        testSymptoms.sore_throat = 0;
      } else {
        // Set first symptom to 1 for testing
        testSymptoms[supportedSymptoms[0]] = 1;
      }
      
      // Test direct connection
      const testResponse = await fetch('http://localhost:5001/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          symptoms: testSymptoms
        })
      });
      
      if (testResponse.ok) {
        const data = await testResponse.json();
        console.log('✅ Direct fetch successful:', data);
        alert('✅ AI Connection Test Successful!\nCheck console for details.');
      } else {
        console.log('❌ Direct fetch failed:', testResponse.status);
        alert('❌ AI Connection Test Failed!\nStatus: ' + testResponse.status);
      }
    } catch (error) {
      console.log('❌ Direct fetch error:', error);
      alert('❌ AI Connection Test Failed!\nError: ' + error.message);
    }
  };

  const loadDailyStats = () => {
    // Load daily stats from local storage or API
    const today = new Date().toDateString();
    const stored = localStorage.getItem(`ai_stats_${today}`);
    if (stored) {
      setDailyStats(JSON.parse(stored));
    }
  };

  const updateDailyStats = (type) => {
    const today = new Date().toDateString();
    const newStats = { ...dailyStats };
    newStats[type]++;
    setDailyStats(newStats);
    localStorage.setItem(`ai_stats_${today}`, JSON.stringify(newStats));
  };

  const handleInputChange = (field, value) => {
    setPatientInput(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const detectSymptomsFromText = (text) => {
    const symptomMap = {
      // Fatigue variations (including your "heise" example)
      'heise': 'fatigue',
      'tired': 'fatigue', 
      'exhausted': 'fatigue',
      'fatigue': 'fatigue',
      'weakness': 'fatigue',
      'energy': 'fatigue',
      'weary': 'fatigue',
      'drained': 'fatigue',
      'lethargic': 'fatigue',
      'sluggish': 'fatigue',
      
      // Fever variations
      'fever': 'fever',
      'hot': 'fever',
      'temperature': 'fever',
      'burning': 'fever',
      'feverish': 'fever',
      'chills': 'fever',
      'sweating': 'fever',
      'sweats': 'fever',
      'pyrexia': 'fever',
      
      // Cough variations  
      'cough': 'cough',
      'coughing': 'cough',
      'hacking': 'cough',
      'dry cough': 'cough',
      'persistent cough': 'cough',
      'productive cough': 'cough',
      
      // Headache variations
      'headache': 'headache',
      'head': 'headache',
      'migraine': 'headache',
      'head pain': 'headache',
      'skull': 'headache',
      'temple': 'headache',
      'pressure in head': 'headache',
      
      // Sore throat variations
      'throat': 'sore_throat',
      'sore throat': 'sore_throat',
      'swallow': 'sore_throat',
      'swallowing': 'sore_throat',
      'throat pain': 'sore_throat',
      'scratchy throat': 'sore_throat',
      'raw throat': 'sore_throat',
      
      // Shortness of breath variations
      'breath': 'shortness_of_breath',
      'breathing': 'shortness_of_breath',
      'shortness': 'shortness_of_breath',
      'dyspnea': 'shortness_of_breath',
      'wheezing': 'shortness_of_breath',
      'gasping': 'shortness_of_breath',
      'air': 'shortness_of_breath',
      'oxygen': 'shortness_of_breath',
      'can\'t breathe': 'shortness_of_breath',
      'difficulty breathing': 'shortness_of_breath'
    };
    
    const detectedSymptoms = {};
    const lowerText = text.toLowerCase();
    
    // Initialize all supported symptoms to 0
    supportedSymptoms.forEach(symptom => {
      detectedSymptoms[symptom] = 0;
    });
    
    // If no supported symptoms loaded, use default set
    if (supportedSymptoms.length === 0) {
      ['fever', 'cough', 'fatigue', 'shortness_of_breath', 'headache', 'sore_throat'].forEach(symptom => {
        detectedSymptoms[symptom] = 0;
      });
    }
    
    // Detect symptoms from text
    let recognizedCount = 0;
    Object.entries(symptomMap).forEach(([keyword, symptom]) => {
      if (lowerText.includes(keyword)) {
        detectedSymptoms[symptom] = 1;
        recognizedCount++;
      }
    });
    
    // Check if we have any recognizable symptoms
    const hasAnySymptom = Object.values(detectedSymptoms).some(val => val === 1);
    
    return {
      symptoms: detectedSymptoms,
      recognizedCount,
      hasRecognizedSymptoms: hasAnySymptom,
      originalText: text
    };
  };

  const handleAnalyze = async () => {
    if (!patientInput.symptomsHistory.trim()) {
      setError('Please enter symptoms and medical history');
      return;
    }

    setLoading(true);
    setError(null);
    setIsReviewed(false);

    try {
      // Convert text symptoms to dictionary format for backend
      const detection = detectSymptomsFromText(patientInput.symptomsHistory);
      
      console.log('Symptom detection:', detection);
      
      // Check if any symptoms were recognized
      if (!detection.hasRecognizedSymptoms) {
        setError(
          `❌ No recognizable medical symptoms found in: "${detection.originalText}"\n\n` +
          `🩺 Please describe your symptoms using clearer medical terms:\n` +
          `• General: fever, fatigue, weakness, nausea\n` +
          `• Respiratory: cough, shortness of breath, sore throat\n` +
          `• Neurological: headache, dizziness, confusion\n` +
          `• Pain: chest pain, abdominal pain, joint pain\n\n` +
          `⚠️ Medical Disclaimer: This AI assistant is for informational purposes only.\n` +
          `For serious health concerns, please consult a healthcare professional immediately.`
        );
        setLoading(false);
        return;
      }

      // Show what symptoms were detected
      const detectedSymptomNames = Object.keys(detection.symptoms).filter(s => detection.symptoms[s] === 1);
      console.log(`✅ Detected ${detection.recognizedCount} symptoms:`, detectedSymptomNames);
      
      const diagnosisData = {
        symptoms: detection.symptoms, // Send the detected symptoms dictionary
        patient_data: {
          age: patientInput.age,
          gender: patientInput.sex,
          allergies: patientInput.allergies,
          current_medications: patientInput.currentMeds,
          vitals: patientInput.vitals
        },
        symptoms_text: patientInput.symptomsHistory,
        timestamp: new Date().toISOString()
      };

      const response = await aiService.getDiagnosis(diagnosisData);
      
      if (response.success) {
        setDiagnosisResults({
          ...response.data,
          id: Date.now(),
          input_data: patientInput,
          detected_symptoms: detectedSymptomNames, // Add this for display
          // Backend will provide parsed symptoms in response.data.parsed_symptoms
        });

        // Add to audit trail
        const auditEntry = {
          timestamp: new Date().toISOString(),
          action: 'AI Analysis',
          input: patientInput.symptomsHistory,
          modelVersion: modelInfo?.name ? `${modelInfo.name} v${modelInfo.version}` : 'MediChain-AI v2.1',
          result: response.data.diagnosis,
          confidence: response.data.confidence,
          detectedSymptoms: detectedSymptomNames
        };
        setAuditTrail(prev => [auditEntry, ...prev]);
        
        // Update daily stats
        updateDailyStats('diagnoses');
        if (response.data.confidence < 60) {
          updateDailyStats('highRisk');
        }
      } else {
        setError(`🚫 Diagnosis Error: ${response.error || 'Analysis failed'}\n\n⚠️ Please try again or consult a healthcare professional.`);
      }
    } catch (err) {
      console.error('Analysis error:', err);
      setError(
        `🔌 Network Error: ${err.message}\n\n` +
        `• Check if AI service is running on port 5001\n` +
        `• Verify your internet connection\n` +
        `• Contact support if this issue persists\n\n` +
        `⚠️ For urgent medical needs, contact emergency services immediately.`
      );
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setPatientInput({
      symptomsHistory: '',
      age: '',
      sex: '',
      vitals: {
        bloodPressure: '',
        heartRate: '',
        temperature: '',
        respiratoryRate: ''
      },
      allergies: [],
      currentMeds: []
    });
    setDiagnosisResults(null);
    setError(null);
    setIsReviewed(false);
  };

  const markAsReviewed = () => {
    setIsReviewed(true);
    const reviewEntry = {
      timestamp: new Date().toISOString(),
      action: 'Clinical Review',
      clinician: user?.name || 'Clinician',
      reviewed: true
    };
    setAuditTrail(prev => [reviewEntry, ...prev]);
    updateDailyStats('reviewed');
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 80) return '#4CAF50';
    if (confidence >= 60) return '#FF9800';
    return '#f44336';
  };

  const getStatusIcon = () => {
    switch (aiStatus) {
      case 'connected':
        return <Zap size={16} className="status-icon connected" />;
      case 'disconnected':
        return <AlertTriangle size={16} className="status-icon disconnected" />;
      default:
        return <RefreshCw size={16} className="status-icon checking" />;
    }
  };

  return (
    <div className="dashboard-container">
      {/* Background crosses - matching dashboard style */}
      <div className="background-crosses">
        {[...Array(24)].map((_, i) => (
          <span key={i} className={`cross cross-${i + 1}`}>+</span>
        ))}
      </div>

      <Header />

      <main className="dashboard-main-content">
        {/* Header Section */}
        <div className="dashboard-header-section">
          <div className="dashboard-title-section">
            <h1 className="dashboard-title">
              <Brain size={32} className="title-icon" />
              AI DIAGNOSTIC ASSISTANT
            </h1>
            {user && (
              <div className="user-welcome">
                <span>AI-powered diagnosis for <strong>{user.name}</strong></span>
                <div className="ai-status-display">
                  {getStatusIcon()}
                  <span className={`status-text ${aiStatus}`}>
                    {aiStatus === 'connected' ? 'AI Model Online' : 
                     aiStatus === 'disconnected' ? 'AI Model Offline' : 'Checking Status...'}
                  </span>
                </div>
              </div>
            )}
          </div>
          <div className="dashboard-actions">
            <button 
              className="action-btn refresh-btn"
              onClick={checkAIStatus}
              disabled={loading}
            >
              <RefreshCw size={20} />
              Refresh Status
            </button>
            <button 
              className="action-btn debug-btn"
              onClick={debugAIConnection}
              style={{ backgroundColor: '#f59e0b', borderColor: '#f59e0b' }}
            >
              <Zap size={20} />
              Debug AI
            </button>
            <button 
              className="action-btn audit-btn"
              onClick={() => setShowAuditTrail(!showAuditTrail)}
            >
              <FileText size={20} />
              Audit Trail
            </button>
          </div>
        </div>

        {/* Context Info Bar */}
        <div className="context-info-bar">
          <div className="context-badges">
            <span className="context-badge model-badge">
              <Shield size={16} />
              Model: {modelInfo?.name ? `${modelInfo.name} v${modelInfo.version}` : 'MediChain-AI v2.1'}
            </span>
            <span className="context-badge time-badge">
              <Clock size={16} />
              {new Date().toLocaleString()}
            </span>
            <span className="context-badge user-badge">
              <Users size={16} />
              {user?.name || 'Clinician'}
            </span>
          </div>
          <div className="context-controls">
            <label className="toggle-switch">
              <input
                type="checkbox"
                checked={showRationale}
                onChange={(e) => setShowRationale(e.target.checked)}
              />
              <span className="toggle-slider"></span>
              <span>Show AI Rationale</span>
            </label>
          </div>
        </div>

        <div className="dashboard-grid ai-assistant-grid">
          {/* Stats Cards Row - AI Performance Metrics */}
          <div className="stats-cards-row">
            <div className="stat-card ai-stat accuracy-stat">
              <div className="stat-icon ai-icon">
                <TrendingUp size={32} />
              </div>
              <div className="stat-info">
                <span className="stat-label">Model Accuracy</span>
                <span className="stat-value">{modelInfo?.accuracy || 87.5}%</span>
                <span className="stat-trend">+2.3% this month</span>
              </div>
            </div>
            
            <div className="stat-card ai-stat diagnosis-stat">
              <div className="stat-icon ai-icon">
                <Stethoscope size={32} />
              </div>
              <div className="stat-info">
                <span className="stat-label">Diagnoses Today</span>
                <span className="stat-value">{dailyStats.diagnoses}</span>
                <span className="stat-trend">Active sessions</span>
              </div>
            </div>
            
            <div className="stat-card ai-stat review-stat">
              <div className="stat-icon ai-icon">
                <CheckCircle size={32} />
              </div>
              <div className="stat-info">
                <span className="stat-label">Reviewed Cases</span>
                <span className="stat-value">{dailyStats.reviewed}</span>
                <span className="stat-trend">Clinical oversight</span>
              </div>
            </div>
            
            <div className="stat-card ai-stat risk-stat">
              <div className="stat-icon ai-icon">
                <AlertTriangle size={32} />
              </div>
              <div className="stat-info">
                <span className="stat-label">High Risk Cases</span>
                <span className="stat-value">{dailyStats.highRisk}</span>
                <span className="stat-trend">Require attention</span>
              </div>
            </div>
          </div>

          <div className="main-and-sidebar-grid ai-main-grid">
            {/* Main Content Area - Patient Input */}
            <div className="main-content-area">
              <div className="content-card patient-input-card">
                <div className="card-header">
                  <h3>
                    <FileText size={24} />
                    Patient Assessment
                  </h3>
                  <div className="card-status">
                    {aiStatus === 'connected' ? (
                      <span className="status-badge connected">
                        <Zap size={14} />
                        AI Ready
                      </span>
                    ) : (
                      <span className="status-badge disconnected">
                        <AlertTriangle size={14} />
                        AI Offline
                      </span>
                    )}
                  </div>
                </div>
                
                {/* Primary Input */}
                <div className="input-section">
                  <label htmlFor="symptoms-history" className="input-label">
                    <Stethoscope size={16} />
                    Symptoms & Medical History
                  </label>
                  <textarea
                    id="symptoms-history"
                    value={patientInput.symptomsHistory}
                    onChange={(e) => handleInputChange('symptomsHistory', e.target.value)}
                    placeholder={`Describe patient symptoms: ${supportedSymptoms.join(', ') || 'fever, cough, fatigue, shortness of breath, headache, sore throat'}...`}
                    rows="6"
                    className="symptoms-textarea"
                  />
                  <div className="input-hint">
                    <span>💡 AI recognizes: {supportedSymptoms.join(', ') || 'fever, cough, fatigue, shortness of breath, headache, sore throat'}</span>
                  </div>
                </div>

                {/* Quick Patient Info */}
                <div className="patient-info-section">
                  <h4>Patient Information</h4>
                  <div className="quick-info-grid">
                    <div className="quick-input">
                      <label>Age</label>
                      <input
                        type="number"
                        value={patientInput.age}
                        onChange={(e) => handleInputChange('age', e.target.value)}
                        placeholder="Years"
                        min="0"
                        max="120"
                      />
                    </div>
                    <div className="quick-input">
                      <label>Sex</label>
                      <select
                        value={patientInput.sex}
                        onChange={(e) => handleInputChange('sex', e.target.value)}
                      >
                        <option value="">Select</option>
                        <option value="male">Male</option>
                        <option value="female">Female</option>
                        <option value="other">Other</option>
                      </select>
                    </div>
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="action-buttons-section">
                  <button
                    className="analyze-btn primary-btn"
                    onClick={handleAnalyze}
                    disabled={loading || aiStatus !== 'connected' || !patientInput.symptomsHistory.trim()}
                  >
                    {loading ? (
                      <>
                        <div className="spinner"></div>
                        Analyzing...
                      </>
                    ) : (
                      <>
                        <Send size={20} />
                        AI Analyze
                      </>
                    )}
                  </button>
                  <button className="clear-btn secondary-btn" onClick={handleClear}>
                    <RefreshCw size={16} />
                    Clear All
                  </button>
                </div>

                {error && (
                  <div className="error-alert">
                    <AlertTriangle size={20} />
                    <span>{error}</span>
                    {error.includes('Network') && (
                      <button onClick={checkAIStatus} className="retry-link">
                        Retry Connection
                      </button>
                    )}
                  </div>
                )}
              </div>
            </div>

            {/* Sidebar Area - AI Results */}
            <div className="sidebar-area">
              {diagnosisResults ? (
                <>
                  {/* AI Results Card */}
                  <div className="content-card results-card">
                    <div className="card-header">
                      <h3 className="card-title">
                        <Brain size={20} />
                        AI Diagnosis Results
                      </h3>
                      <div 
                        className="confidence-badge"
                        style={{ backgroundColor: getConfidenceColor(diagnosisResults.confidence) }}
                      >
                        {diagnosisResults.confidence}%
                      </div>
                    </div>
                    
                    {/* Primary Diagnosis */}
                    <div className="primary-diagnosis">
                      <div className="diagnosis-content">
                        <h4 className="diagnosis-name">{diagnosisResults.diagnosis}</h4>
                        
                        {showRationale && diagnosisResults.explanation && (
                          <div className="rationale-box">
                            <strong>AI Rationale:</strong>
                            <p>{diagnosisResults.explanation}</p>
                          </div>
                        )}

                        {/* Enhanced Medical Information from AI Assistant */}
                        {diagnosisResults.detected_symptoms && diagnosisResults.detected_symptoms.length > 0 && (
                          <div className="detected-symptoms-section">
                            <strong>Detected Symptoms:</strong>
                            <div className="symptom-chips">
                              {diagnosisResults.detected_symptoms.map((symptom, index) => (
                                <span key={index} className="symptom-chip active">
                                  {symptom.replace('_', ' ')}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Medications Section */}
                        {diagnosisResults.medications && diagnosisResults.medications.length > 0 && (
                          <div className="medications-section">
                            <strong>💊 Recommended Medications:</strong>
                            <div className="medications-list">
                              {diagnosisResults.medications.map((med, index) => (
                                <div key={index} className="medication-item">
                                  <div className="medication-info">
                                    {typeof med === 'string' ? med : (
                                      <>
                                        <div className="med-name">{med.name || med}</div>
                                        {med.dosage && <div className="med-dosage">Dosage: {med.dosage}</div>}
                                        {med.duration && <div className="med-duration">Duration: {med.duration}</div>}
                                        {med.type && <div className="med-type">Type: {med.type}</div>}
                                      </>
                                    )}
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Treatments Section */}
                        {diagnosisResults.treatments && diagnosisResults.treatments.length > 0 && (
                          <div className="treatments-section">
                            <strong>🩺 Treatment Recommendations:</strong>
                            <div className="treatments-list">
                              {diagnosisResults.treatments.map((treatment, index) => (
                                <div key={index} className="treatment-item">
                                  <div className="treatment-bullet">•</div>
                                  <div className="treatment-text">{treatment}</div>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Medical Warnings Section */}
                        {diagnosisResults.medical_warnings && diagnosisResults.medical_warnings.length > 0 && (
                          <div className="medical-warnings-section">
                            <strong>⚠️ Medical Warnings:</strong>
                            <div className="medical-warnings-list">
                              {diagnosisResults.medical_warnings.map((warning, index) => (
                                <div key={index} className="medical-warning-item">
                                  <AlertTriangle size={14} />
                                  <span>{warning}</span>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Patient Advice Section */}
                        {diagnosisResults.patient_advice && (
                          <div className="patient-advice-section">
                            <strong>📋 Patient Advice:</strong>
                            <div className="patient-advice-content">
                              {diagnosisResults.patient_advice}
                            </div>
                          </div>
                        )}

                        {/* Follow-up Recommendations */}
                        {diagnosisResults.follow_up_recommendations && diagnosisResults.follow_up_recommendations.length > 0 && (
                          <div className="followup-section">
                            <strong>📅 Follow-up Recommendations:</strong>
                            <div className="followup-list">
                              {diagnosisResults.follow_up_recommendations.map((recommendation, index) => (
                                <div key={index} className="followup-item">
                                  <div className="followup-bullet">•</div>
                                  <div className="followup-text">{recommendation}</div>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                        {diagnosisResults.parsed_symptoms && (
                          <div className="supporting-symptoms">
                            <strong>Parsed Symptoms:</strong>
                            <div className="symptom-chips">
                              {Object.entries(diagnosisResults.parsed_symptoms)
                                .filter(([_, value]) => value)
                                .map(([symptom, _]) => (
                                  <span key={symptom} className="symptom-chip">
                                    {symptom.replace('_', ' ')}
                                  </span>
                                ))}
                            </div>
                          </div>
                        )}

                        {/* Top Predictions */}
                        {diagnosisResults.top_predictions && diagnosisResults.top_predictions.length > 1 && (
                          <div className="differential-diagnoses">
                            <strong>Alternative Diagnoses:</strong>
                            <div className="diagnosis-list">
                              {diagnosisResults.top_predictions.slice(1, 3).map((pred, index) => (
                                <div key={index} className="diagnosis-item">
                                  <span className="diagnosis-name">
                                    {pred.condition || pred.diagnosis || 'Unknown'}
                                  </span>
                                  <span className="diagnosis-confidence">
                                    {Math.round(pred.confidence || pred.probability || 0)}%
                                  </span>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Warnings */}
                    {diagnosisResults.warnings && diagnosisResults.warnings.length > 0 && (
                      <div className="warnings-section">
                        <h4 className="warning-title">
                          <AlertTriangle size={16} />
                          Clinical Alerts
                        </h4>
                        {diagnosisResults.warnings.map((warning, index) => (
                          <div key={index} className="warning-item">
                            {warning}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Clinical Review Card */}
                  <div className="content-card review-card">
                    <h3 className="card-title">
                      <CheckCircle size={20} />
                      Clinical Review
                    </h3>
                    {!isReviewed ? (
                      <div className="review-section">
                        <p className="review-instruction">
                          Please review the AI diagnosis and mark as clinically validated.
                        </p>
                        <button className="review-action-btn" onClick={markAsReviewed}>
                          <CheckCircle size={16} />
                          Mark as Clinically Reviewed
                        </button>
                      </div>
                    ) : (
                      <div className="reviewed-status">
                        <div className="review-info">
                          <CheckCircle size={16} className="check-icon" />
                          <div>
                            <span>Reviewed by {user?.name || 'Clinician'}</span>
                            <small>{new Date().toLocaleString()}</small>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </>
              ) : (
                /* Empty State */
                <div className="content-card empty-results">
                  <div className="empty-state">
                    <Brain size={48} className="empty-icon" />
                    <h3>Ready for AI Analysis</h3>
                    <p>Enter patient symptoms and history to receive AI-powered diagnostic assistance</p>
                    {aiStatus !== 'connected' && (
                      <div className="connection-warning">
                        <AlertTriangle size={16} />
                        <span>AI service is offline. Please check connection.</span>
                        <button className="connect-btn" onClick={checkAIStatus}>
                          <RefreshCw size={14} />
                          Reconnect
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Safety Disclaimer Footer */}
        <div className="safety-disclaimer">
          <div className="disclaimer-content">
            <AlertTriangle size={20} />
            <div className="disclaimer-text">
              <strong>Medical Disclaimer:</strong> This AI system provides clinical decision support only. 
              All recommendations must be reviewed and validated by a licensed healthcare professional before 
              implementation. This tool does not replace clinical judgment.
            </div>
          </div>
        </div>
      </main>

      {/* Audit Trail Drawer */}
      {showAuditTrail && (
        <div className="audit-overlay" onClick={() => setShowAuditTrail(false)}>
          <div className="audit-drawer" onClick={(e) => e.stopPropagation()}>
            <div className="audit-header">
              <h3>
                <FileText size={20} />
                Audit Trail
              </h3>
              <button onClick={() => setShowAuditTrail(false)} className="close-audit">×</button>
            </div>
            <div className="audit-content">
              {auditTrail.length === 0 ? (
                <div className="no-audit-entries">
                  <Activity size={24} />
                  <p>No audit entries yet</p>
                  <small>AI analyses and clinical reviews will appear here</small>
                </div>
              ) : (
                auditTrail.map((entry, index) => (
                  <div key={index} className="audit-entry">
                    <div className="audit-header-info">
                      <div className="audit-action">{entry.action}</div>
                      <div className="audit-timestamp">{new Date(entry.timestamp).toLocaleString()}</div>
                    </div>
                    {entry.input && <div className="audit-input">Input: {entry.input.substring(0, 100)}...</div>}
                    {entry.result && <div className="audit-result">Result: {entry.result}</div>}
                    {entry.confidence && <div className="audit-confidence">Confidence: {entry.confidence}%</div>}
                    {entry.clinician && <div className="audit-clinician">Clinician: {entry.clinician}</div>}
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AIAssistant;
