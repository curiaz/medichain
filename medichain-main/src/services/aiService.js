import axios from 'axios';

// AI Diagnosis Service - connects to the enhanced AI system
const AI_BASE_URL = process.env.REACT_APP_AI_URL || 'http://localhost:5001';

const api = axios.create({
  baseURL: AI_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60000, // 60 seconds timeout for AI processing
});

// Add response interceptor for better error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.code === 'ECONNREFUSED' || error.code === 'ERR_NETWORK') {
      console.error('AI server is not running or unreachable');
      error.isNetworkError = true;
    }
    return Promise.reject(error);
  }
);

export const aiService = {
  /**
   * Get AI diagnosis based on symptoms
   * @param {Object} diagnosisData - The diagnosis request data
   * @returns {Promise<Object>} Diagnosis response
   */
  getDiagnosis: async (diagnosisData) => {
    try {
      const response = await api.post('/predict', diagnosisData);
      
      // Transform the AI response to match frontend expectations
      const aiData = response.data;
      
      // Handle both normal diagnosis and unknown case responses
      if (aiData.status === 'unknown_case') {
        return {
          success: true,
          data: {
            diagnosis: 'Professional Consultation Required',
            confidence: 0,
            severity: 'High',
            urgency: 'immediate',
            prescription: aiData.message,
            recommendations: aiData.suggested_actions || [],
            ai_model_version: 'MediChain-AI',
            requires_consultation: true,
            explanation: aiData.reasoning?.ai_limitation || 'This symptom combination requires professional medical evaluation.'
          }
        };
      }
      
      // Handle normal diagnosis response
      const analysis = aiData.analysis || {};
      const primaryDiagnosis = analysis.primary_diagnosis || {};
      const recommendations = aiData.recommendations || {};
      
      const transformedData = {
        diagnosis: primaryDiagnosis.condition || 'Unknown',
        confidence: Math.round((primaryDiagnosis.confidence || 0) * 100),
        explanation: primaryDiagnosis.explanation || '',
        prescription: {
          medications: recommendations.medications || [],
          treatments: recommendations.treatments || [],
          instructions: recommendations.lifestyle_advice?.join('; ') || 'Follow up with healthcare provider'
        },
        recommendations: recommendations.lifestyle_advice || [],
        warnings: recommendations.warnings || [],
        differential_diagnoses: analysis.differential_diagnoses || [],
        ai_model_version: 'MediChain-AI',
        timestamp: aiData.timestamp,
        medical_disclaimer: aiData.medical_disclaimer,
        severity: aiData.next_steps?.urgency_level || 'Moderate',
        urgency: aiData.next_steps?.immediate_actions ? 'high' : 'normal'
      };
      
      return {
        success: true,
        data: transformedData
      };
    } catch (error) {
      console.error('AI Diagnosis Error:', error);
      
      if (error.isNetworkError) {
        return {
          success: false,
          error: 'AI server is not available. Please ensure the AI diagnosis server is running on port 5001.',
          isNetworkError: true
        };
      }
      
      return {
        success: false,
        error: error.response?.data?.error || 'Failed to get AI diagnosis',
        details: error.response?.data
      };
    }
  },

  /**
   * Provide feedback on a diagnosis
   * @param {Object} feedbackData - The feedback data
   * @returns {Promise<Object>} Feedback response
   */
  provideFeedback: async (feedbackData) => {
    try {
      const response = await api.post('/submit-feedback', feedbackData);
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      console.error('AI Feedback Error:', error);
      return {
        success: false,
        error: error.response?.data?.error || 'Failed to submit feedback'
      };
    }
  },

  /**
   * Get model information and statistics
   * @returns {Promise<Object>} Model info response
   */
  getModelInfo: async () => {
    try {
      const response = await api.get('/learning-stats');
      const data = response.data;
      
      // Transform the response to match frontend expectations
      const modelInfo = data.model_info || {};
      
      return {
        success: true,
        data: {
          version: modelInfo.name || 'MediChain-AI',
          accuracy: modelInfo.accuracy || '87.5',
          training_samples: modelInfo.total_features || 'N/A',
          last_updated: modelInfo.last_trained || 'Unknown',
          supported_conditions: modelInfo.supported_conditions || 'N/A'
        }
      };
    } catch (error) {
      console.error('AI Model Info Error:', error);
      return {
        success: false,
        error: error.response?.data?.error || 'Failed to get model information'
      };
    }
  },

  /**
   * Health check for the AI service
   * @returns {Promise<Object>} Health status
   */
  healthCheck: async () => {
    try {
      const response = await api.get('/health');
      return {
        success: true,
        data: response.data,
        status: 'connected'
      };
    } catch (error) {
      return {
        success: false,
        error: 'AI service unavailable',
        status: 'disconnected'
      };
    }
  }
};

export default aiService;
